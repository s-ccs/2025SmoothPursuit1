from PIL import Image
import numpy as np
import os
from os.path import join
import pandas as pd

"""
this script crops the area outside a given radius of an image into transparence, also produces
a .csv file for running the opensesame experiment
"""

def get_griddists(x, y):
    # given a 2d grid of x, y dimensions, return an (x,y) array with dist 
    # from centre
    xg, yg = np.meshgrid(np.arange(x, dtype=float), np.arange(y, dtype=float))
    xg -= x//2 - .5
    yg -= y//2 - .5
    z = np.sqrt(xg**2 + yg**2)
    return z


img_dir = "/home/jev/Downloads/Big_Masks" # where the the images
radius = 45 # radius of central circle to preserve (in pixels)
alpha_value = (255, 255, 255, 0) # what value represents transparence in image

# get list of files matching desiderata
filelist = os.listdir(img_dir)
filelist = [f for f in filelist if f[-4:] == ".bmp" and (f[0]=="E" or
                                                         f[0]=="F")]

# pandas dataframe for exporting the opensesame csv later
df = pd.DataFrame(columns=["follow", "left", "filename", "triggernum", "triggername"])
for fl in filelist:
    # load the the image, mask, then save
    im = Image.open(join(img_dir, fl))
    rgba = im.convert("RGBA")
    arr = np.array(rgba)
    dists = get_griddists(*arr.shape[:2])
    mask = dists > radius
    arr[mask] = alpha_value
    new_im = Image.fromarray(arr)
    new_filename = fl[:-4] + "_mask.png"
    new_im.save(join(img_dir, new_filename))
    # update dataframe
    for follow in [True, False]:
        for left in [True, False]:
            # calculate the trigger number and triggername
            if fl[0] == "F":
                trig = 100
                trig_str = "face_"
            elif fl[0] == "E":
                trig = 200
                trig_str = "egg_"
            else:
                raise ValueError("Filename can't be categorised.")
            if follow:
                trig += 10
                trig_str += "follow_"
            else:
                trig += 20
                trig_str += "fix_"
            if left:
                trig += 1
                trig_str += "left_"
            else:
                trig += 2
                trig_str += "right_"
            trig_str += fl[:-4]

            df.loc[len(df)] = [follow, left, new_filename, trig, trig_str]

# write out df as csv
df.to_csv(join(img_dir, "main_order.csv"), index=False)



