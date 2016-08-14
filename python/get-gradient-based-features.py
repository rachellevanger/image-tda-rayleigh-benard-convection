


import sys
from optparse import OptionParser
from scipy import misc
import numpy as np
import math
import os


parser = OptionParser('usage: -d dir -i image.bmp -b block_radius -p poincare_radius -n num_steps'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="image",
                  help="bitmap image")
parser.add_option("-b", dest="block_radius",
                  help="block radius for computing orientation field")
parser.add_option("-p", dest="poincare_radius",
                  help="radius for computing poincare index")
parser.add_option("-n", dest="num_steps",
                  help="number of steps for computing poincare index")

(options, args) = parser.parse_args()

# Parse the inputs
blockRadius = int(options.block_radius)
r = float(options.poincare_radius)
numSteps = int(options.num_steps)

# Load the image
bmp = misc.imread(options.dir + "/" + options.image)

# Get the gradient of the image
grad = np.gradient(bmp.astype(float))

# Compute the orientation field
O = np.zeros(bmp.shape)

for x in range(0,bmp.shape[0]):
    for y in range(0,bmp.shape[1]):
        numerator = 0.
        denominator = 0.
        for i in range(max(0,x-blockRadius),min(bmp.shape[0],x+blockRadius)):
            for j in range(max(0,y-blockRadius),min(bmp.shape[0],y+blockRadius)):
                numerator = numerator + 2.*grad[0][i,j]*grad[1][i,j]
                denominator = denominator + (math.pow(grad[0][i,j],2.) - math.pow(grad[1][i,j],2.))
        if denominator==0:
            O[x,y] = 0
        elif denominator > 0:
            O[x,y] = (1./2.)*math.atan(numerator/denominator)
        elif numerator >= 0:
            O[x,y] = (1./2.)*(math.atan(numerator/denominator)+math.pi)
        elif numerator < 0:
            O[x,y] = (1./2.)*(math.atan(numerator/denominator)-math.pi)
            

for x in range(0,bmp.shape[0]):
    for y in range(0,bmp.shape[1]):
        if O[x,y] <= 0:
            O[x,y] = O[x,y] + math.pi
        else:
            O[x,y] = O[x,y]

# Do the poincare index computations
P = np.zeros(bmp.shape)

for x in range(int(r), bmp.shape[0] - int(r)):
    for y in range(int(r), bmp.shape[1] - int(r)):
        for i in range(0,numSteps):
            t1 = i*((2.*math.pi)/float(numSteps))
            x1=x+int(r*math.cos(t1))
            y1=y+int(r*math.sin(t1))
            t2 = (i+1)*((2.*math.pi)/float(numSteps))
            x2=x+int(r*math.cos(t2))
            y2=y+int(r*math.sin(t2))
            d = O[x2,y2] - O[x1,y1]
            if abs(d) <= math.pi/2.:
                P[x,y] = P[x,y] + d
            if d > math.pi/2.:
                P[x,y] = P[x,y] + math.pi - d
            if d < -math.pi/2.:
                P[x,y] = P[x,y] + math.pi + d
        
P = P/math.pi
P = np.rint(P)
P = P.astype(int)

# Output the matrix
print '\n'.join(' '.join(str(cell) for cell in row) for row in P)


