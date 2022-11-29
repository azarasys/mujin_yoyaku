import boto3
import json
import os
import requests

from layer.secrets_manager import get_secret

# 環境変数
S3_CONFIG_BUCKET_NAME = os.environ['S3_CONFIG_BUCKET_NAME']
MESSAGE_BODY_TEMPLATE_JSON_PATH = os.environ['MESSAGE_BODY_TEMPLATE_JSON_PATH']

s3 = boto3.resorce('s3')
sns = boto3.resorce('sns')
bucket = s3.Bucket(S3_CONFIG_BUCKET_NAME)

def generate_body(data: dict):
    body_template = json.loads(bucket.Object(MESSAGE_BODY_TEMPLATE_JSON_PATH).get()['Body'].decode('utf-8'))
    body1 = ''
    body2 = ''
    body3 = ''
    
    body1_id = data.get('body1_id')
    if body1_id:
        body1 = body_template.get(body1_id).format(data.get('body1_args'))

    body2_id = data.get('body2_id')
    if body2_id:
        body2 = body_template.get(body2_id).format(data.get('body2_args'))

    body3_id = data.get('body3_id')
    if body3_id:
        body3 = body_template.get(body3_id).format(data.get('body3_args'))

    return '\n\n'.join([body for body in [body1, body2, body3] if body])


def lambda_handler(event, context):
    data = event['data']

    request_json = {
        'to': data['line_id'],
        'messages': {
            'type': 'text',
            'text': generate_body(data)
        }
    }
    
    channel_secret = get_secret(data['channel_id'])

    headers = {
        'Authorization': f'Bearer {channel_secret}',
        'Content-Type': 'application/json'
    }

    try:
        res = requests.post(
            headers=headers,
            json=request_json
        )
    except Exception:
        print(f'Could not sended line message.')
        raise

    print(res.json())

    return True