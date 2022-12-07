#!/bin/bash 

set -eux 

cd $(dirname $0)/../../ 

TARGET_TEMPLATE=$(basename $0 | sed 's/\.sh$/\.yaml/')

source ./param/secrets.sh 
source ./param/environment.sh 
source ./deploy/sh/common.sh $* 

PARAMETER=" 
Prefix=$PREFIX \
Environment=$ENV \
MainTableName=$(cat $EXPORT | jq -r '."'$PREFIX'-MainTableName"') \
MainTableArn=$(cat $EXPORT | jq -r '."'$PREFIX'-MainTableArn"') \
ChannelId=$CHANNEL_ID \
HashKey=$HASH_KEY \
RangeKey=$RANGE_KEY \
Gsi1Pk=$GSI1_PK \
Gsi2Pk=$GSI2_PK \
Gsi2Sk=$GSI2_SK \
Lsi1Sk=$LSI1_SK \
Lsi2Sk=$LSI2_SK \
Lsi3Sk=$LSI3_SK \
Gsi1IndexName=$GSI1_INDEX_NAME \
Gsi2IndexName=$GSI2_INDEX_NAME \
Lsi1IndexName=$LSI1_INDEX_NAME \
Lsi2IndexName=$LSI2_INDEX_NAME \
Lsi3IndexName=$LSI3_INDEX_NAME \
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