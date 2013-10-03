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

    def getAlbumNameFromPath(self, albumpath):
        """
        build a lychee compatible albumname from an albumpath (relative to the srcdir main argument)
        Takes a string  as input (relative albumpath)
        Returns a string, the lychee album name
        """
        #make a list with directory and sub dirs
        path = albumpath.split(os.sep)
        #remove the first directory (the containes)
        albumname = path[2:]
        #join the rest: no subfolders in lychee yet
        albumname = "_".join(albumname)
        return albumname

    def isAPhoto(self, file):
        """
        Determine if the filename passed is a photo or not based on the file extension
        Takes a string  as input (a file name)
        Returns a boolean
        """
        validimgext = ['.jpg', '.jpeg', '.gif', '.png']
        ext = os.path.splitext(file)[-1].lower()
        return (ext in validimgext)

    def albumExists(self, albumpath):
        """
        Takes a string  as input (relative albumpath)
        Returns an albumid or None if album does not exists
        """
        albumname = self.getAlbumNameFromPath(albumpath)
        return self.dao.albumExists(albumname.lower())

    def createAlbum(self, albumpath):
        """
        Creates an album
        Inputs:
        - albumpath: a string (relative albumpath)
        Returns an albumid or None if album does not exists
        """
        albumid = None
        albumname = self.getAlbumNameFromPath(albumpath)
        if albumname != "":
            albumid = self.dao.createAlbum(albumname.lower())
        return albumid

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
        destimage = os.path.join(destinationpath, destfile)
        img = Image.open(photo.srcfullpath)
        img.thumbnail(res)
        img.save(destimage)
        return destimage

    def makeThumbnail(self, photo):
        """
        Make the 2 thumbnails needed by Lychee for a given photo
        and store their path in the LycheePhoto object
        Parameters:
        - photo: a valid LycheePhoto object
        returns nothing
        """
        #set  thumbnail size
        sizes = [(200, 200), (400, 400)]
        #insert @2x in big thumbnail file name
        filesplit = os.path.splitext(photo.url)
        destfiles = [photo.url, ''.join([filesplit[0], "@2x", filesplit[1]]).lower()]
        #compute destination path
        destpath = os.path.join(self.conf["lycheepath"], "uploads", "thumb")
        #make thumbnails
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
            #copy photo
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

        #Connect db
        #and drop it if dropdb activated
        self.dao = LycheeDAO(self.conf)

        if self.conf['dropdb']:
            self.deleteAllFiles()

        #Load db

        createdalbums = 0
        discoveredphotos = 0
        importedphotos = 0

        #walkthroug each file / dir of the srcdir
        for root, dirs, files in os.walk(self.conf['srcdir']):

            for f in files:
                if self.isAPhoto(f):

                    discoveredphotos += 1
                    albumpath = root

                    # don't know what to do with theses photo
                    # and don't wan't to create a default album
                    if albumpath == self.conf['srcdir']:
                        msg = ("WARN: file at srcdir root won't be added to lychee, " +
                               "please move them in a subfolder"), os.path.join(root, f)
                        print msg
                        continue

                    albumid = self.albumExists(albumpath)
                    if not(albumid):
                        #create album
                        albumid = self.createAlbum(albumpath)
                        createdalbums += 1
                    elif self.conf['replace']:
                        #drop album photos
                        filelist = self.dao.eraseAlbum(albumid)
                        self.deleteFiles(filelist)

                    photo = LycheePhoto(self.conf, f, albumpath, albumid)

                    if not(self.dao.photoExists(photo)):
                        if self.conf['verbose']:
                            print "INFO: adding to lychee", os.path.join(root, f)
                        self.makeThumbnail(photo)
                        res = self.addFileToAlbum(photo)
                        #increment counter
                        if res:
                                importedphotos += 1
                        #report
                        if self.conf['verbose']:
                            if res:
                                print "INFO: successfully added to lychee", os.path.join(root, f)
                            else:
                                print "ERROR: while adding to lychee", os.path.join(root, f)
                    else:
                        if self.conf['verbose']:
                            print "WARN: photo already exists in lychee: ", photo.srcfullpath

        self.dao.close()

        # Final report
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "Directory scanned:", self.conf['srcdir']
        print "Created albums: ", str(createdalbums)
        print str(importedphotos), "photos imported on",  str(discoveredphotos), "discovered"
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
