import os

from layer.dynamodb import put_data

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']

def lambda_handler(event, context):
    data = event['data']
    
    # 登録
    put_data(
        table_name=MAIN_TABLE_NAME,
        item=data
    )
    
    return True