
import scipy
from scipy.cluster import hierarchy as hc
import pandas as pd
from skimage import morphology
from scipy import misc
from matplotlib import pyplot as plt
import math, time
from skimage import measure
from scipy import signal
from scipy.ndimage.filters import gaussian_filter
from PIL import Image
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn.apionly as sns 
from scipy import spatial
import numpy as np



def convertMainOrientationBin(_bin, _nbins):
    # Convert from [0,_nbins] to [0,180] to [0,pi]
    orientation = math.radians(_bin*180*(1/_nbins))
    # Convert from [0,pi] to [-pi/2, pi/2]
    orientation = orientation - math.pi/2.
    # Convert from [-pi/2, pi/2] to [pi/2 -> -pi/2 decreasing]
    orientation = orientation*-1.
    
    return orientation
    

def assignOrientations(_keypoints, _radius, _orientationfield, nbins, max_factor, _bmp, _crop_radius):
    """
    Takes in the list of keypoints, the orientation field, and the number of binning values to
    use for the orientation field. Generates a histogram of orientations. Computes the max peak.
    Assigns corresponding orientation to the original keypoint. Adds copies of keypoint to the
    table with orientations given by other peaks that are at least 80% of max peak.
    """


    centerx = _bmp.shape[0]/2
    centery = _bmp.shape[1]/2
    
    crop_radius = _crop_radius
    
    allKeypoints = _keypoints
    allKeypoints = np.hstack([allKeypoints, np.zeros((_keypoints.shape[0],2), np.int)])
        
    # Get circular crop
    crop = np.zeros((_radius*2, _radius*2))
    crop[_radius, _radius] = 1
    crop = morphology.binary_dilation(crop, morphology.disk(_radius))
    
    for i in range(_keypoints.shape[0]):
                
        x = _keypoints[i,0]
        y = _keypoints[i,1]
        
        if (((x - centerx)**2 + (y - centery)**2) <= crop_radius**2):

            # Crop orientation field
            cropped_orientation = _orientationfield[(y-_radius):(y+_radius), (x-_radius):(x+_radius)]
            
            # Get histogram for the orientation field
            orig_hist = np.histogram(cropped_orientation[crop==1], bins=nbins, range=(0,256))[0]
            hist = scipy.ndimage.filters.gaussian_filter(orig_hist, sigma=0.75)
            maxpeak = max(hist)

            peaks = (hist >= max_factor*float(maxpeak)).astype(np.int)
            
            # Label each of the peak components
            peak_components = measure.label(peaks, background=0)

                        
            # If peak wraps first bin to last bin, combine these peaks
            if (peak_components[0] > 0) & (peak_components[-1] > 0):
                peak_components[(peak_components == peak_components[-1])] = peak_components[0]

            maxorientations = []


            for peak_ind in range(1,max(peak_components)+1):
                # Extract the histogram values that fall on this component
                peak_values = np.multiply((peak_components == peak_ind).astype(int), hist)
                maxorientations.append([np.argmax(peak_values), sum(peak_values)])

            maxorientations = np.asarray(maxorientations)
            

            for j in range(maxorientations.shape[0]):
                orientation_rad = convertMainOrientationBin(maxorientations[j,0], nbins)

                if j == 0:
                    allKeypoints[i,-2:] = maxorientations[0,:]
                else:
                    feature = np.concatenate((_keypoints[i,:], maxorientations[j,:]),axis=0)
                    allKeypoints = np.vstack([allKeypoints, feature])
                    

    return allKeypoints


def getFeatureVector(orientationfield, rotation, x, y, _radius, _inner_radius_factor, _nbins, _sigma_divisor, _bmp):
    """
    Takes in a single local patch from the orientation field and generates keypoint descriptor from it.
    Circular patch of given radius centered at (x,y) is cropped from orientation field and divided
    into eight localized patches, after rotating so that the keypoint orientation is centered at zero.
    
    Each smaller patch gets an orientation histogram with the supplied number
    of bins. The value in each bin is the output feature vector for that localized patch, and each of the
    eight localized patches are concatenated together to form a feature vector of length 4*nbins.
    
    The eight localized patches are concentric quadrants of two circles at an outer radius of radius and
    an inner radius of _radius*_inner_radius_factor.
    """
    
    inner_radius = int(_radius*_inner_radius_factor)
    outer_radius = _radius
    
    # GAUSSIAN WEIGHTS
    # Get circular crop
    weights = np.zeros((outer_radius*2, outer_radius*2))
    weights[outer_radius, outer_radius] = 1
    weights = scipy.ndimage.filters.gaussian_filter(weights, sigma=outer_radius/_sigma_divisor)
    weights = weights/np.amax(weights)
    inner_weights = weights[(outer_radius - inner_radius):(outer_radius+inner_radius), (outer_radius - inner_radius):(outer_radius+inner_radius)]
    
    # INNER CIRCLE
    # Get circular crop
    crop = np.zeros((inner_radius*2, inner_radius*2))
    crop[inner_radius, inner_radius] = 1
    crop = morphology.binary_dilation(crop, morphology.disk(inner_radius))
        
    # Crop orientation field
    cropped_orientation = orientationfield[(y-inner_radius):(y+inner_radius), (x-inner_radius):(x+inner_radius)]
    
    # Rotate cropped orientation field: scale to 180 degrees, subtract rotation, then scale to 255
    rotated_orientation = ((cropped_orientation.astype(np.float)*(180./255.) + float(rotation))*(255./180.)).astype(np.int)%256

    # Get histogram for each of the four inner subregions
    tmp_radius = inner_radius
    hist11_inner = np.histogram(rotated_orientation[0:tmp_radius, 0:tmp_radius][crop[0:tmp_radius, 0:tmp_radius]], bins=_nbins, range=(0,256), weights=inner_weights[0:tmp_radius, 0:tmp_radius][crop[0:tmp_radius, 0:tmp_radius]])[0]
    hist12_inner = np.histogram(rotated_orientation[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)][crop[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)]], bins=_nbins, range=(0,256), weights=inner_weights[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)][crop[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)]])[0]
    hist21_inner = np.histogram(rotated_orientation[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius][crop[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius]], bins=_nbins, range=(0,256), weights=inner_weights[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius][crop[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius]])[0]
    hist22_inner = np.histogram(rotated_orientation[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)][crop[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)]], bins=_nbins, range=(0,256), weights=inner_weights[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)][crop[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)]])[0]
    
    # OUTER CIRCLE
    # Get circular crop
    crop = np.zeros((outer_radius*2, outer_radius*2))
    crop[outer_radius, outer_radius] = 1
    crop = morphology.binary_dilation(crop, morphology.disk(outer_radius))
    remove = np.zeros((outer_radius*2, outer_radius*2))
    remove[outer_radius, outer_radius] = 1
    remove = morphology.binary_dilation(remove, morphology.disk(inner_radius))
    crop = crop ^ remove
    
    # Crop orientation field
    cropped_orientation = orientationfield[(y-outer_radius):(y+outer_radius), (x-outer_radius):(x+outer_radius)]
    
    # Rotate cropped orientation field
    rotated_orientation = ((cropped_orientation.astype(np.float)*(180./255.) + float(rotation))*(255./180.)).astype(np.int)%256

    
    # Get histogram for each of the four outer subregions
    tmp_radius = outer_radius
    hist11_outer = np.histogram(rotated_orientation[0:tmp_radius, 0:tmp_radius][crop[0:tmp_radius, 0:tmp_radius]], bins=_nbins, range=(0,256), weights=weights[0:tmp_radius, 0:tmp_radius][crop[0:tmp_radius, 0:tmp_radius]])[0]
    hist12_outer = np.histogram(rotated_orientation[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)][crop[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)]], bins=_nbins, range=(0,256), weights=weights[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)][crop[0:tmp_radius, (tmp_radius+1):(2*tmp_radius)]])[0]
    hist21_outer = np.histogram(rotated_orientation[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius][crop[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius]], bins=_nbins, range=(0,256), weights=weights[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius][crop[(tmp_radius+1):(2*tmp_radius), 0:tmp_radius]])[0]
    hist22_outer = np.histogram(rotated_orientation[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)][crop[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)]], bins=_nbins, range=(0,256), weights=weights[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)][crop[(tmp_radius+1):(2*tmp_radius), (tmp_radius+1):(2*tmp_radius)]])[0]
    
    
    # Return feature vector
    featurevector = np.concatenate((hist11_inner, hist12_inner, hist21_inner, hist22_inner, hist11_outer, hist12_outer, hist21_outer, hist22_outer), axis=0)

    return featurevector
    
