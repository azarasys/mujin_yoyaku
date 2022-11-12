import os
import requests
import boto3
from layer.dynamodb import get_service_by_id, put_data
from layer.secrets_manager import get_secret
from layer.notice import send_user_register_form_url

LINE_API_URL_AUTH = os.environ['LINE_API_URL_AUTH']
LINE_API_URL_VERIFY = os.environ['LINE_API_URL_VERIFY']
TOKEN_TABLE_NAME = os.environ['TOKEN_TABLE_NAME']
LOGIN_COMPLITE_URL = os.environ['LOGIN_COMPLITE_URL']

def __get_channel_id(event: dict) -> str:
    # リクエスト元のを取得
    service_id = event['requestContext']['stage']
    return get_service_by_id(service_id)

def __get_host_uri(event: dict) -> str:
    # リクエスト元のURIを取得
    host = event['headers']['Host']
    path = event['path']
    return f'{host}/{path}'

def __put_user_token(user_id: str, token: str, channel_id: str, expire_at: int):
    is_put_token = put_data(
        table_name=TOKEN_TABLE_NAME,
        item={
            'UserId': user_id,
            'Token': token,
            'ChannelId': channel_id,
            'ExpireAt': expire_at
        }
    )
    if not is_put_token:
        raise Exception('Could not put token.')

def lambda_handler(event, context):
    channel_id = __get_channel_id(event)
    client_secret = get_secret(channel_id)
    auth_res = requests.post(
        url=LINE_API_URL_AUTH,
        data={
            'grant_type': 'authorization_code',
            'code': event['queryStringParameters']['code'],
            'redirect_uri': __get_host_uri(event),
            'client_id': channel_id,
            'client_secret': client_secret
        }
        
    ).json()
    data = {
        'id_token': auth_res['id_token'],
        'client_id': channel_id
    }
    verify_res = requests.post(
        url=LINE_API_URL_VERIFY,
        data=data
    ).json()
    verify_res.update(data)

    # ユーザ認証トークン登録
    __put_user_token(
        user_id=verify_res['sub'],
        token=auth_res['id_token'],
        channel_id=channel_id,
        expire_at=verify_res['exp']
    )

    # 会員登録フォーム発行
    send_user_register_form_url(
        channel_id=channel_id,
        user_id=verify_res['sub']
    )

    return {
        'statusCode': 302,
        'headers': {
            'Location': LOGIN_COMPLITE_URL
        }
    }
