


import sys
from optparse import OptionParser
import math
import os
import pandas as pd
import numpy as np


parser = OptionParser('usage: -d dir -i input_matching_pattern -f from_index -t to_index --rx region_key_x --ry region_key_y -o output_file'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="input_matching_pattern",
                  help="input matching file pattern relative to directory")
parser.add_option("-f", dest="from_index",
                  help="starting index number")
parser.add_option("-t", dest="to_index",
                  help="ending index number")
parser.add_option("--rx", dest="region_key_x",
                  help="x coordinate for region key for upper-left hand box")
parser.add_option("--ry", dest="region_key_y",
                  help="y coordinate for region key for upper-left hand box")
parser.add_option("-o", dest="output_file_pattern",
                  help="output file pattern for paths")



(options, args) = parser.parse_args()

# Parse the inputs
index_from = int(options.from_index)
index_to = int(options.to_index)
region_key = [int(options.region_key_x), int(options.region_key_y)]

# Initialize the variables
pathid = 0 # Incrementer to label each path with a unique id#
active_paths = [] # List of DataFrames to keep track of active paths

# Loop through the matching files and generate the paths
for i in range(index_from, index_to + 1):
    data = pd.read_csv(options.dir + "/" + options.input_matching_pattern % i)
    
    if ( i == index_from ): # No new paths, so don't bother checking existing stuff
      data = data.loc[data['matchedidx'] > -1]
      for idx, d in data.iterrows():
        active_paths.append( pd.DataFrame(data={ \
          'pathid': pathid, \
          'frame': i, \
          'idx': d['idx'], \
          'birth': d['birth'], \
          'death': d['death'], \
          'lifespan': int(d['death']) - int(d['birth']), \
          'b_x': d['b_x'], \
          'b_y': d['b_y'], \
          'd_x': d['d_x'], \
          'd_y': d['d_y'] \
          }, index=[0]) )
        pathid = pathid + 1

    else:

      # Process points that belong to existing paths

      for d in data:

        # Check to see if point was matched to from previous 


        # Check to see if path terminated by checking if in upper left-hand box or not matched forward or in diagonal section


        # If path terminated, output to the path file
        if (terminated):
            # Output the following for each element in the path:
            # frame, idx, birth, death, lifespan, b_x, b_y, d_x, d_y

print active_paths[0]








# # Output the deviation and matching results
# for i in range(index, index + steps):

#     if i==index:
#         data1.to_csv(options.dir + "/" + options.output_file_1 % i)
#         data2.to_csv(options.dir + "/" + options.output_file_2 % i)

#     data1_tmp = pd.read_csv(options.dir + "/" + options.input_pattern_1 % (i+1))
#     data2_tmp = pd.read_csv(options.dir + "/" + options.input_pattern_2 % (i+1))
#     data1_tmp['deviation'] = -1.
#     data2_tmp['deviation'] = -1.

#     update_deviation1 = (data1['deviation'] >= 0.)
#     update_deviation2 = (data2['deviation'] >= 0.)

#     filter1 = np.asarray(data1.loc[update_deviation1, 'idx_%d' % (i - index + 1)]).astype(int)
#     filter2 = np.asarray(data2.loc[update_deviation2, 'idx_%d' % (i - index + 1)]).astype(int)

#     # # Fix this so that the orders are correct; need to order based on idx_%d
#     data1_tmp.loc[filter1, 'deviation'] = np.asarray(data1.loc[update_deviation1, 'deviation'])
#     data2_tmp.loc[filter2, 'deviation'] = np.asarray(data2.loc[update_deviation2, 'deviation'])
#     data1_tmp.to_csv(options.dir + "/" + options.output_file_1 % i)
#     data2_tmp.to_csv(options.dir + "/" + options.output_file_2 % i)



