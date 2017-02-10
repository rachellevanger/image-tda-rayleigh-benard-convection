


import sys
from optparse import OptionParser
import scipy
import scipy.signal
import scipy.ndimage
from scipy import misc
import numpy as np
import math
import os
import pandas as pd
import numerical_analysis as na
import computer_vision as cv
import data_access as da



parser = OptionParser('usage: -d dir -i image.bmp -r orientation_blur_radius --psub pd_sub.csv --psup pd_sup.csv -m match_to_features.txt --out output_features.txt '  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="bitmap image")
parser.add_option("-r", dest="orientation_blur_radius",
                  default=3,
                  help="orientation blur radius")
parser.add_option("-t", dest="topological_defects",
                  help="topological defect points")
parser.add_option("--psub", dest="pd_sub",
                  help="sublevel persistence")
parser.add_option("--psup", dest="pd_sup",
                  help="superlevel persistence")
parser.add_option("-m", dest="match_to_features",
                  help="optional file to match")
parser.add_option("--out", dest="output_features",
                  help="output file for features")

(options, args) = parser.parse_args()

# Parse input args
orientation_blur_radius = int(options.orientation_blur_radius)

# Set the constants for feature generation
keypoint_radius = 11
keypoint_orientation_bins = 19
keypoint_peak_factor = 0.8

feature_radius = 20
feature_orientation_bins = 12
feature_inner_radius_factor = 0.5
feature_sigma_divisor = 1.



# LOAD ALL OF THE DATA

print "Loading..."

# Load the temperature field
bmp = misc.imread(options.dir + "/" + options.image)

# Compute the topological defects
u = bmp.astype(float)
du = np.gradient(u)
raw_of = na.orientation_field(du, orientation_blur_radius)
of = 255*(raw_of + math.pi/2.0)/math.pi # On scale of 0-255 for printing image. Legacy.
SP = na.singular_points(raw_of)
td = np.asarray([ (i,j,SP[i,j]) for (i,j) in np.argwhere(SP)])
td = td.astype(np.int)

# Combine all keypoints
keypoints = da.loadKeypoints(options.dir + "/" + options.pd_sub, options.dir + "/" + options.pd_sup, td)


# Some computed values
centerx = bmp.shape[0]/2
centery = bmp.shape[1]/2
crop_radius = centerx - 30


print "Generate additional keypoints..."
# Generate the feature vectors

allFeatures = []
orientation_col = keypoints.shape[1]

# Generate additional keypoints based on orientation fields.
allkeypoints = cv.assignOrientations(keypoints, keypoint_radius, of, keypoint_orientation_bins, keypoint_peak_factor, bmp, crop_radius)            

print "Generate feature vectors..."
# Loop through all topological and p.h. defects and generate feature vectors
for i in range(allkeypoints.shape[0]):

    x = int(allkeypoints[i,0])
    y = int(allkeypoints[i,1])

    orientation = allkeypoints[i,orientation_col]
    rotation = -orientation*(180./keypoint_orientation_bins)

    # Only process points within tolerance of boundary
    if (((x - centerx)**2 + (y - centery)**2) <= crop_radius**2):
        features = np.concatenate((allkeypoints[i], [bmp[y, x]], cv.getFeatureVector(of, rotation, x, y, feature_radius, feature_inner_radius_factor, feature_orientation_bins, feature_sigma_divisor, bmp)),axis=0)
        if len(allFeatures) == 0:
            allFeatures = features
        else:
            allFeatures = np.vstack([allFeatures, features])


print "Match feature vectors..."
# Match to existing features
if options.match_to_features:
  prior_keypoints = np.loadtxt(options.dir + "/" + options.match_to_features, delimiter=' ')
  keypoint_matches = cv.getMatchingKeypoints(allFeatures, prior_keypoints)
else:
  keypoint_matches = np.ones((allFeatures.shape[0], 2))*-1


print "Save feature vectors...\n"
# Save feature vectors to file
if len(allFeatures.shape)==1:
    sOut = ' '.join([str(x) for x in allFeatures.tolist()])
    with open(options.dir + '/' + options.output_features, 'w') as f:
        f.write('0 ' + keypoint_matches[0] + ' ' + sOut)
else:
    allFeatures = np.hstack((np.reshape(np.asarray(range(allFeatures.shape[0])), (allFeatures.shape[0], 1)), keypoint_matches, allFeatures))
    np.savetxt(options.dir + '/' + options.output_features,allFeatures,fmt='%d',delimiter=' ')



