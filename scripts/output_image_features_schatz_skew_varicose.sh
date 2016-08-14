
#!/bin/bash



dir=$1

sDir=~/Documents/Research/Projects/Schatz/Data/experimental_data/2016_05_15_skew_varicose/processed_data/$dir

rollWidth=20

startidx=1
endidx=20

crop_x=198
crop_y=198
crop_radius=180

for i in `seq ${startidx} ${endidx}`
do

  echo $i

  python get-image-features.py \
      -d $sDir \
      -p $(printf 'image_properties/%05d.yaml' $i) \
      --subpers $(printf 'sub_diamorse/%05d_persistence.csv' $i) \
      --suppers $(printf 'sup_diamorse/%05d_persistence.csv' $i) \
      --subbnd $(printf 'sub_diamorse/%05d_boundary.csv' $i) \
      --supbnd $(printf 'sup_diamorse/%05d_boundary.csv' $i) \
      > $sDir/$(printf 'pattern_data/%05d_matches.csv' $i)

  python get-image-clusters.py \
      -d $sDir \
      -m $(printf 'pattern_data/%05d_matches.csv' $i) \
      -r $rollWidth \
      > $sDir/$(printf 'pattern_data/%05d_clusters.csv' $i)

done


python get-video-events.py \
    -d $sDir \
    -c 'pattern_data/%05d_clusters.csv' \
    -r $rollWidth \
    -s $startidx \
    -e $endidx \
    -x $crop_x \
    -y $crop_y \
    -z $crop_radius


    #\
    #> $sDir/event_matches/events.csv


