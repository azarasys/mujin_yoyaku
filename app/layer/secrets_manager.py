import ast
import boto3
import base64
import os
from datetime import datetime
from botocore.exceptions import ClientError

REGION_NAME = os.environ['REGION_NAME']

def get_secret(secret_name: str):
    session = boto3.sessin.Session()
    client = session.client(service_name='secretsmanager')

    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            print("The requested secret can't be decrypted using the provided KMS key:", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            print("An error occurred on service side:", e)
    else:
        if 'SecretString' in response:
            secret = response['SecretString']
        else:
            secret = base64.b64decode(response['SecretBinary'])
    return ast.literal_eval(secret)

def create_secret(secret_name: str, secret_value: str):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    now = datetime.now()
    try:
        response = client.create_secret(
            Name=secret_name,
            Description=f'Create at {now.strftime("%Y-%m-%d %H:%M%S")}',
            SecretString=secret_value
        )
    except ClientError as e:
        print(f'Couldnt get secret {secret_name}: {e}')
    else:
        print(f'Created secret {secret_name}.')