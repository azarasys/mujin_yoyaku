import boto3
import json
import os
import requests

from secrets_manager import get_secret

# 環境変数
S3_CONFIG_BUCKET_NAME = os.environ['NOTICE_S3_BUCKET_NAME']
MESSAGE_SUBJECT_TEMPLATE_JSON_PATH = os.environ['MESSAGE_SUBJECT_TEMPLATE_JSON_PATH']
MESSAGE_BODY_TEMPLATE_JSON_PATH = os.environ['MESSAGE_BODY_TEMPLATE_JSON_PATH']
SMS_TOPIC_ARN = os.environ['SMS_TOPIC_ARN']
EMAIL_TOPIC_ARN = os.environ['EMAIL_TOPIC_ARN']
LINE_TOPIC_ARN = os.environ['LINE_TOPIC_ARN']

s3 = boto3.resorce('s3')
sns = boto3.resorce('sns')
bucket = s3.Bucket(S3_CONFIG_BUCKET_NAME)

def generate_subject(params: dict):
    subject_template = json.loads(bucket.Object(MESSAGE_SUBJECT_TEMPLATE_JSON_PATH).get()['Body'].decode('utf-8'))
    subject1 = ''
    subject2 = ''
    subject3 = ''
    
    subject1_id = params.get('subject1_id')
    if subject1_id:
        subject1 = subject_template.get(subject1_id).format(params.get('subject1_args'))

    subject2_id = params.get('subject2_id')
    if subject2_id:
        subject2 = subject_template.get(subject2_id).format(params.get('subject2_args'))

    subject3_id = params.get('subject3_id')
    if subject3_id:
        subject3 = subject_template.get(subject3_id).format(params.get('subject3_args'))

    return f'{subject1}{subject2}{subject3}'

def generate_body(params: dict):
    body_template = json.loads(bucket.Object(MESSAGE_BODY_TEMPLATE_JSON_PATH).get()['Body'].decode('utf-8'))
    body1 = ''
    body2 = ''
    body3 = ''
    
    body1_id = params.get('body1_id')
    if body1_id:
        body1 = body_template.get(body1_id).format(params.get('body1_args'))

    body2_id = params.get('body2_id')
    if body2_id:
        body2 = body_template.get(body2_id).format(params.get('body2_args'))

    body3_id = params.get('body3_id')
    if body3_id:
        body3 = body_template.get(body3_id).format(params.get('body3_args'))

    return '\n\n'.join([body for body in [body1, body2, body3] if body])

def send_sms(params: dict):
    # いつか実装する
    pass

def send_line_push_massage(params):
    request_json = {
        'to': params['line_id'],
        'messages': {
            'type': 'text',
            'text': generate_body(params)
        }
    }
    
    channel_secret = get_secret(params['channel_id'])

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

def send_email(params: dict):
    # いつか実装する
    pass

def send_message(params: dict):
    print('send message start.')

    # 件名を組み立てる
    params['Subject'] = generate_subject(params)
    print('complete generate subject.')
    # 本文を組み立てる
    params['Body']  = generate_body(params)
    print('complete generate body.')
    # 送信する

    if 'LINE' in params['Notice'].keys():
        send_line_push_massage(params)
        print('send line.')
    if 'EMAIL' in params['Notice'].keys():
        send_email(params)
        print('send email.')
    
    print('send message end.')
    
    return True