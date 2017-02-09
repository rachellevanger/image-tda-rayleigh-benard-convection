


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
import computer_vision as cv



parser = OptionParser('usage: -d dir -i image.bmp -o orientation_field.bmp -s singular_points.txt --psub pd_sub.csv --psup pd_sup.csv --out output_features.txt '  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="bitmap image")
parser.add_option("-o", dest="orientation_field",
                  help="orientation field image")
parser.add_option("-s", dest="singular_points",
                  help="topological defect points")
parser.add_option("--psub", dest="pd_sub",
                  help="sublevel persistence")
parser.add_option("--psup", dest="pd_sup",
                  help="superlevel persistence")
parser.add_option("--out", dest="output_features",
                  help="output file for features")

(options, args) = parser.parse_args()

# Parse input args

# Set the constants for feature generation
delta = 10
lowercutoff = 45
uppercutoff = 200

keypoint_radius = 11
keypoint_orientation_bins = 19
keypoint_peak_factor = 0.8

feature_radius = 20
feature_orientation_bins = 12
feature_inner_radius_factor = 0.5
feature_sigma_divisor = 1.



# LOAD ALL OF THE DATA

# Get orientation field
of = misc.imread(options.dir + "/" + options.orientation_field)
bmp = misc.imread(options.dir + "/" + options.image)

centerx = bmp.shape[0]/2
centery = bmp.shape[1]/2

crop_radius = centerx - 30

# Persistent homology lower saddle points
ph_features_sub = pd.read_csv(options.dir + "/" + options.pd_sub)
ph_features_sub = pd.DataFrame(ph_features_sub)

# Persistent homology upper saddle points
ph_features_sup = pd.read_csv(options.dir + "/" + options.pd_sup)
ph_features_sup = pd.DataFrame(ph_features_sup)

# Generate persistent homology defect matrix
ph_lower_saddles = ph_features_sub.loc[(ph_features_sub['dim']==0) & ((ph_features_sub['death'] - ph_features_sub['birth']) >= delta) & (ph_features_sub['death']>=lowercutoff) & (ph_features_sub['death']<=127)][['d_x','d_y']]
ph_lower_saddles.columns = ['x', 'y']
ph_tmp = ph_features_sub.loc[(ph_features_sub['dim']==1) & ((ph_features_sub['death'] - ph_features_sub['birth']) >= delta) & (ph_features_sub['birth']>=lowercutoff) & (ph_features_sub['birth']<=127)][['b_x','b_y']]
ph_tmp.columns = ['x', 'y']
ph_lower_saddles = pd.concat([ph_lower_saddles, ph_tmp])
ph_lower_saddles['ph_sub_0'] = 1
ph_lower_saddles['ph_sub_1'] = 0
ph_lower_saddles['ph_sup_0'] = 0
ph_lower_saddles['ph_sup_1'] = 0
ph_lower_saddles['td_p1'] = 0
ph_lower_saddles['td_m1'] = 0
ph_lower_saddles['td_p2'] = 0
ph_lower_saddles['td_m2'] = 0

ph_upper_saddles = ph_features_sup.loc[(ph_features_sup['dim']==0) & ((ph_features_sup['birth'] - ph_features_sup['death']) >= delta) & (ph_features_sup['death']>=127) & (ph_features_sup['death']<=uppercutoff)][['d_x','d_y']]
ph_upper_saddles.columns = ['x', 'y']
ph_tmp = ph_features_sup.loc[(ph_features_sup['dim']==1) & ((ph_features_sup['birth'] - ph_features_sup['death']) >= delta) & (ph_features_sup['birth']>=127) & (ph_features_sup['birth']<=uppercutoff)][['b_x','b_y']]
ph_tmp.columns = ['x', 'y']
ph_upper_saddles = pd.concat([ph_lower_saddles, ph_tmp])
ph_upper_saddles['ph_sub_0'] = 0
ph_upper_saddles['ph_sub_1'] = 0
ph_upper_saddles['ph_sup_0'] = 1
ph_upper_saddles['ph_sup_1'] = 0
ph_upper_saddles['td_p1'] = 0
ph_upper_saddles['td_m1'] = 0
ph_upper_saddles['td_p2'] = 0
ph_upper_saddles['td_m2'] = 0

ph_lower_plumes = ph_features_sub.loc[(ph_features_sub['dim']==1) & ((ph_features_sub['death'] - ph_features_sub['birth']) >= delta) & (ph_features_sub['birth']<=127) & (ph_features_sub['death']<=uppercutoff)][['d_x','d_y']]
ph_lower_plumes.columns = ['x', 'y']
ph_lower_plumes['ph_sub_0'] = 0
ph_lower_plumes['ph_sub_1'] = 1
ph_lower_plumes['ph_sup_0'] = 0
ph_lower_plumes['ph_sup_1'] = 0
ph_lower_plumes['td_p1'] = 0
ph_lower_plumes['td_m1'] = 0
ph_lower_plumes['td_p2'] = 0
ph_lower_plumes['td_m2'] = 0

ph_upper_plumes = ph_features_sup.loc[(ph_features_sup['dim']==1) & ((ph_features_sup['birth'] - ph_features_sup['death']) >= delta) & (ph_features_sup['birth']>=127) & (ph_features_sup['death']>=lowercutoff)][['d_x','d_y']]
ph_upper_plumes.columns = ['x', 'y']
ph_upper_plumes['ph_sub_0'] = 0
ph_upper_plumes['ph_sub_1'] = 0
ph_upper_plumes['ph_sup_0'] = 0
ph_upper_plumes['ph_sup_1'] = 1
ph_upper_plumes['td_p1'] = 0
ph_upper_plumes['td_m1'] = 0
ph_upper_plumes['td_p2'] = 0
ph_upper_plumes['td_m2'] = 0

ph_defects = np.concatenate((ph_lower_saddles, ph_upper_saddles, ph_lower_plumes, ph_upper_plumes), axis=0)

# Topological defects
td = pd.read_csv(options.dir + "/" + options.singular_points, sep=' ', names=['y', 'x', 'type'])
td_defects = td.astype(np.int)
td_defects['ph_sub_0'] = 0
td_defects['ph_sub_1'] = 0
td_defects['ph_sup_0'] = 0
td_defects['ph_sup_1'] = 0
td_defects['td_p1'] = (td_defects['type'] == 1).astype(np.int)
td_defects['td_m1'] = (td_defects['type'] == -1).astype(np.int)
td_defects['td_p2'] = (td_defects['type'] == 2).astype(np.int)
td_defects['td_m2'] = (td_defects['type'] == -2).astype(np.int)

td_defects = td_defects.drop('type', 1)
td_defects = td_defects[['x', 'y', 'ph_sub_0', 'ph_sub_1', 'ph_sup_0', 'ph_sup_1', 'td_p1', 'td_m1', 'td_p2', 'td_m2']]

# All of the keypoints
keypoints = np.concatenate((ph_defects, td_defects), axis=0)


# Generate the feature vectors

allFeatures = []

orientation_col = keypoints.shape[1]

# Generate additional keypoints based on orientation fields.
allkeypoints = cv.assignOrientations(keypoints, keypoint_radius, of, keypoint_orientation_bins, keypoint_peak_factor, bmp, crop_radius)            

# Loop through all topological and p.h. defects and generate feature vectors
for i in range(allkeypoints.shape[0]):

    x = allkeypoints[i,0]
    y = allkeypoints[i,1]

    orientation = allkeypoints[i,orientation_col]
    rotation = -orientation*(180./keypoint_orientation_bins)

    # Only process points within tolerance of boundary
    if (((x - centerx)**2 + (y - centery)**2) <= crop_radius**2):
        features = np.concatenate((allkeypoints[i], [bmp[y, x]], cv.getFeatureVector(of, rotation, x, y, feature_radius, feature_inner_radius_factor, feature_orientation_bins, feature_sigma_divisor, bmp)),axis=0)
        if len(allFeatures) == 0:
            allFeatures = features
        else:
            allFeatures = np.vstack([allFeatures, features])

# Save feature vectors to file
if len(allFeatures.shape)==1:
    sOut = ' '.join([str(x) for x in allFeatures.tolist()])
    with open(options.dir + '/' + options.output_features, 'w') as f:
        f.write(sOut)
else:
    np.savetxt(options.dir + '/' + options.output_features,allFeatures,fmt='%d',delimiter=' ')



