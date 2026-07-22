import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(areas_client):
    """
    Get existing test data from the system.
    """

    test_data = {
        'area_id': None,
        'area_name': None,
    }

    logger.info('Fetching first area from API')
    response = areas_client.get_areas_list(limit=1, offset=0)

    Assert.response_status(response.status_code, 200)

    areas = response.json()
    Assert.is_not_empty(areas)
    area = areas[0]

    test_data['area_id'] = area.get('area_id')
    test_data['area_name'] = area.get('area_name')

    logger.info(
        f'Area loaded: ID={test_data["area_id"]}, '
        f'Name={test_data["area_name"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Areas API')
@pytest.mark.api
@pytest.mark.areas
class TestAreasAPI:
    """Test suite for Areas API endpoints"""

    TEST_NAME = 'test area'
    TEST_BADGE = 12345678
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1

    @pytest.fixture(scope='class')
    def test_data(self, areas_client):
        """Fixture to get test data once for all tests"""

        data = get_test_data(areas_client)
        return data

    @allure.story('Get areas list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get areas list')
    @pytest.mark.positive
    def test_get_areas_list(self, areas_client):

        logger.info('>>> TEST: Get areas list')

        with AllureReporting.add_step('Get areas list'):
            response = areas_client.get_areas_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()
                Assert.is_not_empty(areas)
                logger.info(f'Retrieved {len(areas)} areas')
            except AssertionError:
                logger.error('Failed to get areas list')
                pytest.fail('Areas list response is empty or invalid')

        with AllureReporting.add_step('Verify area fields'):
            area = areas[0]

            try:
                Assert.has_key(area, 'area_id')
                Assert.has_key(area, 'area_name')
                logger.info(
                    f'Area fields verified for ID={area.get("area_id")}',
                )
            except AssertionError:
                logger.error('Area missing required fields')
                pytest.fail(
                    'Area object missing area_id or area_name fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get areas list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get areas list with pagination')
    @pytest.mark.positive
    def test_get_paginated_areas_list(self, areas_client, test_data):

        logger.info(
            f'>>> TEST: Get areas list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get areas list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = areas_client.get_areas_list(
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

                areas = response.json()
                Assert.is_not_empty(areas)
                logger.info(
                    f'Retrieved {len(areas)} areas with pagination',
                )

            except AssertionError:
                logger.error('Failed to get paginated areas list')
                pytest.fail(
                    'Paginated areas list response is empty or invalid',
                )

        with AllureReporting.add_step(
            'Verify pagination excludes test area',
        ):
            try:
                Assert.less_than(len(areas), self.TEST_LIMIT + 1)

                for area in areas:
                    Assert.not_equal(
                        area.get('area_id'),
                        test_data.get('area_id'),
                    )
                    Assert.not_equal(
                        area.get('area_name'),
                        test_data.get('area_name'),
                    )

                logger.info(
                    'Pagination verified: test area '
                    f'ID={test_data.get("area_id")} excluded',
                )

            except AssertionError:
                logger.error(
                    'Pagination failed - test area found in results',
                )
                pytest.fail(
                    'Test area should be excluded by offset',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get areas list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get area by id')
    @pytest.mark.positive
    def test_get_area_by_id(self, areas_client, test_data):

        area_id = test_data.get('area_id')
        logger.info(f'>>> TEST: Get area by ID={area_id}')

        with AllureReporting.add_step(f'Get area by ID: {area_id}'):
            response = areas_client.get_areas_list(a_id=area_id)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify area data'):
            try:
                Assert.response_status(response.status_code, 200)

                area = response.json()[0]

                Assert.equal(area.get('area_id'), area_id)
                Assert.equal(
                    area.get('area_name'),
                    test_data.get('area_name'),
                )

                logger.info(
                    f'Area verified: ID={area_id}, '
                    f'Name={test_data.get("area_name")}',
                )

            except AssertionError:
                logger.error(f'Area data mismatch for ID={area_id}')
                pytest.fail(
                    f'Area with ID {area_id} not found or data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get areas list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get area by invalid id')
    @pytest.mark.negative
    def test_get_area_by_invalid_id(self, areas_client):

        logger.info(
            f'>>> TEST: Get area by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get area by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = areas_client.get_areas_list(
                a_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid area ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Create new area')
    @pytest.mark.positive
    def test_create_area(self, areas_client):

        logger.info(
            f'>>> TEST: Create new area with name="{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Create area with name="{self.TEST_NAME}"',
        ):
            response = areas_client.create_area(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created area'):
                Assert.response_status(response.status_code, 201)

                area = response.json()

                Assert.has_key(area, 'area_id')
                Assert.equal(area.get('area_name'), self.TEST_NAME)
                area_id = area.get('area_id')

                logger.info(
                    f'Area created with ID: {area_id}, '
                    f'Name: {self.TEST_NAME}',
                )

        except AssertionError:
            logger.error('Failed to create area')
            pytest.fail(
                f'Area creation failed for name="{self.TEST_NAME}"',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete area {area_id}',
            ):
                response = areas_client.delete_area(area_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Area {area_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Create area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Create area with duplicate name')
    @pytest.mark.negative
    def test_create_area_duplicate_name(self, areas_client, test_data):

        existing_name = test_data.get('area_name')
        logger.info(
            f'>>> TEST: Create area with duplicate '
            f'name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create area with duplicate name="{existing_name}"',
        ):
            response = areas_client.create_area(existing_name)
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
                    with AllureReporting.add_step(
                        'Delete invalid duplicate area',
                    ):
                        area_id = response.json().get('area_id')
                        response = areas_client.delete_area(area_id)
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid duplicate area {area_id} deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for duplicate name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Create area with empty name')
    @pytest.mark.negative
    def test_create_area_empty_name(self, areas_client):

        logger.info('>>> TEST: Create area with empty name')

        with AllureReporting.add_step('Create area with empty name'):
            response = areas_client.create_area('')
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for empty name')

            except AssertionError:
                if response.status_code == 200:
                    with AllureReporting.add_step(
                        'Delete invalid area with empty name',
                    ):
                        area_id = response.json().get('area_id')
                        response = areas_client.delete_area(area_id)
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid area {area_id} with empty name '
                            f'deleted',
                        )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Delete existing area')
    @pytest.mark.positive
    def test_delete_area(self, areas_client):

        logger.info('>>> TEST: Delete existing area')

        with AllureReporting.add_step(
            f'Create area for deletion with name="{self.TEST_NAME}"',
        ):
            response = areas_client.create_area(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify area created'):
            try:
                Assert.response_status(response.status_code, 201)

                area = response.json()
                area_id = area.get('area_id')
                logger.info(f'Area created with ID: {area_id}')

            except AssertionError:
                logger.error('Failed to create area for deletion test')
                pytest.fail('Area creation failed for deletion test')

        with AllureReporting.add_step(f'Delete area {area_id}'):
            response = areas_client.delete_area(area_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Area {area_id} deleted (204 No Content)',
                )

            except AssertionError:
                logger.error(f'Area {area_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for area deletion, '
                    f'got {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Delete non-existent area')
    @pytest.mark.negative
    def test_delete_area_not_found(self, areas_client):

        logger.info(
            f'>>> TEST: Delete non-existent area '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent area ID={self.TEST_INVALID_ID}',
        ):
            response = areas_client.delete_area(self.TEST_INVALID_ID)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 404)
                logger.info('Received expected 404 error')

            except AssertionError:
                logger.error(
                    f'Expected 404 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 404 error for non-existent area, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Patch area name')
    @pytest.mark.positive
    def test_patch_area(self, areas_client, test_data):

        area_id = test_data.get('area_id')
        original_name = test_data.get('area_name')

        logger.info(
            f'>>> TEST: Patch area ID={area_id} name to '
            f'"{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch area name to "{self.TEST_NAME}"',
        ):
            response = areas_client.patch_area(area_id, self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                area = response.json()

                Assert.equal(area.get('area_id'), area_id)
                Assert.equal(area.get('area_name'), self.TEST_NAME)

                logger.info(f'Area name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Area {area_id} patch failed')
                pytest.fail(
                    f'Area name update failed for ID={area_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = areas_client.patch_area(area_id, original_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                area = response.json()

                Assert.equal(area.get('area_id'), area_id)
                Assert.equal(area.get('area_name'), original_name)

                logger.info(f'Area name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original area name')
                pytest.fail(
                    f'Failed to restore original name for area '
                    f'ID={area_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Patch area with duplicate name')
    @pytest.mark.negative
    def test_patch_area_duplicate_name(self, areas_client, test_data):

        existing_name = test_data.get('area_name')
        logger.info(
            f'>>> TEST: Patch area with duplicate '
            f'name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create area for patch test with name="{self.TEST_NAME}"',
        ):
            response = areas_client.create_area(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify area created'):
            try:
                Assert.response_status(response.status_code, 201)

                area = response.json()
                area_id = area.get('area_id')
                logger.info(f'Area created with ID: {area_id}')

            except AssertionError:
                logger.error('Failed to create area for patch test')
                pytest.fail(
                    'Area creation failed for patch duplicate test',
                )

        try:
            with AllureReporting.add_step(
                f'Try to patch with duplicate name="{existing_name}"',
            ):
                response = areas_client.patch_area(area_id, existing_name)
                AllureReporting.attach_response(response.status_code)

            with AllureReporting.add_step('Verify conflict response'):
                try:
                    Assert.response_status(response.status_code, 409)
                    logger.info('Received expected 409 conflict error')

                except AssertionError:
                    logger.error(
                        f'Expected 409 conflict, got '
                        f'{response.status_code}',
                    )
                    pytest.fail(
                        f'Expected 409 conflict for duplicate name, '
                        f'got status {response.status_code}',
                    )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete created area {area_id}',
            ):
                response = areas_client.delete_area(area_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Area {area_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Delete area')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-012: Delete area that is assigned to employee')
    @pytest.mark.negative
    def test_delete_area_assigned_to_employee(
            self, areas_client, employees_client, test_data,
    ):

        logger.info('>>> TEST: Delete area assigned to employee')

        with AllureReporting.add_step('Get existing employee'):
            response = employees_client.get_employees_list(limit=1, offset=0)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

            try:
                Assert.response_status(response.status_code, 200)

                employees = response.json()
                Assert.is_not_empty(employees)
                employee = employees[0]
                logger.info(
                    f'Found employee: ID={employee.get("employee_id")}, '
                    f'Name={employee.get("employee_name")}',
                )

            except AssertionError:
                logger.error('Failed to get employee for test')
                pytest.fail('No employee found in the system')

        with AllureReporting.add_step(
            f'Create area "{self.TEST_NAME}" and assign to employee',
        ):
            area_response = areas_client.create_area(self.TEST_NAME)
            Assert.response_status(area_response.status_code, 201)
            new_area = area_response.json()
            new_area_id = new_area.get('area_id')
            logger.info(f'Area created with ID: {new_area_id}')

            response = employees_client.create_employee(
                employee_name=employee.get('employee_name'),
                employee_surname=employee.get('employee_surname'),
                employee_patronymic=employee.get('employee_patronymic'),
                area_id=[new_area_id],
                position_id=employee.get('position_id'),
                employee_badge=self.TEST_BADGE,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

            try:
                Assert.response_status(response.status_code, 201)
                created_employee = response.json()
                created_employee_id = created_employee.get('employee_id')
                logger.info(
                    f'Employee created with ID: {created_employee_id} '
                    f'assigned to area {new_area_id}',
                )

            except AssertionError:
                logger.error('Failed to create employee for test')
                response = areas_client.delete_area(new_area_id)
                Assert.response_status(response.status_code, 204)
                pytest.fail(
                    f'Employee creation failed, area {new_area_id} deleted',
                )

        with AllureReporting.add_step(
            f'Try to delete area {new_area_id} assigned to employee',
        ):
            response = areas_client.delete_area(new_area_id)
            AllureReporting.attach_response(
                response.status_code,
            )

        try:
            with AllureReporting.add_step('Verify conflict response'):
                Assert.response_status(response.status_code, 409)
                logger.info(
                    'Received expected 409 conflict error - '
                    'area assigned to employee',
                )
        except AssertionError:
            logger.error(
                f'Expected 409 conflict, got {response.status_code}',
            )
            pytest.fail(
                f'Expected 409 conflict error for deleting area '
                f'assigned to employee, got status {response.status_code}',
            )

        finally:
            area_deleted_flag = response.status_code == 204

            with AllureReporting.add_step(
                f'Cleanup - delete created employee {created_employee_id}',
            ):
                response = employees_client.delete_employee(
                    created_employee_id,
                )
                AllureReporting.attach_response(response.status_code)

                try:
                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Employee {created_employee_id} deleted (cleanup)',
                    )

                except AssertionError:
                    logger.error(
                        f'Employee {created_employee_id} deletion failed',
                    )
                    pytest.fail('Employee cleanup failed')

            if not area_deleted_flag:
                with AllureReporting.add_step(
                    f'Cleanup - delete created area {new_area_id}',
                ):
                    response = areas_client.delete_area(new_area_id)
                    AllureReporting.attach_response(response.status_code)

                    try:
                        Assert.response_status(
                            response.status_code, 204,
                        )
                        logger.info(f'Area {new_area_id} deleted (cleanup)')

                    except AssertionError:
                        logger.error(f'Area {new_area_id} deletion failed')
                        pytest.fail('Area cleanup failed')

        logger.info('<<< TEST PASSED')
