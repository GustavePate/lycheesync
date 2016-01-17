#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
# from __future__ import unicode_literals
from lycheesync.lycheesyncer import LycheeSyncer
from lycheesync.update_scripts import inf_to_lychee_2_6_2
import logging.config
import click
import os
import sys
import pwd
import grp

from lycheesync.utils.boilerplatecode import script_init

logger = logging.getLogger(__name__)


@click.command()
@click.option('-v', '--verbose', is_flag=True, help='Program verbosity.')
@click.option('-n', '--normal', 'exclusive_mode', flag_value='normal',
              default=True, help='normal mode exclusive with replace and delete mode')
@click.option('-r', '--replace', 'exclusive_mode', flag_value='replace',
              default=False, help='delete mode exclusive with replace mode and normal')
@click.option('-d', '--dropdb', 'exclusive_mode', flag_value='delete',
              default=False, help='delete mode exclusive with replace and normal mode')
@click.option('-s', '--sort_album_by_name', is_flag=True, help='Sort album by name')
@click.option('-c', '--sanitycheck', is_flag=True, help='Sort album by name')
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
def main(verbose, exclusive_mode, sort_album_by_name, sanitycheck, link, updatedb26, imagedirpath, lycheepath, confpath):
    """Lycheesync

    A script to synchronize any directory containing photos with Lychee.
    Source directory should be on the same host than Lychee's
    """

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
    if sanitycheck:
        logger.info("!!!!!!!!!!!!!!!! SANITY ON")
    else:
        logger.info("!!!!!!!!!!!!!!!! SANITY OFF")
    conf_data["sanity"] = sanitycheck
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

    script_init(conf_data)

    # DB update
    if updatedb26:
        inf_to_lychee_2_6_2.updatedb(conf_data)

    logger.info("................start adding to lychee...............")
    try:

        # DELEGATE WORK TO LYCHEESYNCER
        s = LycheeSyncer()
        s.sync()

    except Exception:
        logger.exception('Failed to run batch')
        logger.error("..............script ended with errors...............")

    else:
        logger.info("...............script successfully ended..............")


if __name__ == '__main__':
    main()
