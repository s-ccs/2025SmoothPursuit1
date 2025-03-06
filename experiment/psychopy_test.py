from psychopy import visual, core
from psychopy.data import TrialHandler, importConditions
import numpy as np
from os.path import join

def run_trial(trial_info):
    # runs an individual trial; trial_info should be an iteration of TrialHandler
    img_path = "/home/stimulus/projects/2025SmoothPursuit1/experiment/assets/face_AF-225_mask.png"
    img = visual.ImageStim(win, img_path)

    x_coords = list(np.linspace(-1, 1, refresh_hz*2))
    x_coords += x_coords[::-1]
    x_coords *= 20

    for x_coor in x_coords:
        img.pos = (x_coor, 0)
        img.draw()
        win.flip()



refresh_hz = 390
asset_dir = "assets"
win = visual.Window([1920, 1080], screen=1, fullscr=True, monitor="sec_mon")

