


import numpy as np
import pandas as pd


def loadKeypoints(_pd_sub_file, _pd_sup_file, _td):
  """
  Loads the persistent homology subelvel/superlevel data and locates critical cells to use as
  keypoints. Also receives in topological defects. Combines all data together into a single array.

  Each keypoint begins with its location:
  [x', 'y'] = keypoint coordinate in the image

  Each keypoint is typed by a binary vector:
  ['ph_sub_0'] = persistent homology, sublevel, saddles
  ['ph_sub_1'] = persistent homology, sublevel, local maxima
  ['ph_sup_0'] = persistent homology, superlevel, saddles
  ['ph_sup_1'] = persistent homology, superlevel, local minima
  ['td_p1'] = topological defect, +1 charge
  ['td_m1'] = topological defect, -1 charge
  ['td_p2'] = topological defect, +2 charge (rare)
  ['td_m2'] = topological defect, -2 charge (rare)

  """

  # Constants for keypoints
  delta = 10
  lowercutoff = 45
  uppercutoff = 200

  # Persistent homology lower saddle points
  ph_features_sub = pd.read_csv(_pd_sub_file)
  ph_features_sub = pd.DataFrame(ph_features_sub)

  # Persistent homology upper saddle points
  ph_features_sup = pd.read_csv(_pd_sup_file)
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
  ph_upper_saddles = pd.concat([ph_upper_saddles, ph_tmp])
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
  td_defects = pd.DataFrame(_td, columns=['y', 'x', 'type'])
  td_defects = td_defects.astype(np.int)
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
  return np.concatenate((ph_defects, td_defects), axis=0)



