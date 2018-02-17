# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
import time
import hashlib
import os
import mimetypes
from PIL import Image
from PIL.ExifTags import TAGS
import datetime
import logging
from dateutil.parser import parse

logger = logging.getLogger(__name__)


class ExifData:

    """
    Use to store ExifData
    """

    @property
    def takedate(self):
        return self._takedate

    @takedate.setter
    def takedate(self, value):
        self._takedate = value.replace(':', '-')

    iso = ""
    make = ""
    model = ""
    shutter = None
    aperture = None
    exposure = None
    focal = None
    _takedate = None
    taketime = None
    orientation = 1

    def __str__(self):
        res = ""
        res += "iso: " + str(self.iso) + "\n"
        res += "aperture: " + str(self.aperture) + "\n"
        res += "make: " + str(self.make) + "\n"
        res += "model: " + str(self.model) + "\n"
        res += "shutter: " + str(self.shutter) + "\n"
        res += "exposure: " + str(self.exposure) + "\n"
        res += "focal: " + str(self.focal) + "\n"
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
    _str_datetime = None
    checksum = ""

    def convert_strdate_to_timestamp(self, value):
        # check parameter type
        # logger.debug("convert_strdate input: " + str(value))
        # logger.debug("convert_strdate input_type: " + str(type(value)))

        timestamp = None
        # now in epoch time
        epoch_now = int(time.time())
        timestamp = epoch_now

        if isinstance(value, int):
            timestamp = value
        elif isinstance(value, datetime.date):
            timestamp = (value - datetime.datetime(1970, 1, 1)).total_seconds()
        elif value:

            value = str(value)

            try:
                the_date = parse(value)
                # works for python 3
                # timestamp = the_date.timestamp()
                timestamp = time.mktime(the_date.timetuple())

            except Exception:
                logger.warn('model date impossible to parse: ' + str(value))
                timestamp = epoch_now
        else:
            # Value is None
            timestamp = epoch_now

        return timestamp

    @property
    def epoch_sysdate(self):
        return self.convert_strdate_to_timestamp(self._str_datetime)

    # Compute checksum
    def __generateHash(self):
        sha1 = hashlib.sha1()
        with open(self.srcfullpath, 'rb') as f:
            sha1.update(f.read())
            self.checksum = sha1.hexdigest()

    def __init__(self, id, conf, photoname, album):
        # Parameters storage
        self.conf = conf
        self.id = id
        self.originalname = photoname
        self.originalpath = album['path']
        self.albumid = album['id']
        self.albumname = album['name']

        # if star in file name, photo is starred
        if ('star' in self.originalname) or ('cover' in self.originalname):
            self.star = 1

        assert len(self.id) == 14, "id {} is not 14 character long: {}".format(self.id, str(len(self.id)))

        # Compute file storage url
        m = hashlib.md5()
        m.update(self.id.encode('utf-8'))
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
        logger.debug(type(self.size))
        size_kb = int(self.size / 1024)
        if (size_kb > 1024):
            self.size = "{:.2f}".format(size_kb / 1024) + " Mo"
        else:
            self.size = str(size_kb) + " Ko"

        # Default date
        takedate = datetime.date.today().isoformat()
        taketime = datetime.datetime.now().strftime('%H:%M:%S')
        self._str_datetime = takedate + " " + taketime

        # Exif Data Parsing
        self.exif = ExifData()
        try:

            img = Image.open(self.srcfullpath)
            w, h = img.size
            self.width = float(w)
            self.height = float(h)

            if hasattr(img, '_getexif'):
                try:
                    exifinfo = img._getexif()
                except Exception as e:
                    exifinfo = None
                    logger.warn('Could not obtain exif info for image: %s', e)
                # exifinfo = img.info['exif']
                # logger.debug(exifinfo)
                if exifinfo is not None:
                    for tag, value in exifinfo.items():
                        decode = TAGS.get(tag, tag)
                        if decode == "Orientation":
                            self.exif.orientation = value
                        if decode == "Make":
                            self.exif.make = value
                        if decode == "FNumber":
                            self.exif.aperture = "{0:.1f}".format(value[0] / value[1])

                        # if decode == "MaxApertureValue":
                        #     logger.info("raw aperture: %s %s %s", value[0], value[1], len(value))
                        #     aperture = math.sqrt(2) ** value[0]
                        #     try:
                        #         aperture = decimal.Decimal(aperture).quantize(
                        #             decimal.Decimal('.1'),
                        #             rounding=decimal.ROUND_05UP)
                        #     except Exception as e:
                        #         logger.debug("aperture only a few digit after comma: {}".format(aperture))
                        #         logger.debug(e)
                        #     logger.info("aperture: %s %s", aperture, type(aperture))
                        #     self.exif.aperture = "{0:.2f}".format(aperture)
                        #     logger.info("corrected aperture: %s", self.exif.aperture)
                        if decode == "FocalLength":
                            self.exif.focal = "{0:.1f}".format(value[0] / value[1])
                        if decode == "ISOSpeedRatings":
                            if isinstance(value, list):
                                self.exif.iso = value[0]
                            else:
                                self.exif.iso = value
                        if decode == "Model":
                            self.exif.model = value
                        if decode == "ExposureTime":
                            if isinstance(value, list):
                                self.exif.exposure = "{0:.1f}".format(value[0] / value[1])
                            else:
                                logging.warn("exposure not readable for %s", self.srcfullpath)
                        # if decode == "ShutterSpeedValue":
                        #     s = value[0]
                        #     s = 2 ** s
                        #     s = decimal.Decimal(s).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_05UP)
                        #     if s <= 1:
                        #         s = decimal.Decimal(
                        #             1 /
                        #             float(s)).quantize(
                        #             decimal.Decimal('0.1'),
                        #             rounding=decimal.ROUND_05UP)
                        #     else:
                        #         s = "1/" + str(s)
                        #     self.exif.shutter = str(s) + " s"

                        if decode == "DateTimeOriginal":
                            try:
                                self.exif.takedate = value.split(" ")[0]
                                # logger.debug(" Read DateTimeOriginal -> takedate: " + str(value) + " " + str(self.exif.takedate))
                            except Exception as e:
                                logger.warn('invalid takedate: ' + str(value) + ' for ' + self.srcfullpath)

                        if decode == "DateTimeOriginal":
                            try:
                                # TODO bug here on yyyy:mm:dd hh:mm:ss format
                                self.exif.taketime = value.split(" ")[1]
                                # logger.debug(" Read DateTimeOriginal -> taketime: " + str(value))
                            except Exception as e:
                                logger.warn('invalid taketime: ' + str(value) + ' for ' + self.srcfullpath)

                        if decode == "DateTime" and self.exif.takedate is None:
                            try:
                                self.exif.takedate = value.split(" ")[0]
                                # logger.debug(" Read DateTime -> takedate: " + str(value))
                            except Exception as e:
                                logger.warn('DT invalid takedate: ' + str(value) + ' for ' + self.srcfullpath)

                        if decode == "DateTime" and self.exif.taketime is None:
                            try:
                                self.exif.taketime = value.split(" ")[1]
                                # logger.debug(" Read DateTime -> taketime: " + str(value))
                            except Exception as e:
                                logger.warn('DT invalid taketime: ' + str(value) + ' for ' + self.srcfullpath)

                    # compute shutter speed

                    # if not(self.exif.shutter) and self.exif.exposure:
                    #     if self.exif.exposure < 1:
                    #         e = str(Fraction(self.exif.exposure).limit_denominator())
                    #     else:
                    #         e = decimal.Decimal(
                    #             self.exif.exposure).quantize(
                    #             decimal.Decimal('0.01'),
                    #             rounding=decimal.ROUND_05UP)
                    #     self.exif.shutter = e

                    if self.exif.shutter:
                        self.exif.shutter = str(self.exif.shutter) + " s"
                    else:
                        self.exif.shutter = ""

                    if self.exif.exposure:
                        self.exif.exposure = str(self.exif.exposure) + " s"
                    else:
                        self.exif.exposure = ""

                    if self.exif.focal:
                        self.exif.focal = str(self.exif.focal) + " mm"
                    else:
                        self.exif.focal = ""

                    if self.exif.aperture:
                        self.exif.aperture = 'F/' + str(self.exif.aperture)
                    else:
                        self.exif.aperture = ""

                    # compute takedate / taketime
                    if self.exif.takedate:
                        # logger.debug("final takedate " + self.exif.takedate)
                        takedate = self.exif.takedate.replace(':', '-')
                        taketime = '00:00:00'

                    if self.exif.taketime:
                        taketime = self.exif.taketime

                    # add mesurement units

                    self._str_datetime = takedate + " " + taketime

                    self.description = self._str_datetime

                    # logger.debug("final date " + self._str_datetime)

        except IOError as e:
            # logger.debug('ioerror (corrupted ?): ' + self.srcfullpath)
            raise e

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
        res += "_str_datetime:" + self._str_datetime + "\n"
        res += "epoch_sysdate:" + str(self.epoch_sysdate) + "\n"
        res += "checksum:" + self.checksum + "\n"
        res += "Exif: \n" + str(self.exif) + "\n"
        return res
