import os
from datetime import datetime

from layer.dynamodb import get_user_by_id_channel, put_data

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']


def lambda_handler(event, content):
    data = event['data']
    user = get_user_by_id_channel(data['channel_id'], data['line_id'])

    # 多重起動は終了
    if user['active'] == False:
        print(f'{user["line_id"]} had unsubscribe.')
        return True

    user['active'] = False
    user['end_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 登録によって会員情報を上書き
    put_data(
        table_name=MAIN_TABLE_NAME,
        item=data
    )

    return True    