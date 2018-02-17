# -*- coding: utf-8 -*-

import pytest
import json
import os
import logging
from tests.configuration import TestBorg
from tests.testutils import TestUtils

logger = logging.getLogger(__name__)

# py.test tweaking
# in this exemple: initialize configuration borg for the whole test session


def pytest_report_header(config):
    """ return a string in test report header """
    return "Hey this are the tests"


def pytest_addoption(parser):
    """create a confpath command line arg for py.test"""
    parser.addoption(
        '--confpath',
        dest="confpath",
        action="append",
        default=[],
        help="configuration full path")


@pytest.fixture(scope="function")
def clean(request):
    """ will be run for each test function see pytest.ini """
    tu = TestUtils()
    if tu.db_exists():
        tu.clean_db()
    tu.clean_fs()


@pytest.fixture(scope="function")
def carriagereturn(request):
    """ will be run for each test function see pytest.ini """
    print(" ")


@pytest.fixture(scope="session")
def initdb_and_fs(request):

    if request.config.getoption('confpath') is not None:
        print("Launch test with conf:", pytest.config.getoption('confpath', default=None))
        conf_path = request.config.getoption('confpath')
        # previously returns a list, get the string
        if len(request.config.getoption('confpath')) > 0:
            conf_path = request.config.getoption('confpath')[0]

    if os.path.exists(conf_path):
        with open(conf_path, 'rt') as f:
            conf = json.load(f)

    logger.info("#FIXTURE: init db and fs")
    tu = TestUtils()

    # Impossible because conf not loaded
    tu.drop_db()
    tu.make_fake_lychee_db()
    tu.make_fake_lychee_fs(tu.conf['lycheepath'])


@pytest.fixture(scope="session")
def initloggers(request):
    print("#FIXTURE: initloggers")
    """ will be run for each test session see pytest.ini """
    # initialize basic loggers
    print("****** INIT LOGGERS ******")
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s - %(name)s.%(funcName)s l. %(lineno)d - %(message)s',
        datefmt='%H:%M:%S')


@pytest.fixture(scope="session")
def confborg(request):
    """
    - allow confborg to be a valid test parameter,
    this code will be executed before the test code
    once per session
    """
    print("#FIXTURE: confborg")

    print("********** Test session init **********")

    if request.config.getoption('confpath') is not None:
        print("Launch test with conf:", pytest.config.getoption('confpath', default=None))
        conf_path = request.config.getoption('confpath')
        # previously returns a list, get the string
        if len(request.config.getoption('confpath')) > 0:
            conf_path = request.config.getoption('confpath')[0]

    if os.path.exists(conf_path):
        with open(conf_path, 'rt') as f:
            conf = json.load(f)

        # add data path which is calculated at run time
        conf['data_path'] = os.path.dirname(os.path.dirname(conf_path))
        conf['data_path'] = os.path.join(conf['data_path'], 'data')
        res = TestBorg(conf)
        logger.info("TestBorg initialized")
    return res
