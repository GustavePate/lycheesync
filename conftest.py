import pytest
import json
import os
import logging
from lycheesync.utils.configuration import ConfBorg
from tests.testutils import TestUtils

logger = logging.getLogger(__name__)

# py.test tweaking
# in this exemple: initialize configuration borg for the whole test session


def pytest_report_header(config):
    """ return a string in test report header """
    return "Hey this are the tests"


def pytest_addoption(parser):
    """create a confpath command line arg for py.test"""
    parser.addoption('--confpath', action="append", default=[], help="configuration full path")


@pytest.fixture(scope="function")
def clean(request):
    """ will be run for each test function see pytest.ini """
    logger.info("DropDb")
    tu = TestUtils()
    tu.clean_db()
    tu.clean_fs()


@pytest.fixture(scope="function")
def carriagereturn(request):
    """ will be run for each test function see pytest.ini """
    print(" ")


@pytest.fixture(scope="session")
def initloggers(request):
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

    def run_only_at_session_end():
        print("\n ********** End of test session **********")
    request.addfinalizer(run_only_at_session_end)

    print("********** Test session init **********")

    if pytest.config.getoption('confpath') is not None:
        print("Launch test with conf:", pytest.config.getoption('confpath', default=None))
        conf_path = pytest.config.getoption('confpath')
        # previously returns a list, get the string
        if len(pytest.config.getoption('confpath')) > 0:
            conf_path = pytest.config.getoption('confpath')[0]

    if os.path.exists(conf_path):
        with open(conf_path, 'rt') as f:
            conf = json.load(f)

        # add data path which is calculated at run time
        conf['data_path'] = os.path.dirname(os.path.dirname(conf_path))
        conf['data_path'] = os.path.join(conf['data_path'], 'data')
        res = ConfBorg(conf)
        logger.info("ConfBorg initialized")
    return res
