import os
import random
from datetime import datetime
from layer.sqs import send_sqs_message
from layer.dynamodb import get_password_by_channel_date

CHANNEL_ID = os.environ['CHANNEL_ID']
RESERVE_SQS_URL = os.environ['RESERVE_SQS_URL']
REGISTER_SQS_URL = os.environ['REGISTER_SQS_URL']
UNSUBSCRIBE_SQS_URL = os.environ['UNSUBSCRIBE_SQS_URL']
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']

# 固定値
DEFAULT_MIN_NUM = 0
DEFAULT_MAX_NUM = 10

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

def get_input_form_value(event: dict):
    # 入力フォームの会員情報取得
    event['channel_id'] = CHANNEL_ID
    if event['type'] == 'reserve':
        start_time = datetime.strptime(event['start_date'] + event['start_time'], '%Y年%m月%d日%H:%M')
        end_time = datetime.strptime(event['end_date'] + event['end_time'], '%Y年%m月%d日%H:%M')
        event['key'] = f"reserve_{event['line_id']}_{start_time.strftime('%Y%m%d%H%M')}_{event['line_id']}"
        event['start_time'] = start_time
        event['end_time'] = end_time
        event['password'] = generate_random_password(CHANNEL_ID, start_time)
        event['active'] = True
    elif event['type'] == 'register':
        event['key'] =  f"user_{event['line_id']}",
        event['active'] = True
        event['is_woner'] = False
    elif event['type'] == 'unsubscribe':
        event['key'] = f"unsbscribe_{event['line_id']}"
    elif event['type'] == 'cancel':
        event['key'] = f"unsbscribe_{event['line_id']}"

    return event

def lambda_handler(event, context):
    data = get_input_form_value(event)
    
    # 予約
    if data['type'] == 'reserve':
        sqs_url = RESERVE_SQS_URL
    # ユーザ登録
    elif data['type'] == 'register':
        sqs_url = REGISTER_SQS_URL
    # 退会
    else:
        sqs_url = UNSUBSCRIBE_SQS_URL

    send_sqs_message(sqs_url, data)

    return True