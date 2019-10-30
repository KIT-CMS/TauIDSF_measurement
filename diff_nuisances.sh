#!/bin/bash

ERA=$1

source utils/setup_cmssw.sh

python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py -a -f html -g 2017_diff_nuisances.root fitDiagnostics${ERA}.root > ${ERA}_diff_nuisances.html
