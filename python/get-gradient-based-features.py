


import sys
from optparse import OptionParser
from scipy import misc
import numpy as np
import os


parser = OptionParser('usage: -d dir -i image.bmp'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="bitmap image")

(options, args) = parser.parse_args()


# Load the image
bmp = misc.imread(options.image)

# Get the gradient of the image
grad = np.gradient(bmp)

