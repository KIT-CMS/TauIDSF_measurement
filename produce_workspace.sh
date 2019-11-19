#!/bin/bash

source utils/setup_cmssw.sh
source utils/setup_python.sh

ERA=$1
CATEGORIES=$2

NUM_THREADS=10

# Collect input directories for eras and define output path for workspace
INPUT=output/${ERA}_tauid_*_${CATEGORIES}*
echo "[INFO] Add datacards to workspace from path "${INPUT}"."

# Clean previous workspace
# rm -f $OUTPUT

# Set stack size to unlimited, otherwise the T2W tool throws a segfault if
# combining all eras
ulimit -s unlimited

combineTool.py -M T2W  -i ${INPUT}/htt_mt_*/ --parallel ${NUM_THREADS} -m 125
