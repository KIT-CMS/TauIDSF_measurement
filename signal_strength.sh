#!/bin/bash

ERA=$1
CATEGORIES=$2

source utils/setup_cmssw.sh


INPUT=${PWD}/output/${ERA}_tauid

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

if [ $CATEGORIES == "robustHesse" ]
then
    combineTool.py -M FitDiagnostics -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
        --robustFit 1 -n $ERA -v1 \
        --robustHesse 1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --parallel 10 --there
    #python combine/check_mlfit.py fitDiagnostics${ERA}.root
    for RESDIR in ${INPUT}/htt_mt*
    do
        echo "[INFO] Printing fitDiagnostics result for category `basename $RESDIR`"
        root -l ${RESDIR}/fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" | grep "covariance matrix quality"
    done
fi

if [ $CATEGORIES == "inclusive" ] || [ $CATEGORIES == "pt_binned" ] || [ $CATEGORIES == "ptdm_binned" ]
then
    combineTool.py -M MultiDimFit -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
        --algo singles --robustFit 1 \
        --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
        --floatOtherPOIs 1 \
        -n $ERA -v3 \
        --parallel 10 --there
    for RESDIR in ${INPUT}/htt_mt*
    do
        echo "[INFO] Printing fit result for category `basename $RESDIR`"
        python combine/print_fitresult.py ${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
    done
fi
