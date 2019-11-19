#!/bin/bash

BINNING=TauIDSF_measurement/shapes/binning.yaml
ERA=$1
CHANNEL=$2
VARIABLES=${@:3}

source utils/setup_cvmfs_sft.sh
source utils/setup_python.sh
source utils/setup_samples.sh $ERA

for VAR in $VARIABLES
do
    nice -n 13 python TauIDSF_measurement/shapes/produce_shapes_${ERA}.py \
        --directory $ARTUS_OUTPUTS \
        --fake-factor-friend-directory $ARTUS_FRIENDS_FAKE_FACTOR \
        --datasets $KAPPA_DATABASE \
        --binning $BINNING \
        --gof-channel $CHANNEL \
        --gof-variable $VAR \
        --era $ERA \
        --tag ${ERA}_control_${VAR} \
        --num-threads 20 \
        --skip-systematic-variations true
done

# Normalize fake-factor shapes to nominal
# python fake-factor-application/normalize_shifts.py ${ERA}_shapes.root
