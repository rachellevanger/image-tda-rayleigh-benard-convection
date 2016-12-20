

# SEARCH FOR PLUME PATTERN
# Look for sublevel dim=1 generators with same death coordinates +-1 as superlevel dim=0 birth generators

def getMatches(sub_pers, sup_pers, birth_upper, birth_lower):

  def hasMatch(x):
      radius = 1
      result = sup_pers.loc[ (sup_pers['dim']==0) & \
                       (abs(sup_pers['b_x']-x['d_x']) <= radius) & \
                       (abs(sup_pers['b_y']-x['d_y']) <= radius) ]
      return len(result) > 0

  matches = sub_pers.loc[ (sub_pers['dim']==1) & \
                          (sub_pers['birth'] <= birth_upper) & \
                          (sub_pers['birth'] > birth_lower) & \
                          (sub_pers['death'] - sub_pers['birth'] > 10)]
  # matches = matches.loc[ sub_pers.apply(hasMatch, axis=1) ]

  return matches


