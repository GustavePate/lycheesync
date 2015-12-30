# coding: utf8
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
from lycheesync.lycheesyncer import LycheeSyncer
from lycheesync.update_scripts import inf_to_lychee_2_6_2
import logging.config
import click
import os
import argparse
import json
import sys
import pwd
import grp

from lycheesync.utils.boilerplatecode import script_init

logger = logging.getLogger(__name__)


# Other main
def other_main():
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
    parser.add_argument(
        '-l',
        '--link',
        help='do not copy photos to lychee uploads directory, just create a symlink',
        action='store_true')
    parser.add_argument(
        '-u',
        '--updatedb26',
        action='store_const',
        dest='updatedb_to_version_2_6_2',
        const='2.6.2',
        help='Update lycheesync added data in lychee db to the lychee 2.6.2 required values')
    args = parser.parse_args()
    shouldquit = False

    if (args.replace and args.dropdb):
        shouldquit = True
        print("you have to choose between replace and dropdb behaviour")

    if not os.path.exists(os.path.join(args.lycheepath, 'uploads')):
        shouldquit = True
        print("lychee install path may be wrong:" + args.lycheepath)

    if not os.path.exists(args.conf):
        shouldquit = True
        print("configuration file  does not exist:" + args.conf)
    else:
        conf_file = open(args.conf, 'r')
        conf_data = json.load(conf_file)
        conf_file.close()

    if args.updatedb_to_version_2_6_2:
        print("updatedb")
    elif not os.path.exists(args.srcdir):
        shouldquit = True
        print("photo directory does not exist:" + args.srcdir)

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
    conf_data["sort"] = args.sort_album_by_name
    conf_data["link"] = args.link
    if conf_data["dropdb"]:
        conf_data["sort"] = True

    if conf_data["updatedb"] == "2.6.2":
        if args.verbose:
            # show_args()
            pass
        inf_to_lychee_2_6_2.updatedb(conf_data)

    else:

        # read permission of the lycheepath directory to apply it to the uploade photos
        img_path = os.path.join(conf_data["lycheepath"], "uploads", "big")
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
            # show_args()
            pass
        main(conf_data)


@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Program verbosity.')
@click.option('-n', '--normal', 'exclusive_mode', flag_value='normal',
              default=True, help='normal mode exclusive with replace and delete mode')
@click.option('-r', '--replace', 'exclusive_mode', flag_value='replace',
              default=False, help='delete mode exclusive with replace mode and normal')
@click.option('-d', '--dropdb', 'exclusive_mode', flag_value='delete',
              default=False, help='delete mode exclusive with replace and normal mode')
@click.option('-s', '--sort_album_by_name', is_flag=True, help='Sort album by name')
@click.option('-l', '--link', is_flag=True, help="Don't copy files create link instead")
@click.option('-u26', '--updatedb26', is_flag=True,
              help="Update lycheesync added data in lychee db to the lychee 2.6.2 required values")
@click.argument('imagedirpath', metavar='PHOTO_DIRECTORY_ROOT',
                type=click.Path(exists=True, resolve_path=True))
@click.argument('lycheepath', metavar='PATH_TO_LYCHEE_INSTALL',
                type=click.Path(exists=True, resolve_path=True))
@click.argument('confpath', metavar='PATH_TO_YOUR_CONFIG_FILE',
                type=click.Path(exists=True, resolve_path=True))
# checks file existence and attributes
# @click.argument('file2', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True))
def main(verbose, exclusive_mode, sort_album_by_name, link, updatedb26, imagedirpath, lycheepath, confpath):
    """Lycheesync

    A script to synchronize any directory containing photos with Lychee.
    Source directory should be on the same host than Lychee's
    """

    ERROR = False

    if sys.version_info.major == 2:
        imagedirpath = imagedirpath.decode('UTF-8')
        lycheepath = lycheepath.decode('UTF-8')
        confpath = confpath.decode('UTF-8')

    conf_data = {}
    conf_data['verbose'] = verbose
    conf_data["srcdir"] = imagedirpath
    conf_data["lycheepath"] = lycheepath
    conf_data['confpath'] = confpath
    conf_data["dropdb"] = False
    conf_data["replace"] = False

    if exclusive_mode == "delete":
        conf_data["dropdb"] = True
    elif exclusive_mode == "replace":
        conf_data["replace"] = True

    conf_data["user"] = None
    conf_data["group"] = None
    conf_data["uid"] = None
    conf_data["gid"] = None
    conf_data["sort"] = sort_album_by_name
    conf_data["link"] = link
    # if conf_data["dropdb"]:
    #    conf_data["sort"] = True

    # read permission of the lycheepath directory to apply it to the uploade photos
    img_path = os.path.join(conf_data["lycheepath"], "uploads", "big")
    stat_info = os.stat(img_path)
    uid = stat_info.st_uid
    gid = stat_info.st_gid

    user = pwd.getpwuid(uid)[0]
    group = grp.getgrgid(gid)[0]

    conf_data["user"] = user
    conf_data["group"] = group
    conf_data["uid"] = uid
    conf_data["gid"] = gid

    if verbose:
        # show_args()
        pass

    script_init(conf_data)

    # DB update
    if updatedb26:
        if conf_data['verbose']:
            print(conf_data)
        inf_to_lychee_2_6_2.updatedb(conf_data)

    logger.info("................start...............")
    try:

        # DELEGATE WORK TO LYCHEESYNCER
        s = LycheeSyncer()
        s.sync()

    except Exception:
        logger.exception('Failed to run batch')
        ERROR = True

    else:
        logger.debug("Success !!!")

    finally:
        if ERROR:
            logger.error("..............script ended with errors...............")
        else:
            logger.info("...............script successfully ended..............")


if __name__ == '__main__':
    main()
