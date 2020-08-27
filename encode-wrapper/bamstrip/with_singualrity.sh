#!/bin/bash


image=../images/chip_seq_pipeline_v1_1_4-sambamba-0_7_1-rev1.sif 
singularity exec -B $PWD,$binds $image ./bamstrip $1
