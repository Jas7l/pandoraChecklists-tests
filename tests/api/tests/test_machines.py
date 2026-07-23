import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(machines_client, areas_client):
    """
    Get existing test data from the system.
    """

    test_data = {
        'machine_id': None,
        'machine_name': None,
        'area_id': None,
        'status': None,
        'status_updated_at': None,
        'new_area_id': None,
    }

    logger.info('Fetching first machine from API')
    response = machines_client.get_machines_list(limit=1, offset=0)

    Assert.response_status(response.status_code, 200)

    machines = response.json()
    Assert.is_not_empty(machines)
    machine = machines[0]

    test_data['machine_id'] = machine.get('machine_id')
    test_data['machine_name'] = machine.get('machine_name')
    test_data['area_id'] = machine.get('area_id')
    test_data['status'] = machine.get('status')
    test_data['status_updated_at'] = machine.get('status_updated_at')

    logger.info(
        f'Machine loaded: ID={test_data["machine_id"]}, '
        f'Name={test_data["machine_name"]}',
    )

    logger.info('Fetching areas list for new area selection')
    areas_response = areas_client.get_areas_list(limit=10, offset=0)
    Assert.response_status(areas_response.status_code, 200)

    all_areas = areas_response.json()
    Assert.is_not_empty(all_areas)

    current_area_id = test_data['area_id']
    for area in all_areas:
        area_id = area.get('area_id')
        if area_id != current_area_id:
            test_data['new_area_id'] = area_id
            break

    if test_data['new_area_id'] is None:
        logger.error('No new area found for machine')
        pytest.fail('No new area found for machine')

    logger.info(
        f'New area selected: ID={test_data["new_area_id"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Machines API')
@pytest.mark.api
@pytest.mark.machines
class TestMachinesAPI:
    """Test suite for Machines API endpoints"""

    TEST_NAME = 'test machine'
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1
    TEST_VALID_STATUSES = ['not_checked', 'accident', 'ok']
    TEST_INVALID_STATUS = 'invalid_status'

    @pytest.fixture(scope='class')
    def test_data(self, machines_client, areas_client):
        """Fixture to get test data once for all tests"""

        data = get_test_data(machines_client, areas_client)
        return data

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get machines list')
    @pytest.mark.positive
    def test_get_machines_list(self, machines_client):

        logger.info('>>> TEST: Get machines list')

        with AllureReporting.add_step('Get machines list'):
            response = machines_client.get_machines_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                machines = response.json()
                Assert.is_not_empty(machines)
                logger.info(f'Retrieved {len(machines)} machines')
            except AssertionError:
                logger.error('Failed to get machines list')
                pytest.fail('Machines list response is empty or invalid')

        with AllureReporting.add_step('Verify machine fields'):
            machine = machines[0]

            try:
                Assert.has_key(machine, 'machine_id')
                Assert.has_key(machine, 'machine_name')
                Assert.has_key(machine, 'area_id')
                Assert.has_key(machine, 'status')
                Assert.has_key(machine, 'status_updated_at')
                logger.info(
                    f'Machine fields verified for '
                    f'ID={machine.get("machine_id")}',
                )
            except AssertionError:
                logger.error('Machine missing required fields')
                pytest.fail(
                    'Machine object missing required fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get machines list with pagination')
    @pytest.mark.positive
    def test_get_paginated_machines_list(self, machines_client, test_data):

        logger.info(
            f'>>> TEST: Get machines list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get machines list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = machines_client.get_machines_list(
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

                machines = response.json()
                Assert.is_not_empty(machines)
                logger.info(
                    f'Retrieved {len(machines)} machines with pagination',
                )

            except AssertionError:
                logger.error('Failed to get paginated machines list')
                pytest.fail(
                    'Paginated machines list response is empty or invalid',
                )

        with AllureReporting.add_step(
            'Verify pagination excludes test machine',
        ):
            try:
                Assert.less_than(len(machines), self.TEST_LIMIT + 1)

                for machine in machines:
                    Assert.not_equal(
                        machine.get('machine_id'),
                        test_data.get('machine_id'),
                    )
                    Assert.not_equal(
                        machine.get('machine_name'),
                        test_data.get('machine_name'),
                    )

                logger.info(
                    'Pagination verified: test machine '
                    f'ID={test_data.get("machine_id")} excluded',
                )

            except AssertionError:
                logger.error(
                    'Pagination failed - test machine found in results',
                )
                pytest.fail(
                    'Test machine should be excluded by offset',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get machine by id')
    @pytest.mark.positive
    def test_get_machine_by_id(self, machines_client, test_data):

        machine_id = test_data.get('machine_id')
        logger.info(f'>>> TEST: Get machine by ID={machine_id}')

        with AllureReporting.add_step(f'Get machine by ID: {machine_id}'):
            response = machines_client.get_machines_list(
                machine_id=machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machine data'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()[0]

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(
                    machine.get('machine_name'),
                    test_data.get('machine_name'),
                )
                Assert.equal(
                    machine.get('area_id'),
                    test_data.get('area_id'),
                )
                Assert.equal(
                    machine.get('status'),
                    test_data.get('status'),
                )

                logger.info(
                    f'Machine verified: ID={machine_id}, '
                    f'Name={test_data.get("machine_name")}',
                )

            except AssertionError:
                logger.error(f'Machine data mismatch for ID={machine_id}')
                pytest.fail(
                    f'Machine with ID {machine_id} not found or '
                    f'data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get machine by invalid id')
    @pytest.mark.negative
    def test_get_machine_by_invalid_id(self, machines_client):

        logger.info(
            f'>>> TEST: Get machine by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get machine by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = machines_client.get_machines_list(
                machine_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid machine ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Get machines by area_id')
    @pytest.mark.positive
    def test_get_machines_by_area_id(self, machines_client, test_data):

        area_id = test_data.get('area_id')
        logger.info(f'>>> TEST: Get machines by area_id={area_id}')

        with AllureReporting.add_step(f'Get machines by area_id={area_id}'):
            response = machines_client.get_machines_list(
                area_id=area_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machines data'):
            try:
                Assert.response_status(response.status_code, 200)

                machines = response.json()
                Assert.is_not_empty(machines)

                for machine in machines:
                    Assert.equal(machine.get('area_id'), area_id)

                logger.info(
                    f'Found {len(machines)} machines for area_id={area_id}',
                )

            except AssertionError:
                logger.error(f'No machines found for area_id={area_id}')
                pytest.fail(
                    f'Expected machines for area_id={area_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Get machines by invalid area_id')
    @pytest.mark.negative
    def test_get_machines_by_invalid_area_id(self, machines_client):

        invalid_area_id = self.TEST_INVALID_ID
        logger.info(
            f'>>> TEST: Get machines by invalid area_id={invalid_area_id}',
        )

        with AllureReporting.add_step(
            f'Get machines by invalid area_id={invalid_area_id}',
        ):
            response = machines_client.get_machines_list(
                area_id=invalid_area_id,
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

                machines = response.json()
                Assert.is_empty(machines)
                logger.info('Received empty response for invalid area_id')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'area_id={invalid_area_id}',
                )
                pytest.fail(
                    'Expected empty response for invalid area_id '
                    f'{invalid_area_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Get machines by status')
    @pytest.mark.positive
    @pytest.mark.parametrize('status', TEST_VALID_STATUSES)
    def test_get_machines_by_status(self, machines_client, status):

        logger.info(f'>>> TEST: Get machines by status="{status}"')

        with AllureReporting.add_step(f'Get machines by status="{status}"'):
            response = machines_client.get_machines_list(
                status=status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machines data'):
            try:
                Assert.response_status(response.status_code, 200)

                machines = response.json()

                for machine in machines:
                    Assert.equal(machine.get('status'), status)

                logger.info(
                    f'Found {len(machines)} machines with status="{status}"',
                )

            except AssertionError:
                logger.error(
                    f'No machines found for status="{status}"',
                )
                pytest.fail(
                    f'Expected machines for status="{status}", '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get machines list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Get machines by invalid status')
    @pytest.mark.negative
    def test_get_machines_by_invalid_status(self, machines_client):

        invalid_status = self.TEST_INVALID_STATUS
        logger.info(
            f'>>> TEST: Get machines by invalid status="{invalid_status}"',
        )

        with AllureReporting.add_step(
            f'Get machines by invalid status="{invalid_status}"',
        ):
            response = machines_client.get_machines_list(
                status=invalid_status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify error response for invalid status',
        ):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for invalid status')

            except AssertionError:
                if response.status_code == 200:
                    machines = response.json()
                    Assert.is_empty(machines)
                    logger.info('Received empty response for invalid status')
                else:
                    logger.error(
                        f'Expected 400 error, got {response.status_code}',
                    )
                    pytest.fail(
                        f'Expected 400 error for invalid status, '
                        f'got status {response.status_code}',
                    )

        logger.info('<<< TEST PASSED')

    @allure.story('Create machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Create new machine')
    @pytest.mark.positive
    def test_create_machine(self, machines_client, test_data):

        logger.info(
            f'>>> TEST: Create new machine with name="{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Create machine with name="{self.TEST_NAME}"',
        ):
            response = machines_client.create_machine(
                machine_name=self.TEST_NAME,
                area_id=test_data.get('area_id'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created machine'):
                Assert.response_status(response.status_code, 201)

                machine = response.json()

                Assert.has_key(machine, 'machine_id')
                Assert.equal(machine.get('machine_name'), self.TEST_NAME)
                Assert.equal(machine.get('area_id'), test_data.get('area_id'))
                Assert.equal(machine.get('status'), 'not_checked')
                machine_id = machine.get('machine_id')

                logger.info(
                    f'Machine created with ID: {machine_id}, '
                    f'Name: {self.TEST_NAME}',
                )

        except AssertionError:
            logger.error('Failed to create machine')
            pytest.fail(
                f'Machine creation failed for name="{self.TEST_NAME}"',
            )

        with AllureReporting.add_step(
            f'Cleanup - delete machine {machine_id}',
        ):
            response = machines_client.delete_machine(machine_id)
            AllureReporting.attach_response(response.status_code)

            Assert.response_status(response.status_code, 204)
            logger.info(f'Machine {machine_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Create machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Create machine with non-existent area')
    @pytest.mark.negative
    def test_create_machine_invalid_area(self, machines_client):

        logger.info(
            f'>>> TEST: Create machine with invalid area_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Create machine with invalid area_id={self.TEST_INVALID_ID}',
        ):
            response = machines_client.create_machine(
                machine_name=self.TEST_NAME,
                area_id=self.TEST_INVALID_ID,
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
                if response.status_code == 201:
                    machine_id = response.json().get('machine_id')
                    response = machines_client.delete_machine(machine_id)
                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Invalid machine {machine_id} deleted (cleanup)',
                    )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid area_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Delete existing machine')
    @pytest.mark.positive
    def test_delete_machine(self, machines_client, test_data):

        logger.info('>>> TEST: Delete existing machine')

        with AllureReporting.add_step(
            f'Create machine for deletion with name="{self.TEST_NAME}"',
        ):
            response = machines_client.create_machine(
                machine_name=self.TEST_NAME,
                area_id=test_data.get('area_id'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machine created'):
            try:
                Assert.response_status(response.status_code, 201)

                machine = response.json()
                machine_id = machine.get('machine_id')
                logger.info(f'Machine created with ID: {machine_id}')

            except AssertionError:
                logger.error('Failed to create machine for deletion test')
                pytest.fail('Machine creation failed for deletion test')

        with AllureReporting.add_step(f'Delete machine {machine_id}'):
            response = machines_client.delete_machine(machine_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Machine {machine_id} deleted (204 No Content)',
                )

            except AssertionError:
                logger.error(f'Machine {machine_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for machine deletion, '
                    f'got {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-012: Delete non-existent machine')
    @pytest.mark.negative
    def test_delete_machine_not_found(self, machines_client):

        logger.info(
            f'>>> TEST: Delete non-existent machine '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent machine ID={self.TEST_INVALID_ID}',
        ):
            response = machines_client.delete_machine(self.TEST_INVALID_ID)
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
                    f'Expected 404 error for non-existent machine, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-013: Patch machine name')
    @pytest.mark.positive
    def test_patch_machine_name(self, machines_client, test_data):

        machine_id = test_data.get('machine_id')
        original_name = test_data.get('machine_name')

        logger.info(
            f'>>> TEST: Patch machine ID={machine_id} name to '
            f'"{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch machine name to "{self.TEST_NAME}"',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                machine_name=self.TEST_NAME,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('machine_name'), self.TEST_NAME)

                logger.info(f'Machine name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Machine {machine_id} patch failed')
                pytest.fail(
                    f'Machine name update failed for ID={machine_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                machine_name=original_name,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('machine_name'), original_name)

                logger.info(f'Machine name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original machine name')
                pytest.fail(
                    f'Failed to restore original name for machine '
                    f'ID={machine_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-014: Patch machine area')
    @pytest.mark.positive
    def test_patch_machine_area(self, machines_client, test_data):

        machine_id = test_data.get('machine_id')
        original_area_id = test_data.get('area_id')
        new_area_id = test_data.get('new_area_id')

        logger.info(
            f'>>> TEST: Patch machine ID={machine_id} area to '
            f'area_id={new_area_id}',
        )

        with AllureReporting.add_step(
            f'Patch machine area to area_id={new_area_id}',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                area_id=new_area_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('area_id'), new_area_id)

                logger.info(f'Machine area updated to: {new_area_id}')

            except AssertionError:
                logger.error(f'Machine {machine_id} patch failed')
                pytest.fail(
                    f'Machine area update failed for ID={machine_id}',
                )

        with AllureReporting.add_step(
            f'Restore original area_id={original_area_id}',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                area_id=original_area_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('area_id'), original_area_id)

                logger.info(f'Machine area restored to: {original_area_id}')

            except AssertionError:
                logger.error('Failed to restore original area')
                pytest.fail(
                    f'Failed to restore original area for machine '
                    f'ID={machine_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-015: Patch machine status')
    @pytest.mark.parametrize('status', TEST_VALID_STATUSES)
    @pytest.mark.positive
    def test_patch_machine_status(self, machines_client, test_data, status):

        machine_id = test_data.get('machine_id')
        original_status = test_data.get('status')

        logger.info(
            f'>>> TEST: Patch machine ID={machine_id} status to '
            f'"{status}"',
        )

        with AllureReporting.add_step(
            f'Patch machine status to "{status}"',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                status=status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('status'), status)

                new_status_updated_at = machine.get('status_updated_at')
                Assert.is_not_none(new_status_updated_at)
                Assert.not_equal(
                    new_status_updated_at,
                    test_data.get('status_updated_at'),
                )

                logger.info(f'Machine status updated to: "{status}"')

            except AssertionError:
                logger.error(f'Machine {machine_id} patch failed')
                pytest.fail(
                    f'Machine status update failed for ID={machine_id}',
                )

        with AllureReporting.add_step(
            f'Restore original status "{original_status}"',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                status=original_status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                machine = response.json()

                Assert.equal(machine.get('machine_id'), machine_id)
                Assert.equal(machine.get('status'), original_status)

                logger.info(f'Machine status restored to: "{original_status}"')

            except AssertionError:
                logger.error('Failed to restore original status')
                pytest.fail(
                    f'Failed to restore original status for machine '
                    f'ID={machine_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-016: Patch machine with invalid status')
    @pytest.mark.negative
    def test_patch_machine_invalid_status(self, machines_client, test_data):

        machine_id = test_data.get('machine_id')
        original_status = test_data.get('status')

        logger.info(
            f'>>> TEST: Patch machine ID={machine_id} with invalid '
            f'status "{self.TEST_INVALID_STATUS}"',
        )

        with AllureReporting.add_step(
            f'Patch machine with invalid status "{self.TEST_INVALID_STATUS}"',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                status=self.TEST_INVALID_STATUS,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for invalid status')

            except AssertionError:
                if response.status_code == 200:
                    response = machines_client.patch_machine(
                        machine_id=machine_id,
                        status=original_status,
                    )
                    Assert.response_status(response.status_code, 200)
                    logger.info(
                        f'Machine status restored to: {original_status}',
                    )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for invalid status, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch machine')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-017: Patch machine with non-existent area')
    @pytest.mark.negative
    def test_patch_machine_invalid_area(self, machines_client, test_data):

        machine_id = test_data.get('machine_id')
        original_area_id = test_data.get('area_id')

        logger.info(
            f'>>> TEST: Patch machine ID={machine_id} with invalid '
            f'area_id={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Patch machine with invalid area_id={self.TEST_INVALID_ID}',
        ):
            response = machines_client.patch_machine(
                machine_id=machine_id,
                area_id=self.TEST_INVALID_ID,
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
                    machines_client.patch_machine(
                        machine_id=machine_id,
                        area_id=original_area_id,
                    )
                    logger.info(
                        f'Machine area restored to: {original_area_id}',
                    )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid area_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')
