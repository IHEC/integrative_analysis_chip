#!/bin/bash

set -eufx -o pipefail       

# this should be run on the container
#   e.g. singularity exec -B $binds $image_sif $base/postprocess.sh $bamfile $fragmentsize
#   $fragmentsize is required if bam is SET, otherwise it's not needed
# you will need to wget the bamstrip.jar in this directory
#   wget http://www.epigenomes.ca/data/CEMT/resources/bamstrip.jar

bamfile=$1

outdir="/projects/edcc_new/e/chip-may20/integrative_analysis_chip/encode-wrapper/temp-postprocess"
outdir=$(dirname $bamfile)

resources=$(dirname "${BASH_SOURCE[0]}")
bin="/usr/local/bin"
strippedbam="$outdir/$(basename $1 bam)noseq.bam"


#  samtools view -bS - > out.bam # http://samtools.sourceforge.net/pipe.shtml

$bin/samtools view -h $bamfile | /usr/bin/java -jar $resources/bamstrip.jar | $bin/samtools view -hSb - > $strippedbam
echo "#return:$? $strippedbam $1"                                                                                                                                    

$bin/samtools index $strippedbam
$bin/samtools flagstat $strippedbam > "$strippedbam".flagstats

echo "#flagstats ${strippedbam}.flagstats"

bw=$outdir/$(basename $bamfile bam)raw.bigwig

extendreads="--extendReads ${2:-}"

$bin/bamCoverage $extendreads -b $bamfile -o $bw -of bigwig --binSize 1 --maxFragmentLength 1000 -p 8
echo "#return:$? $bw $bamfile"

echo "#out $@ $strippedbam $bw"



