import base64
import json
import os
import requests
import time
import hashlib
import hmac
import uuid

from layer.sqs import get_sqs_message
from layer.dynamodb import get_device_by_channel_room
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

def delete_onetime_password(password_id: int, device_id: str, headers: dict) -> dict:
    url = f'{SWITCHBOT_API_HOST}/v1.1/devices/{device_id}/commands'
    params = {
        'commandType': 'command',
        'command': 'deleteKey',
        'parameter': {
            'id': password_id,
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
    device = get_device_by_channel_room(data['channel_id'], data['room_id'])
    headers = generate_headers(data['channel_id'])
    res = delete_onetime_password(
        password_id=data['password_id'],
        device_id=device['device_id'],
        headers=headers
    )

    if not res['message'] == 'success':
        raise Exception(res)

    return True