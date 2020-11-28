#!/bin/bash

gmx='gmx mdrun'
tpr=None
nsteps=15000
resetstep=10000
ntrials=3
workdir=`pwd`

################################################################################

group=1
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=2
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 0011 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done




exit
