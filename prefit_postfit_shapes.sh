#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

INPUT=${PWD}/output/${ERA}_tauid
for DATACARD in $INPUT/htt_mt*/combined.txt.cmb
do
    DIR=$(dirname $DATACARD)
    # Prefit shapes
    # NOTE: The referenced datacard is used for rebinning
    PostFitShapesFromWorkspace -m 125 -w ${DATACARD}.root \
        -d $DATACARD -o ${DIR}/${ERA}_datacard_shapes_prefit.root

    # Postfit shapes
    PostFitShapesFromWorkspace -m 125 -w ${DATACARD}.root \
        -d $DATACARD -o ${DIR}/${ERA}_datacard_shapes_postfit_sb.root -f ${DIR}/fitDiagnostics${ERA}.root:fit_s --postfit
done
