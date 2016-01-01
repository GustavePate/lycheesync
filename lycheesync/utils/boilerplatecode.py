#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import logging
from logging.handlers import BaseRotatingHandler

from lycheesync.utils.configuration import ConfBorg
import sys

logger = logging.getLogger(__name__)


def init_loggers(logconf, verbose=False):
    with open(logconf, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    logger.debug("**** logging conf -> read from: " + logconf)
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        for h in logging.getLogger().handlers:
            if h.name == "stream_handler":
                h.setLevel(logging.DEBUG)

def script_init(cli_args):
    """
    - will initialize a ConfBorg object containing cli arguments, configutation file elements
    - will initialize loggers
    """

    root_level = ".."

    # compute log file absolute path
    pathname = os.path.dirname(sys.argv[0])
    full_path = os.path.abspath(pathname)

    # root level is different if main.py or sync.py is used to launch script
    log_conf_path = os.path.join(full_path, root_level, "ressources", 'logging.json')
    log_conf_path2 = os.path.join(full_path, "ressources", 'logging.json')

    # append path to configuration
    cli_args['full_path'] = full_path


    # read log configuration
    if os.path.exists(log_conf_path):
        init_loggers(log_conf_path, cli_args['verbose'])
    elif os.path.exists(log_conf_path2):
        init_loggers(log_conf_path2, cli_args['verbose'])
    else:
        # default value
        logging.basicConfig(level=logging.DEBUG)
        logging.warn("**** logging conf -> default conf")

    # read application configuration
    if os.path.exists(cli_args['confpath']):
        with open(cli_args['confpath'], 'rt') as f:
            conf = json.load(f)
    else:
        logger.warn("**** Loading default conf in ressources/conf.json")
        conf_path = os.path.join(full_path, root_level, "ressources", 'conf.json')
        if os.path.exists(conf_path):
            with open(conf_path, 'rt') as f:
                conf = json.load(f)


    # initialize conf with items loaded from conf file AND command lines arguments
    # cli args have priority over configuration file
    z = conf.copy()
    z.update(cli_args)
    borg = ConfBorg(z)
    logger.debug("**** loaded configuration: ")
    logger.debug("**** " + borg.pretty)
