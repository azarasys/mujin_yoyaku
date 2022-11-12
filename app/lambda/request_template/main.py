import json
import os
import boto3
import jinja2

# 環境変数
S3_CONFIG_BUCKET_NAME = os.environ['S3_CONFIG_BUCKET_NAME']

# 固定値
PREFIX_TEMPLATE_PATH = 'template'

s3 = boto3.resource('s3')
jinja2_env = jinja2.Environment(
    variable_start_string='${',
    variable_end_string='}',
    block_start_string='--{%'
)

def lambda_handler(event, context):
    params = event.get('queryStringParameters')
    template = params['template']
    
    if not params:
        # 多重起動はここで排除
        return True
    
    bucket = s3.Bucket(S3_CONFIG_BUCKET_NAME)
    
    template = bucket.Object(f'{PREFIX_TEMPLATE_PATH}/{template}.html').get()['Body'].read().decode('utf-8')
    str_html = jinja2_env.from_string(template).render(params)
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html; charset=utf-8;'},
        'body': str_html
    }