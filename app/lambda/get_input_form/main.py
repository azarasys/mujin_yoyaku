import os
from datetime import datetime
from layer.sqs import send_sqs_message

CHANNEL_ID = os.environ['CHANNEL_ID']
RESERVE_SQS_URL = os.environ['RESERVE_SQS_URL']
REGISTER_SQS_URL = os.environ['REGISTER_SQS_URL']
UNSUBSCRIBE_SQS_URL = os.environ['UNSUBSCRIBE_SQS_URL']

def get_input_form_value(event: dict):
    # 入力フォームの会員情報取得
    event['channel_id'] = CHANNEL_ID
    if event['type'] == 'reserve':
        start_time = datetime.strptime(event['start_date'] + event['start_time'], '%Y年%m月%d日%H:%M')
        end_time = datetime.strptime(event['end_date'] + event['end_time'], '%Y年%m月%d日%H:%M')
        event['key'] = f"reserve_{event['line_id']}_{start_time.strftime('%Y%m%d%H%M')}_{event['line_id']}"
        event['start_time'] = start_time
        event['end_time'] = end_time
        event['active'] = True
    elif event['type'] == 'register':
        event['key'] =  f"user_{event['line_id']}",
        event['active'] = True
        event['is_woner'] = False
    elif event['type'] == 'unsubscribe':
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