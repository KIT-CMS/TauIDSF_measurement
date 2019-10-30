#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
CATEGORIES=$2
JETFAKES=$3
EMBEDDING=$4
CHANNELS=${@:5}

NUM_THREADS=8

# Remove output directory
rm -rf output/${ERA}_tauid

# Create datacards
$CMSSW_BASE/bin/slc6_amd64_gcc530/MorphingTauID2017 \
    --base_path=$PWD \
    --input_folder_mt="/" \
    --input_folder_mm="/" \
    --real_data=true \
    --classic_bbb=false \
    --binomial_bbb=true \
    --jetfakes=$JETFAKES \
    --embedding=$EMBEDDING \
    --postfix="-ML" \
    --channel="${CHANNELS}" \
    --auto_rebin=true \
    --categories=$CATEGORIES \
    --era=$ERA \
    --output="${ERA}_tauid"

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
THIS_PWD=${PWD}
echo $THIS_PWD
cd output/${ERA}_tauid/
for FILE in htt_mt_*/*.txt
do
    sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
done
cd $THIS_PWD
