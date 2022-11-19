import base64
import hashlib
import hmac
import json
import os
import requests
import time
import uuid

from layer.sqs import get_sqs_message
from layer.notice import send_line_push_massage
from layer.secrets_manager import get_secret
from layer.dynamodb import get_user_by_owner, put_data

# 環境変数
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
SWITCHBOT_API_HOST = os.environ['SWITCHBOT_API_HOST']

def generate_push_message(channel_id: str, room_name: str):
    data = {
        'channel_id': channel_id,
        'line_id': get_user_by_owner(channel_id)
    }
    data['body1_id'] = '900'
    data['body1_args'] = []
    data['body2_id'] = '901'
    data['body2_args'] = [room_name]
    data['body3_id'] = ''
    data['body3_args'] = []
    return data

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

def get_device_list(channel_id: str) -> list[dict]:
    headers = generate_headers(channel_id)
    api_url = f'{SWITCHBOT_API_HOST}/v1.1/devices'
    res = requests.get(url=api_url, headers=headers)
    return res.json()['body']


def lambda_handler(event, context):

    msg = get_sqs_message(event)

    channel_id = msg['channle_id']
    room_name = msg['room_name']
    keypad_name = msg['keypad_name']
    device_list = get_device_list(channel_id)

    if not device_list:
        raise Exception(f'Could not find devices. {channel_id=}')

    for device in device_list:
        if device['Nmae'] == keypad_name and 'Keypad' in device['deviceType']:
            device_id = device['deviceId']
            item = {
                'channel_id': channel_id,
                'key': f'device_{room_name}_{device_id}',
                'device_id': device_id,
                'type': device['deviceType'],
                'active': True
            }
            put_data(
                table_name=DYNAMODB_TABLE_NAME,
                item=item
            )
            print(f'register device keypad. evice_{room_name}_{device_id}')
            break
    
    data = generate_push_message(channel_id, room_name)

    send_line_push_massage(data)
    
    return True