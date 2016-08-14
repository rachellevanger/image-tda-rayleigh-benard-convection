

# SEARCH FOR PINCH-OFF PATTERN IN LOW INTENSITY VALUES
# Look for sublevel dim=0 with same death coordinates +-1 as superlevel dim=0 death coordinates

def getMatches(sub_pers, sup_pers, death_lower, death_upper):

  def hasMatch(x):
      radius = 1
      result = sup_pers.loc[ ((sup_pers['dim']==0) & \
                       (abs(sup_pers['d_x']-x['d_x']) <= radius) & \
                       (abs(sup_pers['d_y']-x['d_y']) <= radius)) | \
                        ((sup_pers['dim']==1) & \
                       (abs(sup_pers['b_x']-x['d_x']) <= radius) & \
                       (abs(sup_pers['b_y']-x['d_y']) <= radius)) ]
      return len(result) > 0

  matches = sub_pers.loc[ (sub_pers['dim']==0) & \
                         (sub_pers['death'] >= death_lower) & \
                         (sub_pers['death'] < death_upper) & \
                         ((abs(sub_pers['b_x']-sub_pers['d_x'])+abs(sub_pers['b_y']-sub_pers['d_y'])) > 2) ]
  #matches = matches.loc[ sub_pers.apply(hasMatch, axis=1) ]

  return matches

