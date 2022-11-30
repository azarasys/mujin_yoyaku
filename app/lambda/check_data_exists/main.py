from layer.dynamodb import get_user_by_id, get_reserves_by_room_start


def lambda_handler(event, context):

    data = event['data']

    if data['type'] == 'register':
        user = get_user_by_id(data['channel_id'], data['line_id'])
        return False if user else True
    if data['type'] == 'reserve':
        reserve = get_reserves_by_room_start(data['room_id'], data['start_time'])
        return False if reserve else True
    if data['type'] == 'unsubscribe':
        user = get_user_by_id(data['channel_id'], data['line_id'])
        return user['active']