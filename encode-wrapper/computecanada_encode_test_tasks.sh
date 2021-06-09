#!/bin/bash

OUTPUTDIR=$1

JOB_OUTPUT=encode_test.$OUTPUTDIR.log
JOB_NAME=encode_test.$OUTPUTDIR
cat /dev/null > $JOB_OUTPUT
cmd="module load singularity/3.6 mugqic/java/openjdk-jdk1.8.0_72 && bash $1 $2"
current_JOBID=$(echo "#!/bin/bash
$cmd" | sbatch --mail-type=END,FAIL --mail-user=$JOB_MAIL -A $RAP_ID -D $PWD -o $JOB_OUTPUT -J $JOB_NAME --time=02:00:00 --mem-per-cpu=4700M -n 10 -N 1 | grep "[0-9]" | cut -d\  -f4)
echo $current_JOBID submitted...