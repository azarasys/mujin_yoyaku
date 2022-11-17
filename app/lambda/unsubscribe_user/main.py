import os
from datetime import datetime

from layer.notice import send_line_push_massage
from layer.sqs import get_sqs_message, send_sqs_message
from layer.dynamodb import get_user_by_id_channel, put_data

# 環境変数
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']

def generate_push_message(data: dict):
    data['body1_id'] = '103'
    data['body1_args'] = []
    data['body2_id'] = '203'
    data['body2_args'] = []
    data['body3_id'] = '303'
    data['body3_args'] = []
    return data

def lambda_handler(event, content):
    data = get_sqs_message(event)
    user = get_user_by_id_channel(data['channel_id'], data['line_id'])

    # 多重起動は終了
    if user['active'] == False:
        print(f'{user["line_id"]} had unsubscribe.')
        return True

    user['active'] = False
    user['end_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 登録によって会員情報を上書き
    put_data(
        table_name=DYNAMODB_TABLE_NAME,
        item=data
    )

    # リッチメニューをデフォルトに更新する
    send_sqs_message(
        sqs_url=CHANGE_RICHMENU_SQS_URL,
        message={'line_id': data['line_id'], 'menu_type': data['type']}
    )

    # 会員登録できたとプッシュメッセージ
    data = generate_push_message(data)

    send_line_push_massage(data)

    return True    