#!/bin/bash

WDL=$1
jobFile=$2
RESULT=$3
BACKEND=$4

CROMWELL_HOME="{home_mnt}"
BACKEND_CONF="{backend}"
WORKFLOW_OPT="{container}"
PREFIX=$(basename $WDL .wdl)
METADATA="$PREFIX".metadata.json # metadata

java -jar -Dconfig.file=$BACKEND_CONF -Dbackend.default=$BACKEND $CROMWELL_HOME/cromwell-34.jar run $WDL -i $jobFile -o $WORKFLOW_OPT -m $METADATA
echo "return:$?"

cat $METADATA | python -c "import json,sys;obj=json.load(sys.stdin);print(obj['outputs']['"$PREFIX".compare_md5sum.json_str'])" > $RESULT
cat $RESULT
