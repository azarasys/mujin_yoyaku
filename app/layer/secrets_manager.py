import boto3
import base64
import json
import os
from datetime import datetime
from botocore.exceptions import ClientError

REGION_NAME = os.environ['REGION_NAME']
RECOVERY_WINDOW_IN_DAYS = os.environ['RECOVERY_WINDOW_IN_DAYS']

def get_secret(secret_name: str):
    ''' シークレットキーを取得する
    '''
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        print(f'Couldnt fetch secret {secret_name}: {e}')
    else:
        print(f'Get secrets {secret_name}')
        if 'SecretString' in response:
            return response['SecretString']
        else:
            return base64.b64decode(response['SecretBinary'])

def create_secret(secret_name: str, secret_value: dict):
    ''' キーペアのシークレットキーを作成する
    '''
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        response = client.create_secret(
            Name=secret_name,
            Description=f'Create at {datetime.now().strftime("%Y-%m-%d %H:%M%S")}',
            SecretString=json.dumps(secret_value)
        )
    except ClientError as e:
        print(f'Couldnt get secret {secret_name}: {e}')
    else:
        print(f'Created secret {secret_name}.')

def update_secret(secret_name: str, secret_value: str):
    ''' キーペアのシークレットキーを更新する
    '''
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        response = client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(secret_value)
        )
    except ClientError as e:
        print(f'Couldnt upgrade secret {secret_name}: {e}')
    else:
        print(f'Updated secret {secret_name}.')

def delete_secret(secret_name: str):
    ''' シークレットキーを更新する
    '''
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        response = client.delete_secret(
            SecretId=secret_name,
            RecoveryWindowInDays=RECOVERY_WINDOW_IN_DAYS
        )
    except ClientError as e:
        print(f'Couldnt delete secret {secret_name}: {e}')
    else:
        print(f'Deleted secret {secret_name}.')