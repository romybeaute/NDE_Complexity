from numpy import *
from numpy.linalg import * 
from scipy import signal
from random import shuffle
import numpy as np
from scipy.signal import hilbert
from scipy.stats import ranksums
from scipy.io import savemat
from scipy.io import loadmat
from random import *
from itertools import combinations
from pylab import *

'''
Python code to compute LZc complexity measure as described in "Complexity of multi-dimensional spontaneous EEG decreases during propofol induced general anaesthesia"; and adapted to compute univariate time series


Adaptation : r.beaut@sussex.ac.uk
Date: 05/11/23
Modification : adapt the script to compute the Lempel-Ziv Complexity (LZc) for each electrode separately (assuming each electrode corresponds to a univariate time series)

To compute the complexity meaures LZc for continuous multidimensional time series X, where rows are time series (minimum 2), and columns are observations, type the following in ipython: 
 
execfile('CompMeasures.py')
LZc(X)


Some functions are shared between the measures.
'''



def Pre_uni(X):
    '''
    Detrend and normalize input data, X a univariate time series
    '''
    X = signal.detrend(X - np.mean(X), axis=0)
    return X




##########
'''
LZc - Lempel-Ziv Complexity, column-by-column concatenation
'''
##########



### Binarise data ###
def binarise_epoch(epoch_data,threshold=None):
    # Binarize eeg based on the mean amplitude
    if threshold is None:
        threshold = np.mean(epoch_data)
    return ''.join('1' if x > threshold else '0' for x in epoch_data)


def binarise_univariateTS(X, threshold):
    '''
    Binarise univariate TS based on a threshold.
    '''
    return ''.join('1' if x > threshold else '0' for x in X)



def cpr_uni(bin_string):
    '''
    Lempel-Ziv-Welch compression of binary input string, e.g. string='0010101'. It outputs the size of the dictionary of binary words.
    '''
    
    d = {}
    w = ''
    for c in bin_string:
        wc = w + c
        if wc in d:
            w = wc
        else:
            d[wc] = wc
            w = c
    return len(d) #counts the number of patterns



def compute_comprehensive_LZc(epochs):
    '''
    Computes LZc values in three different ways:
    1. LZc values for each channel and each epoch.
    2. LZc values averaged across all channels for each epoch.
    3. LZc values averaged across all epochs for each channel.

    Args:
        epochs (mne.Epochs): The epochs of EEG data.

    Returns:
        dict: A dictionary containing LZc values as per the three computations.
    '''
    # Initialize the data structures
    LZc_per_channel_and_epoch = {channel: [] for channel in epochs.ch_names}
    LZc_avg_across_channels_per_epoch = []
    LZc_avg_across_epochs_per_channel = {channel: [] for channel in epochs.ch_names}

    # Iterate over each epoch
    for epoch_idx in range(len(epochs)):
        LZc_values_this_epoch = []

        # Compute LZc for each channel within the epoch
        for channel in epochs.ch_names:
            epoch_data = epochs.get_data(picks=channel)[epoch_idx].flatten()
            binarized_data = binarise_epoch(epoch_data)
            LZc_epoch = cpr_uni(binarized_data)

            # Store LZc for each channel and each epoch
            LZc_per_channel_and_epoch[channel].append(LZc_epoch)
            LZc_values_this_epoch.append(LZc_epoch)

        # Compute and store the average LZc across all channels for this epoch
        LZc_avg_across_channels_per_epoch.append(np.mean(LZc_values_this_epoch))

    # Compute the average LZc across all epochs for each channel
    for channel in epochs.ch_names:
        LZc_avg_across_epochs_per_channel[channel] = np.mean(LZc_per_channel_and_epoch[channel])

    # Compile results into a dictionary
    results = {
        'LZc_per_channel_and_epoch': LZc_per_channel_and_epoch,
        'LZc_avg_across_channels_per_epoch': LZc_avg_across_channels_per_epoch,
        'LZc_avg_across_epochs_per_channel': LZc_avg_across_epochs_per_channel
    }

    return results






# USE FOR TEMPORAL ANALYSIS
def compute_LZc_for_all_channels_and_epochs(epochs):
    '''
    - computes the LZc for each epoch within each channel and stores all of the LZc values in a list for that channel
    - result is a dictionary where each key is a channel name, and the corresponding value is a list of LZc values, one for each epoch
    - allows for analysis of the LZc over time, as you can see how the complexity changes from one epoch to the next

    '''
    LZc_values = {channel: [] for channel in epochs.ch_names}
    for channel in epochs.ch_names:
        data = epochs.get_data(picks=channel)
        
        for epoch_data in data:
            epoch_data = epoch_data.flatten()
            binarized_data = binarise_epoch(epoch_data)
            LZc_epoch = cpr_uni(binarized_data)
            LZc_values[channel].append(LZc_epoch)
    return LZc_values




def compute_LZc_for_all_channels(epochs):
    '''
    computes the LZc for each epoch within each channel, but instead of storing each individual LZc value, it computes the average LZc for each channel across all epochs.
    - result : dictionary where each key is a channel name, and the corresponding value is a single number representing the average LZc value for that channel across all epochs.
    - useful for getting a general sense of the complexity for each channel but doesn't preserve the temporal information (i.e., how LZc changes over time).
    '''

    # Calculate LZc for each channel
    LZc_values = {}
    for channel in epochs.ch_names:
        LZc_channel = []
        data = epochs.get_data(picks=channel)  # extracts the preprocessed data for a specific channel across all epochs
        
        # Iterate over epochs for the channel
        for epoch_data in data:

            # Flatten the epoch_data to ensure it is 1D
            epoch_data = epoch_data.flatten()
            
            # Binarize the data for the epoch
            threshold = np.mean(epoch_data)
            binarized_data = ''.join('1' if x > threshold else '0' for x in epoch_data)
            
            # Compute the Lempel-Ziv complexity for the binarized epoch
            LZc_epoch = cpr_uni(binarized_data)
            LZc_channel.append(LZc_epoch)
        
        # Store the average LZc for the channel
        LZc_values[channel] = np.mean(LZc_channel)
    
    return LZc_values


# This function will plot the LZc values as a time series for each channel
def plot_LZc_time_series(LZc_values):
    fig, axes = plt.subplots(nrows=len(LZc_values), ncols=1, figsize=(15, 2*len(LZc_values)))
    for i, (channel, lzcs) in enumerate(LZc_values.items()):
        axes[i].plot(lzcs, label=f'LZc {channel}')
        axes[i].set_title(f'Channel {channel}')
        axes[i].set_xlabel('Epoch')
        axes[i].set_ylabel('LZc')
        axes[i].legend()
    plt.tight_layout()
    plt.show()



def LZc_uni(X):
    '''
    Compute LZc for a unidimensional time series.
    '''
    X = Pre_uni(X)
    threshold = np.mean(X)
    binarized_data = binarise_univariateTS(X, threshold)
    randomized_data = list(binarized_data)
    shuffle(randomized_data)
    randomized_data = ''.join(randomized_data)
    return cpr_uni(binarized_data) / float(cpr_uni(randomized_data))





# def normalize_LZc(epochs, num_shuffles=1000):
#     """
#     Normalizes LZc values by shuffling binarized epoch data.

#     Args:
#         epochs (mne.Epochs): The epochs of EEG data.
#         num_shuffles (int): Number of times to shuffle for creating reference distribution.

#     Returns:
#         list: Normalized LZc values.
#     """
#     normalized_lzc_per_epoch = []
#     shuffled_distribution = []

#     # Iterate over each epoch to calculate LZc for shuffled data
#     for epoch_idx in range(len(epochs)):
#         # Store LZc values for shuffled data of this epoch
#         shuffled_lzc_values = []
        
#         for _ in range(num_shuffles):
#             # Shuffle the binarized data of this epoch
#             for channel in epochs.ch_names:
#                 binarized_data = binarise_epoch(epochs.get_data(picks=channel)[epoch_idx].flatten())
#                 shuffled_binarized_data = list(binarized_data)
#                 shuffle(shuffled_binarized_data)
#                 shuffled_lzc_values.append(cpr_uni(''.join(shuffled_binarized_data)))
        
#         # Calculate mean LZc for shuffled data of this epoch
#         shuffled_distribution.append(np.mean(shuffled_lzc_values))

#     # Normalize actual LZc values
#     for epoch_idx in range(len(epochs)):
#         actual_lzc_values = []
#         for channel in epochs.ch_names:
#             binarized_data = binarise_epoch(epochs.get_data(picks=channel)[epoch_idx].flatten())
#             actual_lzc_values.append(cpr_uni(binarized_data))
        
#         mean_actual_lzc = np.mean(actual_lzc_values)
#         normalized_lzc = (mean_actual_lzc - np.mean(shuffled_distribution)) / np.std(shuffled_distribution)
#         normalized_lzc_per_epoch.append(normalized_lzc)

#     return normalized_lzc_per_epoch




def normalize_LZc(epochs, num_shuffles=100):
    """
    Normalizes LZc values by shuffling binarized epoch data.

    Args:
        epochs (mne.Epochs): The epochs of EEG data.
        num_shuffles (int): Number of times to shuffle for creating reference distribution.

    Returns:
        list: Normalized LZc values.
    """
    normalized_lzc_per_epoch = []
    shuffled_distribution = []

    # Iterate over each epoch to calculate LZc for shuffled data
    for epoch_idx in range(len(epochs)):
        # Store LZc values for shuffled data of this epoch
        shuffled_lzc_values = []
        
        for _ in range(num_shuffles):
            # Shuffle the binarized data of this epoch
            for channel in epochs.ch_names:
                binarized_data = binarise_epoch(epochs.get_data(picks=channel)[epoch_idx].flatten())
                shuffled_binarized_data = list(binarized_data)
                shuffle(shuffled_binarized_data)
                shuffled_lzc_values.append(cpr_uni(''.join(shuffled_binarized_data)))
        
        # Calculate mean LZc for shuffled data of this epoch
        shuffled_distribution.append(np.mean(shuffled_lzc_values))

    # Normalize actual LZc values
    for epoch_idx in range(len(epochs)):
        actual_lzc_values = []
        for channel in epochs.ch_names:
            binarized_data = binarise_epoch(epochs.get_data(picks=channel)[epoch_idx].flatten())
            actual_lzc_values.append(cpr_uni(binarized_data))
        
        mean_actual_lzc = np.mean(actual_lzc_values)
        normalized_lzc = mean_actual_lzc/np.mean(shuffled_distribution)
        # normalized_lzc = (mean_actual_lzc - np.mean(shuffled_distribution)) / np.std(shuffled_distribution)
        normalized_lzc_per_epoch.append(normalized_lzc)

    return normalized_lzc_per_epoch



