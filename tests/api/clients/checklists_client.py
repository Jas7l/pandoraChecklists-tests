import requests
from typing import Optional, List

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class ChecklistsClient(BaseApiClient):
    """API client for Checklists service"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)

    def get_checklists_list(
            self,
            limit: int = 0,
            offset: int = 0,
            checklist_id: Optional[int] = None,
            machine_id: Optional[int] = None,
            status: Optional[bool] = None,
    ) -> requests.Response:
        """Get paginated list of checklists with filters"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if checklist_id is not None:
            params['id'] = checklist_id
        if machine_id is not None:
            params['machine_id'] = machine_id
        if status is not None:
            params['status'] = status

        return self.get('/checklists', params=params)

    def create_checklist(
            self,
            checklist_name: str,
            machine_id: int,
            task_id: List[int],
    ) -> requests.Response:
        """Create new checklist"""

        payload = {
            'checklist_name': checklist_name,
            'machine_id': machine_id,
            'task_id': task_id,
        }

        return self.post('/checklists', json=payload)

    def delete_checklist(self, checklist_id: int) -> requests.Response:
        return self.delete(f'/checklists/{checklist_id}')

    def patch_checklist(
            self,
            checklist_id: int,
            checklist_name: Optional[str] = None,
            machine_id: Optional[int] = None,
            status: Optional[bool] = None,
            task_id: Optional[List[int]] = None,
    ) -> requests.Response:
        """Patch checklist by id"""

        payload = {}

        if checklist_name is not None:
            payload['checklist_name'] = checklist_name
        if machine_id is not None:
            payload['machine_id'] = machine_id
        if status is not None:
            payload['status'] = status
        if task_id is not None:
            payload['task_id'] = task_id

        return self.patch(f'/checklists/{checklist_id}', json=payload)

    def copy_checklist(
            self,
            source_checklist_id: int,
            target_machine_id: int,
    ) -> requests.Response:
        """Copy checklist to another machine"""

        payload = {
            'machine_id': target_machine_id,
        }

        return self.post(
            f'/checklists/{source_checklist_id}/copy', json=payload,
        )

    def add_task_to_checklist(
            self,
            checklist_id: int,
            task_id: int,
    ) -> requests.Response:
        """Add one task in existed checklist"""

        payload = {
            'task_id': task_id,
        }

        return self.post(f'/checklists/{checklist_id}/tasks', json=payload)

    def remove_task_from_checklist(
            self,
            checklist_id: int,
            task_id: int,
    ) -> requests.Response:
        """Remove task from checklist by id"""

        return self.delete(f'/checklists/{checklist_id}/tasks/{task_id}')

    def search_checklists(
            self,
            q: str,
            status: Optional[bool] = None,
            limit: int = 20,
            offset: int = 0,
    ) -> requests.Response:
        """Search checklists by name substring"""

        params = {
            'q': q,
            'limit': limit,
            'offset': offset,
        }
        if status is not None:
            params['status'] = status

        return self.get('/checklists/search', params=params)
