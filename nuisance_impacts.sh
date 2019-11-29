#!/bin/bash

ERA=$1
CATEGORIES=$2

SUBMIT=false

source utils/setup_cmssw.sh
# INPUT=${PWD}/output/${ERA}_tauid_*_${CATEGORIES}*
INPUT=${PWD}/output/${ERA}_tauid*${CATEGORIES}*

# Change limits on zjXsec rateParam based on era
if [ "$ERA" == "2016" ]
then
    RANGE="0.85,1.05"
elif [ "$ERA" == "2017" ] || [ "$ERA" == "2018" ]
then
    RANGE="0.96,1.02"
else
    echo "[ERROR] Given era $ERA does not exist. Aborting..."
    exit
fi

for DIR in ${INPUT}/htt_mt*
do
    pushd $DIR
    combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --doInitialFit --robustFit 1 --setParameterRanges CMS_htt_zjXsec=$RANGE \
        --parallel 25 -v1
    if [ "$SUBMIT" = true ]
    then
        echo "Trying to submit"
        combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --doFits --robustFit 1 --setParameterRanges CMS_htt_zjXsec=$RANGE \
            -v1 --job-mode condor --dry-run
        chmod u+x condor_combine_task.sh
        echo "getenv = true\n+RemoteJob = True\n+RequestWalltime = 1800\naccounting_group = cms.higgs\nuniverse = docker\ndocker_image = mschnepf/docker_cc7\n" >> condor_combine_task.sub
    else
        combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --doFits --robustFit 1 --setParameterRanges CMS_htt_zjXsec=$RANGE \
            # --setCrossingTolerance 9.99999999975e-05 \
            # --setRobustFitTolerance 0.10000000001 \
            --parallel 25 -v1 | tee nuisance_impacts_fits.log
    fi
    combineTool.py -M Impacts -m 125 -d combined.txt.cmb.root --output ${ERA}_impacts.json
    plotImpacts.py -i ${ERA}_impacts.json -o ${ERA}_impacts
    popd
done
