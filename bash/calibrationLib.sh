#!/bin/bash

# This script will queue processes on the cluster up to the configured limit. The filenames
# will encode the values based using the name ZONE-POPUATION-ACCESS-BETA-COUNTRY.yml although a fixed
# study id is in place as well.

# The maximum number of jobs that can run
LIMIT=99

# Step size used when iterating over the files 
STEP=0.05

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

function generateZoneAsc() {
  eval zones=$1
  for zone in $zones; do
    sed 's/#ZONE#/'"$zone"'/g' zone.asc > $zone.asc
  done
}

function run() {
  eval zone=$1
  eval population_list=$2
  eval treatment_list=$3
  eval country=$4
  eval user=$5

  echo "Running zone, $zone"
  sed 's/#ZONE#/'"$zone"'/g' zone.asc > $zone.asc
  for population in $population_list; do
    for access in $treatment_list; do
      for beta in `seq 0.00 $STEP 1.75`; do
        check_delay $user

        # Prepare the configuration file
        sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $zone-$population-$access-$beta-$country.yml
        sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-$country.yml  
        sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-$country.yml
        sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-$country.yml
    
        sed 's/#BETA#/'"$beta"'/g' template.job > $zone-$population-$access-$beta-$country.pbs
        sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-$country.pbs
        sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-$country.pbs
        sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-$country.pbs
        sed -i 's/#COUNTRY#/'"$country"'/g' $zone-$population-$access-$beta-$country.pbs
    
        # Queue the next item
        qsub $zone-$population-$access-$beta-$country.pbs
      done
    done
  done
}

function runCsv() {
  eval filename=$1
  eval country=$2
  eval user=$3

  while IFS=, read -r zone population access beta
  do
    check_delay $user

    # Trim the return
    beta="$(echo "$beta"|tr -d '\r')"

    # Prepare the configuration file
    sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $zone-$population-$access-$beta-$country.yml
    sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-$country.yml  
    sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-$country.yml
    sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-$country.yml

    sed 's/#BETA#/'"$beta"'/g' template.job > $zone-$population-$access-$beta-$country.pbs
    sed -i 's/#POPULATION#/'"$population"'/g' $zone-$population-$access-$beta-$country.pbs
    sed -i 's/#ACCESS#/'"$access"'/g' $zone-$population-$access-$beta-$country.pbs
    sed -i 's/#ZONE#/'"$zone"'/g' $zone-$population-$access-$beta-$country.pbs
    sed -i 's/#COUNTRY#/'"$country"'/g' $zone-$population-$access-$beta-$country.pbs    

    # Queue the next item
    qsub $zone-$population-$access-$beta-$country.pbs

  done < $filename
}

function runReplicates() {
  eval filename=$1
  eval user=$2

  while IFS=, read -r replicate count; do
    # Trim the return from the count
    count="$(echo "$count"|tr -d '\r')"

    # Loop for the count, note that we are assuming that the configuration 
    # already exists in the database so collisions will not be a concern
    for ndx in `seq 1 1 $count`; do
      check_delay $user
      qsub $replicate
    done
  done < $filename
}