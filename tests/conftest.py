import pytest
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SRC_PATH = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_PATH))

from tests.fixtures.ui_fixtures import *
from tests.fixtures.api_fixtures import *
from tests.utils.logger import get_logger
from tests.config.settings import settings

logger = get_logger(__name__)


def pytest_configure(config):
    """Print configuration"""

    logger.info('=' * 70)
    logger.info('Test Automation Framework Started')
    logger.info(f'Environment: {settings.environment}')
    logger.info(f'Base URL: {settings.base_url}')
    logger.info(f'Headless Mode: {settings.headless_mode}')
    logger.info('=' * 70)


def pytest_sessionstart(session):
    """Start session hook"""

    logger.info('Test session started')


def pytest_sessionfinish(session, exitstatus):
    """End session hook"""

    logger.info(f'Test session finished with exit status: {exitstatus}')


@pytest.fixture(scope='session', autouse=True)
def configure_logging():
    """Configure logger for tests"""

    logger.info('Logging configured')
    yield
    logger.info('Test session cleanup completed')


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Create report"""

    outcome = yield

    rep = outcome.get_result()

    if rep.when == 'call':
        if rep.passed:
            logger.info(f'[PASS] {item.name}')
        elif rep.failed:
            logger.error(f'[FAIL] {item.name}')
        elif rep.skipped:
            logger.warning(f'[SKIP] {item.name}')


@pytest.fixture(scope='function')
def test_logger():
    """Logger for test"""

    return logger
