import os
from datetime import datetime, timedelta

from layer.dynamodb import get_reserves_by_channel_date, put_data
from layer.sqs import send_sqs_message

# 環境変数
CHANNEL_ID = os.environ['CHANNEL_ID']
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
CHANGE_RICHMENU_SQS_URL = os.environ['CHANGE_RICHMENU_SQS_URL']

def generate_date_str_jst():
    '''検索用日付値を生成
    '''
    system_dt = datetime.now()
    jst_dt = system_dt + timedelta(hours=9)
    return jst_dt.strftime('%Y-%m-%d')

def lambda_handler(event, context):
    # 終了した時間が過ぎた予約をFalseにする
    datas = get_reserves_by_channel_date(CHANNEL_ID, generate_date_str_jst())

    faileds_datas = []
    for data in datas:
        data['active'] = False
        try:
            put_data(
                table_name=DYNAMODB_TABLE_NAME,
                item=data
            )
             # リッチメニューを会員専用に更新する
            send_sqs_message(
                sqs_url=CHANGE_RICHMENU_SQS_URL,
                message={'line_id': data['line_id'], 'menu_type': 'member'}
            )
        except Exception as e:
            print(f'failed update data.')
            faileds_datas.append(data)
    
    if faileds_datas:
        raise Exception('exists faileds datas.')

    return True