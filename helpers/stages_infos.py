'''
*** Tailored functions to annotate the different stages for Gang et al.,2023 dataset ***

@Author: Romy Beauté
@Contact: r.beaut@sussex.ac.uk
@Date: 2024-02-23
@Last modification: 2024-02-29
'''


import matplotlib.pyplot as plt
import numpy as np
import sys
import mne


from helpers.helper4pipeline import read_EEG


### DICTIONARY OF PATIENTS AND STAGES ###
#values of duration (in sec) for each stage
time_values = {
"pt1": [120, 108, 18, 18, 16, 67, 46, 51, 45, 123, 46],
"pt2": [100, 100, 87, 157, 96, 216, 191, 773],  
"pt3": [100, 454, 76, 33, 32, 47, 208, 243],  
"pt4": [100, 300, 57, 36, 124, 83, 128, 84, 52]}

stage_descriptions = {
    "pt1": {
    "S1": "Comatose baseline",
    "S2": "Ventilator removal",
    "S3": "EEG suppression to start pacemaking",
    "S4": "First episode of pacemaking",
    "S5": "Pacemaker off",
    "S6": "Pacemaker restarted",
    "S7": "Rapid heart rate drop to pacemaker off by clinical staff",
    "S8": "Bradycardia period (RR interval > 5s)",
    "S9": "Partial heart rate recovery (RRI < 5s)",
    "S10": "Reappearance of P-waves and further heart rate recovery",
    "S11": "Last recorded heartbeat with PAC-like ECG pattern"
    },

    "pt2": {
    "S1": "Comatose baseline",
    "S2": "Start of ECMO and ventilation turn-off",
    "S3": "Marked EEG amplitude suppression",
    "S4": "Linear expansion of RRI",
    "S5": "Continued linear RRI expansion, occasional interruption",
    "S6": "Brief RRI shortening followed by lengthening",
    "S7": "Rhythmic RRI lengthening and shortening",
    "S8": "Longest near-death state, stable RRI, last heartbeat"
    },

    "pt3": {
    "S1": "Comatose baseline",
    "S2": "Extubation procedure",
    "S3": "EEG suppression, gradual heart rate reduction",
    "S4": "Asystole (33s)",
    "S5": "Partial heart rate recovery",
    "S6": "Continued partial heart rate recovery with R-peak width normalization",
    "S7": "Further heart rate recovery, PR interval lengthening",
    "S8": "Continued PR interval expansion, last heartbeat"
    },

    "pt4" :{
    "S1": "Comatose baseline",
    "S2": "Continuation of EEG burst suppression",
    "S3": "Severe EEG amplitude reduction",
    "S4": "Not specifically detailed",
    "S5": "Not specifically detailed",
    "S6": "Not specifically detailed",
    "S7": "Brief episodes of asystole",
    "S8": "QRS complex changes, last second recovery",
    "S9": "Continued QRS complex changes, last recorded heartbeat"
}}


def stage_annotations(eeg_rec, time_values,stage_descriptions, sub_id,stage_start=0,plot=True):
    # Check existing annotations
    if len(eeg_rec.annotations) > 0:
        print("Existing annotations found:")
        print(eeg_rec.annotations)
    else:
        print("No existing annotations found. Adding new annotations...")

        # Prepare new annotations

        stage_durations = time_values[f"pt{sub_id}"][stage_start:] 
        descriptions = [stage_descriptions[f"pt{sub_id}"][f"S{i+1}"] for i in range(1, len(stage_durations)+1)]  

        # Create Annotations object
        my_annotations = mne.Annotations(onset=np.cumsum([0] + stage_durations[:-1]),  # cumulative sum to get onset times
                                        duration=stage_durations, 
                                        description=descriptions,
                                        orig_time=eeg_rec.info['meas_date'])

        # Add annotations to the raw object
        eeg_rec.set_annotations(my_annotations)

        print("New annotations added.")
    if plot:
        eeg_rec.plot(title=f"Pt {sub_id}",scalings='auto')

    return eeg_rec


def timing_stages():
    patient_timing_data = {
    "pt1": {f"S{i}": None for i in range(1, 12)},
    "pt2": {f"S{i}": None for i in range(1, 9)},
    "pt3": {f"S{i}": None for i in range(1, 9)},
    "pt4": {f"S{i}": None for i in range(1, 10)}}


    for patient, times in time_values.items():
        for i, time_value in enumerate(times, start=1):
            patient_timing_data[patient][f"S{i}"] = f"{time_value}s"

    return patient_timing_data




def plot_patient_stages(patient_id, time_values, stage_descriptions):
    # Calculate start and end times for each stage
    start_times = [0] + np.cumsum(time_values[:-1]).tolist()
    end_times = np.cumsum(time_values).tolist()

    # Create a figure to show the timing of different stages
    plt.figure(figsize=(14, 8))
    for i, (start, end) in enumerate(zip(start_times, end_times), start=1):
        plt.plot([start, end], [i, i], marker='o', markersize=6, label=f'S{i}')
        plt.text(start, i, f'Begin {stage_descriptions[f"S{i}"]}', verticalalignment='bottom', horizontalalignment='right', color='green', fontsize=9)
        plt.text(end, i, f'End {stage_descriptions[f"S{i}"]}', verticalalignment='top', horizontalalignment='left', color='red', fontsize=9)

    plt.xlabel('Time (s)')
    plt.ylabel('Stages')
    plt.title(f'Identification of Near-Death Stages in {patient_id}')
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.show()







def load_and_label_EEG_data(patient_id, DATASET_path):
    # Load baseline EEG data
    EEG_S1 = f"Pt{patient_id}_S1.edf"
    raw_eeg_baseline = read_EEG(EEG_S1, DATASET_path, print_infos=False, plot_raw=False)

    # Load EEG data from S2 to the end
    EEG_S2_end = f"Pt{patient_id}_S2-end.edf"
    raw_eeg_end = read_EEG(EEG_S2_end, DATASET_path, print_infos=False, plot_raw=False)

    # Segment and label the data
    segmented_data = []
    start_time = 0
    for i, duration in enumerate(time_values[f"pt{patient_id}"], start=1):
        end_time = start_time + duration
        segment = raw_eeg_end.segment(start_time, end_time)  # Assuming .segment() is a method to segment the EEG data
        label = stage_descriptions[f"pt{patient_id}"][f"S{i}"]
        segmented_data.append((segment, label))
        start_time = end_time

    return raw_eeg_baseline, segmented_data













