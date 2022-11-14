import secrets
import string
import os
import uuid

from layer.dynamodb import put_data

# 環境変数
DEFAULT_PASSWORD_LENGTH = os.environ['DEFAULT_PASSWORD_LENGTH']
TMP_REGISTER_TABLE_NAME = os.environ['TMP_REGISTER_TABLE_NAME']
URL_TABLE_NAME = os.environ['URL_TABLE_NAME']
REGISTER_COMPLITE_URL = os.environ['REGISTER_COMPLITE_URL']

# 固定値
PREFIX_KEY = 'user'

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
    
    is_put = put_data(
        table_name=TMP_REGISTER_TABLE_NAME,
        item=input_form_data
    )

    if not is_put:
        raise Exception('Could not registered temporary user.')
    
    # 各チャンネル用Lineログイン画面URL取得
    return {
        'statusCode': 302,
        'headers': {
            'Location': REGISTER_COMPLITE_URL
        }
    }