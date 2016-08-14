

# SEARCH FOR DIMPLE PATTERN
# Look for superlevel dim=1 generators with same death coordinates +-1 as sublevel dim=0 birth generators

def getMatches(sub_pers, sup_pers, med, lifespan):

  def hasMatch(x):
      radius = 1
      result = sub_pers.loc[ (sub_pers['dim']==0) & \
                       (abs(sub_pers['d_x']-x['b_x']) <= radius) & \
                       (abs(sub_pers['d_y']-x['b_y']) <= radius) ]
      return len(result) > 0

  matches = sup_pers.loc[ (sup_pers['dim']==1) & \
                           (sup_pers['birth'] >= med) & \
                           ((sup_pers['birth'] - sup_pers['death']) <= lifespan) ]

  #matches = matches.loc[ sup_pers.apply(hasMatch, axis=1) ]
  
  return matches


