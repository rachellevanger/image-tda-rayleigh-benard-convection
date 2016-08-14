


import sys
from optparse import OptionParser
from PIL import Image
import numpy as np
import os

import pandas as pd


parser = OptionParser('usage: -d dir --img1 image1 --sub1 sublevel1 --sup1 superlevel1 --img2 image2 --sub2 sublevel2 --sup2 superlevel2 --osub outputsub --osup outputsup'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("--img1", dest="img1",
                  help="first image")
parser.add_option("--sub1", dest="sub1",
                  help="first sublevel")
parser.add_option("--sup1", dest="sup1",
                  help="first superlevel")
parser.add_option("--img2", dest="img2",
                  help="second image")
parser.add_option("--sub2", dest="sub2",
                  help="second sublevel")
parser.add_option("--sup2", dest="sup2",
                  help="second superlevel")
parser.add_option("--osub", dest="osub",
                  help="sublevel match")
parser.add_option("--osup", dest="osup",
                  help="superlevel match")

(options, args) = parser.parse_args()


# Load the bitmap images.
im1 = Image.open(options.dir + "/" + options.img1)
im1.load()
bmp1 = np.array(im1).astype(int)

im2 = Image.open(options.dir + "/" + options.img2)
im2.load()
bmp2 = np.array(im2).astype(int)

# Compute the sup norm between the two images to use as stability criteria
max_error = np.absolute(np.subtract(bmp1, bmp2)).max()

# Load the diamorse data
sub1 = pd.read_csv(options.dir + "/" + options.sub1)
sup1 = pd.read_csv(options.dir + "/" + options.sup1)
sub2 = pd.read_csv(options.dir + "/" + options.sub2)
sup2 = pd.read_csv(options.dir + "/" + options.sup2)

# Add a column of zeros for isMatched
sub1['isMatched'] = -1
sup1['isMatched'] = -1
sub2['isMatched'] = -1
sup2['isMatched'] = -1

# Convert data frames to numeric
sub1 = sub1.convert_objects(convert_numeric=True)
sup1 = sup1.convert_objects(convert_numeric=True)
sub2 = sub2.convert_objects(convert_numeric=True)
sup2 = sup2.convert_objects(convert_numeric=True)

# MATCH INFINITY POINTS
sub1.loc[0,'isMatched'] = 0
sup1.loc[0,'isMatched'] = 0
sub2.loc[0,'isMatched'] = 1
sup2.loc[0,'isMatched'] = 1


# BOTTLENECK MATCHES
# For each point in sub1, sup1, look for points in corresponding dimensions in sub2, sup2 
# that are within the max_error. If only one match, this is a matched point by stability.
def bottleneckMatches(pt, data):
  result = data.loc[ 
                   (data['isMatched'] == -1) & \
                   (data['dim']==pt['dim']) & \
                   (abs(data['birth']-pt['birth']) <= max_error) & \
                   (abs(data['death']-pt['death']) <= max_error) 
                   ]

  if len(result) == 1:
    return result.index.tolist()[0]
  else:
    return -1

def findBottleneckMatches():
  for i in range(0,len(sub1.index)):
    if sub1.loc[i,'isMatched'] == -1:
      match = bottleneckMatches(sub1.iloc[i], sub2)
      sub1.loc[i,'isMatched'] = match
      if match > -1:
        sub2.loc[match,'isMatched'] = 1

  for i in range(0,len(sup1.index)):
    if sup1.loc[i,'isMatched'] == -1:
      match = bottleneckMatches(sup1.iloc[i], sup2)
      sup1.loc[i,'isMatched'] = match
      if match > -1:
        sup2.loc[match,'isMatched'] = 1

# STABLE GENERATOR MATCHES
# Match the stable generators to within +-5 pixels
def stableGeneratorMatches(pt, data):
  radius = 5
  result = data.loc[ 
                   (data['isMatched'] == -1) & \
                   (data['dim']==pt['dim']) & \
                   (abs(data['b_x']-pt['b_x']) <= radius) & \
                   (abs(data['b_y']-pt['b_y']) <= radius)  & \
                   (abs(data['d_x']-pt['d_x']) <= radius) & \
                   (abs(data['d_y']-pt['d_y']) <= radius) 
                   ]

  if len(result) == 1:
    return result.index.tolist()[0]
  else:
    return -1

def findStableGeneratorMatches():
  for i in range(0,len(sub1.index)):
    if sub1.loc[i,'isMatched'] == -1:
      match = stableGeneratorMatches(sub1.iloc[i], sub2)
      sub1.loc[i,'isMatched'] = match
      if match > -1:
        sub2.loc[match,'isMatched'] = 1

  for i in range(0,len(sup1.index)):
    if sup1.loc[i,'isMatched'] == -1:
      match = stableGeneratorMatches(sup1.iloc[i], sup2)
      sup1.loc[i,'isMatched'] = match
      if match > -1:
        sup2.loc[match,'isMatched'] = 1

# PINCH-OFF GENERATOR MATCHES
# Match the pinch-off to within +-5 pixels
def stablePinchOffMatches(pt, data, type):
  radius = 5
  if type == 'sub':
    result = data.loc[ 
                     (data['isMatched'] == -1) & \
                     (data['dim']==pt['dim']) & \
                     (abs(data['d_x']-pt['d_x']) <= radius) & \
                     (abs(data['d_y']-pt['d_y']) <= radius) 
                     ]
  else:
    result = data.loc[ 
                     (data['isMatched'] == -1) & \
                     (data['dim']==pt['dim']) & \
                     (abs(data['d_x']-pt['d_x']) <= radius) & \
                     (abs(data['d_y']-pt['d_y']) <= radius) 
                     ]

  if len(result) == 1:
    return result.index.tolist()[0]
  else:
    return -1

def findStablePinchOffMatches():
  for i in range(0,len(sub1.index)):
    if (sub1.loc[i,'isMatched'] == -1) & (sub1.loc[i,'dim'] == 0) & (sub1.loc[i,'death'] < 170):
      match = stablePinchOffMatches(sub1.iloc[i], sub2, 'sub')
      sub1.loc[i,'isMatched'] = match
      if match > -1:
        sub2.loc[match,'isMatched'] = 1

  # MAKE SUPERLEVEL CRITERIA
  # for i in range(0,len(sup1.index)):
  #   if (sub1.loc[i,'isMatched'] == -1) & (sub1.loc[i,'dim'] == 0) & (sub1.loc[i,'death'] < 170):
  #     match = stablePinchOffMatches(sup1.iloc[i], sup2)
  #     sup1.loc[i,'isMatched'] = match
  #     if match > -1:
  #       sup2.loc[match,'isMatched'] = 1



# STBLE ROLL MATCHES
# Match birth generators of death abve the pinch-off level to within +-5 pixels
def stableRollMatches(pt, data, type):
  radius = 5
  if type == 'sub':
    result = data.loc[ 
                     (data['isMatched'] == -1) & \
                     (data['dim']==pt['dim']) & \
                     (abs(data['b_x']-pt['b_x']) <= radius) & \
                     (abs(data['b_y']-pt['b_y']) <= radius) 
                     ]
  else:
    result = data.loc[ 
                     (data['isMatched'] == -1) & \
                     (data['dim']==pt['dim']) & \
                     (abs(data['b_x']-pt['b_x']) <= radius) & \
                     (abs(data['b_y']-pt['b_y']) <= radius) 
                     ]

  if len(result) == 1:
    return result.index.tolist()[0]
  else:
    return -1

def findStableRollMatches():
  for i in range(0,len(sub1.index)):
    if (sub1.loc[i,'isMatched'] == -1) & (sub1.loc[i,'dim'] == 0) & (sub1.loc[i,'death'] >= 170):
      match = stableRollMatches(sub1.iloc[i], sub2, 'sub')
      sub1.loc[i,'isMatched'] = match
      if match > -1:
        sub2.loc[match,'isMatched'] = 1

  # MAKE SUPERLEVEL CRITERIA
  # for i in range(0,len(sup1.index)):
  #   if (sub1.loc[i,'isMatched'] == -1) & (sub1.loc[i,'dim'] == 0) & (sub1.loc[i,'death'] < 170):
  #     match = stablePinchOffMatches(sup1.iloc[i], sup2)
  #     sup1.loc[i,'isMatched'] = match
  #     if match > -1:
  #       sup2.loc[match,'isMatched'] = 1


# MATCHING PROCEDURE
findStableGeneratorMatches() # Find the stable generator matches
findStablePinchOffMatches() # Find the stable pinch-off matches
findStableRollMatches() # Find the stable roll matches
findBottleneckMatches() # Rerun bottleneck match after eliminations

sub_match = sub1.loc[sub1['isMatched']==-1]
sup_match = sup1.loc[sup1['isMatched']==-1]
# sub_match = sub1.loc[sub1['isMatched']>-1]
# sup_match = sup1.loc[sup1['isMatched']>-1]

sub_match.to_csv(options.osub)
sup_match.to_csv(options.osup)









