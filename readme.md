**Author:** Romy Beauté  
**Contact:** [r.beaut@sussex.ac.uk](mailto:r.beaut@sussex.ac.uk)  
**Date:** 23-02-2024
**Last Modification:** 29-02-2024


## Overview

This repository contains utility scripts and notebooks designed to assist with EEG analysis, including data processing, life stage definition, and visualization of EEG data from Gang et al.,2023
- Original paper :  Surge of neurophysiological coupling and connectivity of gamma oscillations in the dying human brain (Xu et al.,2023) https://www.pnas.org/doi/abs/10.1073/pnas.2216268120

- Data available here : https://zenodo.org/records/7803212#.ZC3Cb-zML0q

- Supporting information available here : https://universityofsussex-my.sharepoint.com/:b:/r/personal/rb666_sussex_ac_uk/Documents/Projects/LZ%20NDE/Supplementary%20pnas.2216268120.sapp.pdf?csf=1&web=1&e=TY5ZjD

## Contents

- `helpers/`: A directory containing manually defined functions to support the processing steps, definition of life stages, and the overall pipeline for EEG analyses.

### Key Notebooks



0. **Visualisation of EEG Data (`artdet_NDE.ipynb`):**  
   Use this notebook to visualize non-preprocessed or epoched data, including channels, montage, and ECG.

1. **Life Stage Analysis and Preprocessing (`NDE_stages.ipynb`):**  
   - Visualize data
   - Annotate and visualize stages
   - Preprocess data
   - Create epochs  
     Preprocessed data is saved in `/Users/rb666/projects/DATA/EEG/Gang_2023/preprocessed/`, including:
     - `eeg.fif` files: Preprocessed and stage annotated EEG
     - `epo.fif` files: Preprocessed and stage annotated epochs
     - `params.txt` files: Log of the preprocessing steps applied


2. **Univariate LZ Complexity Analysis (`univariate_LZc_NDE_preprocessed.ipynb`):**  
   - Obtain LZ values for baseline and end stages
   - Perform temporal and spatial LZ visualization


## Getting Started

To get started with this project, clone this repository and ensure you have the required Python environment set up. For details on the environment and dependencies, please refer to the provided `environment.yml` file (if available) or set up a Python virtual environment with the necessary packages as outlined in the notebooks.

## Contribution

For any suggestions, improvements, or questions, please contact me at [r.beaut@sussex.ac.uk](mailto:r.beaut@sussex.ac.uk).