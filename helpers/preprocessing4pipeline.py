'''
*** Tailored preprocessing functions to work with EEG processing pipeline for Gang et al.,2023 dataset ***

@Author: Romy Beauté
@Contact: r.beaut@sussex.ac.uk
@Date: 2024-02-23
@Last modification: 2024-02-23
'''

import matplotlib.pyplot as plt
import mne
from mne.preprocessing import ICA
import numpy as np
import os

from scipy import signal
from scipy.signal import hilbert, detrend

from helpers.stages_infos import *



def check_channels(raw,plot_sensors=False):
    #check EEG vs other channels, and montage

    print("All channels : ",raw.info['ch_names'])

    # select only EEG channels
    eeg_chans = [ch for ch in raw.info['ch_names'] if ch != 'EKG1']
    raw_EEG = raw.copy().pick(eeg_chans)
    raw_ECG = raw.copy().pick('EKG1')
    ecg_events, _, average_pulse, ecg_data = mne.preprocessing.find_ecg_events(raw, ch_name='EKG1', verbose=True, return_ecg=True)
    # print("ECG events : ",ecg_events)


    # sanity check to check if EEG and ECG channels well applied to the 2 TS
    print("Selected EEG channels : ",raw_EEG.info['ch_names']) 


    ##### MONTAGE #####
    # Check if existing montage specified 
    if raw.info['dig'] is not None and len(raw.info['dig']) > 0:
        print("A montage is already associated with this data.")
    else:
        print("No montage associated yet. Proceeding with renaming and setting new montage.")

    # apply standard 10-20 montage
    montage = mne.channels.make_standard_montage('standard_1020')
    raw_EEG = raw_EEG.set_montage(montage)
    if plot_sensors:
        raw_EEG.plot_sensors(kind='topomap', show_names=True) #check if montage well applied

    # Re-reference the EEG data to the average and apply it 
    raw_EEG = raw_EEG.set_eeg_reference('average', projection=True)
    raw_EEG = raw_EEG.apply_proj()
    print("Average reference projection applied.")

    return raw_EEG,raw_ECG






def preprocess_epoch_hilbert(epoch_data,already_detrended=False, already_normalized=False):
    # Apply Hilbert transform to the data to get the envelope
    amplitude_envelope = np.abs(hilbert(epoch_data))
    # Detrend the amplitude envelope and normalize
    if not already_detrended:
        # Detrend the amplitude envelope
        amplitude_envelope = detrend(amplitude_envelope - np.mean(amplitude_envelope))
    if not already_normalized:
        # Normalize the amplitude envelope
        amplitude_envelope = amplitude_envelope / np.std(amplitude_envelope)
    return amplitude_envelope



def raw_preprocess(raw,notchf=[60,120,180],downsampling=250,epoch_duration=2,detrend=False,normalise=True,apply_hilbert=False,baseline_correction=False,apply_ica=False,plot_preproc=False):

    # Create a dictionary of preprocessing parameters
    preproc_params = {
        'notch_filter_frequencies': notchf,
        'downsampling_rate': downsampling,
        'epoch_duration': epoch_duration,
        'detrend': detrend,
        'normalise': normalise,
        'apply_hilbert': apply_hilbert,
        'baseline_correction': baseline_correction,
        'apply_ica': apply_ica,
    }
    
    #check if annotated events
    print("-------------DATA INFOS-----------------")
    raw.info.keys()
    raw.info['events']
    print(raw.annotations)
    events, event_ids = mne.events_from_annotations(raw)
    print("------------------------------------")


    
    # Notch filter to remove line noise
    print("----------PREPROCESSING 1 (ON CONTINUOUS DATA) ----------------")
    raw_filtered = raw.notch_filter(freqs=notchf)
    print("Notch filter applied at ",notchf,"Hz")
    raw_filtered = raw_filtered.resample(sfreq=downsampling)
    print("Data downsampled to ",downsampling,"Hz")

    if apply_ica :
        print("Applying ICA to remove artefacts")
        ica = mne.preprocessing.ICA(n_components=0.99, random_state=77, max_iter="auto", method="picard")
        ica.fit(raw_filtered)
        ica.apply(raw_filtered)
        ica.plot_components()
        ica.plot_sources(raw_filtered, show_scrollbars=True)

        raw_filtered.interpolate_bads(reset_bads=True)

        explained_var_ratio = ica.get_explained_variance_ratio(raw_filtered)
        for channel_type, ratio in explained_var_ratio.items():
            print(f"Fraction of {channel_type} variance explained by all components: " f"{ratio}")

        explained_var_ratio = ica.get_explained_variance_ratio(raw_filtered, components=[0], ch_type="eeg")
        # print as percentage.
        ratio_percent = round(100 * explained_var_ratio["eeg"])
        print(
            f"Fraction of variance in EEG signal explained by first component: "
            f"{ratio_percent}%")

    print("------------------------------------")


    # Epoching  
    print("----------- PREPROCESSING 2 (ON EPOCHS) ----------------")
    print("Creating epochs...")
    picks = mne.pick_types(raw_filtered.info, meg=False, eeg=True,exclude=['EKG1']) #select only EEG channels

    if event_ids:
        # convert annotations to events
        events_annotated, event_id_annotated = mne.events_from_annotations(raw_filtered, event_id=None)
        print("Events from annotations:", events_annotated)

        events = mne.make_fixed_length_events(raw_filtered, duration=epoch_duration)

        
        if not baseline_correction:
            # Create epochs without baseline correction
            # epochs = mne.Epochs(raw_filtered, events, event_id=event_id, tmin=0, tmax=epoch_duration, preload=True, baseline=None) #no baseline correction
            # epochs = mne.Epochs(raw_filtered, events, event_id=None, tmin=0, tmax=epoch_duration, preload=True, baseline=None) #no baseline correction
            epochs = mne.Epochs(raw_filtered, events, tmin=0, tmax=epoch_duration, baseline=None, preload=True,picks=picks)
            print("Created 2-second epochs without baseline correction:", epochs)

        else:
            # Create epochs with baseline correction, assuming a suitable baseline period exists
            # epochs = mne.Epochs(raw_filtered, events, event_id=event_id, tmin=0, tmax=epoch_duration, preload=True, baseline=(-0.2, 0))
            # epochs = mne.Epochs(raw_filtered, events, event_id=None, tmin=0, tmax=epoch_duration, preload=True, baseline=(-0.2, 0))
            epochs = mne.Epochs(raw_filtered, events, tmin=0, tmax=epoch_duration,baseline=(-0.2, 0),preload=True,picks=picks)
            print("Created 2-second epochs with baseline correction:", epochs)
    
    
    else:
        print("No events found in annotations. Creating fixed-length epochs.")
        events = mne.make_fixed_length_events(raw_filtered, duration=epoch_duration) #create events that are spaced by the duration of each epoch
        epochs = mne.Epochs(raw_filtered, events, tmin=0, tmax=epoch_duration, baseline=None, preload=True,picks=picks)

    # Detrending and normalization
    if detrend: #removes linear trends from the data => can help reduce low-freq noise
        epochs = epochs.apply_function(lambda x: signal.detrend(x, type='constant'), channel_wise=True)
        print("Detrending applied.")
    if normalise: # adjusts the range of the EEG signal so that it has a defined scale
        epochs = epochs.apply_function(lambda x: (x - np.mean(x)) / np.std(x), channel_wise=True)
        print("Normalization applied.")

    # apply Hilbert transform if want to extract the envelope of the EEG signal representing the amplitude changes over time
    if apply_hilbert:
        # Applying Hilbert transform to each epoch
        for i in range(len(epochs)):
            epochs._data[i] = preprocess_epoch_hilbert(epochs._data[i],already_detrended=detrend, already_normalized=normalise)
        print("Hilbert transform applied.")

    if plot_preproc:
        epochs.plot_psd(fmin=0.5, fmax=50)  # Plot the power spectral density for the normalized data
    

    return raw_filtered,epochs,preproc_params







def save_preprocessed_data(preprocessed_data, preprocessed_folder, EEG_files, preproc_params_list, save_preproc=True):
    if save_preproc:

        # Check if "preprocessed" folder exists
        if not os.path.exists(preprocessed_folder):
            os.makedirs(preprocessed_folder)
        print("Preprocessed data will be saved in the following folder: ", preprocessed_folder)

        # Define the path and preproc params for the preprocessed data
            
        data_types = ['eeg', 'epo']

        for i, stage in enumerate(['baseline', 'end']):
            preproc_params = preproc_params_list[i] # Get preprocessing parameters for the current stage

            EEG_file = EEG_files[stage]  # Get the correct EEG file name for the stage
            preprocessing_params_file_name = EEG_file.replace('.edf', f'_{stage}_preprocessing_params.txt')
            preprocessing_params_file_path = os.path.join(preprocessed_folder, preprocessing_params_file_name)

            with open(preprocessing_params_file_path, 'w') as f:
                for param, value in preproc_params.items():
                    f.write(f"{param}: {value}\n")


            for j, data_type in enumerate(data_types):
                # Access the correct preprocessed data
                current_data = preprocessed_data[i*2 + j]

                # Define the file name and path for each preprocessed data
                preprocessed_file_name = EEG_file.replace('.edf', f'_{stage}_preprocessed_{data_type}.fif')
                preprocessed_file_path = os.path.join(preprocessed_folder, preprocessed_file_name)
                print(f"Saving preprocessed data to {preprocessed_file_path}")

                # Save preprocessed data
                current_data.save(preprocessed_file_path, overwrite=True)

            # Define the path for the text file with preprocessing parameters for each stage
            preprocessing_params_file_name = EEG_file.replace('.edf', f'_{stage}_preprocessing_params.txt')
            preprocessing_params_file_path = os.path.join(preprocessed_folder, preprocessing_params_file_name)