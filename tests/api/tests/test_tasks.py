import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(tasks_client):
    """
    Get existing test data from the system.
    """

    test_data = {
        'task_id': None,
        'task_name': None,
    }

    logger.info('Fetching first task from API')
    response = tasks_client.get_tasks_list(limit=1, offset=0)

    Assert.response_status(response.status_code, 200)

    tasks = response.json()
    Assert.is_not_empty(tasks)
    task = tasks[0]

    test_data['task_id'] = task.get('task_id')
    test_data['task_name'] = task.get('task_name')

    logger.info(
        f'Task loaded: ID={test_data["task_id"]}, '
        f'Name={test_data["task_name"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Tasks API')
@pytest.mark.api
@pytest.mark.tasks
class TestTasksAPI:
    """Test suite for Tasks API endpoints"""

    TEST_NAME = 'test task'
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1

    @pytest.fixture(scope='class')
    def test_data(self, tasks_client):
        """Fixture to get test data once for all tests"""

        data = get_test_data(tasks_client)
        return data

    @allure.story('Get tasks list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get tasks list')
    @pytest.mark.positive
    def test_get_tasks_list(self, tasks_client):

        logger.info('>>> TEST: Get tasks list')

        with AllureReporting.add_step('Get tasks list'):
            response = tasks_client.get_tasks_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                tasks = response.json()
                Assert.is_not_empty(tasks)
                logger.info(f'Retrieved {len(tasks)} tasks')
            except AssertionError:
                logger.error('Failed to get tasks list')
                pytest.fail('Tasks list response is empty or invalid')

        with AllureReporting.add_step('Verify task fields'):
            task = tasks[0]

            try:
                Assert.has_key(task, 'task_id')
                Assert.has_key(task, 'task_name')
                logger.info(
                    f'Task fields verified for ID={task.get("task_id")}',
                )
            except AssertionError:
                logger.error('Task missing required fields')
                pytest.fail(
                    'Task object missing task_id or task_name fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get tasks list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get tasks list with pagination')
    @pytest.mark.positive
    def test_get_paginated_tasks_list(self, tasks_client, test_data):

        logger.info(
            f'>>> TEST: Get tasks list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get tasks list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = tasks_client.get_tasks_list(
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

                tasks = response.json()
                Assert.is_not_empty(tasks)
                logger.info(
                    f'Retrieved {len(tasks)} tasks with pagination',
                )

            except AssertionError:
                logger.error('Failed to get paginated tasks list')
                pytest.fail(
                    'Paginated tasks list response is empty or invalid',
                )

        with AllureReporting.add_step(
            'Verify pagination excludes test task',
        ):
            try:
                Assert.less_than(len(tasks), self.TEST_LIMIT + 1)

                for task in tasks:
                    Assert.not_equal(
                        task.get('task_id'),
                        test_data.get('task_id'),
                    )
                    Assert.not_equal(
                        task.get('task_name'),
                        test_data.get('task_name'),
                    )

                logger.info(
                    'Pagination verified: test task '
                    f'ID={test_data.get("task_id")} excluded',
                )

            except AssertionError:
                logger.error(
                    'Pagination failed - test task found in results',
                )
                pytest.fail(
                    'Test task should be excluded by offset',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get tasks list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get task by id')
    @pytest.mark.positive
    def test_get_task_by_id(self, tasks_client, test_data):

        task_id = test_data.get('task_id')
        logger.info(f'>>> TEST: Get task by ID={task_id}')

        with AllureReporting.add_step(f'Get task by ID: {task_id}'):
            response = tasks_client.get_tasks_list(task_id=task_id)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify task data'):
            try:
                Assert.response_status(response.status_code, 200)

                task = response.json()[0]

                Assert.equal(task.get('task_id'), task_id)
                Assert.equal(
                    task.get('task_name'),
                    test_data.get('task_name'),
                )

                logger.info(
                    f'Task verified: ID={task_id}, '
                    f'Name={test_data.get("task_name")}',
                )

            except AssertionError:
                logger.error(f'Task data mismatch for ID={task_id}')
                pytest.fail(
                    f'Task with ID {task_id} not found or data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get tasks list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get task by invalid id')
    @pytest.mark.negative
    def test_get_task_by_invalid_id(self, tasks_client):

        logger.info(
            f'>>> TEST: Get task by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get task by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = tasks_client.get_tasks_list(
                task_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid task ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Create new task')
    @pytest.mark.positive
    def test_create_task(self, tasks_client):

        logger.info(
            f'>>> TEST: Create new task with name="{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Create task with name="{self.TEST_NAME}"',
        ):
            response = tasks_client.create_task(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify created task'):
            try:
                Assert.response_status(response.status_code, 201)
            except AssertionError:
                logger.error('Failed to create task')
                pytest.fail(
                    f'Task creation failed for name="{self.TEST_NAME}"',
                )

            task = response.json()

            try:
                Assert.has_key(task, 'task_id')
                Assert.equal(task.get('task_name'), self.TEST_NAME)
                task_id = task.get('task_id')
                logger.info(
                    f'Task created with ID: {task_id}, '
                    f'Name: {self.TEST_NAME}',
                )

            except AssertionError:
                logger.error('Created task missing required fields')
                pytest.fail(
                    'Created task missing task_id or has invalid name',
                )

        with AllureReporting.add_step(
            f'Cleanup - delete task {task_id}',
        ):
            response = tasks_client.delete_task(task_id)
            AllureReporting.attach_response(response.status_code)

            try:
                Assert.response_status(response.status_code, 204)
                logger.info(f'Task {task_id} deleted (cleanup)')
            except AssertionError:
                logger.error(f'Task {task_id} deletion failed')
                pytest.fail(
                    f'Task {task_id} deletion failed during cleanup',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Create task with duplicate name')
    @pytest.mark.negative
    def test_create_task_duplicate_name(self, tasks_client, test_data):

        existing_name = test_data.get('task_name')
        logger.info(
            f'>>> TEST: Create task with duplicate name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create task with duplicate name="{existing_name}"',
        ):
            response = tasks_client.create_task(existing_name)
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
                        'Delete invalid duplicate task',
                    ):
                        task_id = response.json().get('task_id')
                        response = tasks_client.delete_task(task_id)
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid duplicate task {task_id} deleted',
                        )

                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for duplicate name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Create task with empty name')
    @pytest.mark.negative
    def test_create_task_empty_name(self, tasks_client):

        logger.info('>>> TEST: Create task with empty name')

        with AllureReporting.add_step('Create task with empty name'):
            response = tasks_client.create_task('')
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
                    with AllureReporting.add_step(
                        'Delete invalid task with empty name',
                    ):
                        task_id = response.json().get('task_id')
                        response = tasks_client.delete_task(task_id)
                        AllureReporting.attach_response(
                            response.status_code,
                        )

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Invalid task {task_id} with empty name deleted',
                        )

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for empty name, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Delete existing task')
    @pytest.mark.positive
    def test_delete_task(self, tasks_client):

        logger.info('>>> TEST: Delete existing task')

        with AllureReporting.add_step(
            f'Create task for deletion with name="{self.TEST_NAME}"',
        ):
            response = tasks_client.create_task(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify task created'):
            try:
                Assert.response_status(response.status_code, 201)

                task = response.json()
                task_id = task.get('task_id')
                logger.info(f'Task created with ID: {task_id}')

            except AssertionError:
                logger.error('Failed to create task for deletion test')
                pytest.fail('Task creation failed for deletion test')

        with AllureReporting.add_step(f'Delete task {task_id}'):
            response = tasks_client.delete_task(task_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(f'Task {task_id} deleted (204 No Content)')

            except AssertionError:
                logger.error(f'Task {task_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for task deletion, '
                    f'got {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Delete non-existent task')
    @pytest.mark.negative
    def test_delete_task_not_found(self, tasks_client):

        logger.info(
            f'>>> TEST: Delete non-existent task ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent task ID={self.TEST_INVALID_ID}',
        ):
            response = tasks_client.delete_task(self.TEST_INVALID_ID)
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
                    f'Expected 404 error for non-existent task, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Patch task name')
    @pytest.mark.positive
    def test_patch_task(self, tasks_client, test_data):

        task_id = test_data.get('task_id')
        original_name = test_data.get('task_name')

        logger.info(
            f'>>> TEST: Patch task ID={task_id} name to "{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch task name to "{self.TEST_NAME}"',
        ):
            response = tasks_client.patch_task(task_id, self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                task = response.json()

                Assert.equal(task.get('task_id'), task_id)
                Assert.equal(task.get('task_name'), self.TEST_NAME)

                logger.info(f'Task name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Task {task_id} patch failed')
                pytest.fail(
                    f'Task name update failed for ID={task_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = tasks_client.patch_task(task_id, original_name)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                task = response.json()

                Assert.equal(task.get('task_id'), task_id)
                Assert.equal(task.get('task_name'), original_name)

                logger.info(f'Task name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original task name')
                pytest.fail(
                    f'Failed to restore original name for task '
                    f'ID={task_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch task')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Patch task with duplicate name')
    @pytest.mark.negative
    def test_patch_task_duplicate_name(self, tasks_client, test_data):

        existing_name = test_data.get('task_name')
        logger.info(
            f'>>> TEST: Patch task with duplicate name="{existing_name}"',
        )

        with AllureReporting.add_step(
            f'Create task for patch test with name="{self.TEST_NAME}"',
        ):
            response = tasks_client.create_task(self.TEST_NAME)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify task created'):
            try:
                Assert.response_status(response.status_code, 201)

                task = response.json()
                task_id = task.get('task_id')
                logger.info(f'Task created with ID: {task_id}')

            except AssertionError:
                logger.error('Failed to create task for patch test')
                pytest.fail('Task creation failed for patch duplicate test')

        try:
            with AllureReporting.add_step(
                f'Try to patch with duplicate name="{existing_name}"',
            ):
                response = tasks_client.patch_task(task_id, existing_name)
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
                        f'Expected 409 conflict, got {response.status_code}',
                    )
                    pytest.fail(
                        f'Expected 409 conflict for duplicate name, '
                        f'got status {response.status_code}',
                    )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete created task {task_id}',
            ):
                response = tasks_client.delete_task(task_id)
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(f'Task {task_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')
