import mne

bids_root = "/scratch/users/hanna/2025SmoothPursuit1_data"
deriv_root = "/scratch/users/hanna/2025SmoothPursuit1_data/derivs"
subjects = ["998"]
ch_types = ["eeg"]
interactive = False
task = "2025SmoothPursuit1"

task_is_rest = True
epochs_tmin = 0
rest_epochs_duration = 10
rest_epochs_overlap = 0
baseline = None

eeg_reference = "average"
ica_l_freq = 1
h_freq = 100
l_freq = .1
notch_freq = [50, 100]

spatial_filter = "ica"
ica_n_components = 96
ica_algorithm = "picard-extended_infomax"
ica_use_icalabel = True

sync_eyelink = True
sync_eventtype_regex = "3-trigger=10 Image moves"
sync_eventtype_regex_et = "trigger=10 Image moves"
eeg_bipolar_channels = {"HEOG": ("LE1", "RE1"), "VEOG": ("Z1", "Z13")}
eog_channels = ["HEOG", "VEOG"]
sync_heog_ch = ("HEOG")
#sync_et_ch = "xpos_right"
sync_plot_samps = 3000

run_source_estimation = False

montage = mne.channels.read_dig_fif("~/NA-271_ASA.fif")
eeg_template_montage = montage
