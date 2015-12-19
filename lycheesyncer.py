# coding: utf8
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
import os
import shutil
import stat
import traceback
from lycheedao import LycheeDAO
from lycheemodel import LycheePhoto
from PIL import Image
import datetime
import time
import sys


def remove_file(path):
    try:
        os.remove(path)
    except:
        print("WARN problem removing: " + path)


class LycheeSyncer:

    """
    This class contains the logic behind this program
    It consist mainly in filesystem operations
    It relies on:
    - LycheeDAO for dtabases operations
    - LycheePhoto to store (and compute) photos propreties
    """

    conf = {}

    def __init__(self, conf):
        """
        Takes a dictionnary of conf as input
        """
        self.conf = conf

    def getAlbumNameFromPath(self, album):
        """
        build a lychee compatible albumname from an albumpath (relative to the srcdir main argument)
        Takes an album properties list  as input. At least the path sould be specified (relative albumpath)
        Returns a string, the lychee album name
        """
        # make a list with directory and sub dirs
        print("ENCODING: " + str(sys.getfilesystemencoding()))
        alb_path_utf8 = album['relpath']  # .decode('UTF-8')
        print("THE PATH: " + alb_path_utf8)

        path = alb_path_utf8.split(os.sep)

        # join the rest: no subfolders in lychee yet
        if len(path) > 1:
            print("JOIN")
            album['name'] = "_".join(path)
        else:
            album['name'] = alb_path_utf8
        print("album name:" + album['name'])
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
            img = Image.open(photo.srcfullpath)
        except:
            print("ERROR ioerror (corrupted file?): " + photo.srcfullpath)
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

    def addFileToAlbum(self, photo):
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
            except:
                if self.conf["verbose"]:
                    print(
                        "WARN: chgrp error,  check file permission for " +
                        photo.destfullpath +
                        ' fix: eventually adjust source file permissions')

            if not(self.conf['link']):
                st = os.stat(photo.destfullpath)
                os.chmod(photo.destfullpath, st.st_mode | stat.S_IRWXU | stat.S_IRWXG)
            else:
                st = os.stat(photo.srcfullpath)
                os.chmod(photo.srcfullpath, st.st_mode | stat.S_IROTH)

            res = self.dao.addFileToAlbum(photo)

        except Exception:
            print("addFileToAlbum", Exception)
            traceback.print_exc()
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

    def rotatephoto(self, photo, rotation):
        # rotate main photo
        img = Image.open(photo.destfullpath)
        img2 = img.rotate(rotation)
        img2.save(photo.destfullpath, quality=99)
        # rotate Thumbnails
        img = Image.open(photo.thumbnailx2fullpath)
        img2 = img.rotate(rotation)
        img2.save(photo.thumbnailx2fullpath, quality=99)
        img = Image.open(photo.thumbnailfullpath)
        img2.rotate(rotation)
        img2.save(photo.thumbnailfullpath, quality=99)

    def adjustRotation(self, photo):
        """
        Rotates photos according to the exif orienttaion tag
        Returns nothing
        """
        if photo.exif.orientation not in (0, 1):
            # There is somthing to do
            if photo.exif.orientation == 6:
                # rotate 90° clockwise
                # AND LOOSE EXIF DATA
                self.rotatephoto(photo, -90)
            if photo.exif.orientation == 8:
                # rotate 90° counterclockwise
                # AND LOOSE EXIF DATA
                self.rotatephoto(photo, 90)

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
        print("last2min: " + str(last2min_epoch))
        print("last2min: " + str(datetime.datetime.fromtimestamp(last2min_epoch)))

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
                        if self.conf["verbose"]:
                            print(
                                "INFO album " +
                                a['name'] +
                                " sysstamp changed to: ",
                                time.strftime(
                                    '%Y-%m-%d %H:%M:%S',
                                    time.localtime(newdate)))
            except Exception as e:
                print("ERROR: updating album date for album:" + a['name'], e)
                traceback.print_exc()

    def deleteAllFiles(self):
        """
        Deletes every photo file in Lychee
        Returns nothing
        """
        filelist = []
        photopath = os.path.join(self.conf["lycheepath"], "uploads", "big")
        filelist = [f for f in os.listdir(photopath)]
        self.deleteFiles(filelist)

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
                root = root.decode('UTF-8')
            # Init album data
            album['id'] = None
            album['name'] = None
            album['path'] = None
            album['relpath'] = None  # path relative to srcdir
            album['photos'] = []  # path relative to srcdir

            # if a there is at least one photo in the files
            if any([self.isAPhoto(f) for f in files]):
                album['path'] = root

                # don't know what to do with theses photo
                # and don't wan't to create a default album
                if album['path'] == self.conf['srcdir']:
                    msg = ("WARN: file at srcdir root won't be added to lychee, " +
                           "please move them in a subfolder"), os.path.join(root, f)
                    print(msg)
                    continue

                # Fill in other album properties
                # albumnames start at srcdir (to avoid absolute path albumname)
                album['relpath'] = os.path.relpath(album['path'], self.conf['srcdir'])
                album['name'] = self.getAlbumNameFromPath(album)

                if len(album['name']) > album_name_max_width:
                    print("WARN: album name too long, will be truncated " + album['name'])
                    album['name'] = album['name'][0:album_name_max_width]
                    if self.conf['verbose']:
                        print("WARN: album name is now " + album['name'])

                album['id'] = self.dao.albumExists(album)

                if self.conf['replace'] and album['id']:
                    # drop album photos
                    filelist = self.dao.eraseAlbum(album)
                    self.deleteFiles(filelist)
                    assert self.dao.dropAlbum(album['id'])
                    # Album should be recreated
                    album['id'] = False

                if not(album['id']):
                    # create album
                    album['id'] = self.createAlbum(album)
                    # TODO go to next album if it fails
                    if not(album['id']):
                        print("ERROR didn't manage to create album for: " + album['relpath'])
                        continue

                    createdalbums += 1

                # Albums are created or emptied, now take care of photos
                for f in files:
                    if sys.version_info.major == 2:
                        f = f.decode('UTF-8')
                    if self.isAPhoto(f):

                        try:
                            discoveredphotos += 1
                            photo = LycheePhoto(self.conf, f, album)

                            if not(self.dao.photoExists(photo)):
                                if self.conf['verbose']:
                                    print("INFO: adding to lychee", os.path.join(root, f))
                                self.makeThumbnail(photo)
                                res = self.addFileToAlbum(photo)
                                self.adjustRotation(photo)
                                # increment counter
                                if res:
                                    importedphotos += 1
                                # report
                                if self.conf['verbose']:
                                    if res:
                                        album['photos'].append(photo)
                                    else:
                                        print("ERROR: while adding to lychee", os.path.join(root, f))
                            else:
                                if self.conf['verbose']:
                                    print(
                                        "WARN: photo already exists in lychee with same name or same checksum: ",
                                        photo.srcfullpath)
                        except Exception:
                            traceback.print_exc()
                            print("ERROR could not add " + str(f) + " to album " + album['name'])

                a = album.copy()
                albums.append(a)

        self.updateAlbumsDate(albums)
        if self.conf['sort']:
            self.reorderalbumids(albums)
            self.dao.reinitAlbumAutoIncrement()
        self.dao.close()

        # Final report
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Directory scanned:", self.conf['srcdir'])
        print("Created albums: ", str(createdalbums))
        if (importedphotos == discoveredphotos):
            print(str(importedphotos), "photos imported on", str(discoveredphotos), "discovered")
        else:
            print('ERROR: ' + str(importedphotos), "photos imported on", str(discoveredphotos), "discovered")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
