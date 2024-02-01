#!/bin/bash

# This script uses the task-spooler to queue up replicates to run locally.
# For calibration replicates, filenames are encoded using values for the 
# replicate as follows: ZONE-POPUATION-ACCESS-BETA-COUNTRY.yml
#
# NOTE This script is dependent upon task-spooler, https://viric.name/soft/ts/

# The limit on the number of jobs that can run
LIMIT=$((`nproc`-1))

# Step size used when iterating over the files 
STEP=0.05

# Adjustment for over-5 access to treatment
O5ADJUST=1.0

# Check to ensure that file dependencies are present
function check_dependencies {
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

# Generate the population ASC files
function generate_asc() {
  eval populations=$1
  for population in $populations; do
    sed 's/#POPULATION#/'"$population"'/g' population.asc > $population.asc
  done
}

# Generate the zone ASC files
function generate_zone_asc() {
  eval zones=$1
  for zone in $zones; do
    sed 's/#ZONE#/'"$zone"'/g' zone.asc > $zone.asc
  done
}

# Check for the task-spooler and set the job limit
function set_spooler {
  if [[ -z `which tsp` ]]; then
    echo "The task-spooler does not appear to be installed, exiting."
    exit 1
  fi

  tsp -S $LIMIT
  echo "Spool limit set to $LIMIT"
}

# Run the initial beta calibration sweep
function run_sweep() {
  eval zone=$1
  eval population_list=$2
  eval treatment_list=$3
  eval country=$4
  eval user=$5

  # Set the initial job counter
  counter=1

  echo "Running zone, $zone"
  sed 's/#ZONE#/'"$zone"'/g' zone.asc > $zone.asc
  for population in $population_list; do
    for access in $treatment_list; do
      for beta in `seq 0.00 $STEP 2.5`; do

        # Prepare the configuration file
        filename=$zone-$population-$access-$beta-$country
        sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $filename.yml
        sed -i 's/#POPULATION#/'"$population"'/g' $filename.yml
        sed -i 's/#ACCESSU5#/'"$access"'/g' $filename.yml
        sed -i 's/#ACCESSO5#/'"$(bc -l <<< $access*$O5ADJUST)"'/g' $filename.yml
        sed -i 's/#ZONE#/'"$zone"'/g' $filename.yml
    
        # Queue the job, update the counter
        tsp ./MaSim -i $filename.yml -r SQLiteDistrictReporter -j $counter
        ((counter++))
      done
    done
  done
}

# Run a beta calibration CSV file
function run_csv() {
  eval filename=$1
  eval country=$2
  eval user=$3

  # Set the job counter based on the number of files in this folder
  counter=`ls . | wc -l`  

  while IFS=, read -r zone population access beta
  do
    # Trim the return
    beta="$(echo "$beta"|tr -d '\r')"

    # Prepare the configuration file
    filename=$zone-$population-$access-$beta-$country
    sed 's/#BETA#/'"$beta"'/g' $country-calibration.yml > $filename.yml
    sed -i 's/#POPULATION#/'"$population"'/g' $filename.yml
    sed -i 's/#ACCESSU5#/'"$access"'/g' $filename.yml
    sed -i 's/#ACCESSO5#/'"$(bc -l <<< $access*$O5ADJUST)"'/g' $filename.yml
    sed -i 's/#ZONE#/'"$zone"'/g' $filename.yml

    # Queue the job, update the counter
    tsp ./MaSim -i $filename.yml -r SQLiteDistrictReporter -j $counter
    ((counter++))

  done < $filename
}

# Run a CSV file of replicates (i.e., commands), append the job counter
function run_replicates() {
  eval filename=$1
  eval user=$2

  # Set the job counter based on the number of files in this folder
  counter=`ls . | wc -l`  

  while IFS=, read -r command count; do
    # Trim the return from the count
    count="$(echo "$count"|tr -d '\r')"

    # Loop for the count, queue the 
    for ndx in `seq 1 1 $count`; do
      tsp $command -j $counter
      ((counter++))
    done
  done < $filename
}
