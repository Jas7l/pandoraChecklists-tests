import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(positions_client):
    """
    Get existing test data from the system.
    """

    test_data = {
        'position_id': None,
        'position_name': None,
    }

    logger.info('Fetching first position from API')
    response = positions_client.get_positions_list(limit=1, offset=0)

    Assert.response_status(response.status_code, 200)

    positions = response.json()
    Assert.is_not_empty(positions)
    position = positions[0]

    test_data['position_id'] = position.get('position_id')
    test_data['position_name'] = position.get('position_name')

    logger.info(
        f'Position loaded: ID={test_data["position_id"]}, '
        f'Name={test_data["position_name"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Positions API')
@pytest.mark.api
@pytest.mark.positions
class TestPositionsAPI:
    """Test suite for Positions API endpoints"""

    TEST_NAME = 'test position'
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1

    @pytest.fixture(scope='class')
    def test_data(self, positions_client):
        """Fixture to get test data once for all tests"""

        data = get_test_data(positions_client)
        return data

    @allure.story('Get positions list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get positions list')
    @pytest.mark.positive
    def test_get_positions_list(self, positions_client):

        logger.info('>>> TEST: Get positions list')

        with AllureReporting.add_step('Get positions list'):
            response = positions_client.get_positions_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                positions = response.json()
                Assert.is_not_empty(positions)
                logger.info(f'Retrieved {len(positions)} positions')
            except AssertionError:
                logger.error('Failed to get positions list')
                pytest.fail('Positions list response is empty or invalid')

        with AllureReporting.add_step('Verify position fields'):
            position = positions[0]

            try:
                Assert.has_key(position, 'position_id')
                Assert.has_key(position, 'position_name')
                logger.info(
                    f'Position fields verified for '
                    f'ID={position.get("position_id")}',
                )
            except AssertionError:
                logger.error('Position missing required fields')
                pytest.fail(
                    'Position object missing position_id or '
                    'position_name fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get positions list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get positions list with pagination')
    @pytest.mark.positive
    def test_get_paginated_positions_list(self, positions_client, test_data):

        logger.info(
            f'>>> TEST: Get positions list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get positions list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = positions_client.get_positions_list(
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

                positions = response.json()
                Assert.is_not_empty(positions)
                logger.info(
                    f'Retrieved {len(positions)} positions with pagination',
                )

            except AssertionError:
                logger.error('Failed to get paginated positions list')
                pytest.fail(
                    'Paginated positions list response is empty or invalid',
                )

        with AllureReporting.add_step(
            'Verify pagination excludes test position',
        ):
            try:
                Assert.less_than(len(positions), self.TEST_LIMIT + 1)

                for position in positions:
                    Assert.not_equal(
                        position.get('position_id'),
                        test_data.get('position_id'),
                    )
                    Assert.not_equal(
                        position.get('position_name'),
                        test_data.get('position_name'),
                    )

                logger.info(
                    'Pagination verified: test position '
                    f'ID={test_data.get("position_id")} excluded',
                )

            except AssertionError:
                logger.error(
                    'Pagination failed - test position found in results',
                )
                pytest.fail(
                    'Test position should be excluded by offset',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get positions list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get position by id')
    @pytest.mark.positive
    def test_get_position_by_id(self, positions_client, test_data):

        position_id = test_data.get('position_id')
        logger.info(f'>>> TEST: Get position by ID={position_id}')

        with AllureReporting.add_step(f'Get position by ID: {position_id}'):
            response = positions_client.get_positions_list(p_id=position_id)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify position data'):
            try:
                Assert.response_status(response.status_code, 200)

                position = response.json()[0]

                Assert.equal(position.get('position_id'), position_id)
                Assert.equal(
                    position.get('position_name'),
                    test_data.get('position_name'),
                )

                logger.info(
                    f'Position verified: ID={position_id}, '
                    f'Name={test_data.get("position_name")}',
                )

            except AssertionError:
                logger.error(f'Position data mismatch for ID={position_id}')
                pytest.fail(
                    f'Position with ID {position_id} not found or '
                    f'data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get positions list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get position by invalid id')
    @pytest.mark.negative
    def test_get_position_by_invalid_id(self, positions_client):

        logger.info(
            f'>>> TEST: Get position by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get position by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = positions_client.get_positions_list(
                p_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid position ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Create new position')
    @pytest.mark.positive
    def test_create_position(self, positions_client):

        logger.info(
            f'>>> TEST: Create new position with name="{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Create position with name="{self.TEST_NAME}"',
        ):
            response = positions_client.create_position(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created position'):
                Assert.response_status(response.status_code, 201)

                position = response.json()

                Assert.has_key(position, 'position_id')
                Assert.equal(position.get('position_name'), self.TEST_NAME)
                position_id = position.get('position_id')

                logger.info(
                    f'Position created with ID: {position_id}, '
                    f'Name: {self.TEST_NAME}',
                )

        except AssertionError:
            logger.error('Failed to create position')
            pytest.fail(
                f'Position creation failed for name="{self.TEST_NAME}"',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete position {position_id}',
            ):
                response = positions_client.delete_position(position_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Position {position_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Create position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Create position with duplicate name')
    @pytest.mark.negative
    def test_create_position_duplicate_name(self, positions_client, test_data):

        existing_name = test_data.get('position_name')
        logger.info(
            f'>>> TEST: Create position with duplicate '
            f'name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create position with duplicate name="{existing_name}"',
        ):
            response = positions_client.create_position(existing_name)
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
                        'Delete invalid duplicate position',
                    ):
                        position_id = response.json().get('position_id')
                        response = positions_client.delete_position(
                            position_id,
                        )
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid duplicate position {position_id} '
                            f'deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for duplicate name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Create position with empty name')
    @pytest.mark.negative
    def test_create_position_empty_name(self, positions_client):

        logger.info('>>> TEST: Create position with empty name')

        with AllureReporting.add_step('Create position with empty name'):
            response = positions_client.create_position('')
            AllureReporting.attach_response(
                response.status_code,
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for empty name')

            except AssertionError:
                if response.status_code == 201:
                    with AllureReporting.add_step(
                        'Delete invalid position with empty name',
                    ):
                        position_id = response.json().get('position_id')
                        response = positions_client.delete_position(
                            position_id,
                        )
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid position {position_id} with empty '
                            f'name deleted',
                        )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Delete existing position')
    @pytest.mark.positive
    def test_delete_position(self, positions_client):

        logger.info('>>> TEST: Delete existing position')

        with AllureReporting.add_step(
            f'Create position for deletion with name="{self.TEST_NAME}"',
        ):
            response = positions_client.create_position(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify position created'):
            try:
                Assert.response_status(response.status_code, 201)

                position = response.json()
                position_id = position.get('position_id')
                logger.info(f'Position created with ID: {position_id}')

            except AssertionError:
                logger.error('Failed to create position for deletion test')
                pytest.fail('Position creation failed for deletion test')

        with AllureReporting.add_step(f'Delete position {position_id}'):
            response = positions_client.delete_position(position_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Position {position_id} deleted (204 No Content)',
                )

            except AssertionError:
                logger.error(f'Position {position_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for position deletion, '
                    f'got {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Delete non-existent position')
    @pytest.mark.negative
    def test_delete_position_not_found(self, positions_client):

        logger.info(
            f'>>> TEST: Delete non-existent position '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent position ID={self.TEST_INVALID_ID}',
        ):
            response = positions_client.delete_position(
                self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
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
                    f'Expected 404 error for non-existent position, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Patch position name')
    @pytest.mark.positive
    def test_patch_position(self, positions_client, test_data):

        position_id = test_data.get('position_id')
        original_name = test_data.get('position_name')

        logger.info(
            f'>>> TEST: Patch position ID={position_id} name to '
            f'"{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch position name to "{self.TEST_NAME}"',
        ):
            response = positions_client.patch_position(
                position_id, self.TEST_NAME,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                position = response.json()

                Assert.equal(position.get('position_id'), position_id)
                Assert.equal(position.get('position_name'), self.TEST_NAME)

                logger.info(f'Position name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Position {position_id} patch failed')
                pytest.fail(
                    f'Position name update failed for ID={position_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = positions_client.patch_position(
                position_id,
                original_name,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                position = response.json()

                Assert.equal(position.get('position_id'), position_id)
                Assert.equal(position.get('position_name'), original_name)

                logger.info(f'Position name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original position name')
                pytest.fail(
                    f'Failed to restore original name for position '
                    f'ID={position_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch position')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Patch position with duplicate name')
    @pytest.mark.negative
    def test_patch_position_duplicate_name(self, positions_client, test_data):

        existing_name = test_data.get('position_name')
        logger.info(
            f'>>> TEST: Patch position with duplicate '
            f'name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create position for patch test with name="{self.TEST_NAME}"',
        ):
            response = positions_client.create_position(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify position created'):
            try:
                Assert.response_status(response.status_code, 201)

                position = response.json()
                position_id = position.get('position_id')
                logger.info(f'Position created with ID: {position_id}')

            except AssertionError:
                logger.error('Failed to create position for patch test')
                pytest.fail(
                    'Position creation failed for patch duplicate test',
                )

        try:
            with AllureReporting.add_step(
                f'Try to patch with duplicate name="{existing_name}"',
            ):
                response = positions_client.patch_position(
                    position_id,
                    existing_name,
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
                f'Cleanup - delete created position {position_id}',
            ):
                response = positions_client.delete_position(position_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Position {position_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')
