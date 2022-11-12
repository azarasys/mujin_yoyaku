import os
import requests
import boto3
from layer.dynamodb import get_service_by_id, put_data
from layer.secrets_manager import get_secret
from layer.notice import send_line_push_massage, generate_body

LINE_API_URL_AUTH = os.environ['LINE_API_URL_AUTH']
LINE_API_URL_VERIFY = os.environ['LINE_API_URL_VERIFY']
TOKEN_TABLE_NAME = os.environ['TOKEN_TABLE_NAME']
LOGIN_COMPLITE_URL = os.environ['LOGIN_COMPLITE_URL']
REGISTER_FORM_URL = os.environ['REGISTER_FORM_URL']

def __get_channel_id(event: dict) -> str:
    '''リクエスト元のを取得
    '''
    service_id = event['requestContext']['stage']
    return get_service_by_id(service_id)

def __get_host_uri(event: dict) -> str:
    '''リクエスト元のURIを取得
    '''
    host = event['headers']['Host']
    path = event['path']
    return f'{host}/{path}'

def __put_user_token(line_id: str, token: str, channel_id: str, expire_at: int):
    '''ユーザ認証トークン登録
    '''
    is_put_token = put_data(
        table_name=TOKEN_TABLE_NAME,
        item={
            'line_id': line_id,
            'token': token,
            'channel_id': channel_id,
            'expire_at': expire_at
        }
    )
    if not is_put_token:
        raise Exception('Could not put token.')

def __generate_massage_params(channel_id: str, line_id: str):
    '''送信用メッセージパラメータ作成
    '''
    return {
        'line_id': line_id,
        'channel_id': channel_id,
        'body1_id': '100',
        'body1_args': [REGISTER_FORM_URL],
        'body2_id': '',
        'body2_args': '',
        'body3_id': '',
        'body3_args': ''
    }

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

    
    line_id =  verify_res['sub'],
    token =  auth_res['id_token'],
    expire_at =  verify_res['exp']

    # ユーザ認証トークン登録
    __put_user_token(
        user_id=line_id,
        token=token,
        channel_id=channel_id,
        expire_at=expire_at
    )

    # 会員登録フォーム発行
    send_line_push_massage(__generate_massage_params(channel_id, line_id))

    return {
        'statusCode': 302,
        'headers': {
            'Location': LOGIN_COMPLITE_URL
        }
    }
