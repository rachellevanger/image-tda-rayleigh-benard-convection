


import sys
from optparse import OptionParser
import math
import os
import pandas as pd
import numpy as np


parser = OptionParser('usage: -d dir -i input_pattern -n index -l linear_steps -o output_file'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-i", dest="input_pattern",
                  help="input matching file pattern relative to directory")
parser.add_option("-n", dest="index",
                  help="index number for beginning matching file")
parser.add_option("-l", dest="linear_steps",
                  help="number of steps for end-to-end matching")
parser.add_option("-o", dest="output_file",
                  help="output for deviations relative to directory")

(options, args) = parser.parse_args()

# Parse the inputs
index = int(options.index)
steps = int(options.linear_steps)

# Load initial data
data = pd.read_csv(options.dir + "/" + options.input_pattern % index)
for i in range(1, steps+1):
    data['birth_%d' % i] = -1
    data['death_%d' % i] = -1
data['finalmatch'] = data['isMatched']
data['deviation'] = -1
all_index = set(range(0,len(data)))

# Load all the matching data into an array and update the finalmatch in the initial data.
# That is, update to new match if found, update to -1 if not matched through.
for i in range(index + 1, index + steps + 1):
    matchdata = pd.read_csv(options.dir + "/" + options.input_pattern % i)
    result = data.merge(matchdata, left_on='finalmatch', right_index=True, how='inner')

    result_index = set(result['Unnamed: 0_x'])
    result_not_index = set(all_index) - result_index

    result_index = sorted(result_index)
    result_not_index = sorted(result_not_index)

    # Update matched
    data.loc[result_index, 'finalmatch'] = result['isMatched_y']
    data.loc[result_index, 'birth_%d' % (i - index)] = result['birth_y']
    data.loc[result_index, 'death_%d' % (i - index)] = result['death_y']
    # Update unmatched to -1
    data.loc[result_not_index, 'finalmatch'] = -1

    matchdata = []

matched_indices = (data['finalmatch'] != -1)

# For any transitively-matched points (finalmatch != -1), compute the largest deviation 
# from the planar linear interpolation based on the two terminal matched points.
for i in range(1, steps+1):

    # Parameterize line between starting and terminal point in number of steps
    L = pd.DataFrame(columns=['birth', 'death'])
    L['birth'] = data.loc[matched_indices, 'birth'] + (float(i)/float(steps))*(data.loc[matched_indices, 'birth_%d' % i] - data.loc[matched_indices, 'birth'])
    L['death'] = data.loc[matched_indices, 'death'] + (float(i)/float(steps))*(data.loc[matched_indices, 'death_%d' % i] - data.loc[matched_indices, 'death'])

    # Compute distance between the line and the actual point on the transitive matching path
    D = pd.DataFrame(columns=['tmp', 'deviation'])
    D['tmp'] = ((L['birth'] - data.loc[matched_indices, 'birth'])**2 + (L['death'] - data.loc[matched_indices, 'death'])**2).apply(np.sqrt)
    D['deviation'] = data.loc[matched_indices, 'deviation']

    # Update max deviation
    data.loc[matched_indices, 'deviation'] = D.max(axis=1)

# Output the deviation and matching results
data = data.rename(columns={'Unnamed: 0': 'idx'})
data.to_csv(options.dir + "/" + options.output_file)


