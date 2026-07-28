import requests
from typing import Optional, List, Dict, Any

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class ChecklistRunsClient(BaseApiClient):
    """API client for Checklist Runs service"""

    def __init__(self, base_url: str, timeout: int = 30):
        super().__init__(base_url, timeout)

    def create_checklist_run(
            self,
            checklist_id: int,
            employee_badge: int,
            tasks: List[Dict[str, Any]],
    ) -> requests.Response:
        """Create checklist run"""

        payload = {
            'employee_badge': employee_badge,
            'tasks': tasks,
        }

        return self.post(f'/checklists/{checklist_id}/runs', json=payload)

    def get_checklist_runs_list(
            self,
            limit: int = 0,
            offset: int = 0,
            run_id: Optional[int] = None,
            machine_id: Optional[int] = None,
            employee_id: Optional[int] = None,
            checklist_id: Optional[int] = None,
            result_status: Optional[str] = None,
            date_from: Optional[str] = None,
            date_to: Optional[str] = None,
    ) -> requests.Response:
        """Get history of checklist runs"""

        params = {
            'limit': limit,
            'offset': offset,
        }

        if run_id is not None:
            params['id'] = run_id
        if machine_id is not None:
            params['machine_id'] = machine_id
        if employee_id is not None:
            params['employee_id'] = employee_id
        if checklist_id is not None:
            params['checklist_id'] = checklist_id
        if result_status is not None:
            params['result_status'] = result_status
        if date_from is not None:
            params['date_from'] = date_from
        if date_to is not None:
            params['date_to'] = date_to

        return self.get('/checklist-runs', params=params)
