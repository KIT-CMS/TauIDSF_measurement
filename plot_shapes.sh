#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh

ERA=$1
CATEGORIES=$2
JETFAKES=$3
EMBEDDING=$4
CHANNELS=${@:5}

EMBEDDING_ARG=""
if [ $EMBEDDING == 1 ]
then
    EMBEDDING_ARG="--embedding"
fi

JETFAKES_ARG=""
if [ $JETFAKES == 1 ]
then
    JETFAKES_ARG="--fake-factor"
fi

INPUT=${PWD}/output/${ERA}_tauid
for DIR in ${INPUT}/htt_mt*
do
    mkdir -p ${ERA}_plots
    BIN=$(echo `basename $DIR/htt_mt*` | sed 's@^[^0-9]*\([0-9]\+\).*@\1@')
    for FILE in "${DIR}/${ERA}_datacard_shapes_prefit.root" "${DIR}/${ERA}_datacard_shapes_postfit_sb.root"
    do
        for OPTION in "" "--png"
        do
            ./TauIDSF_measurement/plot_shapes.py -i $FILE -c $CHANNELS -e $ERA $OPTION --categories $CATEGORIES $JETFAKES_ARG $EMBEDDING_ARG -l --bin $BIN
        done
    done
    mv ${ERA}_plots/ ${DIR}
done
