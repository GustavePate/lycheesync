#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import unicode_literals
import logging.config
import click
from pps.utils.boilerplatecode import script_init
import lycheesync.lycheedao as demo_template
logger = logging.getLogger(__name__)

# click demonstrator


@click.command()
@click.option('--verbose', '-v', default=False, help='Program verbosity.')
@click.option('-m1', '--mode1', 'exclusive_mode', flag_value='mode1',
              default=True, help='functionnal mode 1, exclusive with mode 2')
@click.option('-m2', '--mode2', 'exclusive_mode', flag_value='mode2',
              help='functionnal mode 2, exclusive withe mode 1')
@click.option('-s', '--string', help='A simple string')
@click.option('-x', '--closed_choice', type=click.Choice(['md5', 'sha1']), help='a closed value choice')
@click.argument('file1', type=click.Path(resolve_path=True))
# checks file existence and attributes
# @click.argument('file2', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True, resolve_path=True))
def main(verbose, string, exclusive_mode, closed_choice, file1):
    """The perfect python script.

    A template and technology demonstrator
    for running really good python scripts.
    """

    ERROR = False

    cli_args = {}
    cli_args[u'verbose'] = verbose
    cli_args[u'string'] = string
    cli_args[u'exclusive_mode'] = exclusive_mode
    cli_args[u'closed_choice'] = closed_choice
    cli_args[u'file1'] = file1

    script_init(cli_args)

    logger.info("................start...............")
    try:

        demo_seaborn.demo()

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
