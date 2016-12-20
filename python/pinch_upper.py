

# SEARCH FOR PINCH-OFF PATTERN
# Look for sublevel dim=0 with same death coordinates +-1 as superlevel dim=0 death coordinates

def getMatches(sub_pers, sup_pers, death_lower, death_upper):

  def hasMatch(x):
      radius = 1
      result = sub_pers.loc[ ((sub_pers['dim']==0) & \
                       (abs(sub_pers['d_x']-x['d_x']) <= radius) & \
                       (abs(sub_pers['d_y']-x['d_y']) <= radius)) | \
                        ((sub_pers['dim']==1) & \
                       (abs(sub_pers['b_x']-x['d_x']) <= radius) & \
                       (abs(sub_pers['b_y']-x['d_y']) <= radius))]
      return len(result) > 0

  matches = sup_pers.loc[ (sup_pers['dim']==0) & \
                         (sup_pers['death'] >= death_lower) & \
                         (sup_pers['death'] <= death_upper) & \
                         # ((abs(sup_pers['b_x']-sup_pers['d_x'])+abs(sup_pers['b_y']-sup_pers['d_y'])) > 2)  & \
                         (sup_pers['birth'] - sup_pers['death'] > 10) ]
  #matches = matches.loc[ sup_pers.apply(hasMatch, axis=1) ]

  return matches

