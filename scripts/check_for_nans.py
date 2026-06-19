import mne
import numpy as np
import os

raw_dir = "/scratch/data/2025SmoothPursuit1/"
subjects = ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", 
            "012", "013", "015", "016", "017", "018", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]
subjects = ['003', '004', '005', '007', '009', '012', '013', '022', '032', '035']
not_nans = ['001', '002', '006', '008', '010', '011', '015', '016', '017', '018', '020', '021', '023', '024', '025', '028', '029', '031', '033', '034', '036', '037']

nan_dict = {}

for subject in subjects:
    infile = os.path.join(raw_dir, 
                          f"sub-{subject}/ses-001/eeg/sub-{subject}_ses-001_task-sp1_run-1_eeg.set")
    raw = mne.io.read_raw_eeglab(infile)
    nan_dict[subject] = np.sum(np.isnan(raw.get_data()))
    print(nan_dict)
