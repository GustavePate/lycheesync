
import time
import hashlib
import os
import mimetypes
from PIL import Image
from PIL.ExifTags import TAGS
import datetime


class ExifData:
    """
    Use to store ExifData
    """

    iso = ""
    aperture = ""
    make = ""
    model = ""
    shutter = ""
    focal = ""
    takedate = ""
    taketime = ""

    def __str__(self):
        res = ""
        res += "iso: " + str(self.iso) + "\n"
        res += "aperture: " + str(self.aperture) + "\n"
        res += "make: " + str(self.make) + "\n"
        res += "model: " + str(self.model) + "\n"
        res += "shutter: " + str(self.shutter) + "\n"
        res += "focal: " + str(self.focal) + "\n"
        res += "takedate: " + str(self.takedate) + "\n"
        res += "taketime: " + str(self.taketime) + "\n"
        return res


class LycheePhoto:
    """
    Use to store photo data
    """

    originalname = ""  # import_name
    originalpath = ""
    id = ""
    albumname = ""
    albumid = ""
    thumbnailfullpath = ""
    thumbnailx2fullpath = ""
    title = ""
    description = ""
    url = ""
    public = 0  # private by default
    type = ""
    width = ""
    height = ""
    size = ""
    star = 0  # no star by default
    thumbUrl = ""
    srcfullpath = ""
    destfullpath = ""
    exif = None
    sysdate = ""
    systime = ""

    def __init__(self, conf, photoname, photopath, albumid):
        # Parameters storage
        self.conf = conf
        self.originalname = photoname
        self.originalpath = photopath
        self.albumid = albumid

        # Compute Photo ID
        self.id = str(time.time())
        self.id = self.id.replace('.', '')
        self.id = self.id.ljust(14, '0')

        # Compute file storage url
        m = hashlib.md5()
        m.update(self.id)
        crypted = m.hexdigest()

        ext = os.path.splitext(photoname)[1]
        self.url = ''.join([crypted, ext]).lower()
        self.thumbUrl = self.url

        # src and dest fullpath
        self.srcfullpath = os.path.join(self.originalpath, self.originalname)
        self.destfullpath = os.path.join(self.conf["lycheepath"], "uploads", "big", self.url)

        #thumbnails already in place (see makeThumbnail)

        # Auto file some properties
        self.type = mimetypes.guess_type(self.originalname, False)[0]
        self.size = os.path.getsize(self.srcfullpath)
        self.size = str(self.size/1024) + " KB"
        self.sysdate = datetime.date.today().isoformat()
        self.systime = datetime.datetime.now().strftime('%H:%M:%S')

        # Exif Data Parsing
        self.exif = ExifData()
        try:

            img = Image.open(self.srcfullpath)
            self.width, self.height = img.size
            if hasattr(img, '_getexif'):
                exifinfo = img._getexif()
                if exifinfo is not None:
                    for tag, value in exifinfo.items():
                        decode = TAGS.get(tag, tag)

                        if decode == "Make":
                            self.exif.make = value
                        if decode == "MaxApertureValue":
                            self.exif.aperture = value
                        if decode == "FocalLength":
                            self.exif.focal = value
                        if decode == "ISOSpeedRatings":
                            self.exif.iso = value
                        if decode == "Model":
                            self.exif.model = value
                        if decode == "ExposureTime":
                            self.exif.shutter = value
                        if decode == "DateTime":
                            self.exif.takedate = value.split(" ")[0]
                        if decode == "DateTime":
                            self.exif.taketime = value.split(" ")[1]
        except IOError:
            print 'IOERROR ' + self.srcfullpath

    def __str__(self):
            res = ""
            res += "originalname:" + str(self.originalname) + "\n"
            res += "originalpath:" + str(self.originalpath) + "\n"
            res += "id:" + str(self.id) + "\n"
            res += "albumname:" + str(self.albumname) + "\n"
            res += "albumid:" + str(self.albumid) + "\n"
            res += "thumbnailfullpath:" + str(self.thumbnailfullpath) + "\n"
            res += "thumbnailx2fullpath:" + str(self.thumbnailx2fullpath) + "\n"
            res += "title:" + str(self.title) + "\n"
            res += "description:" + str(self.description) + "\n"
            res += "url:" + str(self.url) + "\n"
            res += "public:" + str(self.public) + "\n"
            res += "type:" + str(self.type) + "\n"
            res += "width:" + str(self.width) + "\n"
            res += "height:" + str(self.height) + "\n"
            res += "size:" + str(self.size) + "\n"
            res += "star:" + str(self.star) + "\n"
            res += "thumbUrl:" + str(self.thumbUrl) + "\n"
            res += "srcfullpath:" + str(self.srcfullpath) + "\n"
            res += "destfullpath:" + str(self.destfullpath) + "\n"
            res += "sysdate:" + self.sysdate + "\n"
            res += "systime:" + self.systime + "\n"
            res += "Exif: \n" + str(self.exif) + "\n"
            return res
