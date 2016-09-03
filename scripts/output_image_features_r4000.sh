
#!/bin/bash



sDir=~/Documents/Research/Projects/Schatz/Data/g21chaotic/r4000_2016_02_04_superfast/g21flow

startidx=$1
endidx=$2

rollWidth=26

N=($(ls -1f $sDir/BMPs_sublevel | grep .bmp | wc -l))

# startidx=20
# endidx=$N

crop_x=210
crop_y=210
crop_radius=195

for i in `seq ${startidx} ${endidx}`
do

  echo $i

  # python ../python/get-image-features.py \
  #     -d $sDir \
  #     -p $(printf 'image_properties/%05d.yaml' $i) \
  #     --subpers $(printf 'sub_diamorse/%05d_persistence.csv' $i) \
  #     --suppers $(printf 'sup_diamorse/%05d_persistence.csv' $i) \
  #     --subbnd $(printf 'sub_diamorse/%05d_boundary.csv' $i) \
  #     --supbnd $(printf 'sup_diamorse/%05d_boundary.csv' $i) \
  #     -u 1.6 -l 0.4 \
  #     > $sDir/$(printf 'pattern_data/%05d_matches.csv' $i)

  # python ../python/get-image-clusters.py \
  #     -d $sDir \
  #     -m $(printf 'pattern_data/%05d_matches.csv' $i) \
  #     -r $rollWidth \
  #     > $sDir/$(printf 'pattern_data/%05d_clusters.csv' $i)

  python ../python/get-orientation-field.py \
      -d $sDir \
      -i $(printf 'BMPs_sublevel/%05d.bmp' $i) \
      -b 5 \
      > $sDir/$(printf 'pattern_data/%05d_orientation_field.csv' $i)

  python ../python/get-gradient-based-features.py \
      -d $sDir \
      -i $(printf 'BMPs_sublevel/%05d.bmp' $i) \
      -b 5 \
      -p 5 \
      -n 75 \
      > $sDir/$(printf 'pattern_data/%05d_poincare_indices.csv' $i)

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


