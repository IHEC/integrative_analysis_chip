#!/bin/bash

set -eufx -o pipefail

chipdir="./integrative_analysis_chip-1.0"

which singularity

if [ ! -d "$chipdir" ]; then
  wget https://github.com/IHEC/integrative_analysis_chip/archive/v1.0.tar.gz
  tar xvzf v1.0.tar.gz
fi

cd $chipdir/encode-wrapper

chmod +x ./get_encode_resources.sh
./get_encode_resources.sh &> get_encode_resources.log
apy chip.py -get &> chip_get.log
apy chip.py -pullimage -bindpwd -pwd2ext0 $PWD/v2/ihec &> chip_pull_image.log


chmod +x ./*sh
./singularity_encode_test_tasks.sh Local try1 > singularity_encode_test_tasks.log
