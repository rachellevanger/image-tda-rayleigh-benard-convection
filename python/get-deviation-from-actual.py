


import sys
from optparse import OptionParser
import math
import os
import pandas as pd
import numpy as np


parser = OptionParser('usage: -d dir --i1 input_pattern_1 --i2 input_pattern_2 -n index -s step_size --o1 output_file_1 --o2 output_file_2'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("--i1", dest="input_pattern_1",
                  help="first input matching file pattern relative to directory")
parser.add_option("--i2", dest="input_pattern_2",
                  help="second input matching file pattern relative to directory")
parser.add_option("-n", dest="index",
                  help="index number for beginning matching file")
parser.add_option("-s", dest="step_size",
                  help="number of steps for each end-to-end matching")
parser.add_option("--o1", dest="output_file_1",
                  help="output for deviations relative to directory")
parser.add_option("--o2", dest="output_file_2",
                  help="output for deviations relative to directory")

(options, args) = parser.parse_args()

# Parse the inputs
index = int(options.index)
steps = int(options.step_size)

# Load data for first matchings
data1 = pd.read_csv(options.dir + "/" + options.input_pattern_1 % index)
for i in range(1, steps+1):
    data1['idx_%d' % i] = -1
    data1['birth_%d' % i] = -1
    data1['death_%d' % i] = -1
    data1['b_x_%d' % i] = -1
    data1['b_y_%d' % i] = -1
    data1['d_x_%d' % i] = -1
    data1['d_y_%d' % i] = -1
data1['finalmatch'] = data1['matchedidx']
data1['deviation'] = -1
all_index_1 = set(range(0,len(data1)))

# Load initial data for second matchings (assumed to be same as initial data for first matchings)
# Note that terminal matching files are also assumed to be the same for both datasets.
data2 = pd.read_csv(options.dir + "/" + options.input_pattern_2 % index)
for i in range(1, steps+1):
    data2['idx_%d' % i] = -1
    data2['birth_%d' % i] = -1
    data2['death_%d' % i] = -1
    data2['b_x_%d' % i] = -1
    data2['b_y_%d' % i] = -1
    data2['d_x_%d' % i] = -1
    data2['d_y_%d' % i] = -1
data2['finalmatch'] = data2['matchedidx']
data2['deviation'] = -1
all_index_2 = set(range(0,len(data2)))

###### MAKE NICE ERROR MESSAGE IF THE LENGTHS OF THESE FILES IS DIFFERENT ######
print "(%d, %d)" % (len(data1), len(data2))


# Load all the matching data into an array and update the finalmatch in the initial data.
# That is, update to new match if found, update to -1 if not matched through.
for i in range(index + 1, index + steps + 1):
    matchdata = pd.read_csv(options.dir + "/" + options.input_pattern_1 % i)
    result = data1.merge(matchdata, left_on='finalmatch', right_index=True, how='inner')

    result_index = set(result['idx_x'])
    result_not_index = set(all_index_1) - result_index

    result_index = sorted(result_index)
    result_not_index = sorted(result_not_index)

    # Update matched
    if (i < (index + steps)):
        data1.loc[result_index, 'finalmatch'] = result['matchedidx_y'].astype(int)
    data1.loc[result_index, 'idx_%d' % (i - index)] = result['idx_y'].astype(int)
    data1.loc[result_index, 'birth_%d' % (i - index)] = result['birth_y'].astype(int)
    data1.loc[result_index, 'death_%d' % (i - index)] = result['death_y'].astype(int)
    data1.loc[result_index, 'b_x_%d' % (i - index)] = result['b_x_y'].astype(int)
    data1.loc[result_index, 'b_y_%d' % (i - index)] = result['b_y_y'].astype(int)
    data1.loc[result_index, 'd_x_%d' % (i - index)] = result['d_x_y'].astype(int)
    data1.loc[result_index, 'd_y_%d' % (i - index)] = result['d_y_y'].astype(int)

    # Update unmatched to -1
    data1.loc[result_not_index, 'finalmatch'] = -1

    matchdata = []

matched_indices_1 = (data1['finalmatch'] != -1)

# Load all the matching data into an array and update the finalmatch in the initial data.
# That is, update to new match if found, update to -1 if not matched through.
for i in range(index + 1, index + steps + 1):
    matchdata = pd.read_csv(options.dir + "/" + options.input_pattern_2 % i)
    result = data2.merge(matchdata, left_on='finalmatch', right_index=True, how='inner')

    result_index = set(result['idx_x'])
    result_not_index = set(all_index_2) - result_index

    result_index = sorted(result_index)
    result_not_index = sorted(result_not_index)

    # Update matched
    if (i < (index + steps)):
        data2.loc[result_index, 'finalmatch'] = result['matchedidx_y'].astype(int)
    # Change this to output the ids.
    data2.loc[result_index, 'idx_%d' % (i - index)] = result['idx_y'].astype(int)
    data2.loc[result_index, 'birth_%d' % (i - index)] = result['birth_y'].astype(int)
    data2.loc[result_index, 'death_%d' % (i - index)] = result['death_y'].astype(int)
    data2.loc[result_index, 'b_x_%d' % (i - index)] = result['b_x_y'].astype(int)
    data2.loc[result_index, 'b_y_%d' % (i - index)] = result['b_y_y'].astype(int)
    data2.loc[result_index, 'd_x_%d' % (i - index)] = result['d_x_y'].astype(int)
    data2.loc[result_index, 'd_y_%d' % (i - index)] = result['d_y_y'].astype(int)

    # Update unmatched to -1
    data2.loc[result_not_index, 'finalmatch'] = -1

    matchdata = []

matched_indices_2 = (data2['finalmatch'] != -1)

# Get the indices that were matched by both processes
allmatches = matched_indices_1.to_frame().merge(matched_indices_2.to_frame(),left_index=True, right_index=True)
allmatches['matched'] = allmatches['finalmatch_x']&allmatches['finalmatch_y']

matched_indices = (allmatches['matched'] == True)



# For any points matched in both processes (matched==True), compute the largest deviation 
# from between the two inputs by computing pointwise distances.
for i in range(1, steps+1):

    print "Step %d. %d" % (i, len(matched_indices))

    # Compute distance between corresponding points on the transitive matching paths
    D = pd.DataFrame(columns=['tmp', 'deviation'])
    D['tmp'] = ((data1.loc[matched_indices, 'birth_%d' % i] - data2.loc[matched_indices, 'birth_%d' % i])**2 + (data1.loc[matched_indices, 'death_%d' % i] - data2.loc[matched_indices, 'death_%d' % i])**2).apply(np.sqrt)
    # Get current max deviations
    D['deviation'] = data1.loc[matched_indices, 'deviation']

    # Update max deviation
    data1.loc[matched_indices, 'deviation'] = D.max(axis=1)
    data2.loc[matched_indices, 'deviation'] = D.max(axis=1)


# Output the deviation and matching results
for i in range(index, index + steps):

    if i==index:
        data1.to_csv(options.dir + "/" + options.output_file_1 % i)
        data2.to_csv(options.dir + "/" + options.output_file_2 % i)

    data1_tmp = pd.read_csv(options.dir + "/" + options.input_pattern_1 % (i+1))
    data2_tmp = pd.read_csv(options.dir + "/" + options.input_pattern_2 % (i+1))
    data1_tmp['deviation'] = -1.
    data2_tmp['deviation'] = -1.

    update_deviation1 = (data1['deviation'] >= 0.)
    update_deviation2 = (data2['deviation'] >= 0.)

    filter1 = np.asarray(data1.loc[update_deviation1, 'idx_%d' % (i - index + 1)]).astype(int)
    filter2 = np.asarray(data2.loc[update_deviation2, 'idx_%d' % (i - index + 1)]).astype(int)

    # # Fix this so that the orders are correct; need to order based on idx_%d
    data1_tmp.loc[filter1, 'deviation'] = np.asarray(data1.loc[update_deviation1, 'deviation'])
    data2_tmp.loc[filter2, 'deviation'] = np.asarray(data2.loc[update_deviation2, 'deviation'])
    data1_tmp.to_csv(options.dir + "/" + options.output_file_1 % i)
    data2_tmp.to_csv(options.dir + "/" + options.output_file_2 % i)



