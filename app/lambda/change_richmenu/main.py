import os
import requests

from layer.secrets_manager import get_secret
from layer.sqs import get_sqs_message

# 環境変数
DEFAULT_RICHMENU_ID = os.environ['DEFAULT_RICHMENU_ID']
MENBER_RICHMENU_ID = os.environ['MENBER_RICHMENU_ID']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

# 固定値
SECRET_KEY_CHANNEL_ACCESS_TOKEN = 'channel_access_token'
API_URL_BASE = 'https://api.line.me/v2/bot/user/{user_id}/richmenu/{richmenu_id}'


def change_richmenu(line_id: str, menu_type: str):
    '''リッチメニューを変更する
    '''
    token = get_secret(SECRET_KEY_CHANNEL_ACCESS_TOKEN)
    headers = {
        'Authorization': f'Bearer {token}'
    }

    richmenu_id = MENBER_RICHMENU_ID if menu_type == 'member' else DEFAULT_RICHMENU_ID

    res = requests.post(
        url=API_URL_BASE.format(user_id=line_id, richmenu_id=richmenu_id),
        headers=headers
    )

    if res.status_code in [429, 500, 503, 504]:
        print(res.json())
        raise Exception(res.json())

    print(res.json())

def lambda_handler(event, context):
    params = get_sqs_message(event)

    change_richmenu(**params)