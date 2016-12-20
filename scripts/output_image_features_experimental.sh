
#!/bin/bash



sDir=~/Documents/Research/Projects/Schatz/Data/experimental_data/2016_05_20_spirals_targets/processed_20160520_run_07_27M

startidx=$1
endidx=$2

rollWidth=13

# N=($(ls -1f $sDir/BMPs_sublevel | grep .bmp | wc -l))

# startidx=20
# endidx=$N

crop_x=210
crop_y=210
crop_radius=195

for i in `seq ${startidx} ${endidx}`
do

  echo $i

  python ../python/get-image-features.py \
      -d $sDir \
      -p $(printf 'image_properties/%05d.yaml' $i) \
      --subpers $(printf 'pd_sublevel/%05d_sub_all.csv' $i) \
      --suppers $(printf 'pd_superlevel/%05d_super_all.csv' $i) \
      -u 1.75 -l 0.9 \
      > $sDir/$(printf 'pattern_data/%05d_matches.csv' $i)

  # python ../python/get-image-clusters.py \
  #     -d $sDir \
  #     -m $(printf 'pattern_data/%05d_matches.csv' $i) \
  #     -r $rollWidth \
  #     > $sDir/$(printf 'pattern_data/%05d_clusters.csv' $i)

  # python ../python/get-orientation-field.py \
  #     -d $sDir \
  #     -i $(printf 'BMPs_sublevel/%05d.bmp' $i) \
  #     -b 5 \
  #     > $sDir/$(printf 'pattern_data/%05d_orientation_field.csv' $i)

  # python ../python/get-gradient-based-features.py \
  #     -d $sDir \
  #     -i $(printf 'BMPs_sublevel/%05d.bmp' $i) \
  #     -b 5 \
  #     -p 5 \
  #     -n 75 \
  #     > $sDir/$(printf 'pattern_data/%05d_poincare_indices.csv' $i)

done



# python ../python/get-video-events.py \
#     -d $sDir \
#     -c 'pattern_data/%05d_clusters.csv' \
#     -r $rollWidth \
#     -s $startidx \
#     -e $endidx \
#     -x $crop_x \
#     -y $crop_y \
#     -z $crop_radius \
#     > $sDir/event_matches/events.csv


