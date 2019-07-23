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
#./utils/clean.sh

# Create shapes of systematics
ERA=$1
CHANNELS=${@:2}

./TauIDSF_measurement/produce_shapes.sh $ERA $CHANNELS

python shapes/convert_to_synced_shapes.py ${ERA} ${ERA}_shapes.root .

for CHANNEL in $CHANNELS; do
# Write datacard
# TODO: maybe add switch for decay mode dependent fits analogous to stxs binning switch in ml analysis.
# first add possibility to produce decay mode dependent shapes in signal categories
CATEGORIES=stxs_stage0
JETFAKES=false
EMBEDDING=false
./TauIDSF_measurement/produce_datacard.sh $ERA  $CATEGORIES $JETFAKES $EMBEDDING $CHANNEL

./TauIDSF_measurement/produce_workspace.sh ${ERA} inclusive

# Run statistical inference
./TauIDSF_measurement/signal_strength.sh ${ERA} inclusive
./TauIDSF_measurement/signal_strength.sh ${ERA} "robustHesse"
#./TauIDSF_measurement/diff_nuisances.sh ${ERA}
#./TauIDSF_measurement/nuisance_impacts.sh ${ERA}

# Make prefit and postfit shapes
./TauIDSF_measurement/prefit_postfit_shapes.sh ${ERA}
#./TauIDSF_measurement/plot_shapes.sh $CHANNEL

python combine/print_fitresult.py fitDiagnostics${ERA}.root
done
