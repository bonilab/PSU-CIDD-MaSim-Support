#!/bin/bash

# This script will queue processes on the cluster up to the configured limit. The filenames
# will encode the values based using the name ZONE-POPUATION-ACCESS-BETA-bfa.yml although a fixed
# study id is in place as well.

# Get the current job count, note the overcount due to the delay.
# Wait if there are currently too many jobs
LIMIT=20
function check_delay {
  eval user=$1
  while [ `qstat -u $user | grep $user | wc -l` -gt $LIMIT ]; do
    sleep 10s
  done
}

function generateAsc() {
  eval populations=$1
  for population in $populations; do
    sed 's/#POPULATION#/'"$population"'/g' population.asc > $population.asc
  done
}

function run() {
  eval zone=$1
  eval population_list=$2
  eval treatment_list=$3
  eval user=$4

  echo "Running zone, $zone"
  sed 's/#ZONE#/'"$zone"'/g' zone.asc > $zone.asc
  for population in $population_list; do
    for access in $treatment_list; do
      for beta in `seq 0.00 0.05 1.20`; do
        check_delay $user

        # Prepare the configuration file
        sed 's/#BETA#/'"$beta"'/g' rwa-calibration.yml > $zone-$population-$access-$beta-bfa.yml
        sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-bfa.yml  
        sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-bfa.yml
        sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-bfa.yml
    
        sed 's/#BETA#/'"$beta"'/g' template.job > $zone-$population-$access-$beta-bfa.pbs
        sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-bfa.pbs
        sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-bfa.pbs
        sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-bfa.pbs
    
        # Queue the next item
        qsub $zone-$population-$access-$beta-bfa.pbs
      done
    done
  done
}
