import boto3
import os
import uuid
import logging
from datetime import datetime, date, timedelta
from boto3 import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO())

# 環境変数
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
DYNAMODB_PARTITION_KEY_COLUMN = os.environ['DYNAMODB_PARTITION_KEY_COLUMN']
DYNAMODB_SORT_KEY_COLUMN = os.environ['DYNAMODB_SORT_KEY_COLUMN']
DYNAMODB_GSI1_PARTITION_KEY_COLUMN = os.environ['DYNAMODB_GSI1_PARTITION_KEY_COLUMN']
DYNAMODB_GSI1_SORT_KEY_COLUMN = os.environ['DYNAMODB_GSI1_SORT_KEY_COLUMN']
DYNAMODB_GSI2_PARTITION_KEY_COLUMN = os.environ['DYNAMODB_GSI2_PARTITION_KEY_COLUMN']
DYNAMODB_GSI2_SORT_KEY_COLUMN = os.environ['DYNAMODB_GSI2_SORT_KEY_COLUMN']
GSI1_INDEX_NAME = os.environ['GSI1_INDEX_NAME']
GSI2_INDEX_NAME = os.environ['GSI2_INDEX_NAME']

# 固定値
KEY_USER_SERVICE_ID = 'UserServiceId'
KEY_DEVICE_SERVICE_ID = 'DeviceServiceId'
KEY_RESERVE_USER_ID = 'ReserveServiceId'
KEY_RESERVE_SERVICE_ID = 'ReserveServiceId'
KEY_RESERVE_DATE = 'ReserveDate'
KEY_RESERVE_START = 'ReserveStart'
KEY_RESERVE_END = 'ReserveEnd'
KEY_ACTIVE = 'Active'

dynamodb = boto3.resource('dynamodb')

def get_data_by_partition_key(dynamodb_table_name:str, partition_key_column: str, partition_key_value: str) -> dict:
    table = dynamodb.Table(dynamodb_table_name)
    options = {
        'KeyConditionExpression': Key(partition_key_column).eq(partition_key_value)
    }
    res = table.query(**options)
    return {item['DataType']['S']: item['DataValue']['S'] for item in res['Items']}

def get_id_by_partition_key(dynamodb_table_name:str, partition_key_column: str, partition_key_value: str, index_name: str='') -> str:
    table = dynamodb.Table(dynamodb_table_name)
    options = {
        'KeyConditionExpression': Key(partition_key_column).eq(partition_key_value)
    }
    if index_name:
        options['IndexName'] = index_name
    res = table.query(**options)
    return res['Items'][0][DYNAMODB_PARTITION_KEY_COLUMN]

def get_user_by_id(user_id: str) -> dict:
    '''ユーザIDでユーザ情報取得
    '''
    return get_data_by_partition_key(
        dynamodb_table_name=DYNAMODB_TABLE_NAME,
        partition_key_column=DYNAMODB_PARTITION_KEY_COLUMN,
        partition_key_value=user_id
    )

def get_user_by_email(email: str) -> dict:
    '''メールアドレスでユーザ情報取得
    '''
    user_id = get_id_by_partition_key(
        dynamodb_table_name=DYNAMODB_TABLE_NAME,
        partition_key_column=DYNAMODB_GSI1_PARTITION_KEY_COLUMN,
        partition_key_value=email,
        index_name=GSI1_INDEX_NAME
    )
    return get_user_by_id(user_id)

def get_users_by_service_id(service_id: str -> list[dict]):
    '''サービスIDでユーザ情報取得
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'IndexName': GSI1_INDEX_NAME,
        'KeyConditionExpression': Key(DYNAMODB_GSI1_PARTITION_KEY_COLUMN).eq(service_id) & Key(DYNAMODB_GSI1_SORT_KEY_COLUMN).eq(KEY_USER_SERVICE_ID)
    }
    res = table.query(**options)
    return [get_user_by_id(item[DYNAMODB_PARTITION_KEY_COLUMN]) for item in res['Items']]

def get_service_by_id(service_id: str) -> dict:
    '''サービスIDでサービス情報取得
    '''
    return get_data_by_partition_key(DYNAMODB_TABLE_NAME, DYNAMODB_PARTITION_KEY_COLUMN, service_id)

def get_service_by_user_id(user_id: str) -> dict:
    '''ユーザIDでサービス情報取得
    '''
    user = get_user_by_id(user_id)
    return get_service_by_id(user[KEY_USER_SERVICE_ID])

def get_device_by_device_id(device_id: str) -> dict:
    '''デバイスIDでデバイス情報取得
    '''
    return get_data_by_partition_key(
        dynamodb_table_name=DYNAMODB_TABLE_NAME,
        partition_key_column=DYNAMODB_PARTITION_KEY_COLUMN,
        partition_key_value=device_id
    )

def get_devices_by_service_id(service_id: str) -> list[dict]:
    '''デバイスIDでデバイス情報取得
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'IndexName': GSI1_INDEX_NAME,
        'KeyConditionExpression': Key(DYNAMODB_GSI1_PARTITION_KEY_COLUMN).eq(service_id) & Key(DYNAMODB_GSI1_SORT_KEY_COLUMN).eq(KEY_DEVICE_SERVICE_ID)
    }
    res = table.query(**options)
    return [get_device_by_device_id(item[DYNAMODB_PARTITION_KEY_COLUMN]) for item in res['Items']]

def get_reserve_by_id(reserve_id: str) -> dict:
    '''予約IDで予約情報取得
    '''
    return get_data_by_partition_key(
        dynamodb_table_name=DYNAMODB_TABLE_NAME,
        partition_key_column=DYNAMODB_PARTITION_KEY_COLUMN,
        partition_key_value=reserve_id
    )

def get_reserves_by_user_id(user_id: str) -> list[dict]:
    '''ユーザIDで予約情報取得
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'IndexName': GSI1_INDEX_NAME,
        'KeyConditionExpression': Key(DYNAMODB_GSI1_PARTITION_KEY_COLUMN).eq(user_id) & Key(DYNAMODB_GSI1_SORT_KEY_COLUMN).eq(KEY_RESERVE_USER_ID)
    }
    res = table.query(**options)
    # ユーザは複数予約することはできないので
    return get_reserve_by_id(res['Items'][0][DYNAMODB_PARTITION_KEY_COLUMN])

def get_reserves_by_service(service_id: str) -> list[dict]:
    '''サービスIDで全ての予約情報取得
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'IndexName': GSI1_INDEX_NAME,
        'KeyConditionExpression': Key(DYNAMODB_GSI1_PARTITION_KEY_COLUMN).eq(service_id) & Key(DYNAMODB_GSI1_SORT_KEY_COLUMN).eq(KEY_RESERVE_SERVICE_ID)
    }
    res = table.query(**options)
    return [get_reserve_by_id(item[DYNAMODB_PARTITION_KEY_COLUMN]) for item in res['Items']]

def get_reserves_by_service_date(service_id: str, date_str: str) -> list[dict]:
    '''日付で予約情報取得
    '''
    reserves = get_reserves_by_service(service_id)
    return [reserve for reserve in reserves if reserve[KEY_RESERVE_DATE] == date_str]

def get_reserves_by_service_date_period(service_id: str, start_date_str: str, end_date_str: str) -> list[dict]:
    '''日付の期間で予約情報取得
    '''
    reserves = get_reserves_by_service(service_id)
    target_reserve = []
    for reserve in reserves:
        start_dt = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date_str, '%Y-%m-%d')
        target_dt = datetime.strptime(reserve[KEY_RESERVE_DATE], '%Y-%m-%d')
        if start_dt <= target_dt <= end_dt:
            target_reserve.append(reserve)
    return target_reserve

def get_reserves_by_service_time(service_id: str, start_timestamp: int, end_timestamp: int):
    '''時間帯で予約情報取得
    '''
    reserves = get_reserves_by_service(service_id)
    target_reserve = []
    for reserve in reserves:
        start_dt = datetime.fromtimestamp(start_timestamp)
        end_dt = datetime.strptime(end_timestamp)
        if all([start_dt <= int(reserve[KEY_RESERVE_START]), end_dt >= int(reserve[KEY_RESERVE_END])]):
            target_reserve.append(reserve)
    return target_reserve

def get_active_false_ids() -> list[str]:
    '''非活性データのIDをすべて取得する
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'IndexName': GSI1_INDEX_NAME,
        'KeyConditionExpression': Key(DYNAMODB_GSI1_PARTITION_KEY_COLUMN).eq(str(False)) & Key(DYNAMODB_GSI1_SORT_KEY_COLUMN).eq(KEY_ACTIVE)
    }
    res = table.query(**options)
    return [item[DYNAMODB_PARTITION_KEY_COLUMN] for item in res['Items']]

def put_data(dynamodb_table_name:str, data: dict):
    '''データを追加する
    '''
    # 識別子をここで入れる
    id = str(uuid.uuid4())
    items = [
        {
            DYNAMODB_PARTITION_KEY_COLUMN: {'S': id},
            DYNAMODB_SORT_KEY_COLUMN: {'S': key},
            DYNAMODB_GSI1_PARTITION_KEY_COLUMN: {'S': str(value)}
        } for key, value in data.items()
    ]
    client = boto3.client('dynamodb')
    transact_items = [{'Put': {'TableName': dynamodb_table_name, 'Item': item}} for item in items]
    try:
        res = client.transact_write_items(RequesTransactItemstItems=transact_items)
    except Exception as e:
        print(f'Could not writed data: {e}')
        return False
    print(f'Put: {id}')
    return True

def delete_id_data(id: str) -> bool:
    '''データを削除する
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    items = get_data_by_partition_key(
        dynamodb_table_name=DYNAMODB_TABLE_NAME,
        partition_key_column=DYNAMODB_PARTITION_KEY_COLUMN,
        partition_key_value=id
    )
    try:
        with table.batch_writer() as batch:
            for item in items:
                table.delete_item(Key={
                    DYNAMODB_PARTITION_KEY_COLUMN: item[DYNAMODB_PARTITION_KEY_COLUMN],
                    DYNAMODB_SORT_KEY_COLUMN: item[DYNAMODB_SORT_KEY_COLUMN]
                })
    except Exception as r:
        print(f'Could not delete: {id}')
        return False
    print(f'Delete: {id}')
    return True

def delete_active_false():
    '''非活性データを全て削除する
    '''
    for id in get_active_false_ids():
        delete_id_data(id)
    
def update_active_false(id: str) -> bool:
    '''データを非活性にする
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    item = {
        DYNAMODB_PARTITION_KEY_COLUMN: id,
        DYNAMODB_SORT_KEY_COLUMN: KEY_ACTIVE,
        DYNAMODB_GSI1_PARTITION_KEY_COLUMN: str(False)
    }
    try:
        res = table.put_item(Item=item)
    except Exception as e:
        print(f'Could not update active: {id}')
        return False
    print(f'Update active: {id}')
    return True