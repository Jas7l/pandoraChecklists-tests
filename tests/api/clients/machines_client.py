import requests
from typing import Optional

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class MachinesClient(BaseApiClient):
    """API client for Machines service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize Machines API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)

    def get_machines_list(
            self,
            limit: int = 0,
            offset: int = 0,
            machine_id: Optional[int] = None,
            area_id: Optional[int] = None,
            status: Optional[str] = None,
    ) -> requests.Response:
        """Get paginated list of machines"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if machine_id is not None:
            params['id'] = machine_id
        if area_id is not None:
            params['area_id'] = area_id
        if status is not None:
            params['status'] = status

        return self.get('/machines', params=params)

    def create_machine(
            self,
            machine_name: str,
            area_id: int,
    ) -> requests.Response:
        """Create new machine"""

        payload = {
            'machine_name': machine_name,
            'area_id': area_id,
        }

        return self.post('/machines', json=payload)

    def delete_machine(self, machine_id: int) -> requests.Response:
        """Delete machine by id"""

        return self.delete(f'/machines/{machine_id}')

    def patch_machine(
            self,
            machine_id: int,
            machine_name: Optional[str] = None,
            area_id: Optional[int] = None,
            status: Optional[str] = None,
    ) -> requests.Response:
        """Patch machine by id"""

        payload = {}

        if machine_name is not None:
            payload['machine_name'] = machine_name
        if area_id is not None:
            payload['area_id'] = area_id
        if status is not None:
            payload['status'] = status

        return self.patch(f'/machines/{machine_id}', json=payload)
