import boto3
import calendar
import os
import logging
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO())

# 環境変数
MAIN_TABLE_NAME = os.environ['MAIN_TABLE_NAME']
HASH_KEY = os.environ['HASH_KEY']
RANGE_KEY = os.environ['RANGE_KEY']
GSI1_PK = os.environ['GSI1_PK']
GSI2_PK = os.environ['GSI2_PK']
GSI2_SK = os.environ['GSI2_SK']
LSI1_SK = os.environ['LSI1_SK']
LSI2_SK = os.environ['LSI2_SK']
LSI3_SK = os.environ['LSI3_SK']
GSI1_INDEX_NAME = os.environ['GSI1_INDEX_NAME']
LSI1_INDEX_NAME = os.environ['LSI1_INDEX_NAME']
LSI2_INDEX_NAME = os.environ['LSI2_INDEX_NAME']
LSI3_INDEX_NAME = os.environ['LSI3_INDEX_NAME']

# 固定値
KEY_PREFIX_SERVICE = 'channel'
KEY_PREFIX_USER = 'user'
KEY_PREFIX_RESERVE = 'reserve'
KEY_PREFIX_DEVICE = 'device'
KEY_PREFIX_PASSWORD = 'password'
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

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

def get_channel_by_id(channel_id: str) -> dict:
    '''LINEチャネルIDでLINEチャネル情報取得
    '''
    return get_data_by_pk(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id
    )

def get_user_by_owner(channel_id: str) -> dict:
    '''LINEチャネルのオーナーユーザ情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=LSI1_SK,
        sk_value=True,
        index=LSI1_INDEX_NAME
    )

def get_user_by_id_channel(channel_id: str, line_id: str) -> list[dict]:
    '''LINEチャネル内の全ユーザ情報取得
    '''
    return get_data_by_pk_sk(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_USER}_{line_id}'
    )

def get_users_by_channel(channel_id: str) -> list[dict]:
    '''LINEチャネル内の全ユーザ情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_USER}_'
    )

def get_reserves_by_channel(channel_id: str) -> list[dict]:
    '''LINEチャネル内の全予約情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_RESERVE}_'
    )

def get_reserves_by_channel_date(channel_id: str, date_str: str) -> list[dict]:
    '''LINEチャネル内の特定の日付の予約情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=LSI2_SK,
        sk_value=date_str,
        index=LSI2_INDEX_NAME
    )

def get_devices_by_channel(channel_id: str) -> list[dict]:
    '''LINEチャネル内の全デバイス情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_DEVICE}_'
    )

def get_devices_by_channel_type(channel_id: str, device_type: str) -> list[dict]:
    '''LINEチャネル内の特定の種類の全デバイス情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_DEVICE}_{device_type}_'
    )

def get_device_by_channel_room(channel_id: str, room_name: str) -> list[dict]:
    '''LINEチャネル内の特定の部屋のデバイス情報取得
    '''
    return get_data_by_pk_sk(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=LSI3_SK,
        sk_value=room_name,
        index=LSI3_INDEX_NAME
    )

def get_user_by_id(channel_id: str, line_id: str) -> dict:
    '''ラインIDでユーザ情報取得
    '''
    return get_data_by_pk(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_USER}_{line_id}'
    )

def get_reserves_by_user(channel_id: str, user_id: str) -> list[dict]:
    '''ユーザの全予約情報取得
    '''
    return get_data_by_pk(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_RESERVE}_{user_id}'
    )

def get_reserves_by_room_start(room_id: str, start_time: str) -> list[dict]:
    '''特定の施設の特定日時の予約情報取得
    '''
    return get_data_by_pk_sk(
        table_name=MAIN_TABLE_NAME,
        pk_column=GSI2_PK,
        pk_value=room_id,
        sk_column=GSI2_SK,
        sk_value=start_time
    )

def get_password_by_channel_date(channel_id: str, start_time: str) -> list[dict]:
    '''チャネルIDの特定日時の全パスワード情報取得
    '''
    return get_data_by_pk_sk_beginwith(
        table_name=MAIN_TABLE_NAME,
        pk_column=HASH_KEY,
        pk_value=channel_id,
        sk_column=RANGE_KEY,
        sk_value=f'{KEY_PREFIX_PASSWORD}_{start_time}'
    )

def put_data(table_name:str, item: dict) -> bool:
    '''データを追加する
    '''
    table = dynamodb.Table(table_name)
    if not item.get('create_at'):
        item['create_at'] = datetime.now().strftime(DATE_TIME_FORMAT)
    else:
        item['modify_at'] = datetime.now().strftime(DATE_TIME_FORMAT)
    try:
        res = table.put_item(Item=item)
    except Exception as e:
        print(f'Could not writed data: {e}')
        raise e
    print(f'Put: {res}')

def delete_id_data(channel_id: str, key: str) -> bool:
    '''LINEチャネル内の特定データを削除する
    '''
    table = dynamodb.Table(MAIN_TABLE_NAME)
    options = {
        'Key': {HASH_KEY: channel_id, RANGE_KEY: key},
    }
    try:
        res = table.delete_item(**options)
    except Exception as e:
        print(f'Could not delete: {key}')
        raise e
    print(f'Delete: {key}')

def delete_user(channel_id: str, user_id: str):
    '''LINEチャネル内のユーザを削除する
    '''
    delete_id_data(
        channel_id=channel_id,
        key=f'{KEY_PREFIX_USER}_{user_id}'
    )

def delete_reserve(channel_id: str, user_id: str, reserve_id: str):
    '''LINEチャネル内の予約を削除する
    '''
    delete_id_data(
        channel_id=channel_id,
        key=f'{KEY_PREFIX_RESERVE}_{user_id}_{reserve_id}'
    )

def delete_device(channel_id: str, device_type: str, device_id: str):
    '''LINEチャネル内のデバイスを削除する
    '''
    delete_id_data(
        channel_id=channel_id,
        key=f'{KEY_PREFIX_DEVICE}_{device_type}_{device_id}'
    )

def update_active_false(channel_id:str, key: str) -> bool:
    '''データを活性フラグをオフにする
    '''
    table = dynamodb.Table(MAIN_TABLE_NAME)
    dt = datetime.now() + timedelta(hours=9)
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    end_at = dt.replace(day=last_day, hour=23, minute=59, second=59)
    options = {
        'Key': {HASH_KEY: channel_id, RANGE_KEY: key},
        'UpdateExpression': 'set active = :active, end_at = :end_at',
        'ExpressionAttributeValues': {
            ':active': False,
            ':end_at': end_at.strftime(DATE_TIME_FORMAT)
        },
        'ReturnValues': 'UPDATED_NEW'
    }
    try:
        res = table.update_item(**options)
    except Exception as e:
        print(f'Could not update active: {key}')
        raise e
    print(f'Update active: {id}')