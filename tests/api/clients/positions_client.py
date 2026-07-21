import requests
from typing import Optional

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class PositionsClient(BaseApiClient):
    """API client for Positions service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize Models API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)

    def get_positions_list(
            self,
            limit: int = 0,
            offset: int = 0,
            p_id: Optional[int] = None,
    ) -> requests.Response:
        """Get paginated list of positions"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if p_id is not None:
            params['id'] = p_id

        return self.get('/positions', params=params)

    def create_position(self, name: str) -> requests.Response:
        """Create new position"""

        payload = {
            'position_name': name,
        }

        return self.post('/positions', json=payload)

    def delete_position(self, p_id: int) -> requests.Response:
        """Delete position by id"""

        return self.delete(f'/positions/{p_id}')

    def patch_position(self, p_id: int, name: str) -> requests.Response:
        """Patch position by id"""

        payload = {'position_name': name}

        return self.patch(f'/positions/{p_id}', json=payload)
