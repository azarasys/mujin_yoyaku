import os
from layer.dynamodb import update_active_false

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']

def lambda_handler(event, context):
    data = event['data']

    # データを非活性に更新
    update_active_false(
        channel_id=data['channel_id'],
        key=data['key']
    )

    return True