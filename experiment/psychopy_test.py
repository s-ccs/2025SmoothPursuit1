from psychopy import visual, core
import numpy as np

refresh_hz = 60

win = visual.Window([1472, 920], fullscr=True, monitor=0)
img_path = "C:/Users/jevri/Documents/GitHub/2025SmoothPursuit1/experiment/assets/face_AF-225_mask.png"
img = visual.ImageStim(win, img_path)

x_coords = np.linspace(-1, 1, refresh_hz*2)

for x_coor in x_coords:
    img.pos = (x_coor, 0)
    img.draw()
    win.flip()