#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import logging
from lycheesync.utils.configuration import ConfBorg
import sys

logger = logging.getLogger(__name__)


def script_init(cli_args):
    """
    - will initialize a ConfBorg object containing cli arguments, configutation file elements
    - will initialize loggers
    """

    root_level = ".."

    # compute log file absolute path
    pathname = os.path.dirname(sys.argv[0])
    full_path = os.path.abspath(pathname)
    log_conf_path = os.path.join(full_path, root_level, "ressources", 'logging.json')

    # append path to configuration
    cli_args['full_path'] = full_path

    print("try to read logging conf from: " + log_conf_path)
    # read log configuration

    # TODO: try with . and .. as root level depending if main.py is used
    if os.path.exists(log_conf_path):
        with open(log_conf_path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        if cli_args['verbose']:
            logging.getLogger().setLevel(logging.DEBUG)
        logger.info("logging conf -> read from: " + log_conf_path)
    else:
        # default value
        logging.basicConfig(level=logging.INFO)
        logging.info("logging conf -> default conf")

    logger.info("................init...............")
    # read application configuration
    if os.path.exists(cli_args['confpath']):
        with open(cli_args['confpath'], 'rt') as f:
            conf = json.load(f)
    else:
        logger.warn("Loading default conf in ressources/conf.json")
        conf_path = os.path.join(full_path, root_level, "ressources", 'conf.json')
        if os.path.exists(conf_path):
            with open(conf_path, 'rt') as f:
                conf = json.load(f)


    # initialize conf with items loaded from conf file AND command lines arguments
    # cli args have priority over configuration file
    z = conf.copy()
    z.update(cli_args)
    borg = ConfBorg(z)
    logger.info(".......loaded configuration: ")
    logger.info(borg.pretty)
