#!/usr/bin/env python

# Usage: $0 IMAGE LIST_OF_REGIONS_TXT

import pathlib
import sys

from PIL import (
        Image,
        ImageFilter)
import numpy as np

from lib.parse_listof_regions import *

# PARAMS
#THRESHOLD = 130
IMG_EXPORT_AT = "Export"

# lazy argument
_, original_image_file, list_regions_file, *_ = sys.argv

# original image
image = Image.open(original_image_file)

# Which regions should I crop? Queried by my text file.
regions = parse_listof_regions(list_regions_file)
#import pprint
#pprint.pprint(regions)

dynamic_regions = regions["DYNAMIC"]
fixed_regions = regions["FIXED"]

# == And now cropping such parts

mydir = pathlib.Path(IMG_EXPORT_AT)
if not mydir.is_dir():
    print(f"{sys.argv[0]}: mkdir {IMG_EXPORT_AT!r}", file=sys.stderr)
    mydir.mkdir()

num_imgs = len(dynamic_regions)
digits = len(str(num_imgs-1))
#print(num_imgs) or exit("hi")
for idx, [x1, y1, w, h] in enumerate(dynamic_regions):
    one_letter_image = image.crop((x1, y1, x1+w, y1+h))
    filename = pathlib.Path(IMG_EXPORT_AT, f"dynamic_{idx:0{digits}}.png").__str__()
    print(f"{sys.argv[0]}: outputting {filename!r}", file=sys.stderr)
    one_letter_image.save(filename)

num_imgs = len(fixed_regions)
digits = len(str(num_imgs-1))
for idx, [x1, y1, w, h] in enumerate(fixed_regions):
    fixed_str_image = image.crop((x1, y1, x1+w, y1+h))
    filename = pathlib.Path(IMG_EXPORT_AT, f"fixed_{idx:0{digits}}.png").__str__()
    print(f"{sys.argv[0]}: outputting {filename!r}", file=sys.stderr)
    fixed_str_image.save(filename)
