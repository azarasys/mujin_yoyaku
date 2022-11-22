import base64
import json
import os
import requests
import time
import hashlib
import hmac
import uuid
from datetime import datetime

from layer.dynamodb import get_reserves_by_room_start, get_device_by_channel_room
from layer.secrets_manager import get_secret

# 環境変数
SWITCHBOT_API_HOST = os.environ['SWITCHBOT_API_HOST']


def generate_headers(channel_id: str) -> dict:
    open_token = get_secret(f'switchbot_open_token_{channel_id}')
    time_stamp = str(int(round(time.time() * 1000)))
    nonce = str(uuid.uuid4())

    string_to_sign = bytes(f'{open_token}{time_stamp}{nonce}', 'utf-8')
    secret = get_secret(f'switchbot_secret_{channel_id}')
    bytes_secret = bytes(secret, 'utf-8')
    sign = base64.b64encode(hmac.new(bytes_secret, msg=string_to_sign, digestmod=hashlib.sha256).digest())

    return {
        'Authorization': open_token,
        'Content-Type': 'application/json; charset=utf8',
        'sign': sign,
        't': time_stamp,
        'none': nonce
    }

def register_onetime_password(room_id: str, line_id: str, device_id: str, start_time: str, end_time: str, password: str, headers: dict) -> dict:
    
    url = f'{SWITCHBOT_API_HOST}/v1.1/devices/{device_id}/commands'
    start_time = datetime.strptime(start_time,  '%Y年%m月%d日%H:%M')
    end_time = datetime.strptime(end_time,  '%Y年%m月%d日%H:%M')
    params = {
        'commandType': 'command',
        'command': 'createKey',
        'parameter': {
            'name': f'{room_id}_{line_id}_{start_time}',
            'type': 'timeLimit',
            'password': password,
            'startTime': int(start_time.timestamp()),
            'endTime': int(end_time.timestamp())
        }
    }

    res = requests.post(
        url=url,
        data=json.dumps(params),
        header=headers
    )

    return res.json()

def get_registered_password_id(room_id: str, line_id: str, device_id: str, start_time: str, headers: dict) -> str:
    url = f'{SWITCHBOT_API_HOST}/v1.1/devices'
    device_list = requests.get(url, headers=headers).json()['body']['deviceList']
    name = f'{room_id}_{line_id}_{start_time}'
    for device in device_list:
        if device_id == device['deviceId']:
            target_key = [key for key in device['keyList'] if key['name'] == name][0]
            return target_key['id']
    return ''

def lambda_handler(event, context):
    data = event['data']

    reserve = get_reserves_by_room_start(data['room_id'], data['start_time'])
    device = get_device_by_channel_room(reserve['channel_id'], reserve['room_id'])
    headers = generate_headers(data['channel_id'])
    res = register_onetime_password(
        room_id=reserve['room_id'],
        line_id=reserve['line_id'],
        device_id=device['device_id'],
        start_time=reserve['start_time'],
        end_time=reserve['end_time'],
        password=reserve['password'],
        headers=headers
    )

    if not res['message'] == 'success' and not res['message'] == 'Name already exists':
        return False

    return True