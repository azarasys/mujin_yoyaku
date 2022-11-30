import os
from datetime import datetime

from layer.dynamodb import update_active_false

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']


def lambda_handler(event, content):
    data = event['data']

    update_active_false(
        channel_id=data['channel_id'],
        key=data['key']
    )

    return True    