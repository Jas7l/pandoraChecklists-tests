import pytest
import uuid
from datetime import datetime

from tests.config.settings import settings
from tests.api.clients import (
    AreasClient,
    PositionsClient,
    EmployeesClient,
    TasksClient,
    MachinesClient,
    ChecklistsClient,
    ChecklistRunsClient,
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


@pytest.fixture(scope='session')
def tasks_client():
    """Tasks API client"""

    client = TasksClient(settings.api_url)
    yield client

    client.close()
    logger.info('Tasks client closed after test')


@pytest.fixture(scope='session')
def machines_client():
    """Machines API client"""

    client = MachinesClient(settings.api_url)
    yield client

    client.close()
    logger.info('Machines client closed after test')


@pytest.fixture(scope='session')
def checklists_client():
    """Checklists API client"""

    client = ChecklistsClient(settings.api_url)
    yield client

    client.close()
    logger.info('Checklists client closed after test')


@pytest.fixture(scope='session')
def checklist_runs_client():
    """Checklist runs API client"""

    client = ChecklistRunsClient(settings.api_url)
    yield client

    client.close()
    logger.info('Checklist runs client closed after test')


@pytest.fixture
def unique_area_name():
    """Generate unique area name for tests."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    short_uuid = uuid.uuid4().hex[:6]
    return f'test_area_{timestamp}_{short_uuid}'
