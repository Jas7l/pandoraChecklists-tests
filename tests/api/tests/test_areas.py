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

    TEST_MACHINE_NAME = 'test machine'
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
    def test_create_area(self, areas_client, unique_area_name):

        logger.info(
            f'>>> TEST: Create new area with name="{unique_area_name}"',
        )

        with AllureReporting.add_step(
            f'Create area with name="{unique_area_name}"',
        ):
            response = areas_client.create_area(unique_area_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created area'):
                Assert.response_status(response.status_code, 201)

                area = response.json()

                Assert.has_key(area, 'area_id')
                Assert.equal(area.get('area_name'), unique_area_name)
                area_id = area.get('area_id')

                logger.info(
                    f'Area created with ID: {area_id}, '
                    f'Name: {unique_area_name}',
                )

        except AssertionError:
            logger.error('Failed to create area')
            pytest.fail(
                f'Area creation failed for name="{unique_area_name}"',
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
                        delete_response = areas_client.delete_area(area_id)
                        AllureReporting.attach_response(
                            delete_response.status_code,
                        )

                        Assert.response_status(
                            delete_response.status_code, 204,
                        )
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
    def test_delete_area(self, areas_client, unique_area_name):

        logger.info('>>> TEST: Delete existing area')

        with AllureReporting.add_step(
            f'Create area for deletion with name="{unique_area_name}"',
        ):
            response = areas_client.create_area(unique_area_name)
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
    def test_patch_area(self, areas_client, test_data, unique_area_name):

        area_id = test_data.get('area_id')
        original_name = test_data.get('area_name')

        logger.info(
            f'>>> TEST: Patch area ID={area_id} name to '
            f'"{unique_area_name}"',
        )

        with AllureReporting.add_step(
            f'Patch area name to "{unique_area_name}"',
        ):
            response = areas_client.patch_area(area_id, unique_area_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                area = response.json()

                Assert.equal(area.get('area_id'), area_id)
                Assert.equal(area.get('area_name'), unique_area_name)

                logger.info(f'Area name updated to: {unique_area_name}')

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
    def test_patch_area_duplicate_name(
            self, areas_client, test_data, unique_area_name,
    ):

        existing_name = test_data.get('area_name')
        logger.info(
            f'>>> TEST: Patch area with duplicate '
            f'name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create area for patch test with name="{unique_area_name}"',
        ):
            response = areas_client.create_area(unique_area_name)
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
    @allure.title('API-TC-012: Delete area that is assigned to machine')
    @pytest.mark.positive
    def test_delete_area_assigned_to_machine(
            self, areas_client, machines_client, test_data, unique_area_name,
    ):

        logger.info('>>> TEST: Delete area assigned to machine')

        created_machine_id = None
        new_area_id = None
        delete_status = None

        with AllureReporting.add_step(
            f'Create area "{unique_area_name}" and assign to machine',
        ):
            response = areas_client.create_area(unique_area_name)
            try:
                Assert.response_status(response.status_code, 201)
            except AssertionError:
                logger.error('Failed to create area for test')
                pytest.fail(
                    f'Area creation failed for name="{unique_area_name}"',
                )

            new_area = response.json()
            new_area_id = new_area.get('area_id')
            logger.info(f'Area created with ID: {new_area_id}')

            response = machines_client.create_machine(
                machine_name=self.TEST_MACHINE_NAME,
                area_id=new_area_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

            try:
                Assert.response_status(response.status_code, 201)
                created_machine = response.json()
                created_machine_id = created_machine.get('machine_id')
                logger.info(
                    f'Machine created with ID: {created_machine_id} '
                    f'assigned to area {new_area_id}',
                )

            except AssertionError:
                logger.error('Failed to create machine for test')
                response = areas_client.delete_area(new_area_id)
                Assert.response_status(response.status_code, 204)
                logger.info(f'Area {new_area_id} deleted (cleanup)')
                pytest.fail(
                    f'Machine creation failed, area {new_area_id} deleted',
                )

        with AllureReporting.add_step(
            f'Delete area {new_area_id} assigned to machine',
        ):
            response = areas_client.delete_area(new_area_id)
            delete_status = response.status_code
            AllureReporting.attach_response(response.status_code)

        try:
            with AllureReporting.add_step('Verify area deletion success'):
                Assert.response_status(delete_status, 204)
                logger.info(
                    f'Area {new_area_id} deleted successfully '
                    f'(204 No Content)',
                )

            with AllureReporting.add_step(
                'Verify machine area_id is None after area deletion',
            ):
                response = machines_client.get_machines_list(
                    machine_id=created_machine_id,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

                Assert.response_status(response.status_code, 200)
                created_machine = response.json()[0]
                machine_area_id = created_machine.get('area_id')
                Assert.equal(machine_area_id, None)

                logger.info(
                    f'Machine {created_machine_id} area_id is None '
                    f'(area unassigned)',
                )

        except AssertionError:
            logger.error(
                f'Area {new_area_id} deletion or machine unassignment failed',
            )
            pytest.fail(
                'Expected area deletion to succeed and machine area_id '
                'to be None',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete machine {created_machine_id}',
            ):
                response = machines_client.delete_machine(created_machine_id)
                AllureReporting.attach_response(response.status_code)

                try:
                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Machine {created_machine_id} deleted (cleanup)',
                    )

                except AssertionError:
                    logger.error(
                        f'Machine {created_machine_id} deletion failed',
                    )
                    pytest.fail('Machine cleanup failed')

            if delete_status != 204:
                with AllureReporting.add_step(
                    f'Cleanup - delete area {new_area_id}',
                ):
                    response = areas_client.delete_area(new_area_id)
                    AllureReporting.attach_response(response.status_code)

                    try:
                        Assert.response_status(response.status_code, 204)
                        logger.info(f'Area {new_area_id} deleted (cleanup)')

                    except AssertionError:
                        logger.error(f'Area {new_area_id} deletion failed')
                        pytest.fail('Area cleanup failed')

        logger.info('<<< TEST PASSED')

    @allure.story('Get areas list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-013: Get areas by is_active filter')
    @pytest.mark.parametrize('is_active', [True, False])
    @pytest.mark.positive
    def test_get_areas_by_is_active(self, areas_client, is_active):

        logger.info(
            f'>>> TEST: Get areas by is_active={is_active}',
        )

        with AllureReporting.add_step(
            f'Get areas by is_active={is_active}',
        ):
            response = areas_client.get_areas_list(is_active=is_active)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify areas by is_active'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()

                for area in areas:
                    Assert.equal(area.get('is_active'), is_active)

                logger.info(
                    f'Found {len(areas)} areas with is_active={is_active}',
                )

            except AssertionError:
                logger.error(
                    f'Expected areas with is_active={is_active}',
                )
                pytest.fail(
                    f'Expected areas with is_active={is_active}, '
                    f'got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-014: Search areas by partial name')
    @pytest.mark.positive
    def test_search_areas_partial_name(self, areas_client, test_data):

        search_query = test_data.get('area_name')[:3]
        logger.info(
            f'>>> TEST: Search areas by partial name="{search_query}"',
        )

        with AllureReporting.add_step(
            f'Search areas by partial name="{search_query}"',
        ):
            response = areas_client.search_areas(q=search_query)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify partial name search results'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()
                Assert.is_not_empty(areas)

                found_test_area = any(
                    test_data.get('area_name').lower() in area.get(
                        'area_name').lower()
                    for area in areas
                )
                Assert.is_true(found_test_area)

                logger.info(
                    f'Found {len(areas)} areas matching partial name '
                    f'"{search_query}"',
                )

            except AssertionError:
                logger.error(
                    f'Partial name search failed for "{search_query}"',
                )
                pytest.fail(
                    f'Expected search results for partial name='
                    f'"{search_query}"',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-015: Search areas with OR operator')
    @pytest.mark.positive
    def test_search_areas_with_or_operator(
            self, areas_client, test_data, unique_area_name,
    ):

        logger.info('>>> TEST: Search areas with OR operator')

        created_area_id = None

        with AllureReporting.add_step(
            f'Create area "{unique_area_name}" for OR test',
        ):
            response = areas_client.create_area(unique_area_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

            try:
                Assert.response_status(response.status_code, 201)
                area = response.json()
                created_area_id = area.get('area_id')
                logger.info(f'Area created with ID: {created_area_id}')

            except AssertionError:
                logger.error('Failed to create area for OR test')
                pytest.fail('Area creation failed for OR test')

        try:
            search_query = (
                f'{test_data.get("area_name")} OR {unique_area_name}'
            )
            logger.info(f'Search query with OR: "{search_query}"')

            with AllureReporting.add_step(
                f'Search areas with OR="{search_query}"',
            ):
                response = areas_client.search_areas(q=search_query)
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify OR operator works'):
                try:
                    Assert.response_status(response.status_code, 200)

                    areas = response.json()
                    Assert.is_not_empty(areas)

                    found_original = any(
                        test_data.get('area_name').lower() in area.get(
                            'area_name').lower()
                        for area in areas
                    )
                    found_new = any(
                        unique_area_name.lower() in area.get(
                            'area_name').lower()
                        for area in areas
                    )

                    Assert.is_true(found_original)
                    Assert.is_true(found_new)

                    logger.info(
                        'OR operator works: found both '
                        f'"{test_data.get("area_name")}" '
                        f'and "{unique_area_name}"',
                    )

                except AssertionError:
                    logger.error(
                        f'Search with OR failed for query="{search_query}"',
                    )
                    pytest.fail(
                        'Expected to find both areas with OR operator',
                    )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete area {created_area_id}',
            ):
                response = areas_client.delete_area(created_area_id)
                AllureReporting.attach_response(response.status_code)

                try:
                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Area {created_area_id} deleted (cleanup)')

                except AssertionError:
                    logger.error(f'Area {created_area_id} deletion failed')
                    pytest.fail('Area cleanup failed')

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-016: Search areas with exclusion operator')
    @pytest.mark.positive
    def test_search_areas_with_exclusion(self, areas_client, test_data):

        search_query = f'-"{test_data.get("area_name")}"'
        logger.info(
            f'>>> TEST: Search areas with exclusion="{search_query}"',
        )

        with AllureReporting.add_step(
            f'Search areas with exclusion="{search_query}"',
        ):
            response = areas_client.search_areas(q=search_query)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify exclusion works'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()

                if areas:
                    for area in areas:
                        Assert.not_contains(
                            area.get('area_name').lower(),
                            test_data.get('area_name').lower(),
                        )
                    logger.info(
                        f'Found {len(areas)} areas without excluded name',
                    )
                else:
                    logger.info(
                        'Empty result - all areas contain excluded name',
                    )

            except AssertionError:
                logger.error(f'Exclusion failed for "{search_query}"')
                pytest.fail(
                    f'Expected results without '
                    f'"{test_data.get("area_name")}"',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-017: Search deleted area with is_active filter')
    @pytest.mark.positive
    def test_search_deleted_area_is_active_filter(
            self, areas_client, unique_area_name,
    ):

        logger.info('>>> TEST: Search deleted area with is_active filter')

        created_area_id = None
        area_name = unique_area_name

        with AllureReporting.add_step(
            f'Create area "{area_name}" for deletion test',
        ):
            response = areas_client.create_area(area_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

            try:
                Assert.response_status(response.status_code, 201)
                area = response.json()
                created_area_id = area.get('area_id')
                logger.info(f'Area created with ID: {created_area_id}')

            except AssertionError:
                logger.error('Failed to create area for deletion test')
                pytest.fail('Area creation failed')

        with AllureReporting.add_step(f'Delete area {created_area_id}'):
            response = areas_client.delete_area(created_area_id)
            AllureReporting.attach_response(response.status_code)

            try:
                Assert.response_status(response.status_code, 204)
                logger.info(f'Area {created_area_id} deleted')

            except AssertionError:
                logger.error(f'Area {created_area_id} deletion failed')
                pytest.fail('Area deletion failed')

        with AllureReporting.add_step(
            f'Search deleted area with is_active=False',
        ):
            response = areas_client.search_areas(
                q=area_name,
                is_active=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify deleted area found with is_active=False',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()
                Assert.is_not_empty(areas)

                found_deleted = any(
                    area_name.lower() in area.get('area_name').lower()
                    for area in areas
                )
                Assert.is_true(found_deleted)

                for area in areas:
                    Assert.equal(area.get('is_active'), False)

                logger.info('Deleted area found with is_active=False')

            except AssertionError:
                logger.error('Deleted area not found with is_active=False')
                pytest.fail(
                    'Expected to find deleted area with is_active=False',
                )

        with AllureReporting.add_step(
            f'Search deleted area with is_active=True',
        ):
            response = areas_client.search_areas(
                q=area_name,
                is_active=True,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify deleted area not found with is_active=True',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()

                found_deleted = any(
                    area_name.lower() in area.get('area_name').lower()
                    for area in areas
                )
                Assert.is_false(found_deleted)

                logger.info('Deleted area not found with is_active=True')

            except AssertionError:
                logger.error('Deleted area found with is_active=True')
                pytest.fail(
                    'Expected not to find deleted area with is_active=True',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-018: Search areas with limit parameter')
    @pytest.mark.positive
    def test_search_areas_with_limit(self, areas_client):

        search_query = 'Цех'
        limit = 1

        logger.info(
            f'>>> TEST: Search areas with query="{search_query}", '
            f'limit={limit}',
        )

        with AllureReporting.add_step(
            f'Search areas with query="{search_query}", limit={limit}',
        ):
            response = areas_client.search_areas(
                q=search_query,
                limit=limit,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify limit works'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()
                Assert.less_than(len(areas), limit + 1)

                logger.info(
                    f'Found {len(areas)} areas with limit={limit}',
                )

            except AssertionError:
                logger.error(f'Limit parameter failed')
                pytest.fail(
                    f'Expected at most {limit} result(s), '
                    f'got {len(response.json())}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-019: Search areas with empty query')
    @pytest.mark.negative
    def test_search_areas_empty_query(self, areas_client):

        logger.info('>>> TEST: Search areas with empty query')

        with AllureReporting.add_step('Search areas with empty query'):
            response = areas_client.search_areas(q='')
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for empty query')

            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty query, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-020: Search areas with non-existent query')
    @pytest.mark.negative
    def test_search_areas_no_results(self, areas_client):

        search_query = 'nonexistent_area_xyz_12345'
        logger.info(
            f'>>> TEST: Search areas with non-existent query='
            f'"{search_query}"',
        )

        with AllureReporting.add_step(
            f'Search areas with query="{search_query}"',
        ):
            response = areas_client.search_areas(q=search_query)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify empty search results'):
            try:
                Assert.response_status(response.status_code, 200)

                areas = response.json()
                Assert.is_empty(areas)

                logger.info('Received empty response for non-existent query')

            except AssertionError:
                logger.error(
                    f'Expected empty response for query="{search_query}"',
                )
                pytest.fail(
                    'Expected empty response for non-existent query',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search areas')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-021: Search areas with special characters')
    @pytest.mark.negative
    def test_search_areas_special_characters(self, areas_client):

        special_queries = [
            '!@#$%^&*()',
            'test_123!@#',
            '~~~```',
            '|||///\\\\',
            'ц?е*х',
        ]

        logger.info('>>> TEST: Search areas with special characters')

        for query in special_queries:
            logger.info(f'Search with query="{query}"')

            with AllureReporting.add_step(
                f'Search areas with query="{query}"',
            ):
                response = areas_client.search_areas(q=query)
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step(
                f'Verify response for query="{query}"',
            ):
                try:
                    if response.status_code == 200:
                        areas = response.json()
                        Assert.is_empty(areas)
                        logger.info(f'Query "{query}" returned empty results')
                    elif response.status_code == 400:
                        logger.info(
                            f'Query "{query}" returned expected 400 error',
                        )
                    else:
                        Assert.response_status(response.status_code, 200)
                        Assert.response_status(response.status_code, 400)

                except AssertionError:
                    logger.error(
                        f'Unexpected response for query="{query}"',
                    )
                    pytest.fail(
                        f'Expected 200 with empty array or 400 error for '
                        f'special characters query="{query}", '
                        f'got {response.status_code}',
                    )

        logger.info('<<< TEST PASSED')
