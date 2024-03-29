import base64
import hashlib
import hmac
import os
import requests
import time
import uuid

from layer.secrets_manager import get_secret
from layer.dynamodb import put_data
from layer.exception import ExceptionTerminated

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']
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

def get_device_list(channel_id: str) -> list[dict]:
    headers = generate_headers(channel_id)
    api_url = f'{SWITCHBOT_API_HOST}/v1.1/devices'
    res = requests.get(url=api_url, headers=headers)
    return res.json()['body']


def lambda_handler(event, context):

    data = event['data']

    channel_id = data['channle_id']
    room_name = data['room_name']
    keypad_name = data['keypad_name']
    key = data['key']
    device_list = get_device_list(channel_id)

    if not device_list:
        raise ExceptionTerminated(f'Could not find devices. {channel_id=}')

    for device in device_list:
        if device['Nmae'] == keypad_name and 'Keypad' in device['deviceType']:
            device_id = device['deviceId']
            item = {
                'channel_id': channel_id,
                'key': key,
                'device_id': device_id,
                'type': device['deviceType'],
                'active': True
            }
            put_data(
                table_name=MAIN_TABLE_NAME,
                item=item
            )
            print(f'register device keypad. {keypad_name}')
            break
    else:
        raise ExceptionTerminated(f'Could not find keypad. {keypad_name}')
    
    return True