import boto3
import os
from datetime import datetime, date, timedelta

dynamodb = boto3.resource('dynamodb')

def get_user_by_id(user_id: str):
    '''ユーザIDでユーザ情報取得
    '''
    pass

def get_user_by_email(email: str):
    '''メールアドレスでユーザ情報取得
    '''
    pass

def get_users_by_service_id(service_id: str):
    '''サービスIDでユーザ情報取得
    '''
    pass

def get_service_by_id(user_id: str):
    '''サービスIDでサービス情報取得
    '''
    pass

def get_service_by_user_id(user_id: str):
    '''ユーザIDでサービス情報取得
    '''
    pass

def get_service_by_email(user_id: str):
    '''メールアドレスでサービス情報取得
    '''
    pass

def get_device_by_service(service_id: str, device_type: str):
    '''サービスIDとデバイス種類でデバイス情報取得
    '''
    pass

def get_reserve_by_user_id(user_id: str):
    '''ユーザIDで予約情報取得
    '''
    pass

def get_reserves_by_service(service_id: str):
    '''サービスIDで予約情報取得
    '''
    pass

def get_reserves_by_service_date(service_id: str, date: date):
    '''日付で予約情報取得
    '''
    pass

def get_reserves_by_service_date_period(service_id: str, date: date):
    '''日付の期間で予約情報取得
    '''
    pass

def get_reserves_by_service_time(service_id: str, start: datetime, end: datetime):
    '''時間帯で予約情報取得
    '''
    pass