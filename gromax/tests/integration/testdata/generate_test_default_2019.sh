#!/bin/bash

gmx='gmx mdrun'
tpr=None
nsteps=15000
resetstep=10000
workdir=`pwd`

################################################################################

group=1
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=2
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=3
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=4
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 01 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 2 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=5
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0011 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=6
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0011 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=7
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0011 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=8
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0011 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 4 -ntmpi 4 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=9
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_3 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_4 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=10
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_3 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_4 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=11
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_3 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_4 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=12
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 1 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_3 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_4 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 1 -ntmpi 1 -ntomp 1 -pin on -pinoffset 3 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=13
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=14
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 0 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 1 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=15
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=16
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 1 -ntomp 2 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=17
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=18
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme cpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=19
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded cpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done


group=20
groupdir=$workdir/group_${group}
mkdir $groupdir
cd $groupdir
for i in {1..3}; do
  trialdir=${groupdir}/trial_${i}
  mkdir $trialdir
  cd $trialdir
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_1 -gputasks 00 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 0 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr} &
  $gmx -bonded gpu -deffnm group_${group}_trial_${i}_component_2 -gputasks 11 -nb gpu -noconfout -npme 1 -nsteps ${nsteps} -nstlist 80 -nt 2 -ntmpi 2 -ntomp 1 -pin on -pinoffset 2 -pinstride 1 -pme gpu -resetstep ${resetstep} -s ${tpr}
  wait
  cd ${groupdir}
done




exit
