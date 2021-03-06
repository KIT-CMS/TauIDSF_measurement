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
# ./utils/clean.sh

# Create shapes of systematics
ERA=$1
WPs=${@:2}

mkdir tauid_shapes_29_11_2019
for WP in $WPs
do
    ./TauIDSF_measurement/produce_shapes.sh $ERA $WP mt mm
    mkdir tauid_shapes_29_11_2019/${ERA}_${WP}/
    cp ${ERA}_${WP}_shapes.root tauid_shapes_29_11_2019/${ERA}_${WP}/${ERA}_shapes.root
done

for WP in $WPs
do
    # cp tauid_shapes_emb/${ERA}_${WP}/${ERA}_shapes.root .
    cp tauid_shapes_29_11_2019/${ERA}_${WP}/${ERA}_shapes.root .

    bash shapes/convert_to_synced_shapes.sh ${ERA} 

    # Write datacard
    # TODO: Additionally introduce dm and eta binning for measurement 
    for CATEGORIES in "pt_binned" "dm_binned" "inclusive"
    do
        JETFAKES=0
        # EMBEDDING=0
        for EMBEDDING in 0 1
        do
            ./TauIDSF_measurement/produce_datacard.sh $ERA $CATEGORIES $JETFAKES $EMBEDDING $WP mt
        done
    done
    rm ${ERA}_shapes.root
done

JETFAKES=0
for CATEGORIES in "pt_binned" "dm_binned" "inclusive"
do
    ./TauIDSF_measurement/produce_workspace.sh ${ERA} $CATEGORIES | tee ${ERA}_produce_workspace_${CATEGORIES}.log

    # Run statistical inference
    ./TauIDSF_measurement/signal_strength.sh ${ERA} $CATEGORIES $CATEGORIES | tee ${ERA}_signal_strength_${CATEGORIES}.log
    ./TauIDSF_measurement/signal_strength.sh ${ERA} $CATEGORIES "robustHesse" | tee ${ERA}_signal_strength_robustHesse.log
    # ./TauIDSF_measurement/diff_nuisances.sh ${ERA}
    ./TauIDSF_measurement/nuisance_impacts.sh ${ERA} $CATEGORIES | tee ${ERA}_nuisance_impacts.log

    # Make prefit and postfit shapes
    ./TauIDSF_measurement/prefit_postfit_shapes.sh ${ERA} $CATEGORIES
    for EMBEDDING in 0 1
    do
        if [ "$EMBEDDING" == 1 ]
        then
            ./TauIDSF_measurement/plot_shapes.sh $ERA $CATEGORIES $JETFAKES $EMBEDDING mt # $CHANNEL
        else
            ./TauIDSF_measurement/plot_shapes.sh $ERA $CATEGORIES $JETFAKES $EMBEDDING mt mm # $CHANNEL
        fi
    done

    # python combine/print_fitresult.py fitDiagnostics${ERA}.root
done
