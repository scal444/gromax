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
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 6 -ntmpi 2 -ntomp 3 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
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
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 000111 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 6 -ntmpi 6 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
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
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_2 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_3 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_4 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_5 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 4 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_6 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 5 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
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
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 3 -ntmpi 1 -ntomp 3 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_2 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 3 -ntmpi 1 -ntomp 3 -pin on -pinoffset 3 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
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
  $gmx -deffnm group_${group}_trial_${i}_component_1 -gputasks 000 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 3 -ntmpi 3 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -resetstep ${resetstep} -s ${tpr} &
  $gmx -deffnm group_${group}_trial_${i}_component_2 -gputasks 111 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 3 -ntmpi 3 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done




exit
