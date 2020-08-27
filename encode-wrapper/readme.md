# ENCODE ChIP-Seq pipeline singularity wrapper

## ENCODE ChIP-Seq pipeline

Available at https://github.com/ENCODE-DCC/chip-seq-pipeline2/

This wrapper uses http://quay.io/encode-dcc/chip-seq-pipeline:v1.1.4

## IHEC Standard workflows

Documentation on how to define configs for IHEC standard workflows: [IHEC standard workflow](ihec_standard_workflow.md)

## Downloading test data

First run `./get_encode_resources.sh` to get encode test dataset and hg38 genome files.

By default it will use git over http. If you want to use ssh, then pass `ssh` as first argument.

Run `python chip.py -get` to get IHEC ChIP test data for MCF10A cell line.

## Running on cluster

For running on cluster with a SLURM or PBS etc see [this section](https://github.com/IHEC/integrative_analysis_chip/blob/dev-organize-output/encode-wrapper/readme.md#running-on-cluster-1)

## Memory requirements

You will need 10G RAM for ENCODE tests and in excess of 60G for running the IHEC test dataset.  

## QC reports

The analysis will generate a `qc.json` file (as well as an html version) along with peak calls and aligned bam files. This file contains the needed qc metrics.

## Pulling Singularity image and generating wrapper scripts

These scripts require `python 3.6.8` or higher. It's assmumed that the the underlying OS supports `overlayfs` so paths that do not exist on the singularity can be mounted inside singularity (CentOS7 should work fine). CentOS6 does not have `overlayfs` support. If you need support for OS without `overlayfs` please make an issue.  

Check singularity version with `singularity --version` to make sure it's at least `3.0.1`.

Then run `python chip.py -pullimage -bindpwd`

Then run `python chip.py -pullimage -bindpwd`. `bindpwd` will mount the current directory (equivalent to arguments `-B $PWD`). Note that this means singularity must be a recent enough version to be able to bind to directories that do not exist on the image, since your `$PWD` may not exist on the image. Otherwise passing `-pwd2ext0` binds $PWD to `/mnt/ext_0`.

If additional paths are passed like `python chip.py -pullimage -bindpwd /some/directory_A /some/directory_B ...` then these will be mounted inside the image at `/mnt/ext_1`, `/mnt/ext_2` and so on. `/mnt/ext_0` is reserved for mounting `$PWD` if needed.   

This command will write:

* piperunner.sh

* piperunner_ihec_slurm_singularity.sh

* piperunner_ihec_pbs_singularity.sh

* testrun_tasks.sh

* testrun_tasks_ihec_slurm_singularity.sh

* testrun_tasks_ihec_pbs_singularity.sh

* singularity_encode_test_tasks.sh

* singularity_wrapper.sh

* trackoutput.sh

If you are running in `Local` mode using `./chip.py -pullimage -bindpwd $PWD/data_b $PWD/data_a` will mount `$PWD/data_b` as `/mnt/ext_0`, `$PWD/data_a` as `/mnt/ext_1` and so on, and it binds `$PWD` to `$PWD`. If you are on older systems without support for overlayFS, then passing `-pwd2ext0` will bind `$PWD` `/mnt/ext_0` and shift other bind points further along `ext_$i`'s.

For example,

    python ./chip.py -pullimage -bindpwd -pwd2ext0 $PWD/v2/ihec

will set up all binds so that after downloading the cemt0007 test data, you can just use `cemt0007_h3k27me3_mnt_ext_0.json` out of the box like:

    $ ./singularity_wrapper.sh cemt0007_h3k27me3_mnt_ext_0.json

without needing to do `chip.py -maketests` as later described.

This will also create the singularity image in `./images`.

Do `chmod +x ./*sh`.

You can pass `-nobuild` if you just want to regenerate the wrapper scripts without pulling the singularity image again.

`singularity_wrapper.sh` can be examined to see what mount points have been generated.

For example `python chip.py -pullimage -bindpwd -nobuild $PWD/v2/ihec/test_data/` generates: 

    singularity exec --cleanenv -B /usr/edcc/integrative_analysis_chip/encode-wrapper,/usr/edcc/integrative_analysis_chip/encode-wrapper/v2/ihec/test_data/:/mnt/ext_1 /usr/edcc/integrative_analysis_chip/encode-wrapper/images/chip_seq_pipeline_v1_1_4.sif /usr/edcc/integrative_analysis_chip/encode-wrapper/piperunner.sh $1 $BACKEND

## Running tests

### ENCODE tests

To run ENCODE test tasks, do `./singularity_encode_test_tasks.sh try1` to run it locally. The first argument is the config argument to cromwell (see ENCODE pipeline documentation). The output of tests will be written in `test_tasks_results_try1`.  If you are on HPC and prefer to use SLURM, do `./encode_test_tasks_run_ihec_slurm_singularity.sh <installation_dir> slurm_singularity try1` and for PBS do `./encode_test_tasks_run_ihec_pbs_singularity.sh <installation_dir> pbs_singularity try1`.

You will need atleast 10G of memory for running the encode tasks. 

Make sure all test pass, by looking through jsons generated. `./status_encode_tasks.py` can be used here.

    python ./status_encode_tasks.py ./test_tasks_results_try1
    # ok:./test_tasks_results_try1/test_spr.test_task_output.json
    # ok:./test_tasks_results_try1/test_pool_ta.test_task_output.json
    # ok:./test_tasks_results_try1/test_reproducibility.test_task_output.json
    # ok:./test_tasks_results_try1/test_bwa.test_task_output.json
    # ok:./test_tasks_results_try1/test_choose_ctl.test_task_output.json
    # ok:./test_tasks_results_try1/test_trim_fastq.test_task_output.json
    # ok:./test_tasks_results_try1/test_idr.test_task_output.json
    # ok:./test_tasks_results_try1/test_bam2ta.test_task_output.json
    # ok:./test_tasks_results_try1/test_xcor.test_task_output.json
    # ok:./test_tasks_results_try1/test_overlap.test_task_output.json
    # ok:./test_tasks_results_try1/test_merge_fastq.test_task_output.json
    # ok:./test_tasks_results_try1/test_macs2.test_task_output.json
    # ok:./test_tasks_results_try1/test_spp.test_task_output.json
    # ok: ./test_tasks_results_try1/test_filter.test_task_output.json
    {
        "#expected": 14, 
        "#failed": 0, 
        "#ok": 14
    }

### MCF10A tests

For the MCF10A data downloaded with `python chip.py -get`, doing `python chip.py -maketests` will write ChIP test configurations (you also need to pass `-pwd2ext0` if you set `$PWD` to `/ext/mnt_0`):

* ./v2/ihec/cemt0007_h3k4me3.json

* ./v2/ihec/cemt0007_h3k27me3.json

IHEC tests on Local mode can be run with:

`./singularity_wrapper.sh ./v2/ihec/cemt0007_h3k4me3.json` and `./singularity_wrapper.sh ./v2/ihec/cemt0007_h3k27me3.json`

You can also use SLURM or PBS with the pipeline; please see [cluster](https://github.com/IHEC/integrative_analysis_chip/blob/dev-organize-output/encode-wrapper/readme.md#running-on-cluster-1) section. It's recommended that `singularity_runner.sh` is used instead for simplicity. 

`./piperunner_ihec_slurm_singularity.sh ./v2/ihec/cemt0007_h3k4me3.json slurm_singularity h3k4me3_out` and `./piperunner_ihec_slurm_singularity.sh ./v2/ihec/cemt0007_h3k27me3.json slurm_singularity h3k27me3_out`

`./piperunner_ihec_pbs_singularity.sh ./v2/ihec/cemt0007_h3k4me3.json pbs_singularity h3k4me3_out` and `./piperunner_ihec_pbs_singularity.sh ./v2/ihec/cemt0007_h3k27me3.json pbs_singularity h3k27me3_out`

The provided configuration files are for 75bp PET only. Standard configration files for SET and read lengths will be provided. The ENCODE documentation discusses other modes.

For these tests, the running time can be 24 hours depending on hardware. 

To compute md5s of generated file, use `computemd5s.py <output_dir> <script_suffix>` with `<output_dir>` being the output directory of previous step and `<script_suffix>` being the suffix to add at file output basename `computemd5s_`. This will locate peak calls and bam files, and generate scripts to compute the md5s. Note the bam md5s are generated without the bam header as that may contain full paths names.

As an example, supose output of `./singularity_wrapper.sh ./v2/ihec/cemt0007_h3k4me3.json` is in `outdir=$PWD/cromwell-executions/chip/93de85aa-d581-48df-b8ae-a91a6e88a21f`. So do

    python computemd5s.py $outdir test # the first must be the cromwell directory for the analysis, the second a suffix for the script
	chmod +x ./computemd5s_test
	./computemd5s_test > log_h3k4me3
	python status_cemt.py log_h3k4me3 expected_md5s_h3k4me3.json 

This will match md5s for cemt0007 H3K4me3 analysis. And similarly for H3K27me3.

    $ python status_cemt.py computemd5s_0.out ./expected_md5s_h3k27me3.json
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr2_x_ctl_for_rep1.pval0.01.500K.narrowPeak.gz 1c9554fe8b67e61fd7c69a1881ec2e3a
    ok conservative_peak.narrowPeak.hammock.gz b78724bb667cc7bbfece8a587c10c915
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr1_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.hammock.gz defd886ab7923b952e04ee033a722fac
    ok optimal_peak.narrowPeak.hammock.gz b78724bb667cc7bbfece8a587c10c915
    ok rep1-pr.overlap.bfilt.narrowPeak.hammock.gz b78724bb667cc7bbfece8a587c10c915
    ok rep1-pr.overlap.narrowPeak.gz a896c1ec4693ddbd2e098ffa901c1f2a
    ok optimal_peak.narrowPeak.gz 49fdef6c06796ab06e8ac2a1b88075d1
    ok rep1-pr.overlap.bfilt.narrowPeak.gz 49fdef6c06796ab06e8ac2a1b88075d1
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr1_x_ctl_for_rep1.pval0.01.500K.narrowPeak.gz b1ae4fb3f2b68b3c8346c57fa04f476f
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.gz 55de2037c6657d1027fb6b625822fa8b
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr1_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.gz 018ad8f5f3158534320ed359563878d3
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.hammock.gz bf5cd1f743325a0161d4ab77b00af829
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup_x_ctl_for_rep1.pval0.01.500K.narrowPeak.gz 7a52f55148b47e2a48fac330e3672c96
    ok conservative_peak.narrowPeak.gz 49fdef6c06796ab06e8ac2a1b88075d1
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr2_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.gz 0f38658b68706ec12b5faded1141750e
    ok ChIP-Seq.IX1239-A26688-GGCTAC.134224.D2B0LACXX.2.1.merged.nodup.pr2_x_ctl_for_rep1.pval0.01.500K.bfilt.narrowPeak.hammock.gz b1ac6ab70d053b546f186080639252ed
    {
        "failures": 0
    }

## Organizing ENCODE output

See output of `./trackoutput.sh <cromwell_directory_for_analysis> -outdir:$outdir`  to see what files are to be copied over. `trackoutput.sh` will write following lists of files (in `$outdir`):

    ./delete.list              # files that are liklely candidate to deletetion delete
    ./masterfiles.list         # files that will be kept
    ./extraneous_cromwell.list # files that are likely extraneous cromwell files
    ./unresolvedfiles.list     # files that will be kept, but cannot be accessed as they may be hardlinks that cannot be resolved
    ./unexpectedfiles.list     # extraneous cromwell files that do not match patterns for expected cromwell files

Cromwell generates large number of files by creating hardlinks; this script attempts to resolve these links and keeping only one copy of each. `./unresolvedfiles.list` contains hardlinks that the script is unable to resolve because of mount issues or othet OS errors.  

It's expected that `unresolvedfiles.list` and `unexpectedfiles.list` are empty. If they are not empty, the files listed there will need to be looked at. Please review files before deleting to ensure nothing useful is removed.

The recommended workflow is to consider removing files from `delete.list` only (in case diskspace is an issue). And then symlink files from masterfiles.list (while keeping everything else) to a final analysis directory. So all files other than input files and intermediate bam files are still available inside the cromwell directory but the output directory is organized and free of extra logs files and scripts.


## Running on cluster

While the slurm_backend as defined by the encode pipeline will/should work; however, it's recommended that to run analysis on the cluster using slurm (or alternatives) just submit the a shell script containing the `./singularity_wrapper.sh $config` command. This means the entire job will run inside the container on one node on the cluster (i.e. the job will run in Local mode on the node it's submitted to). Using `slurm_singularity` backends (see [ENCODE documentation](https://encode-dcc.github.io/wdl-pipelines/install.html)) will mean cromwell will run on the head node (or where ever the job was launched from), and it will manage farming out each individual task to the cluster, with each task run in its own instance of singularity.   

