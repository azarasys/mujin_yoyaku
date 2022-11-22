#!/bin/bash 
  
 set -eux 
  
 cd $(dirname $0)/../../ 
  
 TARGET_TEMPLATE=applications.yml 
  
 source ./param/environment.sh 
 source ./deploy/sh/common.sh $* 
  
 PARAMETER=" 
 Prefix=$PREFIX \ 
 Environment=$ENV \ 
 PrivateSubnetA=$(cat $EXPORT | jq -r '.PrivateSubnetA') \ 
 RoleRedshiftArn=$(cat $EXPORT | jq -r '.RoleRedshiftArn') \ 
 SecurityGroupRedshift=$(cat $EXPORT | jq -r '.SecurityGroupRedshift') \ 
 SecretRedshiftBisystemArn=$(cat $EXPORT | jq -r '.SecretRedshiftBisystemArn') \ 
 TranInputBucket=$(cat $EXPORT | jq -r '.TranInputBucket') \ 
 MasterInputBucket=$(cat $EXPORT | jq -r '.MasterInputBucket') \ 
 PosInputBucket=$(cat $EXPORT | jq -r '.PosInputBucket') \ 
 WorkBucket=$(cat $EXPORT | jq -r '.WorkBucket') \ 
 BackupBucket=$(cat $EXPORT | jq -r '.BackupBucket') \ 
 UnloadBucket=$(cat $EXPORT | jq -r '.UnloadBucket') \ 
 SpectrumBucket=$(cat $EXPORT | jq -r '.SpectrumBucket') \ 
 TopicTranUpdateStartArn=$(cat $EXPORT | jq -r '.TopicTranUpdateStartArn') \ 
 TopicTranCopyStartArn=$(cat $EXPORT | jq -r '.TopicTranCopyStartArn') \ 
 TopicMasterCopyFinishArn=$(cat $EXPORT | jq -r '.TopicMasterCopyFinishArn') \ 
 TopicMasterUpdateFinishArn=$(cat $EXPORT | jq -r '.TopicMasterUpdateFinishArn') \ 
 TopicPosCopyFinishArn=$(cat $EXPORT | jq -r '.TopicPosCopyFinishArn') \ 
 TopicPosUpdateFinishArn=$(cat $EXPORT | jq -r '.TopicPosUpdateFinishArn') \ 
 TopicSendMailArn=$(cat $EXPORT | jq -r '.TopicSendMailArn') \ 
 TopicUpdateJikanPastStartArn=$(cat $EXPORT | jq -r '.TopicUpdateJikanPastStartArn') \ 
 TopicUpdateJikanJanSakutaiStartArn=$(cat $EXPORT | jq -r '.TopicUpdateJikanJanSakutaiStartArn') \ 
 TopicUpdateJikanShobunruiDatasetStartArn=$(cat $EXPORT | jq -r '.TopicUpdateJikanShobunruiDatasetStartArn') \ 
 TopicUpdateJikanJanDatasetStartArn=$(cat $EXPORT | jq -r '.TopicUpdateJikanJanDatasetStartArn') \ 
 TopicUpdateJikanShobunruiSakutaiStartArn=$(cat $EXPORT | jq -r '.TopicUpdateJikanShobunruiSakutaiStartArn') \ 
 TopicProfitDailyBasicStartArn=$(cat $EXPORT | jq -r '.TopicProfitDailyBasicStartArn') \ 
 TopicProfitDailyAccumSakutaiStartArn=$(cat $EXPORT | jq -r '.TopicProfitDailyAccumSakutaiStartArn') \ 
 TopicProfitDailyV2StartArn=$(cat $EXPORT | jq -r '.TopicProfitDailyV2StartArn') \ 
 TopicProfitDailyVacuumV2StartArn=$(cat $EXPORT | jq -r '.TopicProfitDailyVacuumV2StartArn') \ 
 TopicCopyToDatalakeStartArn=$(cat $EXPORT | jq -r '.TopicCopyToDatalakeStartArn') \ 
 TopicCopyToBiStartArn=$(cat $EXPORT | jq -r '.TopicCopyToBiStartArn') \ 
 TopicRouteSalesDailyStartArn=$(cat $EXPORT | jq -r '.TopicRouteSalesDailyStartArn') \ 
 QueueTranUpdateStartArn=$(cat $EXPORT | jq -r '.QueueTranUpdateStartArn') \ 
 QueueTranCopyStartArn=$(cat $EXPORT | jq -r '.QueueTranCopyStartArn') \ 
 QueueMasterCopyFinishArn=$(cat $EXPORT | jq -r '.QueueMasterCopyFinishArn') \ 
 QueueMasterUpdateFinishArn=$(cat $EXPORT | jq -r '.QueueMasterUpdateFinishArn') \ 
 QueuePosCopyFinishArn=$(cat $EXPORT | jq -r '.QueuePosCopyFinishArn') \ 
 QueuePosUpdateFinishArn=$(cat $EXPORT | jq -r '.QueuePosUpdateFinishArn') \ 
 QueueTopicUpdateJikanPastStartArn=$(cat $EXPORT | jq -r '.QueueTopicUpdateJikanPastStartArn') \ 
 QueueTopicUpdateJikanJanSakutaiStartArn=$(cat $EXPORT | jq -r '.QueueTopicUpdateJikanJanSakutaiStartArn') \ 
 QueueUpdateJikanShobunruiDatasetStartArn=$(cat $EXPORT | jq -r '.QueueUpdateJikanShobunruiDatasetStartArn') \ 
 QueueUpdateJikanJanDatasetStartArn=$(cat $EXPORT | jq -r '.QueueUpdateJikanJanDatasetStartArn') \ 
 QueueUpdateJikanShobunruiSakutaiStartArn=$(cat $EXPORT | jq -r '.QueueUpdateJikanShobunruiSakutaiStartArn') \ 
 QueueTopicProfitDailyBasicStartArn=$(cat $EXPORT | jq -r '.QueueTopicProfitDailyBasicStartArn') \ 
 QueueTopicProfitDailyAccumSakutaiStartArn=$(cat $EXPORT | jq -r '.QueueTopicProfitDailyAccumSakutaiStartArn') \ 
 QueueTopicProfitDailyV2StartArn=$(cat $EXPORT | jq -r '.QueueTopicProfitDailyV2StartArn') \ 
 QueueTopicProfitDailyVacuumV2StartArn=$(cat $EXPORT | jq -r '.QueueTopicProfitDailyVacuumV2StartArn') \ 
 QueueTopicCopyToDatalakeStartArn=$(cat $EXPORT | jq -r '.QueueTopicCopyToDatalakeStartArn') \ 
 QueueTopicCopyToBiStartArn=$(cat $EXPORT | jq -r '.QueueTopicCopyToBiStartArn') \ 
 QueueTopicMonitoringAlarmSendMailStartArn=$(cat $EXPORT | jq -r '.QueueTopicMonitoringAlarmSendMailStartArn') \ 
 QueueTopicRouteSalesDailyStartArn=$(cat $EXPORT | jq -r '.QueueTopicRouteSalesDailyStartArn') \ 
 LambdaLockTableName=$(cat $EXPORT | jq -r '.LambdaLockTableName') \ 
 LambdaLockTableArn=$(cat $EXPORT | jq -r '.LambdaLockTableArn') \ 
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