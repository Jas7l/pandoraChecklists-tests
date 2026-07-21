import requests
from typing import Optional

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class AreasClient(BaseApiClient):
    """API client for Areas service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize Models API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)

    def get_areas_list(
            self,
            limit: int = 0,
            offset: int = 0,
            a_id: Optional[int] = None,
    ) -> requests.Response:
        """Get paginated list of areas"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if a_id is not None:
            params['id'] = a_id

        return self.get('/areas', params=params)

    def create_area(self, name: str) -> requests.Response:
        """Create new area"""

        payload = {
            'area_name': name,
        }

        return self.post('/areas', json=payload)

    def delete_area(self, a_id: int) -> requests.Response:
        """Delete area by id"""

        return self.delete(f'/areas/{a_id}')

    def patch_area(self, a_id: int, name: str) -> requests.Response:
        """Patch area by id"""

        payload = {'area_name': name}

        return self.patch(f'/areas/{a_id}', json=payload)
