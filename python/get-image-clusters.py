


import sys
from optparse import OptionParser
import numpy as np
import scipy
from scipy.cluster import hierarchy as hc
import os
import pandas as pd



parser = OptionParser('usage: -d dir -m pattern_matches.csv -r roll_width'  )

parser.add_option("-d", dest="dir",
                  help="parent directory")
parser.add_option("-m", dest="pattern_matches",
                  help="pattern matches")
parser.add_option("-r", dest="roll_width",
                  help="single roll width")


(options, args) = parser.parse_args()

roll_width = int(options.roll_width)

## Load the pattern matching data
matches = pd.read_csv(options.dir + "/" + options.pattern_matches)

## Get the clusters from the pattern matching data
# Get the vectors from the matches dataframe
vectors = matches.as_matrix(columns=["center_x", "center_y"])

# Run the hierarchical cluster algorithm
fclusters = hc.fclusterdata(vectors, 1.5*roll_width, criterion="distance")

# Append cluster data to pattern matching dataframe
matches['cluster'] = fclusters

## Generate the cluster output table (pivot the matches table)
# Get the counts
counts = matches.pivot_table(index=["cluster"], 
                        columns="match_type",
                        values=["center_x"],
                        aggfunc=len, 
                        fill_value=0)

# Get the averages
averages = matches.groupby(['cluster'])['center_x', 'center_y'].mean()

# Get the diameters

def computeDiameter(x):
    pdist = scipy.spatial.distance.pdist(x.as_matrix(columns=["center_x", "center_y"]), 'euclidean')
    if pdist.size == 0:
      return 0
    else:
      return max(pdist)/roll_width

diameters = matches.groupby('cluster').apply(lambda x: computeDiameter(x)).to_frame('diameter')
diameters.reset_index(inplace=True)

# Merge the results

counts.reset_index(inplace=True)
counts = counts.rename(columns={"center_x":""})
counts.columns = [' '.join(col).strip() for col in counts.columns.values]

averages.reset_index(inplace=True)

output = pd.merge(averages, diameters, on='cluster')
output = pd.merge(output, counts, on='cluster').to_string(index=False)

print output


