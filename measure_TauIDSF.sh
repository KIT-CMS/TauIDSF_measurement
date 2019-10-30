#!/bin/bash

# Error handling to ensure that script is executed from top-level directory of
# this repository
for DIRECTORY in shapes datacards combine plotting utils
do
    if [ ! -d "$DIRECTORY" ]; then
        echo "[FATAL] Directory $DIRECTORY not found, you are not in the top-level directory of the analysis repository?"
        exit 1
    fi
done

# Clean-up workspace
./utils/clean.sh

# Create shapes of systematics
ERA=$1
CHANNELS=${@:2}

./TauIDSF_measurement/produce_shapes.sh $ERA $CHANNELS mm

bash shapes/convert_to_synced_shapes.sh ${ERA} 

for CHANNEL in $CHANNELS; do
# Write datacard
# TODO: Additionally introduce dm and eta binning for measurement 
CATEGORIES="inclusive"  # options: inclusive, pt_binned, ptdm_binned
JETFAKES=false
EMBEDDING=false
./TauIDSF_measurement/produce_datacard.sh $ERA $CATEGORIES $JETFAKES $EMBEDDING $CHANNELS mm

./TauIDSF_measurement/produce_workspace.sh ${ERA} $CATEGORIES | tee ${ERA}_produce_workspace_${CATEGORIES}.log

# Run statistical inference
./TauIDSF_measurement/signal_strength.sh ${ERA} $CATEGORIES | tee ${ERA}_signal_strength_${CATEGORIES}.log
./TauIDSF_measurement/signal_strength.sh ${ERA} "robustHesse" | tee ${ERA}_signal_strength_robustHesse.log
#./TauIDSF_measurement/diff_nuisances.sh ${ERA}
./TauIDSF_measurement/nuisance_impacts.sh ${ERA} | tee ${ERA}_nuisance_impacts.log

# Make prefit and postfit shapes
./TauIDSF_measurement/prefit_postfit_shapes.sh ${ERA}
./TauIDSF_measurement/plot_shapes.sh $ERA $CATEGORIES $JETFAKES $EMBEDDING $CHANNEL

# python combine/print_fitresult.py fitDiagnostics${ERA}.root
done
