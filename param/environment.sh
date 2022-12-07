SYSTEM_VERSION=1.0.0
CHANNEL_NAME=test
CHANNEL_ID=123456789
SYSTEM_NAME=mujinyoyaku
YOUTUBE_URL=https://youtube/

# DynamoDB Keys
HASH_KEY=channel_id
RANGE_KEY=key
GSI1_PK=key
GSI2_PK=room_id
GSI2_SK=start_time
LSI1_SK=owner_id
LSI2_SK=start_time
LSI3_SK=room_id

GSI1_INDEX_NAME=key
GSI2_INDEX_NAME=room-start
LSI1_INDEX_NAME=channel-owner
LSI2_INDEX_NAME=channel-start
LSI3_INDEX_NAME=channel-room