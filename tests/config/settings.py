import os
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """Settings manager"""

    def __init__(self, env_file: Optional[str] = None):
        """init setting from environment variables"""

        if env_file is None:
            env_file = os.path.join(
                os.path.dirname(__file__), 'localhost.env',
            )

        if os.path.exists(env_file):
            load_dotenv(env_file)

    @property
    def base_url(self) -> str:
        """Base frontend url"""

        return os.getenv('BASE_URL', 'http://localhost:3000/dashcams')

    @property
    def api_url(self) -> str:
        """Base api url"""

        return os.getenv('API_URL', 'http://localhost:8080/api/v1')

    @property
    def headless_mode(self) -> bool:
        """Headless mode parameter for reports"""

        return os.getenv('HEADLESS_MODE', 'false').lower() == 'true'

    @property
    def browser_timeout(self) -> int:
        """Browser timeout"""

        return int(os.getenv('BROWSER_TIMEOUT', '30'))

    @property
    def implicit_wait(self) -> int:
        """Implicit wait time"""

        return int(os.getenv('IMPLICIT_WAIT', '10'))

    @property
    def log_level(self) -> str:
        """Log level"""

        return os.getenv('LOG_LEVEL', 'INFO')

    @property
    def environment(self) -> str:
        """Current environment"""

        return os.getenv('ENVIRONMENT', 'localhost')


def get_settings(env: Optional[str] = None) -> Settings:
    """Get settings from environment file"""

    if env is None:
        env = os.getenv('ENVIRONMENT', 'localhost')

    env_file = os.path.join(os.path.dirname(__file__), f'{env}.env')
    return Settings(env_file)


settings = get_settings()
