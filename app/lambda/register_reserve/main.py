import os
import random
from datetime import datetime

from layer.sqs import get_sqs_message, send_sqs_message
from layer.dynamodb import put_data, get_reserves_by_room_start, get_password_by_channel_date
from layer.notice import send_line_push_massage

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

# 固定値
DEFAULT_MIN_NUM = 0
DEFAULT_MAX_NUM = 10
WEEK_DAYS = {0: '月', 1: '火', 2: '水', 3: '木', 4: '金', 5: '土', 6: '日'}

def generate_push_message(data: dict, is_reserve: bool=True):
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


def lambda_handler(event, context):

    data = get_sqs_message(event)

    reserve = get_reserves_by_room_start(data['room_id'], data['start_time'])

    is_reserve = True if not reserve else False
    # 多重起動を考慮
    if is_reserve and all([reserve.get('channel_id') == data['channel_id'], reserve.get('line_id') == data['line_id']]):
        print('this is multiple start.')
        return True

    if is_reserve:
        # 予約登録
        data['password'] = generate_random_password(data['channel_id'], data['start_time'])
        put_data(data)
         # リッチメニューを予約確認に更新する
        send_sqs_message(
            sqs_url=CHANGE_RICHMENU_SQS_URL,
            message={'line_id': data['line_id'], 'menu_type': data['type']}
        )
    
    data = generate_push_message(data, is_reserve)

    send_line_push_massage(data)

    return True