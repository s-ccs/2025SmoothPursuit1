import mne
from os.path import join, exists
import shutil
from pathlib import Path
import pandas as pd
from anoar import BadChannelFind, Anoar
import numpy as np

# define directories and subjects
raw_path = "/scratch/data/2025SmoothPursuit1/"
results_path = join(raw_path, "manual")
Path(results_path).mkdir(exist_ok=True)
subjects = ["001", "007", "008", "009", "010", "011", 
            "012", "013", "015", "016", "017", "018", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]

# filter params
highpass = 0.1
lowpass = 100
notch = [50, 100]
bad_chan_exclude = ["M1", "M2"] # ignore these if algorithmically marked as bad

for subject in subjects:
    fpath = join(raw_path, f"sub-{subject}", "ses-001", "eeg", 
                 f"sub-{subject}_ses-001_task-sp1_run-1_eeg.set")
    chan_fpath = join(raw_path, f"sub-{subject}", "ses-001", "eeg", 
                      f"sub-{subject}_ses-001_task-sp1_run-1_channels.tsv")
    events_fpath = join(raw_path, f"sub-{subject}", "ses-001", "eeg", 
                        f"sub-{subject}_ses-001_task-sp1_run-1_events.tsv")
    # load eeg, backup channels and events files and load them up
    raw = mne.io.read_raw_eeglab(fpath)
    # no point in cleaning on the basis of noise that won't be present in analysis anyway. so filter
    raw.notch_filter(notch)
    raw.filter(l_freq=0.1, h_freq=100.)
    # back up original event and channel files. if they are already backed up, then start from the backups
    if not exists(chan_fpath+".bck"):
        shutil.copyfile(chan_fpath, chan_fpath+".bck")
        chan_df = pd.read_csv(chan_fpath, sep="\t", index_col="name")
    else:
        chan_df = pd.read_csv(chan_fpath+".bck", sep="\t", index_col="name")
    if not exists(events_fpath+".bck"):
        shutil.copyfile(events_fpath, events_fpath+".bck")
        events_df = pd.read_csv(events_fpath, sep="\t")
    else:
        events_df = pd.read_csv(events_fpath+".bck", sep="\t")
    
    # anoar. first we need to make the eog channels
    raw = mne.set_bipolar_reference(raw, ["HEOGL", "VEOGL"], ["HEOGR", "VEOGU"], ["HEOG", "VEOG"])
    raw.set_channel_types({"HEOG":"eog", "VEOG":"eog", "sampleNumber":"misc"})
    raw.set_montage("standard_1005", on_missing="ignore")

    # find globally bad channels
    bcf = BadChannelFind(mne.pick_types(raw.info, eog=False, eeg=True), neighb_n=4, thresh=0.4)
    bad_chans = bcf.recommend(raw)
    bad_chans = [bc for bc in bad_chans if bc not in bad_chan_exclude]
    raw.info["bads"].extend(bad_chans)

    # bad sections
    anoar = Anoar(mne.pick_types(raw.info, eog=True, eeg=False), p_thresh=0.995)
    anoar.recommend(raw)
    events = anoar.events
    bad_trial_starts = events[anoar.bad_trials, 0] // raw.info["sfreq"]
    if bad_trial_starts.size:
        duration = np.repeat(anoar.raw_time, len(bad_trial_starts))
        annotations = mne.Annotations(bad_trial_starts, duration, "bad")
        raw.set_annotations(annotations)
    breakpoint()
    # manual marking
    raw.set_annotations(None) # for making plotting faster, more comprehensible
    raw.plot(n_channels=raw.info["nchan"], block=True, duration=120, highpass=highpass, lowpass=lowpass)

    # amend data frames
    bad_events_df = raw.annotations.to_data_frame(time_format=None).rename(columns={"description":"trial_type"})
    events_df._append(bad_events_df, ignore_index=True)
    for bad in raw.info["bads"]:
        chan_df.loc["Fp1", 'status'] = "bad"

    # export
    chan_df.to_csv(chan_fpath)
    events_df.to_csv(events_fpath)






