
import os
import shutil
import traceback
from lycheemodel import ExifData
from PIL import Image
import sys
from PIL.ExifTags import TAGS

if __name__ == '__main__':

    file = sys.argv[1]
    print file

    exif = ExifData()

    img = Image.open(file)
    if hasattr(img, '_getexif'):
        exifinfo = img._getexif()
        if exifinfo is not None:
            for tag, value in exifinfo.items():
                decode = TAGS.get(tag, tag)
                if decode != "MakerNote":
                    print decode, value
                if decode == "Orientation":
                    exif.orientation = value
                if decode == "Make":
                    exif.make = value
                if decode == "MaxApertureValue":
                    exif.aperture = value
                if decode == "FocalLength":
                    exif.focal = value
                if decode == "ISOSpeedRatings":
                    exif.iso = value
                if decode == "Model":
                    exif.model = value
                if decode == "ExposureTime":
                    exif.shutter = value
                if decode == "DateTime":
                    exif.takedate = value.split(" ")[0]
                if decode == "DateTime":
                    exif.taketime = value.split(" ")[1]

    if exif.orientation not in (0, 1):
        # There is somthing to do
        if exif.orientation == 6:
            # rotate 90° clockwise
            print "ROTATE!!!!!"
            img.rotate(90)
            img.save(file + "ok")
