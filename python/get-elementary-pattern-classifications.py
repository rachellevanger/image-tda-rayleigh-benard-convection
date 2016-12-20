


import sys
from optparse import OptionParser
from PIL import Image
import numpy as np
import os

import pandas as pd

import scipy
from scipy.cluster import hierarchy as hc
from skimage import morphology
from scipy import misc
import math, time
from skimage import measure


parser = OptionParser('usage: -d dir -b image.bmp -p pattern.csv -s singular_points.txt -r roll_width -o output.bmp'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-b", dest="bmp",
                  help="bitmap image")
parser.add_option("-p", dest="pattern",
                  help="persistent homology pattern matching data")
parser.add_option("-s", dest="singular_points",
                  help="singular point data")
parser.add_option("-r", dest="roll_width",
                  help="single roll width")
parser.add_option("-o", dest="output",
                  help="output file")

(options, args) = parser.parse_args()


# Load the input data
bmp = misc.imread(options.dir + "/" + options.bmp)
bmp = bmp.astype(float)

matches = pd.read_csv(options.dir + "/" + options.pattern)

ph_defects = matches[['center_x', 'center_y']]
ph_defects = ph_defects.astype(np.int)

singular_points = pd.read_csv(options.dir + "/" + options.singular_points, sep=' ', names=['x', 'y', 'type'])
singular_points = singular_points.astype(np.int)

roll_width = int(options.roll_width)

# Generate mask info
mask = np.zeros(bmp.shape) # Location of masks
maskids = {0:'Unassigned'} # Definitions of mask types

## GET PARALLEL ROLL REGIONS
# Dilate the absolute value of the topological and p.h. defects by 1 roll_width
# Mask out the original image by this dilation
# Remaining regions are the candidate parallel roll regions

defects = np.zeros(bmp.shape)
defects[singular_points['x'], singular_points['y']] = 1
defects[ph_defects['center_y'], ph_defects['center_x']] = 1

defects_dilated = morphology.binary_dilation(defects, morphology.disk(roll_width))

# Remove small regions not filtered out
# defects_dilated = morphology.binary_dilation(defects_dilated, morphology.disk(0.5*roll_width))
# defects_dilated = morphology.binary_erosion(defects_dilated, morphology.disk(0.5*roll_width))

# Invert to get the indicator function for the parallel roll regions
defects_dilated_mask = np.invert(defects_dilated)

# Add these regions to the mask
mask[defects_dilated_mask] = 255
maskids[255] = 'Parallel rolls'


## OUTPUT MASK
misc.imsave(options.dir + "/" + options.output, mask.astype(np.uint8))
print maskids






