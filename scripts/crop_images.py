from PIL import Image, ImageOps
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
    z = np.sqrt(xg**2 + yg**2).T
    return z

def find_replace_colour(array, find_colour, new_colour, tolerance, method="standard"):
    this_array = array[...,:3]
    find_colour, new_colour = np.array(find_colour[:3]), np.array(new_colour)
    if method == "standard":
        crit = np.std(this_array, axis=-1)
    elif method == "distance":
        crit = np.linalg.norm(this_array - find_colour, axis=-1)
    mask = crit < tolerance
    array[mask] = new_colour
    return array

def _check_frame(cs, max_cs):
    x_pass = True if cs[0] >= 0 and cs[0] < max_cs[0] else False
    y_pass = True if cs[1] >= 0 and cs[1] < max_cs[1] else False
    if x_pass and y_pass:
        return True
    return False

def _check_colour(base_colour, check_colour, tolerance=None):
    base_colour, check_colour = base_colour.astype(np.int32), check_colour.astype(np.int32)
    if tolerance is None:
        return np.array_equal(base_colour, check_colour)
    else:
        return np.linalg.norm(base_colour - check_colour) < tolerance

def paint_in_colour(arr, start_pos, colour, tolerance=None, bw=False):
    to_check = [start_pos]
    checked = np.zeros(arr.shape[:2], dtype=bool)
    paint_inds = np.zeros(arr.shape[:2], dtype=bool)
    base_colour = arr[*start_pos]
    a = 0
    while to_check:
        check = to_check.pop()
        x,y = np.meshgrid([np.arange(check[0]-1, check[0]+2)], 
                          np.arange(check[1]-1, check[1]+2))
        coords = [(xx,yy) for xx,yy in zip(x.flatten(), y.flatten())]
        for coord in coords:
            if not _check_frame(coord, arr.shape[:2]) or checked[*coord]:
                continue
            if _check_colour(base_colour, arr[*coord], tolerance=tolerance):
                to_check.append(coord)
                paint_inds[*coord,] = True
            checked[*coord] = True
    return paint_inds
                

img_dir = "C:/Users/jevri/SP1_images" # where the the images
radius = 70 # radius of central circle to preserve (in pixels)
alpha_value = (255, 255, 255, 0) # what value represents transparence in image

x_res = 256
cropped_x_res = 150
chop_from_each_side = int(round((x_res - cropped_x_res) / 2))

# get list of files matching desiderata
filelist = os.listdir(img_dir)
filelist = [f for f in filelist if f[-4:] == ".bmp"]

# pandas dataframe for exporting the opensesame csv later
df = pd.DataFrame(columns=["follow", "left", "filename", "triggernum", "triggername"])
for fl in filelist:
    cond = "egg" if fl[0:3] == "egg" else "face"
    # load the the image, mask, then save
    im = Image.open(join(img_dir, fl))
    rgba = im.convert("RGBA")
    arr = np.array(rgba)

    if cond == "egg":
        inds = paint_in_colour(arr, [0,0], alpha_value, 5)
        arr[inds] = alpha_value
    else:
        left_inds = paint_in_colour(arr, [0,0], alpha_value, 60)
        right_inds = paint_in_colour(arr, [0, arr.shape[1]-1], alpha_value, 60)
        inds = left_inds & right_inds
        # mask outside the circle
        dists = get_griddists(*arr.shape[:2])
        rad_inds = dists > radius
        mask = left_inds | right_inds | rad_inds
        bw_im = im.copy()
        bw_im = ImageOps.grayscale(bw_im).convert("RGBA")
        bw_arr = np.array(bw_im)
        bw_arr[mask] = alpha_value
        arr = bw_arr

    new_filename = fl[:-4] + "_mask.png"
    new_im = Image.fromarray(arr)
    if cond == "face":
        new_im = new_im.crop((chop_from_each_side, 0, x_res-chop_from_each_side, im.size[1]))
    new_im.save(join(img_dir, new_filename))
    # update dataframe
    for follow in [True, False]:
        for left in [True, False]:
            # calculate the trigger number and triggername
            if cond == "egg":
                trig = 200
                trig_str = "egg_"
            else:
                trig = 100
                trig_str = "face_"
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



