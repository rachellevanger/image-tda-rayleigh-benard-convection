#!/bin/bash


dir=$1
lower=$2 # lower end of index range for searching
upper=$3 # upper end of index range for searching
draws=$4 # number of draws to make


patFlowPDSub='g21flow/matches/%05d_deviations_sub.csv'
patFlowPDSup='g21flow/matches/%05d_deviations_sup.csv'
patPerBMP='g21per/bmps_cropped/%05d.bmp'
output=statistics/lyapunov_proximity_${lower}_${upper}_${draws}.txt 

dev=6
ls=10
radius=10
lval=96
uval=160


python ../python/get-lyapunov-proximity.py \
  -d $dir \
  -l $lower \
  -u $upper \
  -n $draws \
  -r $radius \
  --uval $uval \
  --lval $lval \
  --dev $dev \
  --ls $ls \
  --sub $patFlowPDSub \
  --sup $patFlowPDSup \
  --bmp $patPerBMP \
  > $dir/$output



