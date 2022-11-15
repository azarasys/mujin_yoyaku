import os
from datetime import datetime
from layer.sqs import send_sqs_message

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
RESERVE_COMPLITE_URL = os.environ['RESERVE_COMPLITE_URL']
RESERVE_SQS_URL = os.environ['RESERVE_SQS_URL']

# 固定値
PREFIX_KEY = 'reserve'

def get_input_form_value(event: dict):
    # 入力フォームの会員情報取得
    start_dt = datetime.strptime(event['start_date'] + event['start_time'], '%Y年%m月%d日%H:%M')
    end_dt = datetime.strptime(event['end_date'] + event['end_time'], '%Y年%m月%d日%H:%M')

    return {
        'channel_id': event['channel_id'],
        'key': f"{PREFIX_KEY}_{event['line_id']}_{start_dt.strftime('%Y%m%d%H%M')}_{event['line_id']}",
        'line_id': event['line_id'],
        'room_id': event['room_id'],
        'start_time': start_dt,
        'end_time': end_dt,
        'active': True
    }

def lambda_handler(event, context):

    input_form_data = get_input_form_value(event)

    send_sqs_message(RESERVE_SQS_URL, input_form_data)

    # 完了画面表示
    return {
        'statusCode': 302,
        'headers': {
            'Location': RESERVE_COMPLITE_URL
        }
    }