'''
*** Tailored helper functions to work with EEG processing pipeline for insight dataset ***

@Author: Romy Beauté
@Contact: r.beaut@sussex.ac.uk
@Date: 2024-02-06
@Last modification: 2024-02-22
'''

import os
import mne



# Dictionary mapping file extensions to their respective MNE function : see here to add more extensions https://mne.tools/stable/reading_raw_data.html
read_funcs = {
    '.edf': mne.io.read_raw_edf,
    '.fif': mne.io.read_raw_fif,
    '.egi': mne.io.read_raw_egi
}



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



# Dictionary mapping custom names for Insight2 dataset to standard 10-20 names
new_names = {
    'EEG P3-Pz': 'P3', 'EEG C3-Pz': 'C3', 'EEG F3-Pz': 'F3',
    'EEG Fz-Pz': 'Fz', 'EEG F4-Pz': 'F4', 'EEG C4-Pz': 'C4',
    'EEG P4-Pz': 'P4', 'EEG Cz-Pz': 'Cz', 'EEG A1-Pz': 'A1',
    'EEG Fp1-Pz': 'Fp1', 'EEG Fp2-Pz': 'Fp2', 'EEG T3-Pz': 'T3',
    'EEG T5-Pz': 'T5', 'EEG O1-Pz': 'O1', 'EEG O2-Pz': 'O2',
    'EEG F7-Pz': 'F7', 'EEG F8-Pz': 'F8', 'EEG A2-Pz': 'A2',
    'EEG T6-Pz': 'T6', 'EEG T4-Pz': 'T4'
}