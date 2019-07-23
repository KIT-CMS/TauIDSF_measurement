#!/bin/bash

BINNING=TauIDSF_measurement/shapes/binning.yaml
ERA=$1
CHANNELS=${@:2}


source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes.
nice -n 15 python TauIDSF_measurement/shapes/produce_shapes_${ERA}.py \
    --directory $ARTUS_OUTPUTS \
    --mt-friend-directory $ARTUS_FRIENDS_MT \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag $ERA \
    --num-threads 32

# Normalize fake-factor shapes to nominal
# python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root
