#!/bin/bash

PWD=$1
ERA=$2
WP=$3
CHANNELS=${@:4}

cd $PWD
BINNING=TauIDSF_measurement/shapes/binning.yaml


source utils/setup_python.sh
source utils/setup_samples.sh $ERA

# Produce shapes.
python TauIDSF_measurement/shapes/produce_shapes_${ERA}.py \
    --directory $ARTUS_OUTPUTS \
    --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
    --datasets $KAPPA_DATABASE \
    --binning $BINNING \
    --channels $CHANNELS \
    --era $ERA \
    --tag ${ERA}_${WP} \
    --working-point $WP \
    --num-threads 8

# Normalize fake-factor shapes to nominal
# python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root
