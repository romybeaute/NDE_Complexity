'''
*** Tailored helper functions to work with EEG processing pipeline for insight dataset ***

@Author: Romy Beauté
@Contact: r.beaut@sussex.ac.uk
@Date: 2024-02-06
@Last modification: 2024-02-22
'''

import os
import mne
import numpy as np



# Dictionary mapping file extensions to their respective MNE function : see here to add more extensions https://mne.tools/stable/reading_raw_data.html
read_funcs = {
    '.edf': mne.io.read_raw_edf,
    '.fif': mne.io.read_raw_fif,
    '.egi': mne.io.read_raw_egi
}



def read_EEG(EEG_file,DATASET_path,print_infos=True,plot_raw=False):

    print(f"EEG file : {EEG_file}")
    _, ext = os.path.splitext(EEG_file)
    EEG_path = os.path.join(DATASET_path, EEG_file)

    if ext in read_funcs:
        raw = read_funcs[ext](EEG_path, preload=True)
    else:
        print(f"The file format '{ext}' is not supported by this pipeline.")
        try:
            # Attempt to read with the default function
            raw = mne.io.read_raw(EEG_path, preload=True)
        except Exception as e:
            print(f"Failed to read file with the default reader: {e}")
    if print_infos:
        print(f"Details for file: {EEG_file}\n {raw.info}")
    if plot_raw:
        raw.plot()

    analyze_eeg_recording(EEG_file,raw) #print the duration of the EEG recording
    
    return raw


def analyze_eeg_recording(EEG_file, raw_eeg):
    """
    Analyzes an EEG recording, providing its duration and any annotations present.
    
    Parameters:
    EEG_file (str): The name of the EEG file.
    raw_eeg: The raw EEG data structure.

    Returns:
    dict: A dictionary containing the duration and annotations of the EEG recording.
    """
    analysis_result = {}

    # Calculate the duration of the recording
    duration = len(raw_eeg) / raw_eeg.info['sfreq']
    analysis_result['duration'] = duration
    print(77*"-")
    print(f"Duration of {EEG_file} recording: {duration} seconds")

    # Check for annotations
    if len(raw_eeg.annotations) > 0:
        print(f"Annotations in {EEG_file}:")
        for ann in raw_eeg.annotations:
            print(f" - {ann.description} at {ann.onset} seconds")
        analysis_result['annotations'] = raw_eeg.annotations
    else:
        print(f"No annotations in {EEG_file}")
        analysis_result['annotations'] = None
    print(77*"-")
    return analysis_result


def read_pipeline_EEG(EEG_file,DATASET_path):

    print(f"EEG file : {EEG_file}")
    _, ext = os.path.splitext(EEG_file)
    EEG_path = os.path.join(DATASET_path, EEG_file)

    if ext in read_funcs:
        raw = read_funcs[ext](EEG_path, preload=True)
    else:
        print(f"The file format '{ext}' is not supported by this pipeline.")
        try:
            # Attempt to read with the default function
            raw = mne.io.read_raw(EEG_path, preload=True)
        except Exception as e:
            print(f"Failed to read file with the default reader: {e}")
    
    return raw


def analyze_eeg_recording(EEG_file, raw_eeg):
    """
    Analyzes an EEG recording, providing its duration and any annotations present.
    
    Parameters:
    EEG_file (str): The name of the EEG file.
    raw_eeg: The raw EEG data structure.

    Returns:
    dict: A dictionary containing the duration and annotations of the EEG recording.
    """
    analysis_result = {}

    # Calculate the duration of the recording
    duration = len(raw_eeg) / raw_eeg.info['sfreq']
    analysis_result['duration'] = duration
    print(77*"-")
    print(f"Duration of {EEG_file} recording: {duration} seconds")

    # Check for annotations
    if len(raw_eeg.annotations) > 0:
        print(f"Annotations in {EEG_file}:")
        for ann in raw_eeg.annotations:
            print(f" - {ann.description} at {ann.onset} seconds")
        analysis_result['annotations'] = raw_eeg.annotations
    else:
        print(f"No annotations in {EEG_file}")
        analysis_result['annotations'] = None
    print(77*"-")
    return analysis_result





