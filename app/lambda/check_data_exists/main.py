from layer.dynamodb import get_user_by_id, get_reserves_by_room_start, get_device_by_channel_room_device
from layer.exception import ExceptionTerminated

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
    if data['type'] == 'keypad':
        device = get_device_by_channel_room_device(data['channel_id'], data['keypad_name'])
        return False if device else True
    if data['type'] == 'del_keypad':
        device = get_device_by_channel_room_device(data['channel_id'], data['keypad_name'])
        if not device:
            raise ExceptionTerminated(f"not found keypad {data['keypad_name']}")
        return True