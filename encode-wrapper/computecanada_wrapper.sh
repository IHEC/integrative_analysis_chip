#!/bin/bash

PIPERUNNER=$1
jobFile=$2
BACKEND=$3
if [[ $# -eq 4 ]]; then
  OUTDIR=$4
else
  OUTDIR=""
fi

filename=$(basename -- $2)
filename="${filename%.*}"

JOB_OUTPUT=chipseq.$filename.log
JOB_NAME=chipseq.$filename
cat /dev/null > $JOB_OUTPUT
cmd="module load singularity/3.6 mugqic/java/openjdk-jdk1.8.0_72 && bash $1 $2 $3 $4"
current_JOBID=$(echo "#!/bin/bash
$cmd" | sbatch --mail-type=END,FAIL --mail-user=$JOB_MAIL -A $RAP_ID -D $PWD -o $JOB_OUTPUT -J $JOB_NAME --time=48:00:00 --mem-per-cpu=4700M -n 20 -N 1 | grep "[0-9]" | cut -d\  -f4)
echo $current_JOBID submitted...