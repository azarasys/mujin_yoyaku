import os
import random
from datetime import datetime

from layer.sqs import get_sqs_message
from layer.dynamodb import put_data, get_reserves_by_room_start, get_password_by_channel_date
from layer.notice import send_line_push_massage

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']

# 固定値
DEFAULT_MIN_NUM = 0
DEFAULT_MAX_NUM = 10
WEEK_DAYS = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}

def generate_push_message(params: dict, is_reserve: bool=True):
    start_dt = datetime.strptime(params['start_time'], '%Y%m%d%H%M')
    end_dt = datetime.strptime(params['end_time'], '%Y%m%d%H%M')
    date_str = f"{start_dt.strftime('%Y年%m月%d日')}({WEEK_DAYS[start_dt.weekday()]})"
    start_time = f'{str(start_dt.hour).zfill(2)}:{str(start_dt.min).zfill(2)}'
    end_time = f'{str(end_dt.hour).zfill(2)}:{str(end_dt.min).zfill(2)}'
    params['body1_id'] = '100' if is_reserve else '101'
    params['body1_args'] = []
    params['body2_id'] = '200' if is_reserve else '201'
    params['body2_args'] = [date_str, start_time, end_time]
    params['body3_id'] = '300' if is_reserve else '301'
    params['body3_args'] = []
    return params


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

def check_reserve(room_id: str, start_time: str) -> bool:
    '''予約時間が重複するか確認する
    '''
    data = get_reserves_by_room_start(room_id, start_time)
    return True if not data else False


def lambda_handler(event, context):

    params = get_sqs_message(event)

    is_reserve = check_reserve(params['room_id'], params['start_time'])

    if is_reserve:
        # 予約登録
        params['password'] = generate_random_password(params['channel_id'], params['start_time'])
        put_data(params)
    
    params = generate_push_message(params, is_reserve)

    send_line_push_massage(params)

    return True