#!/bin/bash
ENV=${1:-dev}
CHANNEL_ACCESS_TOKEN=$2

source ./param/secrets.sh
source ./param/environment.sh

PREFIX=$ENV-$CHANNEL_ID-$SYSTEM_NAME

EXPORT=/tmp/export
aws cloudformation list-exports | jq '.[] | from_entries' > $EXPORT

BASE_LINE_API_URL='https://api.line.me/v2/bot/richmenu'

BucketConfigName=$(cat $EXPORT | jq -r '."'${PREFIX}'-BucketConfigName"')

BASE_S3_URL=https://$BucketConfigName

BASE_DIR=./deploy/json/richmenu
rm -rf $BASE_DIR
mkdir -p $BASE_DIR
cp ./app/template/richmenu/* $BASE_DIR

# 仮登録フォームURL
TMP_REGISTER_URL=$BASE_S3_URL/tmp_register.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|TMP_REGISTER_URL|"$TMP_REGISTER_URL"|g"
# 本登録フォームURL
REGISTER_URL=$BASE_S3_URL/register.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|REGISTER_URL|"$REGISTER_URL"|g"
# 予約フォームURL
RESERVE_URL=$BASE_S3_URL/reserve.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|RESERVE_URL|"$RESERVE_URL"|g"
# 予約確認フォームURL
RESERVED_URL=$BASE_S3_URL/reserved.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|RESERVED_URL|"$RESERVED_URL"|g"
# 案内URL
GUIDANCE_URL=$BASE_S3_URL/guidance.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|GUIDANCE_URL|"$GUIDANCE_URL"|g"
# サービス情報URL
SERVICE_URL=$BASE_S3_URL/service.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|SERVICE_URL|"$SERVICE_URL"|g"
# 会員情報URL
INFORMATION_URL=$BASE_S3_URL/information.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|INFORMATION_URL|"$INFORMATION_URL"|g"
# そのたURL
OTHER_URL=$BASE_S3_URL/other.html
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|OTHER_URL|"$OTHER_URL"|g"
# YoutubeURL
find $BASE_DIR -type f -name "*.json" | xargs sed -i -e "s|YOUTUBE_URL|"$YOUTUBE_URL"|g"

# 初期リッチメニュー作成
curl -v -X POST $BASE_LINE_API_URL \
-H "Authorization: Bearer $CHANNEL_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d @$BASE_DIR/default.json

# 仮登録後リッチメニュー作成
curl -v -X POST $BASE_LINE_API_URL \
-H "Authorization: Bearer $CHANNEL_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d @$BASE_DIR/tmp_user.json

# 本登録後リッチメニュー作成
curl -v -X POST $BASE_LINE_API_URL \
-H "Authorization: Bearer $CHANNEL_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d @$BASE_DIR/user.json

# 予約登録後リッチメニュー作成
curl -v -X POST $BASE_LINE_API_URL \
-H "Authorization: Bearer $CHANNEL_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d @$BASE_DIR/reserved.json

# オーナー用リッチメニュー作成
curl -v -X POST $BASE_LINE_API_URL \
-H "Authorization: Bearer $CHANNEL_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d @$BASE_DIR/owner.json

rm -rf $EXPORT