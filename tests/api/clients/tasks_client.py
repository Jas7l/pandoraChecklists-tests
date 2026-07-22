import requests
from typing import Optional

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class TasksClient(BaseApiClient):
    """API client for Tasks service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize Tasks API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)

    def get_tasks_list(
            self,
            limit: int = 0,
            offset: int = 0,
            task_id: Optional[int] = None,
    ) -> requests.Response:
        """Get paginated list of tasks"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if task_id is not None:
            params['id'] = task_id

        return self.get('/tasks', params=params)

    def create_task(self, task_name: str) -> requests.Response:
        """Create new task"""

        payload = {
            'task_name': task_name,
        }

        return self.post('/tasks', json=payload)

    def delete_task(self, task_id: int) -> requests.Response:
        """Delete task by id"""

        return self.delete(f'/tasks/{task_id}')

    def patch_task(self, task_id: int, task_name: str) -> requests.Response:
        """Patch task by id"""

        payload = {
            'task_name': task_name,
        }

        return self.patch(f'/tasks/{task_id}', json=payload)
