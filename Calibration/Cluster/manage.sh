#!/bin/bash

# Basic management script to allow for replicates to be cleaned up while they are running

# Print usage
if [ -z $1 ]; then 
  echo "Usage: ./manage.sh [command]"
  echo
  echo "delete  - deletes jobs that completed successfully"
  echo "requeue - re-queues jobs that are presnt in the directory"
  echo "rerun   - finds jobs that failed, deletes the logs, queues them"
  exit
fi

# Delete what has already run
if [ $1 = 'delete' ]; then
  for item in `find . -name '*.pbs.e*' -size 0 | sed 's/\(.*\)\.pbs.e.*/\1.*/'`; do
    rm $item
  done
  exit
fi

# Requeue jobs that are in the directory
if [ $1 = 'requeue' ]; then
  for item in `find . -name '*.pbs'`; do
    qsub $item
  done
  exit
fi

# Find jobs that failed, delete the logs, and queue the job again
if [ $1 = 'rerun' ]; then
  for item in `find . -name '*.pbs.e*' ! -size 0 | sed 's/\(.*\)\.pbs.e.*/\1/'`; do
    rm -- $item.pbs.*
    qsub $item.pbs
  done


  exit
fi 

echo "Unknown command, $1"
