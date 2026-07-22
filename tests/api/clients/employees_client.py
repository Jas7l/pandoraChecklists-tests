import requests
from typing import Optional, List

from tests.api.clients.base_client import BaseApiClient
from tests.utils.logger import get_logger

logger = get_logger(__name__)


class EmployeesClient(BaseApiClient):
    """API client for Employees service"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize Employees API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        super().__init__(base_url, timeout)

    def get_employees_list(
            self,
            limit: int = 0,
            offset: int = 0,
            employee_id: Optional[int] = None,
            area_id: Optional[int] = None,
            position_id: Optional[int] = None,
            employee_badge: Optional[int] = None,
    ) -> requests.Response:
        """Get paginated list of employees with filters"""

        params = {
            'limit': limit,
            'offset': offset,
        }
        if employee_id is not None:
            params['id'] = employee_id
        if area_id is not None:
            params['area_id'] = area_id
        if position_id is not None:
            params['position_id'] = position_id
        if employee_badge is not None:
            params['employee_badge'] = employee_badge

        return self.get('/employees', params=params)

    def create_employee(
            self,
            employee_name: str,
            employee_surname: str,
            employee_patronymic: str,
            area_id: List[int],
            position_id: int,
            employee_badge: int,
    ) -> requests.Response:
        """Create new employee"""

        payload = {
            'employee_name': employee_name,
            'employee_surname': employee_surname,
            'employee_patronymic': employee_patronymic,
            'area_id': area_id,
            'position_id': position_id,
            'employee_badge': employee_badge,
        }

        return self.post('/employees', json=payload)

    def delete_employee(self, employee_id: int) -> requests.Response:
        """Delete employee by id"""

        return self.delete(f'/employees/{employee_id}')

    def patch_employee(
            self,
            employee_id: int,
            employee_name: Optional[str] = None,
            employee_surname: Optional[str] = None,
            employee_patronymic: Optional[str] = None,
            area_id: Optional[List[int]] = None,
            position_id: Optional[int] = None,
            employee_badge: Optional[int] = None,
    ) -> requests.Response:
        """Patch employee by id"""

        payload = {}

        if employee_name is not None:
            payload['employee_name'] = employee_name
        if employee_surname is not None:
            payload['employee_surname'] = employee_surname
        if employee_patronymic is not None:
            payload['employee_patronymic'] = employee_patronymic
        if area_id is not None:
            payload['area_id'] = area_id
        if position_id is not None:
            payload['position_id'] = position_id
        if employee_badge is not None:
            payload['employee_badge'] = employee_badge

        return self.patch(f'/employees/{employee_id}', json=payload)
