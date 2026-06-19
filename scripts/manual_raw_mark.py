import mne
from os.path import join, exists
import shutil
from pathlib import Path
import pandas as pd

# define directories and subjects
raw_path = "/scratch/data/2025SmoothPursuit1/"
results_path = join(raw_path, "manual")
Path(results_path).mkdir(exist_ok=True)
subjects = ["001", "007", "008", "009", "010", "011", 
            "012", "013", "015", "016", "017", "018", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]
subjects = ["016", "017", "018", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]

# parameters for marking breaks as bad
bad_breaks = True
max_dist = 10.
buffer = 1.
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
    ## load eeg, backup channels and events files and load them up
    raw = mne.io.read_raw_eeglab(fpath)
    ## no point in cleaning on the basis of noise that won't be present in analysis anyway. so filter
    raw.notch_filter(notch)
    raw.filter(l_freq=0.1, h_freq=100.)
    ## back up original event and channel files. if they are already backed up, then start from the backups
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
    
    ## make the eog channels for better viewing
    raw = mne.set_bipolar_reference(raw, ["HEOGL", "VEOGL"], ["HEOGR", "VEOGU"], ["HEOG", "VEOG"])
    raw.set_channel_types({"HEOG":"eog", "VEOG":"eog", "sampleNumber":"misc"})
    raw.set_montage("standard_1005", on_missing="ignore")

    # if desired mark breaks as bad
    if bad_breaks:
        last_time = 0.
        for annot in raw.annotations:
            if "Recalibration" in annot["description"]:
                continue
            distance = annot["onset"] - last_time 
            if distance > max_dist:
                duration = distance - buffer
                raw.annotations.append(last_time, duration, "BAD_BREAK")
            last_time = annot["onset"]
        duration = raw.times[-1] - last_time
        raw.annotations.append(last_time, duration, "BAD_BREAK")

    # make every event the same name here temporarily, just for display purposes
    new_names = {k["description"]:"event" for k in raw.annotations if "BAD" not in k["description"]}
    raw.annotations.rename(new_names)
    ## manual marking
    raw.plot(n_channels=raw.info["nchan"], block=True, duration=180)

    ## amend data frames
    # get rid of our placeholder events; we just want the bad sections here
    bad_inds = [idx for idx, annot in enumerate(raw.annotations) if "BAD" not in annot["description"]]
    raw.annotations.delete(bad_inds)
    # export to dataframe
    bad_events_df = raw.annotations.to_data_frame(time_format=None).rename(columns={"description":"trial_type"})
    events_df = events_df._append(bad_events_df, ignore_index=True)
    # bad channels
    for bad in raw.info["bads"]:
        chan_df.loc[bad, 'status'] = "bad"

    # export
    chan_df.to_csv(chan_fpath, sep="\t")
    events_df.to_csv(events_fpath, sep="\t")






