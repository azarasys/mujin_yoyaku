#!/bin/bash

set -eux

ENV=${1:-dev}
export AWS_PROFILE=${AWS_PROFILE:-${ENV}}

COMMIT_HASH=$(git show -s --format=%H || echo 'unknown')
USER_NAME=$(git config user.name || echo 'unknown')
ACCOUNT_ID=$(aws sts get-caller-identity --output json | jq -r '.Account')
TEMPLATE_BASENAME=$(echo $TARGET_TEMPLATE | tr _ - | sed -r 's/^[0-9]*-?([a-zA-Z0-9-]*)\.yaml/\1/')

PREFIX=$ENV-$CHANNEL_ID-$SYSTEM_NAME
TEMPLATE=deploy/$TARGET_TEMPLATE
EXPORT=/tmp/$TEMPLATE_BASENAME-$$.export
DEPLOY=/tmp/$TEMPLATE_BASENAME-$$.deploy
STACK=$PREFIX-$TEMPLATE_BASENAME
S3_BUCKET=$PREFIX-sam-deployments

aws cloudformation list-exports | jq '.[] | from_entries' > $EXPORT

STATUS=$(aws cloudformation describe-stacks --stack-name $STACK --query 'Stacks[].StackStatus[]' --output text) || true

case "$STATUS" in
  'CREATE_IN_PROGRESS') aws cloudformation wait stack-create-complete --stack-name $STACK ;;
  'UPDATE_IN_PROGRESS') aws cloudformation wait stack-update-complete --stack-name $STACK ;;
  'DELETE_IN_PROGRESS') aws cloudformation wait stack-delete-complete --stack-name $STACK ;;
  'ROLLBACK_COMPLETE')
  aws cloudformation delete-stack --stack-name $STACK
  aws cloudformation wait stack-delete-complete --stack-name $STACK ;;
esac