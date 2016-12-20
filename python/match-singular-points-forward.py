


import sys
from optparse import OptionParser
from PIL import Image
import numpy as np
import os
from scipy import spatial

import pandas as pd


parser = OptionParser('usage: -d dir --sp1 singular_points_1 --sp2 singular_points_2 -o output'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("--sp1", dest="singular_points_1",
                  help="first singular points")
parser.add_option("--sp2", dest="singular_points_2",
                  help="second singular points")
parser.add_option("-o", dest="output",
                  help="output matches")

(options, args) = parser.parse_args()


print("########## Matching %s ###########" % options.singular_points_1)

print("Loading data...")

# Load the singular point data
sp1 = pd.read_csv(options.dir + "/" + options.singular_points_1, sep=' ', names=['x', 'y', 'type']).astype(np.int)
sp2 = pd.read_csv(options.dir + "/" + options.singular_points_2, sep=' ', names=['x', 'y', 'type']).astype(np.int)

for df in [sp1, sp2]: 
  # Add a column of -1 for matchedidx
  df['matchedidx'] = -1
  # Add a column of -1 for distance
  df['matcheddist'] = -1
  # Add -1s for matched birth/death values
  df['matchedx'] = -1
  df['matchedy'] = -1

types = sp1['type'].unique()

print types

print("...data loaded.")


########################################
## MATCHING ALGORITHM
########################################

# ASSUMPTIONS:
# Singular points are moving more-or-less continuously with respect to time,
# and the data is sampled sufficiently dense with respect to time to resolve
# path matchings (your eyes can see it, and so the algorithm should also).

# COMPLICATIONS:
# +1/-1 points annihilate each other
# +1/-1 points are created in pairs

# - For each point in sp1, compute nearest neighbor to same type of point in sp2
# - If two points have same nearest neighbor, tie-break with closest match
# - Flag points for potential cancellations that have opposite signed point closer than
#   the matched point

def buildKDTrees(_sp2, _types):
  data = {}
  trees = {}
  for t in _types:
    tmp = _sp2.loc[(_sp2['type']==t), ['x', 'y']]
    tmp = tmp.reset_index()
    data.update({t: tmp})
    trees.update({t: spatial.KDTree(tmp[['x','y']]) })
  return data, trees

def matchSingularPointsForward(_sp1, _data, _trees):
  print "Performing matching"  

  for i in range(0,len(_sp1)):

    point = _sp1.loc[i,['x','y']]
    t = _sp1.loc[i,['type']][0]

    nn = _trees[t].query(point)

    matched_data = _data[t].loc[nn[1]]

    if nn[0] > 5:

      print "MATCHING: %d, type=%d" % (i, t)
      print point
      print nn
      print _data[t].loc[nn[1], ['index','x','y']]

    _sp1.loc[i,['matchedidx', 'matcheddist', 'matchedx', 'matchedy']] = [matched_data['index'], nn[0], matched_data['x'], matched_data['y']]

data, trees = buildKDTrees(sp2, types)

matchSingularPointsForward(sp1, data, trees)

sp1 = sp1.sort_values(['type', 'matcheddist'])

print sp1.loc[sp1.duplicated(['matchedidx'])]

print pd.concat(g for _, g in sp1.groupby("matchedidx") if len(g) > 1)


