#!/bin/bash

from=$1
to=$2

for i in `seq $from $to`
do

    python ~/Documents/Research/Code/image-tda-rayleigh-benard-convection/python/match-pd-forward.py \
      -d ../testdata/cutoff \
      --img1 bmps_cropped/$(printf "%05d" "$i").bmp \
      --sub1 pd_sublevel/$(printf "%05d" "$i")__sub_all.csv \
      --sup1 pd_superlevel/$(printf "%05d" "$i")__super_all.csv \
      --img2 bmps_cropped/$(printf "%05d" "$(expr $i + 1)").bmp \
      --sub2 pd_sublevel/$(printf "%05d" "$(expr $i + 1)")__sub_all.csv \
      --sup2 pd_superlevel/$(printf "%05d" "$(expr $i + 1)")__super_all.csv \
      --osub matches_new/$(printf "%05d" "$i")_sub.csv \
      --osup matches_new/$(printf "%05d" "$i")_sup.csv

done



