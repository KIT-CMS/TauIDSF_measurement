#!/bin/bash

BINNING=TauIDSF_measurement/shapes/binning.yaml
ERA=$1
WP=$2
CHANNELS=${@:3}


source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes.
nice -n 15 python TauIDSF_measurement/shapes/produce_shapes_${ERA}.py \
    --directory $ARTUS_OUTPUTS \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag ${ERA}_$WP \
    --working-point $WP \
    --num-threads 30

# Normalize fake-factor shapes to nominal
# python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root
