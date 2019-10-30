#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh
INPUT=${PWD}/output/${ERA}_tauid

for DIR in ${INPUT}/htt_mt*
do
    pushd $DIR
    combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 \
        --parallel 32 -v1
    combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doFits --robustFit 1 \
        -v1 | tee nuisance_impacts_fits.log
        #--parallel 32 -v1
    combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root --output ${ERA}_impacts.json
    plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
    popd
done
