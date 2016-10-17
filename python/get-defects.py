


import sys
from optparse import OptionParser
import numpy as np
import scipy
from scipy.cluster import hierarchy as hc
import os
import pandas as pd
from skimage import morphology
from scipy import misc



parser = OptionParser('usage: -d dir -i image.bmp -m pattern_matches.csv -s singular_points.txt -r roll_width'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="input image")
parser.add_option("-m", dest="pattern_matches",
                  help="pattern matches")
parser.add_option("-s", dest="singular_points",
                  help="singular points")
parser.add_option("-r", dest="roll_width",
                  help="single roll width")


(options, args) = parser.parse_args()

roll_width = int(options.roll_width)

## Load the pattern matching data
bmp = misc.imread(options.dir + "/" + options.image)
bmp = bmp.astype(float)
matches = pd.read_csv(options.dir + "/" + options.pattern_matches)
singular_points = pd.read_csv(options.dir + "/" + options.singular_points, sep=' ', names=['x', 'y', 'type'])

## Create mask/classification image
mask = np.zeros(bmp.shape) # Location of masks
maskids = [] # Definitions of mask types

## GET PARALLEL ROLL REGIONS
# Dilate the absolute value of the singular_points by 1 roll_width
# Mask out the original image by this dilation
# Remaining regions are the parallel roll regions
sp = np.zeros(bmp.shape)
sp[singular_points['x'], singular_points['y']] = 1

np.set_printoptions(threshold=np.nan)
sp_dilated = morphology.binary_dilation(sp, morphology.disk(roll_width))

print sp_dilated


## GET POSSIBLE SKEW VARICOSE EVENTS
# Find persistence pinches within parallel roll regions



## IDENTIFY STABLE DEFECTS (marked absense of persistence pinch-off features)
# Dilate the locations of the pinch-off features by 1/2*roll_width
# Mask out the singular points by this dilation
# Remining singular points can identify stable defects

## Perform cluster analysis to classfy defect types
# Single-linkage hierarchical cluster initially at 1 roll_width

# Pair of (1, 1) = spiral
# Compute the center and width (can be used to estimate the number of arms)

# Triple of (1, -1, 1) or (-1, 1, -1) in a chain indicate a grain boundary
# Compute the length of the chain and whether it's an upper or lower grain boundary

# Pair of (1, -1) = dislocation
# Compute upper or lower disclination

# Singleton (-1) = disclination
# Compute upper or lower disclination

# Dilate the locations of the classified singular points by 1 roll_width
# Subtract regions within 1/2*roll_width of pinch-off features
# Classify each region according to the above match type








# ## Get the clusters from the pattern matching data
# # Get the vectors from the matches dataframe
# vectors = matches.as_matrix(columns=["center_x", "center_y"])

# # Run the hierarchical cluster algorithm
# fclusters = hc.fclusterdata(vectors, 1.5*roll_width, criterion="distance")

# # Append cluster data to pattern matching dataframe
# matches['cluster'] = fclusters

# ## Generate the cluster output table (pivot the matches table)
# # Get the counts
# counts = matches.pivot_table(index=["cluster"], 
#                         columns="match_type",
#                         values=["center_x"],
#                         aggfunc=len, 
#                         fill_value=0)

# # Get the averages
# averages = matches.groupby(['cluster'])['center_x', 'center_y'].mean()

# # Get the diameters

# def computeDiameter(x):
#     pdist = scipy.spatial.distance.pdist(x.as_matrix(columns=["center_x", "center_y"]), 'euclidean')
#     if pdist.size == 0:
#       return 0
#     else:
#       return max(pdist)/roll_width

# diameters = matches.groupby('cluster').apply(lambda x: computeDiameter(x)).to_frame('diameter')
# diameters.reset_index(inplace=True)

# # Merge the results

# counts.reset_index(inplace=True)
# counts = counts.rename(columns={"center_x":""})
# counts.columns = [' '.join(col).strip() for col in counts.columns.values]

# averages.reset_index(inplace=True)

# output = pd.merge(averages, diameters, on='cluster')
# output = pd.merge(output, counts, on='cluster').to_string(index=False)

# print output


