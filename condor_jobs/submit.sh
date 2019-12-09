###############################
# Submit shape jobs to condor #
###############################
# create error log out folder if not existens
mkdir -p error log out

# jobs will be submitted directly from this repository, so the logfiles created by the job will be updated.
ERA=$1
WPs=${@:2}
# CHANNELS=${@:3}
PWD=`pwd`
# write arguments.txt
WORKDIR="${PWD}/../.."

for CHANNEL in "mt" "mm" 
do  
    if [ $CHANNEL == "mm" ]; then
        echo "$WORKDIR $ERA mm $CHANNEL"
    else
        for WP in $WPs
        do
            echo "$WORKDIR $ERA $WP $CHANNEL"
        done
    fi
done > arguments.txt

## source LCG Stack and submit the job

if uname -a | grep -E 'el7' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_96/x86_64-centos7-gcc8-opt/setup.sh
    condor_submit produce_shapes_cc7.jdl
elif uname -a | grep -E 'el6' -q
then
    source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc8-opt/setup.sh
    condor_submit produce_shapes_slc6.jdl
else
    echo "Machine unknown, i don't know what to do !"
fi
