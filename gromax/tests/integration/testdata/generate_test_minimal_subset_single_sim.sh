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
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 1 -ntomp 4 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} -update cpu
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
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 1 -ntomp 4 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} -update gpu
  wait
  cd ${groupdir}
done


group=3
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} -update cpu
  wait
  cd ${groupdir}
done


group=4
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} -update gpu
  wait
  cd ${groupdir}
done


group=5
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0000 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} -update cpu
  wait
  cd ${groupdir}
done


group=6
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in $(seq 1 ${ntrials}); do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0000 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} -update gpu
  wait
  cd ${groupdir}
done




exit
