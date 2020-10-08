#!/bin/bash

jobFile=$1
BACKEND=$2
if [[ $# -eq 3 ]]; then 
  OUTDIR="-Dbackend.providers.$BACKEND.config.root=$3"
else
  OUTDIR=""
fi

CROMWELL_HOME="{home_mnt}"
BACKEND_CONF="{backend}"
WORKFLOW_OPT="{container}"
CHIP="{wdl}"

java -jar -Dconfig.file=$BACKEND_CONF -Dbackend.default=$BACKEND $OUTDIR $CROMWELL_HOME/cromwell-34.jar run $CHIP -i $jobFile -o $WORKFLOW_OPT
echo "return:$?"
