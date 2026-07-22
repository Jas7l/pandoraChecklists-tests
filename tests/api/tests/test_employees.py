import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(employees_client, areas_client, positions_client):
    """
    Get existing test data from the system.
    """

    test_data = {
        'employee_id': None,
        'employee_name': None,
        'employee_surname': None,
        'employee_patronymic': None,
        'employee_area_ids': None,
        'employee_position_id': None,
        'new_area_id': None,
        'new_position_id': None,
        'employee_badge': None,
    }

    logger.info('Fetching first employee from API')
    response = employees_client.get_employees_list(limit=1, offset=0)
    Assert.response_status(response.status_code, 200)

    employees = response.json()
    Assert.is_not_empty(employees)
    employee = employees[0]

    test_data['employee_id'] = employee.get('employee_id')
    test_data['employee_name'] = employee.get('employee_name')
    test_data['employee_surname'] = employee.get('employee_surname')
    test_data['employee_patronymic'] = employee.get('employee_patronymic')
    test_data['employee_area_ids'] = employee.get('area_id', [])
    test_data['employee_position_id'] = employee.get('position_id')
    test_data['employee_badge'] = employee.get('employee_badge')

    logger.info(
        f'Employee loaded: ID={test_data["employee_id"]}, '
        f'Name={test_data["employee_name"]} '
        f'{test_data["employee_surname"]}',
    )

    logger.info('Fetching areas list for new area selection')
    areas_response = areas_client.get_areas_list(limit=100, offset=0)
    Assert.response_status(areas_response.status_code, 200)

    all_areas = areas_response.json()
    Assert.is_not_empty(all_areas)

    employee_area_ids = set(test_data['employee_area_ids'])
    for area in all_areas:
        area_id = area.get('area_id')
        if area_id not in employee_area_ids:
            test_data['new_area_id'] = area_id
            break

    if test_data['new_area_id'] is None:
        logger.error('No new area found for employee')
        pytest.fail('No new area found for employee')

    logger.info(
        f'New area selected: ID={test_data["new_area_id"]}',
    )

    logger.info('Fetching positions list for new position selection')
    positions_response = positions_client.get_positions_list(
        limit=100, offset=0,
    )
    Assert.response_status(positions_response.status_code, 200)

    all_positions = positions_response.json()
    Assert.is_not_empty(all_positions)

    employee_position_id = test_data['employee_position_id']
    for position in all_positions:
        position_id = position.get('position_id')
        if position_id != employee_position_id:
            test_data['new_position_id'] = position_id
            break

    if test_data['new_position_id'] is None:
        logger.error('No new position found for employee')
        pytest.fail('No new position found for employee')

    logger.info(
        f'New position selected: ID={test_data["new_position_id"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Employees API')
@pytest.mark.api
@pytest.mark.employees
class TestEmployeesAPI:
    """Test suite for Employees API endpoints"""

    TEST_NAME = 'TestName'
    TEST_SURNAME = 'TestSurname'
    TEST_PATRONYMIC = 'TestPatronymic'
    TEST_BADGE = 12345678
    TEST_INVALID_BADGE = 88888888
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1

    @pytest.fixture(scope='class')
    def test_data(self, employees_client, areas_client, positions_client):
        """Fixture to get test data once for all tests"""

        data = get_test_data(
            employees_client, areas_client, positions_client,
        )
        return data

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get employees list')
    @pytest.mark.positive
    def test_get_employees_list(self, employees_client):

        logger.info('>>> TEST: Get employees list')

        with AllureReporting.add_step('Get employees list'):
            response = employees_client.get_employees_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)
                logger.info(f'Retrieved {len(employees)} employees')
            except AssertionError:
                logger.error('Failed to get employees list')
                pytest.fail('Employees list response is empty or invalid')

        with AllureReporting.add_step('Verify employee fields'):
            employee = employees[0]

            try:
                Assert.has_key(employee, 'employee_id')
                Assert.has_key(employee, 'employee_name')
                Assert.has_key(employee, 'employee_surname')
                Assert.has_key(employee, 'employee_patronymic')
                Assert.has_key(employee, 'area_id')
                Assert.has_key(employee, 'position_id')
                Assert.has_key(employee, 'employee_badge')
                logger.info(
                    f'Employee fields verified for '
                    f'ID={employee.get("employee_id")}',
                )
            except AssertionError:
                logger.error('Employee missing required fields')
                pytest.fail(
                    'Employee object missing required fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get employees list with pagination')
    @pytest.mark.positive
    def test_get_paginated_employees_list(self, employees_client, test_data):

        logger.info(
            f'>>> TEST: Get employees list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get employees list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = employees_client.get_employees_list(
                limit=self.TEST_LIMIT,
                offset=self.TEST_OFFSET,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify paginated response'):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)
                logger.info(
                    f'Retrieved {len(employees)} employees with pagination',
                )

            except AssertionError:
                logger.error('Failed to get paginated employees list')
                pytest.fail(
                    'Paginated employees list response is empty or invalid',
                )

        with AllureReporting.add_step(
            'Verify pagination excludes test employee',
        ):
            try:
                Assert.less_than(len(employees), self.TEST_LIMIT + 1)

                for employee in employees:
                    Assert.not_equal(
                        employee.get('employee_id'),
                        test_data.get('employee_id'),
                    )

                logger.info(
                    'Pagination verified: test employee '
                    f'ID={test_data.get("employee_id")} excluded',
                )

            except AssertionError:
                logger.error(
                    'Pagination failed - test employee found in results',
                )
                pytest.fail(
                    'Test employee should be excluded by offset',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get employee by id')
    @pytest.mark.positive
    def test_get_employee_by_id(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        logger.info(f'>>> TEST: Get employee by ID={employee_id}')

        with AllureReporting.add_step(f'Get employee by ID: {employee_id}'):
            response = employees_client.get_employees_list(
                employee_id=employee_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify employee data'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()[0]

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('employee_name'),
                    test_data.get('employee_name'),
                )
                Assert.equal(
                    employee.get('employee_surname'),
                    test_data.get('employee_surname'),
                )

                logger.info(
                    f'Employee verified: ID={employee_id}, '
                    f'Name={test_data.get("employee_name")} '
                    f'{test_data.get("employee_surname")}',
                )

            except AssertionError:
                logger.error(f'Employee data mismatch for ID={employee_id}')
                pytest.fail(
                    f'Employee with ID {employee_id} not found or '
                    f'data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get employee by invalid id')
    @pytest.mark.negative
    def test_get_employee_by_invalid_id(self, employees_client):

        logger.info(
            f'>>> TEST: Get employee by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get employee by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = employees_client.get_employees_list(
                employee_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid ID',
        ):
            try:
                Assert.response_status(response.status_code, 200)
                Assert.is_empty(response.json())
                logger.info('Received empty response for invalid ID')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'ID={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid employee ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Get employee by area_id')
    @pytest.mark.positive
    def test_get_employee_by_area_id(self, employees_client, test_data):

        area_id = test_data.get('employee_area_ids')[0]
        logger.info(f'>>> TEST: Get employees by area_id={area_id}')

        with AllureReporting.add_step(
            f'Get employees by area_id={area_id}',
        ):
            response = employees_client.get_employees_list(area_id=area_id)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify employees by area'):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)

                for employee in employees:
                    area_ids = employee.get('area_id', [])
                    Assert.contains(area_ids, area_id)

                logger.info(
                    f'Found {len(employees)} employees for area_id={area_id}',
                )

            except AssertionError:
                logger.error(f'No employees found for area_id={area_id}')
                pytest.fail(
                    f'Expected employees for area_id={area_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Get employee by invalid area_id')
    @pytest.mark.negative
    def test_get_employee_by_invalid_area_id(self, employees_client):

        logger.info(
            f'>>> TEST: Get employees by invalid area_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get employees by invalid area_id={self.TEST_INVALID_ID}',
        ):
            response = employees_client.get_employees_list(
                area_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid area_id',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_empty(employees)
                logger.info('Received empty response for invalid area_id')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'area_id={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid area_id '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Get employee by position_id')
    @pytest.mark.positive
    def test_get_employee_by_position_id(self, employees_client, test_data):

        position_id = test_data.get('employee_position_id')
        logger.info(
            f'>>> TEST: Get employees by position_id={position_id}',
        )

        with AllureReporting.add_step(
            f'Get employees by position_id={position_id}',
        ):
            response = employees_client.get_employees_list(
                position_id=position_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify employees by position'):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)

                for employee in employees:
                    Assert.equal(
                        employee.get('position_id'),
                        position_id,
                    )

                logger.info(
                    f'Found {len(employees)} employees for '
                    f'position_id={position_id}',
                )

            except AssertionError:
                logger.error(
                    f'No employees found for position_id={position_id}',
                )
                pytest.fail(
                    f'Expected employees for position_id={position_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Get employee by invalid position_id')
    @pytest.mark.negative
    def test_get_employee_by_invalid_position_id(self, employees_client):

        logger.info(
            f'>>> TEST: Get employees by invalid position_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get employees by invalid position_id={self.TEST_INVALID_ID}',
        ):
            response = employees_client.get_employees_list(
                position_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid position_id',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_empty(employees)
                logger.info('Received empty response for invalid position_id')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'position_id={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid position_id '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Get employee by badge')
    @pytest.mark.positive
    def test_get_employee_by_badge(self, employees_client, test_data):

        badge = test_data.get('employee_badge')
        logger.info(f'>>> TEST: Get employees by badge={badge}')

        with AllureReporting.add_step(
            f'Get employees by badge={badge}',
        ):
            response = employees_client.get_employees_list(
                employee_badge=badge,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify employees by badge'):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)

                for employee in employees:
                    Assert.equal(
                        employee.get('employee_badge'),
                        badge,
                    )

                logger.info(
                    f'Found {len(employees)} employees with badge={badge}',
                )

            except AssertionError:
                logger.error(f'No employees found for badge={badge}')
                pytest.fail(
                    f'Expected employees for badge={badge}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get employees list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Get employee by invalid badge')
    @pytest.mark.negative
    def test_get_employee_by_invalid_badge(self, employees_client):

        logger.info(
            f'>>> TEST: Get employees by invalid badge='
            f'{self.TEST_INVALID_BADGE}',
        )

        with AllureReporting.add_step(
            f'Get employees by invalid badge={self.TEST_INVALID_BADGE}',
        ):
            response = employees_client.get_employees_list(
                employee_badge=self.TEST_INVALID_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid badge',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_empty(employees)
                logger.info('Received empty response for invalid badge')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'badge={self.TEST_INVALID_BADGE}',
                )
                pytest.fail(
                    'Expected empty response for invalid badge '
                    f'{self.TEST_INVALID_BADGE}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Create new employee')
    @pytest.mark.positive
    def test_create_employee(self, employees_client, test_data):

        logger.info('>>> TEST: Create new employee')

        area_id = [test_data.get('new_area_id')]
        position_id = test_data.get('new_position_id')

        with AllureReporting.add_step(
            f'Create employee with name="{self.TEST_NAME}", '
            f'surname="{self.TEST_SURNAME}"',
        ):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=area_id,
                position_id=position_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created employee'):
                Assert.response_status(response.status_code, 201)

                employee = response.json()
                employee_id = employee.get('employee_id')

                Assert.has_key(employee, 'employee_id')
                Assert.equal(employee.get('employee_name'), self.TEST_NAME)
                Assert.equal(
                    employee.get('employee_surname'),
                    self.TEST_SURNAME,
                )
                Assert.equal(
                    employee.get('employee_patronymic'),
                    self.TEST_PATRONYMIC,
                )
                Assert.equal(employee.get('area_id'), area_id)
                Assert.equal(employee.get('position_id'), position_id)
                Assert.equal(employee.get('employee_badge'), self.TEST_BADGE)

                logger.info(
                    f'Employee created with ID: {employee_id}, '
                    f'Name: {self.TEST_NAME} {self.TEST_SURNAME}',
                )

        except AssertionError:
            logger.error('Failed to create employee')
            pytest.fail(
                f'Employee creation failed for name="{self.TEST_NAME}"',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete employee {employee_id}',
            ):
                response = employees_client.delete_employee(employee_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Employee {employee_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-012: Create employee with invalid area_id')
    @pytest.mark.negative
    def test_create_employee_invalid_area(self, employees_client, test_data):

        logger.info(
            f'>>> TEST: Create employee with invalid area_id='
            f'{self.TEST_INVALID_ID}',
        )

        position_id = test_data.get('new_position_id')

        with AllureReporting.add_step(
            f'Create employee with invalid area_id={self.TEST_INVALID_ID}',
        ):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=[self.TEST_INVALID_ID],
                position_id=position_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify conflict response'):
            try:
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

            except AssertionError:
                if response.status_code == 201:
                    employee_id = response.json().get('employee_id')
                    with AllureReporting.add_step(
                        f'Delete invalid employee {employee_id}',
                    ):
                        employees_client.delete_employee(employee_id)
                        logger.info(
                            f'Invalid employee {employee_id} deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid area_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-013: Create employee with invalid position_id')
    @pytest.mark.negative
    def test_create_employee_invalid_position(
            self, employees_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Create employee with invalid position_id='
            f'{self.TEST_INVALID_ID}',
        )

        area_id = [test_data.get('new_area_id')]

        with AllureReporting.add_step(
            f'Create employee with invalid position_id='
            f'{self.TEST_INVALID_ID}',
        ):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=area_id,
                position_id=self.TEST_INVALID_ID,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify conflict response'):
            try:
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

            except AssertionError:
                if response.status_code == 201:
                    employee_id = response.json().get('employee_id')
                    with AllureReporting.add_step(
                        f'Delete invalid employee {employee_id}',
                    ):
                        employees_client.delete_employee(employee_id)
                        logger.info(
                            f'Invalid employee {employee_id} deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid position_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-014: Create employee with empty name')
    @pytest.mark.negative
    def test_create_employee_empty_name(self, employees_client, test_data):

        logger.info('>>> TEST: Create employee with empty name')

        area_id = [test_data.get('new_area_id')]
        position_id = test_data.get('new_position_id')

        with AllureReporting.add_step('Create employee with empty name'):
            response = employees_client.create_employee(
                employee_name='',
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=area_id,
                position_id=position_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for empty name')

            except AssertionError:
                if response.status_code == 201:
                    employee_id = response.json().get('employee_id')
                    with AllureReporting.add_step(
                        f'Delete invalid employee {employee_id}',
                    ):
                        employees_client.delete_employee(employee_id)
                        logger.info(
                            f'Invalid employee {employee_id} deleted',
                        )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-015: Create employee with empty surname')
    @pytest.mark.negative
    def test_create_employee_empty_surname(self, employees_client, test_data):

        logger.info('>>> TEST: Create employee with empty surname')

        area_id = [test_data.get('new_area_id')]
        position_id = test_data.get('new_position_id')

        with AllureReporting.add_step('Create employee with empty surname'):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname='',
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=area_id,
                position_id=position_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for empty surname')

            except AssertionError:
                if response.status_code == 201:
                    employee_id = response.json().get('employee_id')
                    with AllureReporting.add_step(
                        f'Delete invalid employee {employee_id}',
                    ):
                        employees_client.delete_employee(employee_id)
                        logger.info(
                            f'Invalid employee {employee_id} deleted',
                        )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty surname, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-016: Delete existing employee')
    @pytest.mark.positive
    def test_delete_employee(self, employees_client, test_data):

        logger.info('>>> TEST: Delete existing employee')

        area_id = [test_data.get('new_area_id')]
        position_id = test_data.get('new_position_id')

        with AllureReporting.add_step(
            f'Create employee for deletion with name="{self.TEST_NAME}"',
        ):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=area_id,
                position_id=position_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify employee created'):
            try:
                Assert.response_status(response.status_code, 201)

                employee = response.json()
                employee_id = employee.get('employee_id')
                logger.info(f'Employee created with ID: {employee_id}')

            except AssertionError:
                logger.error('Failed to create employee for deletion test')
                pytest.fail('Employee creation failed for deletion test')

        with AllureReporting.add_step(f'Delete employee {employee_id}'):
            response = employees_client.delete_employee(employee_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Employee {employee_id} deleted (204 No Content)',
                )
            except AssertionError:
                logger.error(f'Employee {employee_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for employee deletion, '
                    f'got {response.status_code}',
                )

        with AllureReporting.add_step(
            f'Verify employee {employee_id} is deleted',
        ):
            response = employees_client.get_employees_list(
                employee_id=employee_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )
            try:
                Assert.is_empty(response.json())
                logger.info('Employee deletion confirmed')
            except AssertionError:
                logger.error(f'Employee {employee_id} still exists')
                pytest.fail(
                    f'Employee {employee_id} should be deleted but still '
                    f'exists',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-017: Delete non-existent employee')
    @pytest.mark.negative
    def test_delete_employee_not_found(self, employees_client):

        logger.info(
            f'>>> TEST: Delete non-existent employee '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent employee ID={self.TEST_INVALID_ID}',
        ):
            response = employees_client.delete_employee(
                self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 404)
                logger.info('Received expected 404 error')

            except AssertionError:
                logger.error(
                    f'Expected 404 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 404 error for non-existent employee, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-018: Patch employee name')
    @pytest.mark.positive
    def test_patch_employee_name(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_name = test_data.get('employee_name')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} name to '
            f'"{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch employee name to "{self.TEST_NAME}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_name=self.TEST_NAME,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('employee_name'), self.TEST_NAME)

                logger.info(f'Employee name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Employee name update failed for ID={employee_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_name=original_name,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('employee_name'), original_name)

                logger.info(f'Employee name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original employee name')
                pytest.fail(
                    f'Failed to restore original name for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-019: Patch employee add new area')
    @pytest.mark.positive
    def test_patch_employee_add_area(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_areas = test_data.get('employee_area_ids')
        new_area_id = test_data.get('new_area_id')

        updated_areas = original_areas + [new_area_id]

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} - add area '
            f'{new_area_id}',
        )

        with AllureReporting.add_step(
            f'Patch employee - add new area {new_area_id}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                area_id=updated_areas,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('area_id'), updated_areas)

                logger.info(
                    f'Area added: {new_area_id}. '
                    f'Updated areas: {updated_areas}',
                )

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Failed to add area to employee ID={employee_id}',
                )

        with AllureReporting.add_step('Restore original areas'):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                area_id=original_areas,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('area_id'), original_areas)

                logger.info('Areas restored to original')

            except AssertionError:
                logger.error('Failed to restore original areas')
                pytest.fail(
                    f'Failed to restore original areas for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-020: Patch employee change position')
    @pytest.mark.positive
    def test_patch_employee_change_position(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_position = test_data.get('employee_position_id')
        new_position_id = test_data.get('new_position_id')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} - change '
            f'position to {new_position_id}',
        )

        with AllureReporting.add_step(
            f'Patch employee - change position to {new_position_id}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                position_id=new_position_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('position_id'), new_position_id)

                logger.info(
                    f'Position changed to: {new_position_id}',
                )

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Failed to change position for employee '
                    f'ID={employee_id}',
                )

        with AllureReporting.add_step(
            f'Restore original position {original_position}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                position_id=original_position,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('position_id'),
                    original_position,
                )

                logger.info('Position restored to original')

            except AssertionError:
                logger.error('Failed to restore original position')
                pytest.fail(
                    f'Failed to restore original position for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-021: Patch employee invalid area_id')
    @pytest.mark.negative
    def test_patch_employee_invalid_area(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} with invalid '
            f'area_id={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Patch employee with invalid area_id={self.TEST_INVALID_ID}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                area_id=[self.TEST_INVALID_ID],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

            except AssertionError:
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid area_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-022: Patch employee last name')
    @pytest.mark.positive
    def test_patch_employee_surname(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_surname = test_data.get('employee_surname')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} surname to '
            f'"{self.TEST_SURNAME}"',
        )

        with AllureReporting.add_step(
            f'Patch employee surname to "{self.TEST_SURNAME}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_surname=self.TEST_SURNAME,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('employee_surname'),
                    self.TEST_SURNAME,
                )

                logger.info(
                    f'Employee surname updated to: {self.TEST_SURNAME}',
                )

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Employee surname update failed for ID={employee_id}',
                )

        with AllureReporting.add_step(
            f'Restore original surname "{original_surname}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_surname=original_surname,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('employee_surname'),
                    original_surname,
                )

                logger.info(
                    f'Employee surname restored to: {original_surname}',
                )

            except AssertionError:
                logger.error('Failed to restore original surname')
                pytest.fail(
                    f'Failed to restore original surname for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-023: Patch employee patronymic')
    @pytest.mark.positive
    def test_patch_employee_patronymic(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_patronymic = test_data.get('employee_patronymic')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} patronymic to '
            f'"{self.TEST_PATRONYMIC}"',
        )

        with AllureReporting.add_step(
            f'Patch employee patronymic to "{self.TEST_PATRONYMIC}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_patronymic=self.TEST_PATRONYMIC,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('employee_patronymic'),
                    self.TEST_PATRONYMIC,
                )

                logger.info(
                    f'Employee patronymic updated to: '
                    f'{self.TEST_PATRONYMIC}',
                )

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Employee patronymic update failed for '
                    f'ID={employee_id}',
                )

        with AllureReporting.add_step(
            f'Restore original patronymic "{original_patronymic}"',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_patronymic=original_patronymic,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(
                    employee.get('employee_patronymic'),
                    original_patronymic,
                )

                logger.info(
                    f'Employee patronymic restored to: '
                    f'{original_patronymic}',
                )

            except AssertionError:
                logger.error('Failed to restore original patronymic')
                pytest.fail(
                    f'Failed to restore original patronymic for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-024: Patch employee badge')
    @pytest.mark.positive
    def test_patch_employee_badge(self, employees_client, test_data):

        employee_id = test_data.get('employee_id')
        original_badge = test_data.get('employee_badge')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} badge to '
            f'{self.TEST_BADGE}',
        )

        with AllureReporting.add_step(
            f'Patch employee badge to {self.TEST_BADGE}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('employee_badge'), self.TEST_BADGE)

                logger.info(f'Employee badge updated to: {self.TEST_BADGE}')

            except AssertionError:
                logger.error(f'Employee {employee_id} patch failed')
                pytest.fail(
                    f'Employee badge update failed for ID={employee_id}',
                )

        with AllureReporting.add_step(
            f'Restore original badge {original_badge}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                employee_badge=original_badge,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                employee = response.json()

                Assert.equal(employee.get('employee_id'), employee_id)
                Assert.equal(employee.get('employee_badge'), original_badge)

                logger.info(f'Employee badge restored to: {original_badge}')

            except AssertionError:
                logger.error('Failed to restore original badge')
                pytest.fail(
                    f'Failed to restore original badge for employee '
                    f'ID={employee_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-025: Patch employee with non-existent position')
    @pytest.mark.negative
    def test_patch_employee_invalid_position(
            self, employees_client, test_data,
    ):

        employee_id = test_data.get('employee_id')
        original_position = test_data.get('employee_position_id')

        logger.info(
            f'>>> TEST: Patch employee ID={employee_id} with invalid '
            f'position_id={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Patch employee with invalid position_id='
            f'{self.TEST_INVALID_ID}',
        ):
            response = employees_client.patch_employee(
                employee_id=employee_id,
                position_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

            except AssertionError:
                if response.status_code == 200:
                    response = employees_client.patch_employee(
                        employee_id=employee_id,
                        position_id=original_position,
                    )
                    AllureReporting.attach_response(
                        response.status_code,
                        response.json(),
                    )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid position_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-026: Create employee with duplicate badge')
    @pytest.mark.negative
    def test_create_employee_duplicate_badge(
            self, employees_client, test_data,
    ):

        existing_badge = test_data.get('employee_badge')
        logger.info(
            f'>>> TEST: Create employee with duplicate badge='
            f'{existing_badge}',
        )

        with AllureReporting.add_step(
            f'Create employee with duplicate badge={existing_badge}',
        ):
            response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=[test_data.get('new_area_id')],
                position_id=test_data.get('new_position_id'),
                employee_badge=existing_badge,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify conflict response'):
            try:
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

            except AssertionError:
                if response.status_code == 201:
                    employee_id = response.json().get('employee_id')
                    with AllureReporting.add_step(
                        f'Delete invalid employee {employee_id}',
                    ):
                        employees_client.delete_employee(employee_id)
                        logger.info(
                            f'Invalid employee {employee_id} deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for duplicate badge, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch employee')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-027: Patch employee with duplicate badge')
    @pytest.mark.negative
    def test_patch_employee_duplicate_badge(self, employees_client, test_data):

        logger.info('>>> TEST: Patch employee with duplicate badge')

        with AllureReporting.add_step(
            f'Create employee with unique badge={self.TEST_BADGE}',
        ):
            create_response = employees_client.create_employee(
                employee_name=self.TEST_NAME,
                employee_surname=self.TEST_SURNAME,
                employee_patronymic=self.TEST_PATRONYMIC,
                area_id=[test_data.get('new_area_id')],
                position_id=test_data.get('new_position_id'),
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                create_response.status_code,
                create_response.json(),
            )

            try:
                Assert.response_status(create_response.status_code, 201)
                created_employee = create_response.json()
                created_employee_id = created_employee.get('employee_id')
                logger.info(
                    f'Created employee with ID: {created_employee_id}',
                )

            except AssertionError:
                logger.error('Failed to create employee for patch test')
                pytest.fail(
                    'Employee creation failed for patch duplicate test',
                )

        duplicate_badge = test_data.get('employee_badge')
        logger.info(
            f'Attempting to patch with duplicate badge={duplicate_badge}',
        )

        with AllureReporting.add_step(
            f'Patch employee with duplicate badge={duplicate_badge}',
        ):
            patch_response = employees_client.patch_employee(
                employee_id=created_employee_id,
                employee_badge=duplicate_badge,
            )
            AllureReporting.attach_response(
                patch_response.status_code,
                patch_response.json(),
            )

        try:
            with AllureReporting.add_step('Verify conflict response'):
                Assert.response_status(patch_response.status_code, 409)
                logger.info('Received expected 409 conflict error')

        except AssertionError:
            logger.error(
                f'Expected 409 conflict, got {patch_response.status_code}',
            )
            pytest.fail(
                f'Expected 409 conflict error for duplicate badge, '
                f'got status {patch_response.status_code}',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete created employee {created_employee_id}',
            ):
                delete_response = employees_client.delete_employee(
                    created_employee_id,
                )
                AllureReporting.attach_response(delete_response.status_code)

                try:
                    Assert.response_status(delete_response.status_code, 204)
                    logger.info(
                        f'Deleted employee with ID: {created_employee_id}',
                    )

                except AssertionError:
                    logger.error(
                        f'Failed to delete employee {created_employee_id}',
                    )
                    pytest.fail(
                        f'Expected 204 response for employee deletion, '
                        f'got {delete_response.status_code}',
                    )

        logger.info('<<< TEST PASSED')
