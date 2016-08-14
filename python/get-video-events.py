

import sys
from optparse import OptionParser
import numpy as np
import scipy
import os
import pandas as pd
import math



parser = OptionParser('usage: -d dir -c cluster_pattern -r roll_width -s startidx -e endidx -x crop_x -y crop_y -z crop_radius'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-c", dest="cluster_pattern",
                  help="cluster file pattern")
parser.add_option("-r", dest="roll_width",
                  help="single roll width")
parser.add_option("-s", dest="startidx",
                  help="starting index")
parser.add_option("-e", dest="endidx",
                  help="ending index")
parser.add_option("-x", dest="crop_x",
                  help="circle center x")
parser.add_option("-y", dest="crop_y",
                  help="circle center y")
parser.add_option("-z", dest="crop_radius",
                  help="radius of circle")


(options, args) = parser.parse_args()



roll_width = int(options.roll_width)
startidx = int(options.startidx)
endidx = int(options.endidx)
crop_x = int(options.crop_x)
crop_y = int(options.crop_y)
crop_radius = int(options.crop_radius)

# Print header
print "frame, type, center_x, center_y"

# Import the first cluster data.
prev_clusters = pd.read_csv(options.dir + "/" + options.cluster_pattern % startidx, delim_whitespace=True)

# Loop through the rest of the cluster data and do the logic.
for i in range(startidx+1, endidx+1):
  tmp_clusters = pd.read_csv(options.dir + "/" + options.cluster_pattern % i, delim_whitespace=True)

  # Filter by diameter < .5 roll wide
  small_clusters = tmp_clusters[tmp_clusters['diameter'] <= .5]
  # Filter for at least one pinch
  small_clusters = small_clusters[small_clusters['pinch_upper'] > 0]

  if len(small_clusters) > 0:

    # Filter for at least 3 pixels away from the boundary
    small_clusters = small_clusters[ small_clusters.apply(lambda row: math.sqrt(math.pow(crop_x - row['center_x'],2) + math.pow(crop_y - row['center_y'],2)) <= (crop_radius - 3), axis=1 ) ]

    if len(small_clusters) > 0:

      # Filter for >=2 rolls away from every previous cluster
      def isIsolated(x):
          result = prev_clusters.apply(lambda row: math.sqrt(math.pow(x['center_x'] - row['center_x'],2) + math.pow(x['center_y'] - row['center_y'],2))/roll_width < max(2,row['diameter']*.75), axis=1 ) 
          return sum(result) == 0

      new_clusters = small_clusters.loc[ small_clusters.apply(isIsolated, axis=1)]

      # TO DO: FIX THIS SHIT
      if len(new_clusters) > 0:
        print "skew_varicose at frame %d" % i

        # print new_clusters
        # for cluster in new_clusters:
        #   print "%d, skew_varicose, %f, %f" % i, cluster['center_x'], cluster['center_y']

  prev_clusters = tmp_clusters







