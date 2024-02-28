#helpers contain manually defined functions to help with : 
- processing step 
- definition of the life stages
- overall pipeline for EEG analyses

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