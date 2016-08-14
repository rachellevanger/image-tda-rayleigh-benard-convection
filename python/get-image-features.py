


import sys
from optparse import OptionParser
from PIL import Image
import numpy as np
import os

import pandas as pd

import pinch_upper
import pinch_lower
import plumes_lower
import plumes_upper
import plumes_other
import rings_lower
import rings_upper
import rings_other

import yaml


parser = OptionParser('usage: -d dir -p image_properites.yaml --subpers sub_persistence.csv --suppers sup_persistence.csv --subbnd sub_boundary.csv --supbnd sup_boundary.csv'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-p", dest="imgprop",
                  help="image properties")
parser.add_option("--subpers", dest="sub_persistence",
                  help="sublevel persistence data")
parser.add_option("--suppers", dest="sup_persistence",
                  help="superlevel persistence data")
parser.add_option("--subbnd", dest="sub_boundary",
                  help="sublevel boundary data")
parser.add_option("--supbnd", dest="sup_boundary",
                  help="superlevel boundary data")
parser.add_option("-u", dest="upper_cutoff",
                  help="upper cutoff factor for matching")
parser.add_option("-l", dest="lower_cutoff",
                  help="lower cutoff factor for matching")

(options, args) = parser.parse_args()

# Set static variables 
# TO DO: Make these dynamic.
UPPERFACTOR=float(options.upper_cutoff)
LOWERFACTOR=float(options.lower_cutoff)

# Load the diamorse data
sub = pd.read_csv(options.dir + "/" + options.sub_persistence)
sup = pd.read_csv(options.dir + "/" + options.sup_persistence)

# Load the image properties
stram = open(options.dir + "/" + options.imgprop, "r")
doc = yaml.load(stram)
med=doc["median"]

# Get different types of matches
# TO DO: Separate out the matching criteria to do cheap computations separate from expensive ones.
pinchUpperMatches = pinch_upper.getMatches(sub, sup, med, med*UPPERFACTOR )
pinchLowerMatches = pinch_lower.getMatches(sub, sup, med*LOWERFACTOR, med)
plumeLowerMatches = plumes_lower.getMatches(sub, sup, med, med*LOWERFACTOR)
plumeOtherMatches = plumes_other.getMatches(sub, sup, med*UPPERFACTOR, med)
plumeUpperMatches = plumes_upper.getMatches(sub, sup, med, med*LOWERFACTOR)
ringUpperMatches = rings_upper.getMatches(sub, sup, med, med*LOWERFACTOR)
ringLowerMatches = rings_lower.getMatches(sub, sup, med, med*LOWERFACTOR)
ringOtherMatches = rings_other.getMatches(sub, sup, med, med*LOWERFACTOR)

# Print output
print "match_type,center_x,center_y"

for idx, match in pinchUpperMatches.iterrows():
  print "pinch_upper,%s,%s" % (match['d_x'], match['d_y'])

for idx, match in pinchLowerMatches.iterrows():
  print "pinch_lower,%s,%s" % (match['d_x'], match['d_y'])

for idx, match in plumeLowerMatches.iterrows():
  print "plume_lower,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])

for idx, match in plumeUpperMatches.iterrows():
  print "plume_upper,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])

for idx, match in plumeOtherMatches.iterrows():
  print "plume_other,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])

for idx, match in ringUpperMatches.iterrows():
  print "ring_upper,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])

for idx, match in ringLowerMatches.iterrows():
  print "ring_lower,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])

for idx, match in ringOtherMatches.iterrows():
  print "ring_other,%s,%s" % (match['d_x'], match['d_y'])
  if ((match['birth'] >= med*LOWERFACTOR) & (match['birth'] < med)):
    print "pinch_lower,%s,%s" % (match['b_x'], match['b_y'])
  if ((match['birth'] >= med) & (match['birth'] <= med*UPPERFACTOR)):
    print "pinch_upper,%s,%s" % (match['b_x'], match['b_y'])











