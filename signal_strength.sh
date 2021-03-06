#!/bin/bash

ERA=$1
CATEGORIES=$2
FITKIND=$3
EMBEDDING=$4

source utils/setup_cmssw.sh

SUFFIX="MC"
if [ "$EMBEDDING" == 1 ]
then
    SUFFIX="EMB"
fi

INPUT=${PWD}/output/${ERA}_tauid_*${CATEGORIES}_${SUFFIX}

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

if [ "$EMBEDDING" == 1 ]
then
    # Change limits on zjXsec rateParam based on era
    if [ "$ERA" == "2016" ]
    then
        RANGE="0.95,1.05"
    elif [ "$ERA" == "2017" ] 
    then
        RANGE="0.98,1.02"
    elif [ "$ERA" == "2018" ]
    then
        RANGE="0.98,1.02"
    else
        echo "[FATAL] Given era $ERA does not exist. Aborting..."
        exit 1
    fi
# else
#     # Change limits on zjXsec rateParam based on era
#     if [ "$ERA" == "2016" ]
#     then
#         RANGE="0.85,1.05"
#     elif [ "$ERA" == "2017" ] 
#     then
#         # RANGE="0.96,1.02"
#         RANGE="0.96,1.02"
#     elif [ "$ERA" == "2018" ]
#     then
#         RANGE="0.98,1.02"
#     else
#         echo "[FATAL] Given era $ERA does not exist. Aborting..."
#         exit 1
#     fi
fi

if [ "$EMBEDDING" == 1 ]
then
    if [ "$FITKIND" == "robustHesse" ]
    then
        combineTool.py -M FitDiagnostics -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
            --robustFit 1 -n $ERA -v1 \
            --robustHesse 1 \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --setParameterRanges CMS_htt_doublemutrg_Run${ERA}=$RANGE \
            --parallel 15 --there
        #python combine/check_mlfit.py fitDiagnostics${ERA}.root
        for RESDIR in ${INPUT}/htt_mt*
        do
            echo "[INFO] Printing fitDiagnostics result for category `basename $RESDIR`"
            root -l ${RESDIR}/fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" | grep "covariance matrix quality"
        done
    fi

    if [ "$FITKIND" == "inclusive" ] || [ "$FITKIND" == "pt_binned" ] || [ "$FITKIND" == "ptdm_binned" ] || [ "$FITKIND" == "dm_binned" ]
    then
        combineTool.py -M MultiDimFit -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
            --algo singles --robustFit 1 \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --setParameterRanges CMS_htt_doublemutrg_Run${ERA}=$RANGE \
            --floatOtherPOIs 1 \
            -n $ERA -v3 \
            --parallel 15 --there
        for RESDIR in ${INPUT}/htt_mt*
        do
            echo "[INFO] Printing fit result for category `basename $RESDIR`"
            python combine/print_fitresult.py ${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
        done
    fi
else
    if [ "$FITKIND" == "robustHesse" ]
    then
        combineTool.py -M FitDiagnostics -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
            --robustFit 1 -n $ERA -v1 \
            --robustHesse 1 \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --setParameterRanges CMS_htt_zjXsec=$RANGE \
            --parallel 15 --there
        #python combine/check_mlfit.py fitDiagnostics${ERA}.root
        for RESDIR in ${INPUT}/htt_mt*
        do
            echo "[INFO] Printing fitDiagnostics result for category `basename $RESDIR`"
            root -l ${RESDIR}/fitDiagnostics${ERA}.root <<< "fit_b->Print(); fit_s->Print()" | grep "covariance matrix quality"
        done
    fi

    if [ "$FITKIND" == "inclusive" ] || [ "$FITKIND" == "pt_binned" ] || [ "$FITKIND" == "ptdm_binned" ] || [ "$FITKIND" == "dm_binned" ]
    then
        combineTool.py -M MultiDimFit -m 125 -d ${INPUT}/htt_mt*/combined.txt.cmb.root \
            --algo singles --robustFit 1 \
            --X-rtd MINIMIZER_analytic --cminDefaultMinimizerStrategy 0 \
            --floatOtherPOIs 1 \
            --setParameterRanges CMS_htt_zjXsec=$RANGE \
            -n $ERA -v3 \
            --parallel 15 --there
        for RESDIR in ${INPUT}/htt_mt*
        do
            echo "[INFO] Printing fit result for category `basename $RESDIR`"
            python combine/print_fitresult.py ${RESDIR}/higgsCombine${ERA}.MultiDimFit.mH125.root
        done
    fi
fi
