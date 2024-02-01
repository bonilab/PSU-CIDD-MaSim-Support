#!/bin/bash

# This script will queue processes on the cluster up to the configured limit. The filenames
# will encode the values based using the name ZONE-POPUATION-ACCESS-BETA-COUNTRY.yml although a fixed
# study id is in place as well.

# The maximum number of jobs that can run
LIMIT=100

# Step size used when iterating over the files 
STEP=0.05

# Adjustment for over-5 access to treatment
O5ADJUST=1.0

function check_delay {
  eval user=$1
  while [ `squeue -u $user | grep $user | wc -l` -gt $LIMIT ]; do
    sleep 10s
  done
}

function checkDependencies {
  eval country=$1

  missing=false
  declare -a files=("$country-calibration.yml" "template.job" "population.asc" "zone.asc")
  for file in "${files[@]}"; do
    if [ ! -f "$file" ]; then
      echo "$file does not appear to exist!"
      missing=true
    fi
  done
  if [ "$missing" = true ]; then
    echo "One or more missing files, exiting."
    exit 1
  fi
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
      for beta in `seq 0.00 $STEP 2.5`; do
        check_delay $user

        # Prepare the configuration file
        filename=$zone-$population-$access-$beta-$country
        sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $filename.yml
        sed -i 's/#POPULATION#/'"$population"'/g' $filename.yml
        sed -i 's/#ACCESSU5#/'"$access"'/g' $filename.yml
        sed -i 's/#ACCESSO5#/'"$(bc -l <<< $access*$O5ADJUST)"'/g' $filename.yml
        sed -i 's/#ZONE#/'"$zone"'/g' $filename.yml
    
        # Prepare and queue the job file
        sed 's/#FILENAME#/'"$filename"'/g' template.job > $filename.job    
        sbatch $filename.job
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
    filename=$zone-$population-$access-$beta-$country
    sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $filename.yml
    sed -i 's/#POPULATION#/'"$population"'/g' $filename.yml
    sed -i 's/#ACCESSU5#/'"$access"'/g' $filename.yml
    sed -i 's/#ACCESSO5#/'"$(bc -l <<< $access*$O5ADJUST)"'/g' $filename.yml
    sed -i 's/#ZONE#/'"$zone"'/g' $filename.yml

    # Prepare and queue the job file
    sed 's/#FILENAME#/'"$filename"'/g' template.job > $filename.job    
    sbatch $filename.job

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
      sbatch $replicate
    done
  done < $filename
}