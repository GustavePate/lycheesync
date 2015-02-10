import time
import hashlib
import os
import mimetypes
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
from dateutil.parser import parse


class ExifData:

    """
    Use to store ExifData
    """

    @property
    def takedate(self):
        """I'm the 'x' property."""
        return self._takedate.replace(':', '-')

    @takedate.setter
    def takedate(self, value):
        self._takedate = value.replace(':', '-')

    iso = ""
    aperture = ""
    make = ""
    model = ""
    shutter = ""
    focal = ""
    _takedate = ""
    taketime = ""
    orientation = 0

    def __str__(self):
        res = ""
        res += "iso: " + str(self.iso) + "\n"
        res += "aperture: " + str(self.aperture) + "\n"
        res += "make: " + str(self.make) + "\n"
        res += "model: " + str(self.model) + "\n"
        res += "shutter: " + str(self.shutter) + "\n"
        res += "focal: " + str(self.focal) + "\n"
        res += "_takedate: " + str(self._takedate) + "\n"
        res += "takedate: " + str(self.takedate) + "\n"
        res += "taketime: " + str(self.taketime) + "\n"
        res += "orientation: " + str(self.orientation) + "\n"
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
    width = 0
    height = 0
    size = ""
    star = 0  # no star by default
    thumbUrl = ""
    srcfullpath = ""
    destfullpath = ""
    exif = None
    _sysdate = None
    systime = ""
    checksum = ""

    def convert_sysdate(self, value):
        # check sysdate type
        in_t = type(value)

        epoch_date = None
        # now in epoch time
        epoch_now = int(time.time())

        # (unicode or str -> convert to int)
        if ((in_t is unicode) or (in_t is str)):
            try:
                epoch_date = (parse(value) - datetime.datetime(1970, 1, 1)).total_seconds()
            except:
                print 'WARN model sysdate impossible to parse: ' + str(value)
                epoch_date = epoch_now
        # int assign
        elif (in_t is int):
            epoch_date = value
        # date convert to int
        elif (in_t is datetime.date):
            epoch_date = (value - datetime.datetime(1970, 1, 1)).total_seconds()
        else:
            print 'WARN model.sysdate unknown variation: ' + str(in_t)
            epoch_date = epoch_now

        return epoch_date

    @property
    def sysdate(self):

        if self._sysdate:
            return self.convert_sysdate(self._sysdate)
        else:
            return int(time.time())

    @sysdate.setter
    def sysdate(self, value):
        self._sysdate = self.convert_sysdate(value)

    # Compute checksum
    def __generateHash(self):
        sha1 = hashlib.sha1()
        with open(self.srcfullpath, 'rb') as f:
            sha1.update(f.read())
            self.checksum = sha1.hexdigest()

    def __init__(self, conf, photoname, album):
        # Parameters storage
        self.conf = conf
        self.originalname = photoname
        self.originalpath = album['path']
        self.albumid = album['id']
        self.albumname = album['name']

        # if star in file name, photo is starred
        if ('star' in self.originalname) or ('cover' in self.originalname):
            self.star = 1

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

        # Generate file checksum
        self.__generateHash()

        # thumbnails already in place (see makeThumbnail)

        # Auto file some properties
        self.type = mimetypes.guess_type(self.originalname, False)[0]
        self.size = os.path.getsize(self.srcfullpath)
        self.size = str(self.size / 1024) + " KB"
        self._sysdate = datetime.date.today().isoformat()
        self.systime = datetime.datetime.now().strftime('%H:%M:%S')

        # Exif Data Parsing
        self.exif = ExifData()
        try:

            img = Image.open(self.srcfullpath)
            w, h = img.size
            self.width = float(w)
            self.height = float(h)
            if hasattr(img, '_getexif'):
                exifinfo = img._getexif()
                if exifinfo is not None:
                    for tag, value in exifinfo.items():
                        decode = TAGS.get(tag, tag)
                        # print tag, decode, value
                        # if decode != "MakerNote":
                        #    print decode, value
                        if decode == "Orientation":
                            self.exif.orientation = value
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
                            try:
                                self.exif._takedate = value.split(" ")[0]
                                self._sysdate = self.exif.takedate
                            except:
                                print 'WARN invalid takedate: ' + str(value) + ' for ' + self.srcfullpath

                        if decode == "DateTime":
                            try:
                                self.exif.taketime = value.split(" ")[1]
                                self.systime = self.exif.taketime
                            except:
                                print 'WARN invalid taketime: ' + str(value) + ' for ' + self.srcfullpath

                    # TODO: Bad description sysdate is int
                    self.description = str(self._sysdate) + " " + self.systime
        except IOError:
            print 'ERROR ioerror: ' + self.srcfullpath

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
        res += "sysdate:" + self._sysdate + "\n"
        res += "systime:" + self.systime + "\n"
        res += "checksum:" + self.checksum + "\n"
        res += "Exif: \n" + str(self.exif) + "\n"
        return res
