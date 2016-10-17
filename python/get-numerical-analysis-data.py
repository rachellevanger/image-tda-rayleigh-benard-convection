


import sys
from optparse import OptionParser
import scipy
import scipy.signal
import scipy.ndimage
from scipy import misc
import numpy as np
import math
import os
import numerical_analysis as na


parser = OptionParser('usage: -d dir -i image.bmp -r radius --outf output_orientation_field.bmp --outsp output_singular_points.txt --outwn output_local_wavenumber.bmp '  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="bitmap image")
parser.add_option("-r", dest="radius",
                  help="radius to use for orientation field computation")
parser.add_option("--outf", dest="output_orientation_field",
                  help="output file for orientation field")
parser.add_option("--outsp", dest="output_singular_points",
                  help="output file for poincare index singular points")
parser.add_option("--outwn", dest="output_local_wavenumber",
                  help="output file for local wavenumber")

(options, args) = parser.parse_args()

# Parse input args
radius = int(options.radius)

# Load the image
bmp = misc.imread(options.dir + "/" + options.image)
u = bmp.astype(float)

# Get the gradient of the image
du = np.gradient(u)

# Get the orientation field of the image with [-pi/2, -pi/2] normalized to [0,255]
OF = na.orientation_field(du, radius)

# Get the locations of the singular points of the orientation field
SP = na.singular_points(OF)
locations = np.asarray([ (i,j,SP[i,j]) for (i,j) in np.argwhere(SP)])

# Output the orientation field 
OF = 255*(OF + math.pi/2.0)/math.pi
misc.imsave(options.dir + "/" + options.output_orientation_field, OF.astype(np.uint8))

# Output the locations of the singular points
np.savetxt(options.dir + "/" + options.output_singular_points, locations, fmt='%d', delimiter=' ')

