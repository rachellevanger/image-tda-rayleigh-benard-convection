


import sys
from optparse import OptionParser
import math
import os
import pandas as pd
import numpy as np
import random
from scipy import misc


parser = OptionParser('usage: -d dir -l lower_limit -u upper_limit -n num_draws -r radius --dev deviation --ls lifespan --sub sublevel_pattern --sup superlevel_pattern --bmp lyapunov_bmp'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-l", dest="lower_limit",
                  help="lower limit for drawing")
parser.add_option("-u", dest="upper_limit",
                  help="upper limit for drawing")
parser.add_option("-n", dest="num_draws",
                  help="number of draws")
parser.add_option("-r", dest="radius",
                  help="radius for Lyapunov match")
parser.add_option("--lval", dest="lower_value",
                  help="lower bound for Lyapunov extreme value")
parser.add_option("--uval", dest="upper_value",
                  help="upper bound for Lyapunov extreme value")
parser.add_option("--dev", dest="deviation",
                  help="lower limit for deviation")
parser.add_option("--ls", dest="lifespan",
                  help="lower limit for lifespan")
parser.add_option("--sub", dest="sublevel_pattern",
                  help="pattern for sublevel file")
parser.add_option("--sup", dest="superlevel_pattern",
                  help="pattern for superlevel file")
parser.add_option("--bmp", dest="lyapunov_bmp",
                  help="lyapunov image")

(options, args) = parser.parse_args()

# Parse the inputs
lower = int(options.lower_limit)
upper = int(options.upper_limit)
draws = int(options.num_draws)
radius = int(options.radius)
lval = int(options.lower_value)
uval = int(options.upper_value)
deviation = float(options.deviation)
lifespan = int(options.lifespan)


# Function for checking for a Lyapunov extreme value match
def hasLyapunovMatch(df, dim, deviation, lifespan, bmp, radius, lval, uval):

    result = 0

    # Filter the dataset
    samplespace = df[(df['dim']==dim) & (df['deviation']>=deviation) & (abs(df['death'] - df['birth']) >= lifespan)]
    if (samplespace.shape[0] > 0):

        # Get a random row
        sample = samplespace.sample()

        # Check to see if there is an extreme Lyapunov value within the radius of either the birth critical cell
        lyap_birth = bmp[max(0,int(sample['b_x']) - radius):min(bmp.shape[0]-1,int(sample['b_x']) + radius), \
            (bmp.shape[1]-min(bmp.shape[1]-1,int(sample['b_y']) + radius)):(bmp.shape[1]-max(0,int(sample['b_y']) - radius))]
        if (len(lyap_birth[(lyap_birth <= lval) | (lyap_birth >= uval)]) > 0):
            result = 1

        # Check to see if there is an extreme Lyapunov value within the radius of either the death critical cell
        if (result == 0):
            lyap_birth = bmp[max(0,int(sample['d_x']) - radius):min(bmp.shape[0]-1,int(sample['d_x']) + radius), \
                (bmp.shape[1]-min(bmp.shape[1]-1,int(sample['d_y']) + radius)):(bmp.shape[1]-max(0,int(sample['d_y']) - radius))]
            if (len(lyap_birth[(lyap_birth <= lval) | (lyap_birth >= uval)]) > 0):
                result = 1

    # Return the result of the match
    return result


# Print the header
print 'index, deviation, lifespan, sub_0_dev, sub_1_dev, sup_0_dev, sup_1_dev, sub_0_ls, sub_1_ls, sup_0_ls, sup_1_ls'

for n in range(0,draws):

    # Get a random number in the range [lower, upper]
    index = random.randint(lower, upper)

    # Load the input data
    data_sub = pd.read_csv(options.dir + "/" + options.sublevel_pattern % index)
    data_sup = pd.read_csv(options.dir + "/" + options.superlevel_pattern % index)
    lyap_bmp = misc.imread(options.dir + "/" + options.lyapunov_bmp % index)

    # GATHER ALL OF THE STATISTICS

    # Deviation & Lifespan Filter

    # Sublevel Dim=0
    sub0_dev = hasLyapunovMatch(data_sub, 0, deviation, lifespan, lyap_bmp, radius, lval, uval)

    # Sublevel Dim=1
    sub1_dev = hasLyapunovMatch(data_sub, 1, deviation, lifespan, lyap_bmp, radius, lval, uval)

    # Superlevel Dim=0
    sup0_dev = hasLyapunovMatch(data_sup, 0, deviation, lifespan, lyap_bmp, radius, lval, uval)

    # Superlevel Dim=1
    sup1_dev = hasLyapunovMatch(data_sup, 1, deviation, lifespan, lyap_bmp, radius, lval, uval)

    # Lifespan Filter Only

    # Sublevel Dim=0
    sub0 = hasLyapunovMatch(data_sub, 0, -1., lifespan, lyap_bmp, radius, lval, uval)

    # Sublevel Dim=1
    sub1 = hasLyapunovMatch(data_sub, 1, -1., lifespan, lyap_bmp, radius, lval, uval)

    # Superlevel Dim=0
    sup0 = hasLyapunovMatch(data_sup, 0, -1., lifespan, lyap_bmp, radius, lval, uval)

    # Superlevel Dim=1
    sup1 = hasLyapunovMatch(data_sup, 1, -1., lifespan, lyap_bmp, radius, lval, uval)

    # Print the results
    print '%d, %f, %d, %d, %d, %d, %d, %d, %d, %d, %d' % (index, deviation, lifespan, sub0_dev, sub1_dev, sup0_dev, sup1_dev, sub0, sub1, sup0, sup1)





