import pytest

from tests.config.settings import settings
from tests.api.clients import (
    AreasClient,
    PositionsClient,
    EmployeesClient,
)
from tests.utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture(scope='session')
def areas_client():
    """Areas API client"""

    client = AreasClient(settings.api_url)
    yield client

    client.close()
    logger.info('Areas client closed after test')


@pytest.fixture(scope='session')
def positions_client():
    """Positions API client"""

    client = PositionsClient(settings.api_url)
    yield client

    client.close()
    logger.info('Positions client closed after test')

@pytest.fixture(scope='session')
def employees_client():
    """Employees API client"""

    client = EmployeesClient(settings.api_url)
    yield client

    client.close()
    logger.info('Employees client closed after test')
