import secrets
import string
import os

from layer.notice import send_line_push_massage
from layer.dynamodb import put_data
from layer.sqs import get_sqs_message, send_sqs_message

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
HOW_USE_URL = os.environ['HOW_USE_URL']
ERROR_URL = os.environ['ERROR_URL']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

# 固定値
PREFIX_KEY = 'user'
SECRET_KEY_CHANNEL_ACCESS_TOKEN = 'channel_access_token'
API_URL_BASE = 'https://api.line.me/v2/bot/user/{user_id}/richmenu/{richmenu_id}'


def generate_push_message(data: dict):
    data['body1_id'] = '102'
    data['body1_args'] = []
    data['body2_id'] = '202'
    data['body2_args'] = []
    data['body3_id'] = '302'
    data['body3_args'] = [HOW_USE_URL]
    return data

def lambda_handler(event, context):
    data = get_sqs_message(event)
    
    # 会員情報登録
    put_data(
        table_name=DYNAMODB_TABLE_NAME,
        item=data
    )

    # リッチメニューを会員用に更新する
    send_sqs_message(
        sqs_url=CHANGE_RICHMENU_SQS_URL,
        message={'line_id': data['line_id'], 'menu_type': data['type']}
    )

    # 会員登録できたとプッシュメッセージ
    data = generate_push_message(data)

    send_line_push_massage(data)
    
    return True