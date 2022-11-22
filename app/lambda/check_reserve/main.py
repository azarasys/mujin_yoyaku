from layer.dynamodb import get_reserves_by_room_start


def lambda_handler(event, context):

    data = event['data']

    reserve = get_reserves_by_room_start(data['room_id'], data['start_time'])

    return False if reserve else False