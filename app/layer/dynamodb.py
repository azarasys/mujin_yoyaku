import boto3
import os
import logging
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO())

# 環境変数
DYNAMODB_TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
DYNAMODB_PK_COLUMN = os.environ['DYNAMODB_PK_COLUMN']
DYNAMODB_SK_COLUMN = os.environ['DYNAMODB_SK_COLUMN']
DYNAMODB_GSI1_PK_COLUMN = os.environ['DYNAMODB_GSI1_PK_COLUMN']
DYNAMODB_LSI1_SK_COLUMN = os.environ['DYNAMODB_LSI1_SK_COLUMN']
DYNAMODB_GSI2_PK_COLUMN = os.environ['DYNAMODB_GSI2_PK_COLUMN']
DYNAMODB_GSI2_SK_COLUMN = os.environ['DYNAMODB_GSI2_SK_COLUMN']
GSI1_INDEX_NAME = os.environ['GSI1_INDEX_NAME']
GSI2_INDEX_NAME = os.environ['GSI2_INDEX_NAME']
LSI1_INDEX_NAME = os.environ['LSI1_INDEX_NAME']

# 固定値
KEY_PREFIX_SERVICE = 'Service'
KEY_PREFIX_USER = 'User'
KEY_PREFIX_RESERVE = 'Reserve'
KEY_PREFIX_DEVICE = 'Device'
KEY_PREFIX_DATE = 'Date'
DATE_FORMAT = '%Y-%m-%d'

dynamodb = boto3.resource('dynamodb')

def get_data_by_pk(table_name:str, pk_column: str, pk_value: str, index: str=None) -> dict:
    '''PKによる情報取得
    '''
    table = dynamodb.Table(table_name)
    options = {
        'KeyConditionExpression': Key(pk_column).eq(pk_value)
    }
    if index:
        options['Index'] = index
    res = table.query(**options)
    return res['Items'][0]

def get_data_by_pk_sk(table_name:str, pk_column: str, pk_value: str, sk_column: str, sk_value: str, index: str=None) -> dict:
    '''PKとSKによる情報取得
    '''
    table = dynamodb.Table(table_name)
    options = {
        'KeyConditionExpression': Key(pk_column).eq(pk_value) & Key(sk_column).eq(sk_value)
    }
    if index:
        options['Index'] = index
    res = table.query(**options)
    return res['Items'][0]

def get_data_by_pk_sk_beginwith(table_name:str, pk_column: str, pk_value: str, sk_column: str, sk_value: str, index: str=None) -> list[dict]:
    '''PKのSKで開始する情報を複数取得
    '''
    table = dynamodb.Table(table_name)
    options = {
        'KeyConditionExpression': Key(pk_column).eq(pk_value) & Key(sk_column).begins_with(sk_value)
    }
    if index:
        options['Index'] = index
    res = table.query(**options)
    return res['Items']

def get_service_by_id(service_id: str) -> dict:
    '''サービスIDでサービス情報取得
    '''
    return get_data_by_pk(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id
    )

def get_service_by_channel_id(channel_id: str) -> dict:
    '''LineチャネルIDでサービス情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_GSI2_PK_COLUMN,
        pk_value=channel_id,
        sk_column=DYNAMODB_GSI2_SK_COLUMN,
        sk_value=f'{KEY_PREFIX_SERVICE}_'
    )

def get_service_by_email(email: str) -> dict:
    '''メールアドレスでサービス情報取得
    '''
    return get_data_by_pk(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_GSI1_PK_COLUMN,
        pk_value=f'{KEY_PREFIX_SERVICE}_{email}',
        index=GSI1_INDEX_NAME
    )

def get_users_by_service(service_id: str) -> list[dict]:
    '''サービス内の全ユーザ情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        sk_column=DYNAMODB_SK_COLUMN,
        sk_value=f'{KEY_PREFIX_USER}_'
    )

def get_reserves_by_service(service_id: str) -> list[dict]:
    '''サービス内の全予約情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        sk_column=DYNAMODB_SK_COLUMN,
        sk_value=f'{KEY_PREFIX_RESERVE}_'
    )

def get_reserves_by_service_date(service_id: str, date_str: str) -> list[dict]:
    '''サービス内の特定の日付の予約情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        sk_column=DYNAMODB_LSI1_SK_COLUMN,
        sk_value=date_str,
        index=LSI1_INDEX_NAME
    )

def get_devices_by_service(service_id: str) -> list[dict]:
    '''サービス内の全デバイス情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        sk_column=DYNAMODB_SK_COLUMN,
        sk_value=f'{KEY_PREFIX_DEVICE}_'
    )

def get_devices_by_service_type(service_id: str, device_type: str) -> list[dict]:
    '''サービス内の特定の種類の全デバイス情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        sk_column=DYNAMODB_SK_COLUMN,
        sk_value=f'{KEY_PREFIX_DEVICE}_{device_type}_'
    )

def get_user_by_email(email: str) -> dict:
    '''メールアドレスでユーザ情報取得
    '''
    return get_data_by_pk(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_GSI1_PK_COLUMN,
        pk_value=f'{KEY_PREFIX_USER}_{email}',
        index=GSI1_INDEX_NAME
    )

def get_reserves_by_user(service_id: str, user_id: str) -> list[dict]:
    '''ユーザの全予約情報取得
    '''
    return get_data_by_pk(
        table_name=DYNAMODB_TABLE_NAME,
        pk_column=DYNAMODB_PK_COLUMN,
        pk_value=service_id,
        pk_column=DYNAMODB_SK_COLUMN,
        pk_value=f'{KEY_PREFIX_RESERVE}_{user_id}'
    )

def put_data(table_name:str, item: dict) -> bool:
    '''データを追加する
    '''
    table = dynamodb.Table(table_name)
    try:
        res = table.put_item(Item=item)
    except Exception as e:
        print(f'Could not writed data: {e}')
        return False
    print(f'Put: {id}')
    return True

def delete_id_data(service_id: str, key: str) -> bool:
    '''サービス内の特定データを削除する
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'Key': {DYNAMODB_PK_COLUMN: service_id, DYNAMODB_SK_COLUMN: key},
    }
    try:
        res = table.delete_item(**options)
    except Exception as r:
        print(f'Could not delete: {id}')
        return False
    print(f'Delete: {id}')
    return True

def delete_user(service_id: str, user_id: str):
    '''サービス内のユーザを削除する
    '''
    delete_id_data(
        service_id=service_id,
        key=f'{KEY_PREFIX_USER}_{user_id}'
    )

def delete_reserve(service_id: str, user_id: str, reserve_id: str):
    '''サービス内の予約を削除する
    '''
    delete_id_data(
        service_id=service_id,
        key=f'{KEY_PREFIX_RESERVE}_{user_id}_{reserve_id}'
    )

def delete_device(service_id: str, device_type: str, device_id: str):
    '''サービス内のデバイスを削除する
    '''
    delete_id_data(
        service_id=service_id,
        key=f'{KEY_PREFIX_DEVICE}_{device_type}_{device_id}'
    )

def update_active_false(service_id:str, key: str) -> bool:
    '''データを活性フラグをオフにする
    '''
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    options = {
        'Key': {DYNAMODB_PK_COLUMN: service_id, DYNAMODB_SK_COLUMN: key},
        'UpdateExpression': 'set active = :active',
        'ExpressionAttributeValues': {':active': False},
        'ReturnValues': 'UPDATED_NEW'
    }
    try:
        res = table.update_item(**options)
    except Exception as e:
        print(f'Could not update active: {id}')
        return False
    print(f'Update active: {id}')
    return True