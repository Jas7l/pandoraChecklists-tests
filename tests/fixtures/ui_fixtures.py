import pytest
from pathlib import Path
from tests.config.settings import settings
from tests.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent


@pytest.fixture(scope='session')
def browser_type_launch_args():
    """Playwright browser launch arguments"""

    return {
        'headless': settings.headless_mode,
        'args': [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
        ],
    }


@pytest.fixture(scope='function')
def playwright_browser_context_args():
    """Playwright browser context arguments"""

    return {
        'viewport': {'width': 1920, 'height': 1080},
        'ignore_https_errors': True,
    }


@pytest.fixture(scope='function')
def playwright_page(browser, page):
    """
    Wrapped Playwright page fixture to add
    logging without shadowing plugin fixture
    """

    logger.info(f'Playwright page initialized for {settings.base_url}')
    yield page
    logger.info('Closing Playwright page')


@pytest.fixture(scope='function')
def screenshot_on_failure(playwright_page, request):
    """Take screenshot on test failure"""

    yield

    if hasattr(request.node, 'rep_call') and request.node.rep_call.failed:
        logs_dir = PROJECT_ROOT / 'logs' / 'screenshots'
        logs_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = logs_dir / f'{request.node.name}_failure.png'

        try:
            playwright_page.screenshot(path=str(screenshot_path))
            logger.error(f'Screenshot saved: {screenshot_path}')
        except Exception as e:
            logger.error(f'Could not take screenshot: {e}')
