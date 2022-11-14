import secrets
import string
import os

from layer.dynamodb import put_data
from layer.secrets_manager import get_secret
from layer.sqs import send_sqs_message

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
REGISTER_COMPLITE_URL = os.environ['REGISTER_COMPLITE_URL']
ERROR_URL = os.environ['ERROR_URL']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

# 固定値
PREFIX_KEY = 'user'
SECRET_KEY_CHANNEL_ACCESS_TOKEN = 'channel_access_token'
API_URL_BASE = 'https://api.line.me/v2/bot/user/{user_id}/richmenu/{richmenu_id}'

def _get_random_password(length: int):
    pass_chars = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(pass_chars) for x in range(length))
    return password

def get_input_form_value(event: dict):
    # 入力フォームの会員情報取得
    return {
        'channel_id': event['channel_id'],
        'key': f"{PREFIX_KEY}_{event['line_id']}",
        'line_id': event['line_id'],
        'name': event['name'],
        'email': event['email'],
        'phone': event['phone'],
        'code': event['code'],
        'address1': event['address1'],
        'address2': event['address2'],
        'gender': event['gender'],
        'birthday': event['birthday'],
        'notice': event['notice'],
        'active': True,
        'password': _get_random_password(DEFAULT_PASSWORD_LENGTH)
    }

def lambda_handler(event, context):
    input_form_data = get_input_form_value(event)
    
    # 会員情報登録
    is_put = put_data(
        table_name=DYNAMODB_TABLE_NAME,
        item=input_form_data
    )

    # 登録失敗はエラー画面へリダイレクト
    if not is_put:
        print('Could not registered temporary user.')
        return {
            'statusCode': 302,
            'headers': {
                'Location': ERROR_URL
            }
        }

    # リッチメニューを会員用に更新する
    send_sqs_message(
        sqs_url=CHANGE_RICHMENU_SQS_URL,
        message={'line_id': input_form_data['line_id'], 'menu_type': 'member'}
    )
    
    # 完了画面表示
    return {
        'statusCode': 302,
        'headers': {
            'Location': REGISTER_COMPLITE_URL
        }
    }