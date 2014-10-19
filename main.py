#!/bin/python
# -*- coding: utf-8 -*-

from lycheesyncer import LycheeSyncer
from update_scripts import inf_to_lychee_2_6_2
import argparse
import os
import sys
import json
import pwd
import grp


def main(conf):
    """ just call to LycheeSyncer """

    # DELEGATE WORK TO LYCHEESYNCER
    s = LycheeSyncer(conf)
    s.sync()


def show_args():
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    print "Program Launched with args:"
    print "* dropDB:" + str(args.dropdb)
    print "* replace:" + str(args.replace)
    print "* verbose:" + str(args.verbose)
    print "* srcdir:" + args.srcdir
    print "* lycheepath:" + args.lycheepath
    print "* conf:" + args.conf
    print "* sort_by_name:" + str(conf_data['sort'])
    print "Program Launched with conf:"
    print "* dbHost:" + conf_data['dbHost']
    print "* db:" + conf_data['db']
    print "* dbUser:" + conf_data['dbUser']
    print "* dbPassword:" + conf_data['dbPassword']
    print "* thumbQuality:" + str(conf_data['thumbQuality'])
    print "* publicAlbum:" + str(conf_data['publicAlbum'])
    print "* user:" + str(conf_data["user"])
    print "* group:" + str(conf_data["group"])
    print "* uid:" + str(conf_data["uid"])
    print "* gid:" + str(conf_data["gid"])
    print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

if __name__ == '__main__':

    #     ARGUMENTS PARSING
    #     AND CONFIGURATION FILE READING

    parser = argparse.ArgumentParser(description=("Add all files in a directory to lychee. " +
                                                  "sub directories are albums and files are photos"))
    parser.add_argument('srcdir', help='directory to enslave lychee with', type=str)
    parser.add_argument('lycheepath', help='lychee installation directory', type=str)
    parser.add_argument('conf', help='lychee db configuration file', type=str)
    parser.add_argument('-d', '--dropdb', help=("drop lychee db " +
                                                "and populate it with directory content"), action='store_true')
    parser.add_argument('-r', '--replace', help=("drop albums corresponding to srcdir structure " +
                                                 "but don t drop the entire db"), action='store_true')
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')
    parser.add_argument('-s', '--sort_album_by_name', help='sort album display by name', action='store_true')
    parser.add_argument('-u', '--updatedb26', action='store_const', dest='updatedb_to_version_2_6_2', const='2.6.2', help='Update lycheesync added data in lychee db to the lychee 2.6.2 required values')
    args = parser.parse_args()
    shouldquit = False

    if (args.replace and args.dropdb):
        shouldquit = True
        print "you have to choose between replace and dropdb behaviour"

    if not os.path.exists(os.path.join(args.lycheepath, 'uploads')):
        shouldquit = True
        print "lychee install path may be wrong:" + args.lycheepath

    if not os.path.exists(args.conf):
        shouldquit = True
        print "configuration file  does not exist:" + args.conf
    else:
        conf_file = open(args.conf, 'r')
        conf_data = json.load(conf_file)
        conf_file.close()

    if args.updatedb_to_version_2_6_2:
        print "updatedb"
    elif not os.path.exists(args.srcdir):
        shouldquit = True
        print "photo directory does not exist:" + args.srcdir

    if shouldquit:
        sys.exit(1)

    conf_data["srcdir"] = args.srcdir
    conf_data["lycheepath"] = args.lycheepath
    conf_data["dropdb"] = args.dropdb
    conf_data["replace"] = args.replace
    conf_data["verbose"] = args.verbose
    conf_data["updatedb"] = args.updatedb_to_version_2_6_2
    conf_data["user"] = None
    conf_data["group"] = None
    conf_data["uid"] = None
    conf_data["gid"] = None
    conf_data["sort"] =  args.sort_album_by_name
    if conf_data["dropdb"]:
        conf_data["sort"] = True


    if conf_data["updatedb"] == "2.6.2":
        if args.verbose:
            show_args()
        inf_to_lychee_2_6_2.updatedb(conf_data)

    else:

        # read permission of the lycheepath directory to apply it to the uploade photos
        img_path = os.path.join(conf_data["lycheepath"], "uploads")
        stat_info = os.stat(img_path)
        uid = stat_info.st_uid
        gid = stat_info.st_gid

        user = pwd.getpwuid(uid)[0]
        group = grp.getgrgid(gid)[0]

        conf_data["user"] = user
        conf_data["group"] = group
        conf_data["uid"] = uid
        conf_data["gid"] = gid

        if args.verbose:
            show_args()
        main(conf_data)
