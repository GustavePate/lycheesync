# -*- coding: utf-8 -*-

import os
import shutil
import traceback
from lycheedao import LycheeDAO
from lycheemodel import LycheePhoto
from PIL import Image


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
        path = album['relpath'].split(os.sep)
        # join the rest: no subfolders in lychee yet
        album['name'] = "_".join(path).lower()
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
        album['name'] = self.getAlbumNameFromPath(album)
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
            right = photo.height + left
            lower = photo.height
        else:
            delta = photo.height - photo.width
            left = 0
            upper = int(delta / 2)
            right = photo.width
            lower = photo.width + upper

        destimage = os.path.join(destinationpath, destfile)
        img = Image.open(photo.srcfullpath)
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
            shutil.copy(photo.srcfullpath, photo.destfullpath)
            res = self.dao.addFileToAlbum(photo)

        except Exception:
            print "addFileToAlbum", Exception
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

                os.remove(thumbpath)
                os.remove(thumb2path)
                os.remove(bigpath)

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

        if nbalbum + 1 < min:
            newid = 1
        else:
            newid = max + 1

        for a in sortedalbums:
            self.dao.changeAlbumId(a['id'], newid)
            newid = newid + 1

    def updateAlbumsDate(self, albums):
        for a in albums:
            try:
                datelist = [photo.sysdate for photo in a['photos']]
                if datelist is not None and len(datelist) > 0:
                    maxdate = max(datelist)
                    self.dao.updateAlbumDate(a['id'], maxdate.replace(':', '-'))
            except Exception, e:
                print "ERROR: updating album date for album:" + a['name'], e

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
        # walkthroug each file / dir of the srcdir
        for root, dirs, files in os.walk(self.conf['srcdir']):

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
                    print msg
                    continue

                # Fill in other album properties
                # albumnames start at srcdir (to avoid absolute path albumname)
                album['relpath'] = os.path.relpath(album['path'], self.conf['srcdir'])
                album['name'] = self.getAlbumNameFromPath(album)
                album['id'] = self.dao.albumExists(album)

                if not(album['id']):
                    # create album
                    album['id'] = self.createAlbum(album)
                    createdalbums += 1
                elif self.conf['replace']:
                    # drop album photos
                    filelist = self.dao.eraseAlbum(album)
                    self.deleteFiles(filelist)

                # Albums are created or emptied, now take care of photos
                for f in files:
                    if self.isAPhoto(f):

                        discoveredphotos += 1
                        photo = LycheePhoto(self.conf, f, album)

                        if not(self.dao.photoExists(photo)):
                            if self.conf['verbose']:
                                print "INFO: adding to lychee", os.path.join(root, f)
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
                                    print "ERROR: while adding to lychee", os.path.join(root, f)
                        else:
                            if self.conf['verbose']:
                                print "WARN: photo already exists in lychee: ", photo.srcfullpath

                a = album.copy()
                albums.append(a)

        self.updateAlbumsDate(albums)
        self.reorderalbumids(albums)
        self.dao.reinitAlbumAutoIncrement()
        self.dao.close()

        # Final report
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "Directory scanned:", self.conf['srcdir']
        print "Created albums: ", str(createdalbums)
        print str(importedphotos), "photos imported on", str(discoveredphotos), "discovered"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
