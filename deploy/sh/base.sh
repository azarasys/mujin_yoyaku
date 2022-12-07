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
"

echo $PARAMETER | tr ' ' '\n'

aws cloudformation validate-template --template-body file://$TEMPLATE > /dev/null
aws cloudformation package --template-file $TEMPLATE --output-template-file $DEPLOY --s3-bucket $S3_BUCKET
aws cloudformation deploy \
--template-file $DEPLOY \
--stack-name $STACK \
--capabilities CAPABILITY_NAMED_IAM \
--no-fail-on-empty-changeset \
--parameter-overrides $PARAMETER \
--tags \
CommitHash=$COMMIT_HASH \
Version=$SYSTEM_VERSION \
ManualDeploy=$USER_NAME \
|| true

rm -rf $DEPLOY $EXPORT