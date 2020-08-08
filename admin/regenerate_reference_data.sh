#!/bin/bash

# This script executes the current state of gromax with parameters corresponding to integration
# tests and overwrites the reference run files the integration tests are run against.

topdir=$(git rev-parse --show-toplevel)
if [ -z topdir ]; then
  echo "Not in a gromax git repo" && exit 1
fi

PYTHON=python3

RUNBASE="$topdir/gromax/main.py generate --cpu_ids=0-3 --gpu_ids=0,1"
OUTDIR="$topdir/gromax/tests/integration/testdata"

# Basic 2016 test
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_default_2016.sh --gmx_version=2016

# Basic 2018 test
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_default_2018.sh --gmx_version=2018

# basic 2019 test
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_default_2019.sh --gmx_version=2019

# custom executable test
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_custom_exe.sh --gmx_version=2016 \
  --gmx_executable=/path/to/gmx_mpi

# custom trials test
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_custom_ntrials.sh --gmx_version=2016 \
  --trials_per_group=18

# custom directory is ignored for generate
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_default_2016.sh --gmx_version=2016 \
  --directory=/path/to/nowhere

# custom tpr
$PYTHON $RUNBASE --run_file=$OUTDIR/generate_test_custom_tpr.sh --gmx_version=2016 \
  --tpr=custom_tpr.tpr

exit 0
