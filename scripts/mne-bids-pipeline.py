import mne

bids_root = "/scratch/data/2025SmoothPursuit1/"
deriv_root = "/scratch/data/2025SmoothPursuit1/derivs/"
subjects = ["001", '004', "005", "006", "007", "008", "009", "010", "011", 
            "012", "013", "015", "016", "017", "018", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]

# 013, 018 has only one pca component

# unsync events (might not be vollständig)
# subjects = ["001", "002", "006", "016", '017', '020']
# # had nans
# subjects = ['003', '004', '005', '007', '009', '012', '013', '022', '032', '035']
# # no nans
# subjects = ['008', '010', '011', '015', '016', '017', '018', '020', '021', '023', '024', '025', '028', '029', '031', '033', '034', '036', '037']
# subjects = ['011', '018', '021', '023', '024', '025', '028', '029', '031', '033', '034', '036', '037']
subjects = ["001", "007", "008", "009", "010", "011", 
            "012", "013", "015", "016", "017", "020", "021", "022", "023",
            "024", "025", "028", "029", "031", "032", "033", "034", "035", "036",
            "037"]
subjects = ["011", 
            "012", "013", "015",]
ch_types = ["eeg"]
interactive = False
task = "sp1"

task_is_rest = True
epochs_tmin = 0
epochs_tmax = 1
rest_epochs_duration = 1
rest_epochs_overlap = 0
baseline = None

eeg_reference = "average"
add_online_reference_channel = True
eeg_online_reference_channel = "CPz"
#drop_channel_after_rereference = True # true is default

ica_l_freq = 1
ica_h_freq = 100
ica_use_ecg_detection = False
ica_use_eog_detection = False
h_freq = 100
l_freq = .1
notch_freq = [50, 100]
#bandpass_extra_kws = {"skip_by_annotation":"BAD_NAN"}
#notch_extra_kws = {"skip_by_annotation":"BAD_NAN"}
#ica_filter_extra_kws = {"skip_by_annotation":"BAD_NAN"}

ica_skip_nan = True

spatial_filter = "ica"
ica_n_components = .99
ica_algorithm = "picard-extended_infomax"
ica_use_icalabel = True

sync_eyelink = True
sync_eventtype_regex = "\\d-trigger=10 Image moves"
sync_eventtype_regex_et = "trigger=10 Image moves"
eog_channels = ["HEOGL", "HEOGR", "VEOGL", "VEOGU"]
eeg_bipolar_channels = {"HEOG": ("HEOGL", "HEOGR"), "VEOG": ("VEOGL", "VEOGU")}
et_has_task=True
eog_channels = ["HEOG", "VEOG"]
sync_heog_ch = ("HEOG")
#sync_et_ch = "xpos_right"
sync_plot_samps = 3000

run_source_estimation = False


montage = mne.channels.make_standard_montage("standard_1005")
eeg_template_montage = montage


pyprep_bad_chans = False
pyprep_all_bads_params = {"ransac":False}

zapline_fline: None

on_error = "debug"

