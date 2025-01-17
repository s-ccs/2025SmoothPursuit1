from PIL import Image
import os
from os.path import join
import random
import re

face_dir = join("c:", os.sep, "Users", "jevri", "Downloads", "cfd", "CFD Version 3.0", "Images", "CFD")
out_dir = join("c:", os.sep, "Users", "jevri", "Downloads", "cfd", "CFD Version 3.0", "Images", "CFD", "masked")
# x resolution of face, and desired x res so that they have the same ratio as eggs
x_res = 2444
cropped_x_res = 1432
chop_from_each_side = int(round((x_res - cropped_x_res) / 2))

total = 200
target_res = (256, 180)

hautfarbe = ["W", "B", "L", "A"]
geschlecht = ["M", "F"]

from_each = int(total / len(hautfarbe) / 2)

filelist = os.listdir(face_dir)
for hf in hautfarbe:
    for ge in geschlecht:
        these_dirs = [filename for filename in filelist if hf+ge in filename]
        random.shuffle(these_dirs)
        these_dirs = these_dirs[:from_each]
        for directory in these_dirs:
            files = os.listdir(join(face_dir, directory))
            # get the neutral image
            filename = [x for x in files if "-N.jpg" in x][0]
            stem_name = re.search("CFD-\\D{2}-(\\d{3})-.*.jpg", filename).groups()[0]
            # load
            im = Image.open(join(face_dir, directory, filename))
            # im = im.crop((chop_from_each_side, 0, x_res-chop_from_each_side, im.size[1]))
            im = im.resize(target_res)
            # im = ImageOps.grayscale(im)
            im.save(join(out_dir, f"face_{hf+ge}-{stem_name}.bmp"))





