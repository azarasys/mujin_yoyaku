import base64
import json
import os
import random
import requests
import time
import hashlib
import hmac
import uuid
from datetime import datetime

from layer.sqs import get_sqs_message, send_sqs_message
from layer.dynamodb import put_data, get_reserves_by_room_start, get_password_by_channel_date, get_device_by_channel_room
from layer.notice import send_line_push_massage
from layer.secrets_manager import get_secret

# 環境変数
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
SWITCHBOT_API_HOST = os.environ['SWITCHBOT_API_HOST']
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

# 固定値
DEFAULT_MIN_NUM = 0
DEFAULT_MAX_NUM = 10
WEEK_DAYS = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}

def generate_push_message(data: dict, is_reserve: bool, is_error: bool):
    start_dt = datetime.strptime(data['start_time'], '%Y%m%d%H%M')
    end_dt = datetime.strptime(data['end_time'], '%Y%m%d%H%M')
    date_str = f"{start_dt.strftime('%Y年%m月%d日')}({WEEK_DAYS[start_dt.weekday()]})"
    start_time = f'{str(start_dt.hour).zfill(2)}:{str(start_dt.min).zfill(2)}'
    end_time = f'{str(end_dt.hour).zfill(2)}:{str(end_dt.min).zfill(2)}'
    data['body1_id'] = '100' if is_reserve else '101'
    data['body1_args'] = []
    data['body2_id'] = '200' if is_reserve else '201'
    data['body2_args'] = [date_str, start_time, end_time]
    data['body3_id'] = '300' if is_reserve else '301'
    data['body3_args'] = []
    if is_error:
        data['body1_id'] = '111'
        data['body2_id'] = '211'
        data['body3_id'] = '311'
    return data


def generate_rondom_numbers() -> str:
    '''連続しないランダムな整数の羅列を生成する
    '''
    numbers = [str(random.randint(DEFAULT_MIN_NUM, DEFAULT_MAX_NUM))]
    while len(numbers) < DEFAULT_PASSWORD_LENGTH:
        n = random.randint(DEFAULT_MIN_NUM, DEFAULT_MAX_NUM)
        if numbers[-1] != n:
            numbers.append(str(n))
    return ''.join(numbers)

def generate_random_password(channel_id: str, start_time: str) -> str:
    '''チャネルの同一日に存在しないパスワードを生成する
    '''
    items = get_password_by_channel_date(channel_id, start_time)
    
    passwords = [item['password'] for item in items]

    while True:
        numbers = generate_rondom_numbers()
        if not numbers in passwords:
            break

    return numbers 

def check_duplicate_reserve(reserve: dict, data: dict) -> bool:
    '''予約時間が重複するか確認する
    '''
    if not reserve:
        return True

    return False

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

def register_onetime_password(data: dict) -> dict:
    device = get_device_by_channel_room(data['channel_id'], data['room_id'])
    url = f'{SWITCHBOT_API_HOST}/v1.1/devices{device["device_id"]}/commands'
    start_time = datetime.strptime(data['start_time'],  '%Y年%m月%d日%H:%M')
    end_time = datetime.strptime(data['end_time'],  '%Y年%m月%d日%H:%M')
    params = {
        'name': f'{data["room_id"]}_{data["line_id"]}_{data["start_time"]}',
        'type': 'timeLimit',
        'password': data['password'],
        'startTime': int(start_time.timestamp()),
        'endTime': int(end_time.timestamp()),
    }

    headers = generate_headers(data['channel_id'])

    res = requests.post(
        url=url,
        data=json.dumps(params),
        header=headers
    )

    return res.json()

def register_reserve(data: dict) -> bool:
    # 予約登録
    data['password'] = generate_random_password(data['channel_id'], data['start_time'])
    res = register_onetime_password(data)
    if not res['statusCode'] == 100:
        print(res)
        return False

    put_data(
        table_name=DYNAMODB_TABLE_NAME,
        item=data
    )

        # リッチメニューを予約確認に更新する
    send_sqs_message(
        sqs_url=CHANGE_RICHMENU_SQS_URL,
        message={'line_id': data['line_id'], 'menu_type': data['type']}
    )
    return True

def lambda_handler(event, context):

    data = get_sqs_message(event)

    reserve = get_reserves_by_room_start(data['room_id'], data['start_time'])
    is_error = False
    is_reserve = True if not reserve else False
    # 多重起動を考慮
    if is_reserve and all([reserve.get('channel_id') == data['channel_id'], reserve.get('line_id') == data['line_id']]):
        print('this is multiple start.')
        return True

    if is_reserve:
        is_error = register_reserve()
        
    
    data = generate_push_message(data, is_reserve, is_error)

    send_line_push_massage(data)

    return True