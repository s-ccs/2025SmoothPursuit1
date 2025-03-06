from psychopy import visual, core
from psychopy.data import TrialHandler, importConditions
import numpy as np
from os.path import join

from pylsl import StreamInfo, StreamOutlet
import math
from math import atan2, degrees
import random

def run_trial(trial_info):
    # runs an individual trial; trial_info should be an iteration of TrialHandler
    img_path = join(asset_dir, trial_info["filename"])
    img = visual.ImageStim(win, img_path)

    x_coords = list(np.linspace(-1, 1, refresh_hz*2))
    x_coords += x_coords[::-1]
    x_coords *= 20

    for x_coor in x_coords:
        img.pos = (x_coor, 0)
        img.draw()
        win.flip()

from pylsl import StreamInfo, StreamOutlet
import math
from math import atan2, degrees
import random

# initialise variables we need to run trials
fixated = False
cur_trial = 0
circle_reduction = 0.

random.seed(var.subject_nr) # Set the seed to the subject nr to make the randomization of the images reproducable (especially for the case when the experiments needs to be restarted with a later trial) 

"""variables and functions for converting between visual angle and pixels"""
mon_height = 30.7 # in cm
mon_distance = 74.5 # in cm
mon_refresh = 390#60 # in Hz
deg_per_sec = 10 # visual degrees to move per second

# globals
block_size = 50
circle_kwargs = {"color":"black", "penwidth":14}
follow_str = "After convergence, <b>FOLLOW</b> the moving image."
fix_str = "After convergence, <b>STAY</b> on the still image."
log_vars = ["follow", "left", "filename", "hit_ratio"]
jitt_low, jitt_high = 300, 500

# get the trial number
files = pool.files()
files = [f for f in files if f[-4:] == ".png"]
total_trials = len(files)

# set up eyetracker
eyetracker.send_command("calibration_area_proportion = 0.60 0.75")
eyetracker.send_command("screen_write_prescale = 8")
eyetracker.send_command("validation_area_proportion = 0.60 0.75")
eyetracker.send_command("calibration_type = HV13") # automatically works to set validation_type as well.
# new_pygaze_init runs a calibration by default at init, but that will not have the custom parameters. 
# Thus we have unchecked 'calibrate' from the pygaze_init and are triggering the first calibration here through code.
eyetracker.calibrate()
eyetracker.start_recording()
# Setup your marker streams - EEG

# Setup LSL
# Create stream info
info = StreamInfo(name="experiment_markers", type="Markers", channel_count=1,channel_format="string", source_id="opensesame_markers_001")
outlet = StreamOutlet(info)


## functions
# calculate degrees per pixel
deg_per_px = degrees(atan2(.5*mon_height, mon_distance)) / (.5*height)
def ang2pix(angle):
    # convert visual angle to pixel size
    return int(round(angle / deg_per_px))
def pix2ang(pix):
    # convert pixel size to visual angle
    return pix * deg_per_pix

# calculate these while we're here
pix_per_sec = ang2pix(deg_per_sec)
#pix_per_frame = int(round(
pix_per_frame = pix_per_sec / mon_refresh#))

# trigger function
def send_triggers(trig_no, trig_name):
    """Send value as hardware trigger and LSL marker."""

    trig_str = f"trigger={trig_no:02d} {trig_name} | image={var.filename}"

    # send to ET 
    eyetracker.log(trig_str)
    # send to LSL
    outlet.push_sample([trig_str])
    # show to researcher in console
    print(trig_str)

def centre_eyecoord(coord):
    return (coord[0] - width/2, coord[1] - height/2)

def is_eye_on(point, tolerance):
    gazepos = centre_eyecoord(eyetracker.sample())
    d = math.sqrt((gazepos[0] - point[0])**2 + (gazepos[1] - point[1])**2)
    # check if the distance is 'small enough'
    if d < tolerance:
        return True
    return False

# define eye position checking functions
def wait_for_gaze(point, duration, tolerance=128, gaze_timeout=5000, samplerate=5):
    """
    check if the user is looking at a point within a euclidean distance of 'tolerance' px from a given point. Timeout: recalibrate ET and restart fixation check if not fixated within 'gaze_timeout' ms
    """
    fstart_time = clock.time()
    cur_time = clock.time()
    gaze_in_start_time = clock.time()
    gaze_in_circle = False
    while (cur_time - fstart_time) < gaze_timeout:
        clock.sleep(samplerate) # in ms
        # check if the distance is small enough
        if is_eye_on(point, tolerance):
            # to make sure gaze is within tolerance for 'duration'
            if gaze_in_circle == False:
                gaze_in_start_time = clock.time()
                gaze_in_circle = True
            elif (clock.time() - gaze_in_start_time) > duration:
                # ideally, duration must be larger then diff
                var.fixated = True
                print('fixated -> True')
                return True
        cur_time = clock.time()
    return False

log.write_vars()
column_str = "\n"
for lv in log_vars:
    column_str += f"{lv},"
log.write(column_str[:-1])




refresh_hz = 390
asset_dir = "assets"
win = visual.Window([1920, 1080], screen=1, fullscr=True, monitor="sec_mon")



