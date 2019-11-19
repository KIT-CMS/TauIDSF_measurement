#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
CATEGORIES=$2
JETFAKES=$3
EMBEDDING=$4
WP=$5
CHANNELS=${@:6}

NUM_THREADS=8

if [ $EMBEDDING == 1 ]
then
    SUFFIX="EMB"
    # Don't use the mm control region for the measurement on embedded samples.
    CR="false"
else
    SUFFIX="MC"
    # Use control region to constrain ZTT yield.
    CR="true"
fi

OUTPUT="${ERA}_tauid_${WP}_${CATEGORIES}_${SUFFIX}"
# Remove output directory
if [ -d output/$OUTPUT ] ; then
    rm -rf output/$OUTPUT
fi

# Create datacards
$CMSSW_BASE/bin/slc7_amd64_gcc700/MorphingTauID2017 \
    --base_path=$PWD \
    --input_folder_mt="/" \
    --input_folder_mm="/" \
    --real_data=true \
    --classic_bbb=false \
    --binomial_bbb=false \
    --jetfakes=$JETFAKES \
    --embedding=$EMBEDDING \
    --postfix="-ML" \
    --use_control_region=$CR \
    --auto_rebin=true \
    --categories=$CATEGORIES \
    --era=$ERA \
    --output=$OUTPUT

# Use Barlow-Beeston-lite approach for bin-by-bin systematics
THIS_PWD=${PWD}
echo $THIS_PWD
cd output/$OUTPUT/
for FILE in htt_mt_*/*.txt
do
    sed -i '$s/$/\n * autoMCStats 0.0/' $FILE
done
cd $THIS_PWD
