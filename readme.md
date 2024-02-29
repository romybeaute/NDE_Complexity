@Author: Romy Beauté
@Contact: r.beaut@sussex.ac.uk
@Date: 2024-02-23
@Last modification: 2024-02-29


#helpers contain manually defined functions to help with : 
- processing step 
- definition of the life stages
- overall pipeline for EEG analyses



#0. Just to visualise non preprocessed, or epoched data, the channels, montage and ECG : can run artdet_NDE.ipynb

#1. Run NDE_stages.ipynb to :
- visualise data
- annotate and visualise stages
- preprocess data
- create epochs
=> preprocessed data saved in /Users/rb666/projects/DATA/EEG/Gang_2023/preprocessed/ folder, including : 
- eeg.fif files : preprocessed and stage annotated eeg
- epo.fif files : preprocessed and stage annotated epochs 
- params.txt files : log of the preprocessing steps applied


#2. Run univariate_LZc_NDE_preprocessed.ipynb to :
- get LZ values for baseline and end stages
- temporal and spatial LZ visualisation 