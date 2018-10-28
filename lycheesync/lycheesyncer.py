# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
import os
import shutil
import stat
from lycheesync.lycheedao import LycheeDAO
from lycheesync.lycheemodel import LycheePhoto
from lycheesync.utils.configuration import ConfBorg
from PIL import Image
import datetime
import sys
import logging
import piexif
import fnmatch

logger = logging.getLogger(__name__)


def remove_file(path):
    try:
        os.remove(path)
    except Exception:
        logger.warn("problem removing: " + path)


class LycheeSyncer:

    """
    This class contains the logic behind this program
    It consist mainly in filesystem operations
    It relies on:
    - LycheeDAO for dtabases operations
    - LycheePhoto to store (and compute) photos propreties
    """

    conf = {}

    def __init__(self):
        """
        Takes a dictionnary of conf as input
        """
        borg = ConfBorg()
        self.conf = borg.conf

    def getAlbumNameFromPath(self, album):
        """
        build a lychee compatible albumname from an albumpath (relative to the srcdir main argument)
        Takes an album properties list  as input. At least the path sould be specified (relative albumpath)
        Returns a string, the lychee album name
        """
        # make a list with directory and sub dirs
        alb_path_utf8 = album['relpath']  # .decode('UTF-8')

        path = alb_path_utf8.split(os.sep)

        # join the rest: no subfolders in lychee yet
        if len(path) > 1:
            album['name'] = "_".join(path)
        else:
            album['name'] = alb_path_utf8
        return album['name']

    def isAPhoto(self, file):
        """
        Determine if the filename passed is a photo or not based on the file extension
        Takes a string  as input (a file name)
        Returns a boolean
        """
        validimgext = ['.jpg', '.jpeg', '.gif', '.png']
        ext = os.path.splitext(file)[-1].lower()
        return (ext in validimgext)

    def albumExists(self, album):
        """
        Takes an album properties list  as input. At least the relpath sould be specified (relative albumpath)
        Returns an albumid or None if album does not exists
        """

    def createAlbum(self, album):
        """
        Creates an album
        Inputs:
        - album: an album properties list. at least path should be specified (relative albumpath)
        Returns an albumid or None if album does not exists
        """
        album['id'] = None
        if album['name'] != "":
            album['id'] = self.dao.createAlbum(album)
        return album['id']

    def thumbIt(self, res, photo, destinationpath, destfile):
        """
        Create the thumbnail of a given photo
        Parameters:
        - res: should be a set of h and v res (640, 480)
        - photo: a valid LycheePhoto object
        - destinationpath: a string the destination full path of the thumbnail (without filename)
        - destfile: the thumbnail filename
        Returns the fullpath of the thuumbnail
        """

        if photo.width > photo.height:
            delta = photo.width - photo.height
            left = int(delta / 2)
            upper = 0
            right = int(photo.height + left)
            lower = int(photo.height)
        else:
            delta = photo.height - photo.width
            left = 0
            upper = int(delta / 2)
            right = int(photo.width)
            lower = int(photo.width + upper)

        destimage = os.path.join(destinationpath, destfile)
        try:
            img = Image.open(photo.destfullpath)
        except Exception as e:
            logger.exception(e)
            logger.error("ioerror (corrupted file?): " + photo.srcfullpath)
            raise

        img = img.crop((left, upper, right, lower))
        img.thumbnail(res, Image.ANTIALIAS)
        img.save(destimage, quality=99)
        return destimage

    def makeThumbnail(self, photo):
        """
        Make the 2 thumbnails needed by Lychee for a given photo
        and store their path in the LycheePhoto object
        Parameters:
        - photo: a valid LycheePhoto object
        returns nothing
        """
        # set  thumbnail size
        sizes = [(200, 200), (400, 400)]
        # insert @2x in big thumbnail file name
        filesplit = os.path.splitext(photo.url)
        destfiles = [photo.url, ''.join([filesplit[0], "@2x", filesplit[1]]).lower()]
        # compute destination path
        destpath = os.path.join(self.conf["lycheepath"], "uploads", "thumb")
        # make thumbnails
        photo.thumbnailfullpath = self.thumbIt(sizes[0], photo, destpath, destfiles[0])
        photo.thumbnailx2fullpath = self.thumbIt(sizes[1], photo, destpath, destfiles[1])

    def copyFileToLychee(self, photo):
        """
        add a file to an album, the albumid must be previously stored in the LycheePhoto parameter
        Parameters:
        - photo: a valid LycheePhoto object
        Returns True if everything went ok
        """
        res = False

        try:
            # copy photo
            if self.conf['link']:
                os.symlink(photo.srcfullpath, photo.destfullpath)
            else:
                shutil.copy(photo.srcfullpath, photo.destfullpath)
            # adjust right (chmod/chown)
            try:
                os.lchown(photo.destfullpath, -1, self.conf['gid'])

                if not(self.conf['link']):
                    st = os.stat(photo.destfullpath)
                    os.chmod(photo.destfullpath, st.st_mode | stat.S_IRWXU | stat.S_IRWXG)
                else:
                    st = os.stat(photo.srcfullpath)
                    os.chmod(photo.srcfullpath, st.st_mode | stat.S_IROTH)

            except Exception as e:
                if self.conf["verbose"]:
                    logger.warn(
                        "chgrp error,  check file permission for %s fix: eventually adjust source file permissions",
                        photo.destfullpath)
            res = True

        except Exception as e:
            logger.exception(e)
            res = False

        return res

    def deleteFiles(self, filelist):
        """
        Delete files in the Lychee file tree (uploads/big and uploads/thumbnails)
        Give it the file name and it will delete relatives files and thumbnails
        Parameters:
        - filelist: a list of filenames
        Returns nothing
        """

        for url in filelist:
            if self.isAPhoto(url):
                thumbpath = os.path.join(self.conf["lycheepath"], "uploads", "thumb", url)
                filesplit = os.path.splitext(url)
                thumb2path = ''.join([filesplit[0], "@2x", filesplit[1]]).lower()
                thumb2path = os.path.join(self.conf["lycheepath"], "uploads", "thumb", thumb2path)
                bigpath = os.path.join(self.conf["lycheepath"], "uploads", "big", url)
                remove_file(thumbpath)
                remove_file(thumb2path)
                remove_file(bigpath)

    def adjustRotation(self, photo):
        """
        Rotates photos according to the exif orientaion tag
        Returns nothing DOIT BEFORE THUMBNAILS !!!
        """

        if photo.exif.orientation != 1:

            img = Image.open(photo.destfullpath)
            if "exif" in img.info:
                exif_dict = piexif.load(img.info["exif"])

                if piexif.ImageIFD.Orientation in exif_dict["0th"]:
                    orientation = exif_dict["0th"][piexif.ImageIFD.Orientation]

                    if orientation == 2:
                        img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 3:
                        img = img.rotate(180)
                    elif orientation == 4:
                        img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 5:
                        img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 6:
                        img = img.rotate(-90, expand=True)
                    elif orientation == 7:
                        img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
                    else:
                        if orientation != 1:
                            logger.warn(
                                "Orientation not defined {} for photo {}".format(
                                    orientation,
                                    photo.title))

                    if orientation in [5, 6, 7, 8]:
                        # invert width and height
                        h = photo.height
                        w = photo.width
                        photo.height = w
                        photo.width = h
                    exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
                    exif_bytes = piexif.dump(exif_dict)
                    img.save(photo.destfullpath, exif=exif_bytes, quality=99)
            img.close()

    def reorderalbumids(self, albums):

        # sort albums by title
        def getName(album):
            return album['name']

        sortedalbums = sorted(albums, key=getName)

        # count albums
        nbalbum = len(albums)
        # get higher album id + 1 as a first new album id
        min, max = self.dao.getAlbumMinMaxIds()

        if min and max:

            if nbalbum + 1 < min:
                newid = 1
            else:
                newid = max + 1

            for a in sortedalbums:
                self.dao.changeAlbumId(a['id'], newid)
                newid = newid + 1

    def updateAlbumsDate(self, albums):
        now = datetime.datetime.now()
        last2min = now - datetime.timedelta(minutes=2)
        last2min_epoch = int((last2min - datetime.datetime(1970, 1, 1)).total_seconds())

        for a in albums:
            try:
                # get photos with a real date (not just now)
                datelist = None

                if len(a['photos']) > 0:

                    datelist = [
                        photo.epoch_sysdate for photo in a['photos'] if photo.epoch_sysdate < last2min_epoch]

                    if datelist is not None and len(datelist) > 0:
                        newdate = max(datelist)
                        self.dao.updateAlbumDate(a['id'], newdate)

            except Exception as e:
                logger.exception(e)
                logger.error("updating album date for album:" + a['name'], e)

    def deleteAllFiles(self):
        """
        Deletes every photo file in Lychee
        Returns nothing
        """
        filelist = []
        photopath = os.path.join(self.conf["lycheepath"], "uploads", "big")
        filelist = [f for f in os.listdir(photopath)]
        self.deleteFiles(filelist)

    def deletePhotos(self, photo_list):
        "photo_list: a list of dictionnary containing key url and id"
        if len(photo_list) > 0:
            url_list = [p['url'] for p in photo_list]
            self.deleteFiles(url_list)
            for p in photo_list:
                self.dao.dropPhoto(p['id'])

    def sync(self):
        """
        Program main loop
        Scans files to add in the sourcedirectory and add them to Lychee
        according to the conf file and given parameters
        Returns nothing
        """

        # Connect db
        # and drop it if dropdb activated
        self.dao = LycheeDAO(self.conf)

        if self.conf['dropdb']:
            self.deleteAllFiles()

        # Load db

        createdalbums = 0
        discoveredphotos = 0
        importedphotos = 0
        album = {}
        albums = []

        album_name_max_width = self.dao.getAlbumNameDBWidth()

        # walkthroug each file / dir of the srcdir
        for root, dirs, files in os.walk(self.conf['srcdir']):

            if sys.version_info.major == 2:
                try:
                    root = root.decode('UTF-8')
                except Exception as e:
                    logger.error(e)
            # Init album data
            album['id'] = None
            album['name'] = None
            album['description'] = None
            album['path'] = None
            album['relpath'] = None  # path relative to srcdir
            album['photos'] = []  # path relative to srcdir

            # if a there is at least one photo in the files
            if any([self.isAPhoto(f) for f in files]):
                album['path'] = root

                # Skip any albums that matches one of the exluded patterns
                if 'excludeAlbums' in self.conf:
                    if any(
                            [True for pattern in self.conf['excludeAlbums'] if fnmatch.fnmatch(album['path'], pattern)]):
                        logger.info("Skipping excluded album {}".format(root))
                        continue

                # don't know what to do with theses photo
                # and don't wan't to create a default album
                if album['path'] == self.conf['srcdir']:
                    msg = "file at srcdir root won't be added to lychee, please move them in a subfolder: {}".format(
                        root)
                    logger.warn(msg)
                    continue

                # Fill in other album properties
                # albumnames start at srcdir (to avoid absolute path albumname)
                album['relpath'] = os.path.relpath(album['path'], self.conf['srcdir'])
                album['name'] = self.getAlbumNameFromPath(album)

                # check for desc.txt file existence
                if (os.path.exists(album['path']+"/desc.txt")):
                    fp = open(album['path']+"/desc.txt", "r")
                    album['description'] = fp.read()
                    fp.close()

                if len(album['name']) > album_name_max_width:
                    logger.warn("album name too long, will be truncated " + album['name'])
                    album['name'] = album['name'][0:album_name_max_width]
                    logger.warn("album name is now " + album['name'])

                album['id'] = self.dao.albumExists(album)

                if self.conf['replace'] and album['id']:
                    # drop album photos
                    filelist = self.dao.eraseAlbum(album['id'])
                    self.deleteFiles(filelist)
                    assert self.dao.dropAlbum(album['id'])
                    # Album should be recreated
                    album['id'] = False

                if not(album['id']):
                    # create album
                    album['id'] = self.createAlbum(album)

                    if not(album['id']):
                        logger.error("didn't manage to create album for: " + album['relpath'])
                        continue
                    else:
                        logger.info("##### Album created: %s", album['name'])

                    createdalbums += 1

                # Albums are created or emptied, now take care of photos
                for f in sorted(files):

                    if self.isAPhoto(f):
                        try:
                            discoveredphotos += 1
                            error = False
                            logger.info("**** Adding %s to lychee album: %s",
                                        os.path.join(root, f),
                                        album['name'])
                            # check if tags are stored for a given photo
                            tags = ""
                            if os.path.isfile(os.path.join(root, os.path.splitext(f)[0] + ".txt")):
                                fp = open(os.path.join(root, os.path.splitext(f)[0] + ".txt"), "r")
                                tags = fp.read()
                                fp.close()
                            # corruption detected here by launching exception
                            pid = self.dao.getUniqPhotoId()
                            photo = LycheePhoto(pid, self.conf, f, album, tags)
                            if not(self.dao.photoExists(photo)):
                                res = self.copyFileToLychee(photo)
                                self.adjustRotation(photo)
                                self.makeThumbnail(photo)
                                res = self.dao.addFileToAlbum(photo)
                                # increment counter
                                if res:
                                    importedphotos += 1
                                    album['photos'].append(photo)
                                else:
                                    error = True
                                    logger.error(
                                        "while adding to album: %s photo: %s",
                                        album['name'],
                                        photo.srcfullpath)
                            else:
                                logger.error(
                                    "photo already exists in this album with same name or same checksum: %s it won't be added to lychee",
                                    photo.srcfullpath)
                                error = True
                        except Exception as e:

                            logger.exception(e)
                            logger.error("could not add %s to album %s", f, album['name'])
                            error = True
                        finally:
                            if not(error):
                                logger.info("**** Successfully added %s to lychee album: %s",
                                            os.path.join(root, f),
                                            album['name'])

                a = album.copy()
                albums.append(a)

        self.updateAlbumsDate(albums)
        if self.conf['sort']:
            self.reorderalbumids(albums)
            self.dao.reinitAlbumAutoIncrement()

        if self.conf['sanity']:

            logger.info("************ SANITY CHECK *************")
            # get All Photos albums
            photos = self.dao.get_all_photos()
            albums = [p['album'] for p in photos]
            albums = set(albums)

            # for each album
            for a_id in albums:
                # check if it exists, if not remove photos
                if not(self.dao.albumIdExists(a_id)):
                    to_delete = self.dao.get_all_photos(a_id)
                    self.dao.eraseAlbum(a_id)
                    file_list = [p['url'] for p in to_delete]
                    self.deleteFiles(file_list)

            # get All Photos
            photos = self.dao.get_all_photos()

            to_delete = []
            # for each photo
            for p in photos:
                delete_photo = False
                # check if big exists
                bigpath = os.path.join(self.conf["lycheepath"], "uploads", "big", p['url'])

                # if big is a link check if it's an orphan
                # file does not exists
                if not(os.path.lexists(bigpath)):
                    logger.error("File does not exists %s: will be delete in db", bigpath)
                    delete_photo = True
                # broken link
                elif not(os.path.exists(bigpath)):
                    logger.error("Link is broken: %s will be delete in db", bigpath)
                    delete_photo = True

                if not(delete_photo):
                    # TODO: check if thumbnail exists
                    pass
                else:
                    # if any of it is False remove and log
                    to_delete.append(p)

            self.deletePhotos(to_delete)

            # Detect broken symlinks / orphan files
            for root, dirs, files in os.walk(os.path.join(self.conf['lycheepath'], 'uploads', 'big')):

                for f in files:
                    file_name = os.path.basename(f)
                    # check if DB photo exists
                    if not self.dao.photoExistsByName(file_name):
                        # if not delete photo (or link)
                        self.deleteFiles([file_name])
                        logger.info("%s deleted. Wasn't existing in DB", f)

                    # if broken link
                    if os.path.lexists(f) and not(os.path.exists(f)):
                        id = self.dao.photoExistsByName(file_name)
                        # if exists in db
                        if id:
                            ps = {}
                            ps['id'] = id
                            ps['url'] = file_name
                            self.deletePhotos([ps])
                        else:
                            self.deleteFiles([file_name])
                        logger.info("%s deleted. Was a broken link", f)

            # drop empty albums
            empty = self.dao.get_empty_albums()
            if empty:
                for e in empty:
                    self.dao.dropAlbum(e)

        self.dao.close()

        # Final report
        logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        logger.info("Directory scanned:" + self.conf['srcdir'])
        logger.info("Created albums: " + str(createdalbums))
        if (importedphotos == discoveredphotos):
            logger.info(str(importedphotos) + " photos imported on " + str(discoveredphotos) + " discovered")
        else:
            logger.error(str(importedphotos) + " photos imported on " + str(discoveredphotos) + " discovered")
        logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
