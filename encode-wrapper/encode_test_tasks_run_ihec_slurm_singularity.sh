#!/bin/bash


BASE=$1
BACKEND=$2
tag=${3:-""}
H=$BASE

chmod +x $H/testrun_tasks_ihec_slurm_singularity.sh
testsOut=$H/test_tasks_results_"$tag"
mkdir -p $testsOut || true
cd $BASE/chip-seq-pipeline2/test/test_task
echo "__container__:$BASE,$BACKEND,$PWD $(which python) $(which java)  $PATH $PYTHONPATH"

for t in test_bam2ta test_bwa  test_choose_ctl test_filter test_idr test_macs2 test_merge_fastq test_overlap test_pool_ta test_reproducibility test_spp test_spr test_trim_fastq test_xcor; do
#for t in test_bam2ta; do
  echo "# started: $t $(date)"
  $H/testrun_tasks_ihec_slurm_singularity.sh $PWD/$t.wdl $PWD/$t.json $testsOut/$t.test_task_output.json $BACKEND
  echo "# end: $t $(date) $?"
  echo "ok___________________"
done



