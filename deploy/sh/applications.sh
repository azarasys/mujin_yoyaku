#!/bin/bash 

set -eux 

cd $(dirname $0)/../../ 

TARGET_TEMPLATE=$(basename $0 | sed 's/\.sh$/\.yaml/')

source ./param/environment.sh 
source ./deploy/sh/common.sh $* 

PARAMETER=" 
Prefix=$PREFIX \
Environment=$ENV \
MainTableName=$(cat $EXPORT | jq -r '.MainTableName') \
MainTableArn=$(cat $EXPORT | jq -r '.MainTableArn') \
Prefix=$PREFIX \
Environment=$ENV \
ChannelId=$CHANNEL_ID \
HashKey=$HASH_KEY \
RangeKey=$RANGE_KEY \
Key1=$KEY1 \
Key2=$KEY2 \
Key3=$KEY3 \
" 

echo $PARAMETER | tr ' ' '\n' 

SAM_CLI_TELEMETRY=0 

sam validate -t $TEMPLATE 
sam package --template-file $TEMPLATE --output-template-file $DEPLOY --s3-bucket $S3_BUCKET 
sam deploy \ 
  --template-file $DEPLOY \ 
  --s3-bucket ${S3_BUCKET} \ 
  --stack-name $STACK \ 
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \ 
  --no-fail-on-empty-changeset \ 
  --parameter-overrides $PARAMETER \ 
  --tags \ 
  CommitHash=$COMMIT_HASH \ 
  Version=$SYSTEM_VERSION \ 
  ManualDeploy=$USER_NAME \ 
  || true 

rm -rf $DEPLOY $EXPORT