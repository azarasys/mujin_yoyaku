import json
import boto3

sqs = boto3.resource('sqs')

def get_sqs_message(event: dict):
    '''トリガとなるSQSのメッセージを取得する
    '''
    records = event['Records']
    message = records[0]
    message_body = message['body']
    return json.loads(message_body)

def send_sqs_message(sqs_url: str, message: str):
    '''SQSにメッセージを送信する
    '''
    queue = sqs.Queue(sqs_url)
    msg = json.dumps(message)
    item = {
        'MessageBody': msg
    }
    res = queue.send_message(**item)
    print(res)