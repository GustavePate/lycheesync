#!/bin/python
# -*- coding: utf-8 -*-

from lycheesyncer import LycheeSyncer
import argparse
import os
import sys
import json


def main(conf):
    """ just call to LycheeSyncer """

    #DELEGATE WORK TO LYCHEESYNCER
    s = LycheeSyncer(conf)
    s.sync()


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
    args = parser.parse_args()
    shouldquit = False

    if (args.replace and args.dropdb):
        shouldquit = True
        print "you have to choose between replace and dropdb behaviour"

    if not os.path.exists(args.srcdir):
        shouldquit = True
        print "photo directory does not exist:" + args.dir

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

    if args.verbose:
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "Program Launched with args:"
        print "* dropDB:" + str(args.dropdb)
        print "* replace:" + str(args.replace)
        print "* verbose:" + str(args.verbose)
        print "* srcdir:" + args.srcdir
        print "* lycheepath:" + args.lycheepath
        print "* conf:" + args.conf
        print "Program Launched with conf:"
        print "* dbHost:" + conf_data['dbHost']
        print "* db:" + conf_data['db']
        print "* dbUser:" + conf_data['dbUser']
        print "* dbPassword:" + conf_data['dbPassword']
        print "* thumbQuality:" + str(conf_data['thumbQuality'])
        print "* publicAlbum:" + str(conf_data['publicAlbum'])
        print "* starPhoto:" + str(conf_data['starPhoto'])
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    if shouldquit:
        sys.exit(1)

    conf_data["srcdir"] = args.srcdir
    conf_data["lycheepath"] = args.lycheepath
    conf_data["dropdb"] = args.dropdb
    conf_data["replace"] = args.replace
    conf_data["verbose"] = args.verbose

    main(conf_data)
