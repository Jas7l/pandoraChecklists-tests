import allure
import pytest

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(
        checklists_client, tasks_client, machines_client, areas_client,
):
    test_data = {
        'checklist_id': None,
        'checklist_name': None,
        'machine_id': None,
        'task_ids': None,
        'new_task_id': None,
        'created_machine_id_1': None,
        'created_machine_id_2': None,
        'area_id': None,
    }

    logger.info('Fetching first checklist from API')
    response = checklists_client.get_checklists_list(limit=1, offset=0)
    Assert.response_status(response.status_code, 200)

    checklists = response.json()
    Assert.is_not_empty(checklists)
    checklist = checklists[0]

    test_data['checklist_id'] = checklist.get('checklist_id')
    test_data['checklist_name'] = checklist.get('checklist_name')
    test_data['machine_id'] = checklist.get('machine_id')
    test_data['task_ids'] = checklist.get('task_id', [])
    test_data['status'] = checklist.get('status')

    logger.info(
        f'Checklist loaded: ID={test_data["checklist_id"]}, '
        f'Name={test_data["checklist_name"]}',
    )

    logger.info('Fetching area for machine creation')
    response = areas_client.get_areas_list(limit=1, offset=0)
    Assert.response_status(response.status_code, 200)

    areas = response.json()
    Assert.is_not_empty(areas)
    area_id = areas[0].get('area_id')
    test_data['area_id'] = area_id
    logger.info(f'Area loaded: ID={area_id}')

    logger.info('Creating test machine 1')
    response = machines_client.create_machine(
        machine_name='Test machine 1',
        area_id=area_id,
    )
    Assert.response_status(response.status_code, 201)
    machine_1 = response.json()
    test_data['created_machine_id_1'] = machine_1.get('machine_id')
    logger.info(f'Machine 1 created: ID={test_data["created_machine_id_1"]}')

    logger.info('Creating test machine 2')
    response = machines_client.create_machine(
        machine_name='Test machine 2',
        area_id=area_id,
    )
    Assert.response_status(response.status_code, 201)
    machine_2 = response.json()
    test_data['created_machine_id_2'] = machine_2.get('machine_id')
    logger.info(f'Machine 2 created: ID={test_data["created_machine_id_2"]}')

    logger.info('Fetching tasks list for new task selection')
    response = tasks_client.get_tasks_list(limit=100, offset=0)
    Assert.response_status(response.status_code, 200)

    all_tasks = response.json()
    Assert.is_not_empty(all_tasks)

    existing_task_ids = set(test_data['task_ids'])
    for task in all_tasks:
        task_id = task.get('task_id')
        if task_id not in existing_task_ids:
            test_data['new_task_id'] = task_id
            break

    if test_data['new_task_id'] is None:
        logger.error('No new task found for checklist')
        pytest.fail('No new task found for checklist')

    logger.info(
        f'New task selected: ID={test_data["new_task_id"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Checklists API')
@pytest.mark.api
@pytest.mark.checklists
class TestChecklistsAPI:

    TEST_NAME = 'Test Checklist'
    TEST_INVALID_ID = 9999999
    TEST_LIMIT = 10
    TEST_OFFSET = 1

    @pytest.fixture(scope='class')
    def test_data(
            self,
            checklists_client,
            tasks_client,
            machines_client,
            areas_client,
    ):
        data = get_test_data(
            checklists_client, tasks_client, machines_client, areas_client,
        )
        yield data

        if data.get('created_machine_id_1'):
            machines_client.delete_machine(data['created_machine_id_1'])
            logger.info(
                f'Machine {data["created_machine_id_1"]} deleted (cleanup)',
            )
        if data.get('created_machine_id_2'):
            machines_client.delete_machine(data['created_machine_id_2'])
            logger.info(
                f'Machine {data["created_machine_id_2"]} deleted (cleanup)',
            )

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get checklists list')
    @pytest.mark.positive
    def test_get_checklists_list(self, checklists_client):

        logger.info('>>> TEST: Get checklists list')

        with AllureReporting.add_step('Get checklists list'):
            response = checklists_client.get_checklists_list()
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.is_not_empty(checklists)
                logger.info(f'Retrieved {len(checklists)} checklists')
            except AssertionError:
                logger.error('Failed to get checklists list')
                pytest.fail('Checklists list response is empty or invalid')

        with AllureReporting.add_step('Verify checklist fields'):
            checklist = checklists[0]

            try:
                Assert.has_key(checklist, 'checklist_id')
                Assert.has_key(checklist, 'checklist_name')
                Assert.has_key(checklist, 'machine_id')
                Assert.has_key(checklist, 'status')
                Assert.has_key(checklist, 'task_id')
                logger.info(
                    f'Checklist fields verified for '
                    f'ID={checklist.get("checklist_id")}',
                )
            except AssertionError:
                logger.error('Checklist missing required fields')
                pytest.fail(
                    'Checklist object missing required fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get checklists list with pagination')
    @pytest.mark.positive
    def test_get_checklists_list_with_pagination(
            self, checklists_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Get checklists list with pagination: '
            f'limit={self.TEST_LIMIT}, offset={self.TEST_OFFSET}',
        )

        with AllureReporting.add_step(
            f'Get checklists list with limit={self.TEST_LIMIT}, '
            f'offset={self.TEST_OFFSET}',
        ):
            response = checklists_client.get_checklists_list(
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

                checklists = response.json()
                logger.info(
                    f'Retrieved {len(checklists)} checklists with pagination',
                )

                for checklist in checklists:
                    Assert.not_equal(
                        checklist.get('checklist_id'),
                        test_data.get('checklist_id'),
                    )

                logger.info(
                    'Pagination verified: test checklist '
                    f'ID={test_data.get("checklist_id")} excluded',
                )

            except AssertionError:
                logger.error('Failed to get paginated checklists list')
                pytest.fail(
                    'Paginated checklists list response is empty or invalid',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get checklist by id')
    @pytest.mark.positive
    def test_get_checklist_by_id(self, checklists_client, test_data):

        checklist_id = test_data.get('checklist_id')
        logger.info(f'>>> TEST: Get checklist by ID={checklist_id}')

        with AllureReporting.add_step(f'Get checklist by ID: {checklist_id}'):
            response = checklists_client.get_checklists_list(
                checklist_id=checklist_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify checklist data'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()[0]

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(
                    checklist.get('checklist_name'),
                    test_data.get('checklist_name'),
                )
                Assert.equal(
                    checklist.get('machine_id'),
                    test_data.get('machine_id'),
                )
                Assert.equal(
                    checklist.get('task_id'),
                    test_data.get('task_ids'),
                )

                logger.info(
                    f'Checklist verified: ID={checklist_id}, '
                    f'Name={test_data.get("checklist_name")}',
                )

            except AssertionError:
                logger.error(f'Checklist data mismatch for ID={checklist_id}')
                pytest.fail(
                    f'Checklist with ID {checklist_id} not found or '
                    f'data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get checklist by invalid id')
    @pytest.mark.negative
    def test_get_checklist_by_invalid_id(self, checklists_client):

        logger.info(
            f'>>> TEST: Get checklist by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklist by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = checklists_client.get_checklists_list(
                checklist_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid checklist ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Get checklists by machine_id')
    @pytest.mark.positive
    def test_get_checklists_by_machine_id(self, checklists_client, test_data):

        machine_id = test_data.get('machine_id')
        logger.info(f'>>> TEST: Get checklists by machine_id={machine_id}')

        with AllureReporting.add_step(
            f'Get checklists by machine_id={machine_id}',
        ):
            response = checklists_client.get_checklists_list(
                machine_id=machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify checklists by machine'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.is_not_empty(checklists)

                for checklist in checklists:
                    Assert.equal(checklist.get('machine_id'), machine_id)

                logger.info(
                    f'Found {len(checklists)} checklists for '
                    f'machine_id={machine_id}',
                )

            except AssertionError:
                logger.error(
                    f'No checklists found for machine_id={machine_id}',
                )
                pytest.fail(
                    f'Expected checklists for machine_id={machine_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Get checklists by invalid machine_id')
    @pytest.mark.negative
    def test_get_checklists_by_invalid_machine_id(self, checklists_client):

        logger.info(
            f'>>> TEST: Get checklists by invalid machine_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklists by invalid machine_id={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.get_checklists_list(
                machine_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid machine_id',
        ):
            try:
                Assert.response_status(response.status_code, 200)
                Assert.is_empty(response.json())
                logger.info('Received empty response for invalid machine_id')

            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'machine_id={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid machine_id '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklists list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Get checklists by status')
    @pytest.mark.parametrize('status', [True, False])
    @pytest.mark.positive
    def test_get_checklists_by_status(self, checklists_client, status):

        logger.info(f'>>> TEST: Get checklists by status={status}')

        with AllureReporting.add_step(
            f'Get checklists by status={status}',
        ):
            response = checklists_client.get_checklists_list(status=status)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify checklists by status'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()

                for checklist in checklists:
                    Assert.equal(checklist.get('status'), status)

                logger.info(
                    f'Found {len(checklists)} checklists with status={status}',
                )

            except AssertionError:
                logger.error(
                    f'No checklists found for status={status}',
                )
                pytest.fail(
                    f'Expected checklists for status={status}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Create new checklist')
    @pytest.mark.positive
    def test_create_checklist(self, checklists_client, test_data):

        logger.info(
            f'>>> TEST: Create new checklist with name="{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=test_data.get('task_ids'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created checklist'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()

                Assert.has_key(checklist, 'checklist_id')
                Assert.equal(checklist.get('checklist_name'), self.TEST_NAME)
                Assert.equal(
                    checklist.get('machine_id'),
                    test_data.get('created_machine_id_1'),
                )
                Assert.equal(checklist.get('status'), True)

                created_checklist_id = checklist.get('checklist_id')
                logger.info(
                    f'Checklist created with ID: {created_checklist_id}, '
                    f'Name: {self.TEST_NAME}',
                )

        except AssertionError:
            logger.error('Failed to create checklist')
            pytest.fail(
                f'Checklist creation failed for name="{self.TEST_NAME}"',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete checklist {created_checklist_id}',
            ):
                response = checklists_client.delete_checklist(
                    created_checklist_id,
                )
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Checklist {created_checklist_id} deleted (cleanup)',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Create checklist with invalid machine_id')
    @pytest.mark.negative
    def test_create_checklist_invalid_machine(
            self, checklists_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Create checklist with invalid machine_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Create checklist with invalid machine_id={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=self.TEST_INVALID_ID,
                task_id=test_data.get('task_ids'),
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
                    checklist_id = response.json().get('checklist_id')
                    checklists_client.delete_checklist(checklist_id)
                    logger.info(
                        f'Invalid checklist {checklist_id} deleted (cleanup)',
                    )
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid machine_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Create checklist with invalid task_id')
    @pytest.mark.negative
    def test_create_checklist_invalid_task(self, checklists_client, test_data):

        logger.info(
            f'>>> TEST: Create checklist with invalid task_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Create checklist with invalid task_id={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[self.TEST_INVALID_ID],
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
                    checklist_id = response.json().get('checklist_id')
                    checklists_client.delete_checklist(checklist_id)
                    logger.info(
                        f'Invalid checklist {checklist_id} deleted (cleanup)',
                    )
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid task_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Create checklist with duplicate task_id')
    @pytest.mark.negative
    def test_create_checklist_duplicate_task(
            self, checklists_client, test_data,
    ):

        task_id = test_data.get('new_task_id')
        logger.info(
            f'>>> TEST: Create checklist with duplicate task_id={task_id}',
        )

        with AllureReporting.add_step(
            f'Create checklist with duplicate task_id={task_id}',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[task_id, task_id],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for duplicate task')
            except AssertionError:
                if response.status_code == 201:
                    checklist_id = response.json().get('checklist_id')
                    checklists_client.delete_checklist(checklist_id)
                    logger.info(
                        f'Invalid checklist {checklist_id} deleted (cleanup)',
                    )
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for duplicate task_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-012: Create checklist on busy machine')
    @pytest.mark.negative
    def test_create_checklist_busy_machine(self, checklists_client, test_data):

        logger.info('>>> TEST: Create checklist on busy machine')

        with AllureReporting.add_step(
            'Create checklist on machine with active checklist',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('machine_id'),
                task_id=[test_data.get('new_task_id')],
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
                    checklist_id = response.json().get('checklist_id')
                    checklists_client.delete_checklist(checklist_id)
                    logger.info(
                        f'Invalid checklist {checklist_id} deleted (cleanup)',
                    )
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for busy machine, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-013: Create checklist after deactivating previous')
    @pytest.mark.positive
    def test_create_checklist_after_deactivate(self, checklists_client,
                                               test_data):
        logger.info('>>> TEST: Create checklist after deactivating previous')

        created_checklist_id_1 = None
        created_checklist_id_2 = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify created checklist'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                created_checklist_id_1 = checklist.get('checklist_id')
                logger.info(
                    f'Checklist created with ID: {created_checklist_id_1}',
                )

        except AssertionError:
            logger.error('Failed to create first checklist')
            pytest.fail('First checklist creation failed')

        with AllureReporting.add_step(
            f'Deactivate checklist {created_checklist_id_1}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=created_checklist_id_1,
                status=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify deactivation'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(
                    checklist.get('checklist_id'),
                    created_checklist_id_1,
                )
                Assert.equal(checklist.get('status'), False)

                logger.info(
                    f'Checklist {created_checklist_id_1} deactivated',
                )

            except AssertionError:
                logger.error('Failed to deactivate checklist')
                pytest.fail('Checklist deactivation failed')

        with AllureReporting.add_step(
            'Create second checklist on same machine',
        ):
            response = checklists_client.create_checklist(
                checklist_name=f'{self.TEST_NAME} 2',
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify second checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                created_checklist_id_2 = checklist.get('checklist_id')

                Assert.has_key(checklist, 'checklist_id')
                Assert.equal(
                    checklist.get('checklist_name'),
                    f'{self.TEST_NAME} 2',
                )
                Assert.equal(
                    checklist.get('machine_id'),
                    test_data.get('created_machine_id_1'),
                )
                Assert.equal(checklist.get('status'), True)

                logger.info(
                    f'Second checklist created with ID: '
                    f'{created_checklist_id_2}',
                )

        except AssertionError:
            logger.error('Failed to create second checklist')
            pytest.fail('Second checklist creation failed')

        finally:
            if created_checklist_id_2:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {created_checklist_id_2}',
                ):
                    response = checklists_client.delete_checklist(
                        created_checklist_id_2,
                    )
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Checklist {created_checklist_id_2} deleted '
                        f'(cleanup)',
                    )

            if created_checklist_id_1:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {created_checklist_id_1}',
                ):
                    response = checklists_client.delete_checklist(
                        created_checklist_id_1,
                    )
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Checklist {created_checklist_id_1} deleted '
                        f'(cleanup)',
                    )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-014: Delete existing checklist')
    @pytest.mark.positive
    def test_delete_checklist(self, checklists_client, test_data):

        logger.info('>>> TEST: Delete existing checklist')

        with AllureReporting.add_step(
            f'Create checklist for deletion with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=test_data.get('task_ids'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify checklist created'):
            try:
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                logger.info(f'Checklist created with ID: {checklist_id}')

            except AssertionError:
                logger.error('Failed to create checklist for deletion test')
                pytest.fail('Checklist creation failed for deletion test')

        with AllureReporting.add_step(f'Delete checklist {checklist_id}'):
            response = checklists_client.delete_checklist(checklist_id)
            AllureReporting.attach_response(response.status_code)

        with AllureReporting.add_step('Verify deletion response'):
            try:
                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Checklist {checklist_id} deleted (204 No Content)',
                )

            except AssertionError:
                logger.error(f'Checklist {checklist_id} deletion failed')
                pytest.fail(
                    f'Expected 204 response for checklist deletion, '
                    f'got {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Delete checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-015: Delete non-existent checklist')
    @pytest.mark.negative
    def test_delete_checklist_not_found(self, checklists_client):

        logger.info(
            f'>>> TEST: Delete non-existent checklist '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Delete non-existent checklist ID={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.delete_checklist(
                self.TEST_INVALID_ID,
            )
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
                    f'Expected 404 error for non-existent checklist, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-016: Patch checklist name')
    @pytest.mark.positive
    def test_patch_checklist_name(self, checklists_client, test_data):

        checklist_id = test_data.get('checklist_id')
        original_name = test_data.get('checklist_name')

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} name to '
            f'"{self.TEST_NAME}"',
        )

        with AllureReporting.add_step(
            f'Patch checklist name to "{self.TEST_NAME}"',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                checklist_name=self.TEST_NAME,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('checklist_name'), self.TEST_NAME)

                logger.info(f'Checklist name updated to: {self.TEST_NAME}')

            except AssertionError:
                logger.error(f'Checklist {checklist_id} patch failed')
                pytest.fail(
                    f'Checklist name update failed for ID={checklist_id}',
                )

        with AllureReporting.add_step(
            f'Restore original name "{original_name}"',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                checklist_name=original_name,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('checklist_name'), original_name)

                logger.info(f'Checklist name restored to: {original_name}')

            except AssertionError:
                logger.error('Failed to restore original checklist name')
                pytest.fail(
                    f'Failed to restore original name for checklist '
                    f'ID={checklist_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-017: Patch checklist status')
    @pytest.mark.positive
    def test_patch_checklist_status(self, checklists_client, test_data):

        checklist_id = test_data.get('checklist_id')
        original_status = test_data.get('status')

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} status to False',
        )

        with AllureReporting.add_step(
            'Patch checklist status to False',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                status=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('status'), False)

                logger.info('Checklist status updated to: False')

            except AssertionError:
                logger.error(f'Checklist {checklist_id} patch failed')
                pytest.fail(
                    f'Checklist status update failed for ID={checklist_id}',
                )

        with AllureReporting.add_step(
            f'Restore original status {original_status}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                status=original_status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('status'), original_status)

                logger.info(f'Checklist status restored to: {original_status}')

            except AssertionError:
                logger.error('Failed to restore original status')
                pytest.fail(
                    f'Failed to restore original status for checklist '
                    f'ID={checklist_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-018: Patch checklist add task')
    @pytest.mark.positive
    def test_patch_checklist_tasks(self, checklists_client, test_data):

        checklist_id = test_data.get('checklist_id')
        original_tasks = test_data.get('task_ids')
        new_task_id = test_data.get('new_task_id')

        updated_tasks = original_tasks + [new_task_id]

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} - add task '
            f'{new_task_id}',
        )

        with AllureReporting.add_step(
            f'Patch checklist - add task {new_task_id}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                task_id=updated_tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify patch response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('task_id'), updated_tasks)

                logger.info(
                    f'Task added: {new_task_id}. '
                    f'Updated tasks: {updated_tasks}',
                )

            except AssertionError:
                logger.error(f'Checklist {checklist_id} patch failed')
                pytest.fail(
                    f'Failed to add task to checklist ID={checklist_id}',
                )

        with AllureReporting.add_step('Restore original tasks'):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                task_id=original_tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify restore response'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()

                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('task_id'), original_tasks)

                logger.info('Tasks restored to original')

            except AssertionError:
                logger.error('Failed to restore original tasks')
                pytest.fail(
                    f'Failed to restore original tasks for checklist '
                    f'ID={checklist_id}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-019: Patch checklist with duplicate task')
    @pytest.mark.negative
    def test_patch_checklist_duplicate_task(
            self, checklists_client, test_data,
    ):

        checklist_id = test_data.get('checklist_id')
        task_ids = test_data.get('task_ids')

        duplicate_tasks = task_ids + task_ids

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} with duplicate task',
        )

        with AllureReporting.add_step(
            'Patch checklist with duplicate tasks',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                task_id=duplicate_tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for duplicate task')
            except AssertionError:
                if response.status_code == 200:
                    response = checklists_client.patch_checklist(
                        checklist_id=checklist_id,
                        task_id=task_ids,
                    )
                    AllureReporting.attach_response(
                        response.status_code,
                        response.json(),
                    )
                    logger.info('Tasks restored to original')

                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for duplicate task, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-020: Patch checklist with invalid task_id')
    @pytest.mark.negative
    def test_patch_checklist_invalid_task(self, checklists_client, test_data):

        checklist_id = test_data.get('checklist_id')
        original_task_id = test_data.get('task_ids')
        invalid_task_ids = original_task_id + [self.TEST_INVALID_ID]

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} with invalid '
            f'task_id={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Patch checklist with invalid task_id={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                task_id=invalid_task_ids,
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
                if response.status_code == 200:
                    checklists_client.patch_checklist(
                        checklist_id=checklist_id,
                        task_id=original_task_id,
                    )
                    logger.info('Tasks restored to original')
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid task_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Patch checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-021: Patch checklist with invalid machine_id')
    @pytest.mark.negative
    def test_patch_checklist_invalid_machine(
            self, checklists_client, test_data,
    ):

        checklist_id = test_data.get('checklist_id')
        original_machine_id = test_data.get('machine_id')

        logger.info(
            f'>>> TEST: Patch checklist ID={checklist_id} with invalid '
            f'machine_id={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Patch checklist with invalid machine_id='
            f'{self.TEST_INVALID_ID}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                machine_id=self.TEST_INVALID_ID,
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
                if response.status_code == 200:
                    checklists_client.patch_checklist(
                        checklist_id=checklist_id,
                        machine_id=original_machine_id,
                    )
                    logger.info('Machine restored to original')
                logger.error(
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid machine_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Copy checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-022: Copy checklist to another machine')
    @pytest.mark.positive
    def test_copy_checklist(self, checklists_client, test_data):

        source_checklist_id = test_data.get('checklist_id')
        target_machine_id = test_data.get('created_machine_id_1')

        logger.info(
            f'>>> TEST: Copy checklist ID={source_checklist_id} to '
            f'machine {target_machine_id}',
        )

        with AllureReporting.add_step(
            f'Copy checklist {source_checklist_id} to machine '
            f'{target_machine_id}',
        ):
            response = checklists_client.copy_checklist(
                source_checklist_id=source_checklist_id,
                target_machine_id=target_machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify copied checklist'):
                Assert.response_status(response.status_code, 201)

                copied_checklist = response.json()

                Assert.has_key(copied_checklist, 'checklist_id')
                Assert.equal(
                    copied_checklist.get('machine_id'),
                    target_machine_id,
                )
                Assert.equal(copied_checklist.get('status'), True)

                copied_checklist_id = copied_checklist.get('checklist_id')
                logger.info(
                    f'Checklist copied successfully: '
                    f'ID={copied_checklist_id}',
                )

        except AssertionError:
            logger.error('Failed to copy checklist')
            pytest.fail(
                f'Checklist copy failed for source={source_checklist_id}',
            )

        finally:
            with AllureReporting.add_step(
                f'Cleanup - delete copied checklist {copied_checklist_id}',
            ):
                response = checklists_client.delete_checklist(
                    copied_checklist_id,
                )
                AllureReporting.attach_response(response.status_code)

                Assert.response_status(response.status_code, 204)
                logger.info(
                    f'Copied checklist {copied_checklist_id} deleted '
                    f'(cleanup)',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Copy checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-023: Copy non-existent checklist')
    @pytest.mark.negative
    def test_copy_checklist_not_found(self, checklists_client, test_data):

        logger.info(
            f'>>> TEST: Copy non-existent checklist '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Copy non-existent checklist ID={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.copy_checklist(
                source_checklist_id=self.TEST_INVALID_ID,
                target_machine_id=test_data.get('created_machine_id_1'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 404)

                data = response.json()
                description = data.get('description')
                Assert.equal(description, 'not found')
                logger.info('Received expected 404 error')

            except AssertionError:
                logger.error(
                    f'Expected 404 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 404 error for non-existent checklist, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Copy checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-024: Copy checklist to invalid machine')
    @pytest.mark.negative
    def test_copy_checklist_invalid_machine(
            self, checklists_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Copy checklist to invalid machine '
            f'ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Copy checklist to invalid machine ID={self.TEST_INVALID_ID}',
        ):
            response = checklists_client.copy_checklist(
                source_checklist_id=test_data.get('checklist_id'),
                target_machine_id=self.TEST_INVALID_ID,
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
                    f'Expected 409 conflict, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 409 conflict error for invalid machine, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Copy checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        'API-TC-025: Copy checklist to machine with active checklist',
    )
    @pytest.mark.positive
    def test_copy_checklist_to_machine_with_active_checklist(
            self, checklists_client, test_data,
    ):
        logger.info(
            '>>> TEST: Copy checklist to machine with active checklist',
        )

        created_checklist_id = None
        copied_checklist_id = None

        try:
            with AllureReporting.add_step(
                f'Create active checklist on machine '
                f'{test_data.get("created_machine_id_1")}',
            ):
                response = checklists_client.create_checklist(
                    checklist_name=self.TEST_NAME,
                    machine_id=test_data.get('created_machine_id_1'),
                    task_id=[test_data.get('new_task_id')],
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                created_checklist_id = checklist.get('checklist_id')
                logger.info(
                    f'Active checklist created with ID: '
                    f'{created_checklist_id}',
                )

            with AllureReporting.add_step(
                'Copy checklist to machine with active checklist',
            ):
                response = checklists_client.copy_checklist(
                    source_checklist_id=test_data.get('checklist_id'),
                    target_machine_id=test_data.get('created_machine_id_1'),
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify copy success'):
                Assert.response_status(response.status_code, 201)

                copied_checklist = response.json()
                copied_checklist_id = copied_checklist.get('checklist_id')

                Assert.has_key(copied_checklist, 'checklist_id')
                Assert.equal(
                    copied_checklist.get('machine_id'),
                    test_data.get('created_machine_id_1'),
                )
                Assert.equal(copied_checklist.get('status'), True)

                logger.info(
                    f'Checklist copied with ID: {copied_checklist_id}',
                )

            with AllureReporting.add_step(
                'Verify old checklist deactivated',
            ):
                response = checklists_client.get_checklists_list(
                    checklist_id=created_checklist_id,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify old checklist status'):
                Assert.response_status(response.status_code, 200)

                Assert.is_empty(response.json())

                logger.info(
                    f'Old checklist {created_checklist_id} deactivated',
                )

        except AssertionError:
            logger.error('Test failed during copy checklist flow')
            pytest.fail(
                'Copy checklist to machine with active checklist failed',
            )

        finally:
            if copied_checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete copied checklist '
                    f'{copied_checklist_id}',
                ):
                    response = checklists_client.delete_checklist(
                        copied_checklist_id,
                    )
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Copied checklist {copied_checklist_id} deleted '
                        f'(cleanup)',
                    )

            if created_checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete created checklist '
                    f'{created_checklist_id}',
                ):
                    response = checklists_client.delete_checklist(
                        created_checklist_id,
                    )
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(
                        f'Created checklist {created_checklist_id} deleted '
                        f'(cleanup)',
                    )

        logger.info('<<< TEST PASSED')

    @allure.story('Add task to checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-026: Add task to checklist')
    @pytest.mark.positive
    def test_add_task_to_checklist(self, checklists_client, test_data):
        logger.info('>>> TEST: Add task to checklist')

        checklist_id = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=test_data.get('task_ids'),
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                logger.info(f'Checklist created with ID: {checklist_id}')

            with AllureReporting.add_step(
                f'Add task {test_data.get("new_task_id")} to checklist',
            ):
                response = checklists_client.add_task_to_checklist(
                    checklist_id=checklist_id,
                    task_id=test_data.get('new_task_id'),
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify task added'):
                Assert.response_status(response.status_code, 201)

                updated_checklist = response.json()

                Assert.equal(
                    updated_checklist.get('checklist_id'),
                    checklist_id,
                )
                Assert.contains(
                    updated_checklist.get('task_id'),
                    test_data.get('new_task_id'),
                )

                logger.info(
                    f'Task {test_data.get("new_task_id")} added to '
                    f'checklist {checklist_id}',
                )

        except AssertionError:
            logger.error('Failed to add task to checklist')
            pytest.fail(
                f'Failed to add task to checklist ID={checklist_id}',
            )

        finally:
            if checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {checklist_id}',
                ):
                    response = checklists_client.delete_checklist(checklist_id)
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Checklist {checklist_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Add task to checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-027: Add duplicate task to checklist')
    @pytest.mark.negative
    def test_add_duplicate_task_to_checklist(self, checklists_client,
                                             test_data):
        logger.info('>>> TEST: Add duplicate task to checklist')

        checklist_id = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                existing_task_id = checklist.get('task_id')[0]
                logger.info(
                    f'Checklist created with ID: {checklist_id}, '
                    f'task: {existing_task_id}',
                )

            with AllureReporting.add_step(
                f'Add duplicate task {existing_task_id} to checklist',
            ):
                response = checklists_client.add_task_to_checklist(
                    checklist_id=checklist_id,
                    task_id=existing_task_id,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify conflict response'):
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

        except AssertionError:
            logger.error(
                f'Expected 409 conflict, got {response.status_code}',
            )
            pytest.fail(
                f'Expected 409 conflict error for duplicate task, '
                f'got status {response.status_code}',
            )

        finally:
            if checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {checklist_id}',
                ):
                    response = checklists_client.delete_checklist(checklist_id)
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Checklist {checklist_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Add task to checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-028: Add invalid task to checklist')
    @pytest.mark.negative
    def test_add_invalid_task_to_checklist(self, checklists_client, test_data):
        logger.info(
            f'>>> TEST: Add invalid task ID={self.TEST_INVALID_ID} '
            f'to checklist',
        )

        checklist_id = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                logger.info(f'Checklist created with ID: {checklist_id}')

            with AllureReporting.add_step(
                f'Add invalid task ID={self.TEST_INVALID_ID} to checklist',
            ):
                response = checklists_client.add_task_to_checklist(
                    checklist_id=checklist_id,
                    task_id=self.TEST_INVALID_ID,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify conflict response'):
                Assert.response_status(response.status_code, 409)
                logger.info('Received expected 409 conflict error')

        except AssertionError:
            logger.error(
                f'Expected 409 conflict, got {response.status_code}',
            )
            pytest.fail(
                f'Expected 409 conflict error for invalid task, '
                f'got status {response.status_code}',
            )

        finally:
            if checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {checklist_id}',
                ):
                    response = checklists_client.delete_checklist(checklist_id)
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Checklist {checklist_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Remove task from checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-029: Remove task from checklist')
    @pytest.mark.positive
    def test_remove_task_from_checklist(self, checklists_client, test_data):
        logger.info('>>> TEST: Remove task from checklist')

        checklist_id = None
        original_task_id = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                original_task_id = checklist.get('task_id')[0]
                logger.info(
                    f'Checklist created with ID: {checklist_id}, '
                    f'task: {original_task_id}',
                )

            with AllureReporting.add_step(
                f'Remove task {original_task_id} from checklist',
            ):
                response = checklists_client.remove_task_from_checklist(
                    checklist_id=checklist_id,
                    task_id=original_task_id,
                )
                AllureReporting.attach_response(response.status_code)

            with AllureReporting.add_step('Verify task removed'):
                Assert.response_status(response.status_code, 204)

                get_response = checklists_client.get_checklists_list(
                    checklist_id=checklist_id,
                )
                updated_checklist = get_response.json()[0]
                Assert.not_contains(
                    updated_checklist.get('task_id'),
                    original_task_id,
                )

                logger.info(
                    f'Task {original_task_id} removed from '
                    f'checklist {checklist_id}',
                )

        except AssertionError:
            logger.error('Failed to remove task from checklist')
            pytest.fail(
                f'Failed to remove task from checklist ID={checklist_id}',
            )

        finally:
            if checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {checklist_id}',
                ):
                    response = checklists_client.delete_checklist(checklist_id)
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Checklist {checklist_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Remove task from checklist')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-030: Remove non-existent task from checklist')
    @pytest.mark.negative
    def test_remove_non_existent_task_from_checklist(self, checklists_client,
                                                     test_data):
        logger.info(
            f'>>> TEST: Remove non-existent task ID={self.TEST_INVALID_ID} '
            f'from checklist',
        )

        checklist_id = None

        with AllureReporting.add_step(
            f'Create checklist with name="{self.TEST_NAME}"',
        ):
            response = checklists_client.create_checklist(
                checklist_name=self.TEST_NAME,
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            with AllureReporting.add_step('Verify checklist created'):
                Assert.response_status(response.status_code, 201)

                checklist = response.json()
                checklist_id = checklist.get('checklist_id')
                logger.info(f'Checklist created with ID: {checklist_id}')

            with AllureReporting.add_step(
                f'Remove non-existent task ID={self.TEST_INVALID_ID}',
            ):
                response = checklists_client.remove_task_from_checklist(
                    checklist_id=checklist_id,
                    task_id=self.TEST_INVALID_ID,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify error response'):
                Assert.response_status(response.status_code, 404)

                data = response.json()
                description = data.get('description')
                Assert.equal(description, 'not found')
                logger.info('Received expected 404 error')

        except AssertionError:
            logger.error(
                f'Expected 404 error, got {response.status_code}',
            )
            pytest.fail(
                f'Expected 404 error for non-existent task, '
                f'got status {response.status_code}',
            )

        finally:
            if checklist_id:
                with AllureReporting.add_step(
                    f'Cleanup - delete checklist {checklist_id}',
                ):
                    response = checklists_client.delete_checklist(checklist_id)
                    AllureReporting.attach_response(response.status_code)

                    Assert.response_status(response.status_code, 204)
                    logger.info(f'Checklist {checklist_id} deleted (cleanup)')

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-031: Search checklists by substring')
    @pytest.mark.positive
    def test_search_checklists_by_substring(
            self, checklists_client, test_data,
    ):

        checklist_name = test_data.get('checklist_name')
        search_substring = checklist_name[:5]

        logger.info(
            f'>>> TEST: Search checklists by substring "{search_substring}"',
        )

        with AllureReporting.add_step(
            f'Search checklists with q="{search_substring}"',
        ):
            response = checklists_client.search_checklists(q=search_substring)
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify search results'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.is_not_empty(checklists)

                found_checklist = any(
                    checklist_name.lower() in checklist.get(
                        'checklist_name').lower()
                    for checklist in checklists
                )

                Assert.is_true(found_checklist)
                logger.info(
                    f'Checklist "{checklist_name}" found in search results',
                )

                q_lower = search_substring.lower()
                starts_with_q = []
                contains_q = []

                for checklist in checklists:
                    checklist_name_lower = checklist.get(
                        'checklist_name').lower()
                    if checklist_name_lower.startswith(q_lower):
                        starts_with_q.append(checklist_name_lower)
                    elif q_lower in checklist_name_lower:
                        contains_q.append(checklist_name_lower)

                for checklist in checklists:
                    Assert.is_true(
                        search_substring.lower() in checklist.get(
                            'checklist_name').lower(),
                    )

                logger.info(
                    f'Search results: total={len(checklists)}, '
                    f'starts_with_q={len(starts_with_q)}, '
                    f'contains_q={len(contains_q)}',
                )

            except AssertionError:
                logger.error(
                    f'Search failed for query="{search_substring}"',
                )
                pytest.fail(
                    f'Expected to find checklist "{checklist_name}" '
                    f'in search results',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-032: Search checklists with pagination')
    @pytest.mark.positive
    def test_search_checklists_pagination(self, checklists_client, test_data):

        checklist_name = test_data.get('checklist_name')
        search_substring = checklist_name[:5]

        logger.info(
            f'>>> TEST: Search checklists with pagination, '
            f'q="{search_substring}"',
        )

        with AllureReporting.add_step(
            'Search with limit=1, offset=0',
        ):
            response = checklists_client.search_checklists(
                q=search_substring,
                limit=1,
                offset=0,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify first page'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists_page1 = response.json()
                Assert.is_not_empty(checklists_page1)
                Assert.less_than(len(checklists_page1), 2)

                logger.info(
                    f'First page: {len(checklists_page1)} checklists',
                )

            except AssertionError:
                logger.error('Failed to get first page')
                pytest.fail('Pagination first page failed')

        with AllureReporting.add_step(
            'Search with limit=1, offset=1',
        ):
            response = checklists_client.search_checklists(
                q=search_substring,
                limit=1,
                offset=1,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify second page'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists_page2 = response.json()

                if len(checklists_page1) > 0 and len(checklists_page2) > 0:
                    Assert.not_equal(
                        checklists_page1[0].get('checklist_id'),
                        checklists_page2[0].get('checklist_id'),
                    )
                    logger.info(
                        'Pagination works: different checklists on pages',
                    )

            except AssertionError:
                logger.error('Pagination verification failed')
                pytest.fail('Pagination pages are identical')

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-033: Search checklists with status=false')
    @pytest.mark.positive
    def test_search_checklists_inactive(self, checklists_client, test_data):

        checklist_name = test_data.get('checklist_name')
        search_substring = checklist_name[:5]
        created_checklist_id = None

        logger.info(
            f'>>> TEST: Search inactive checklists with q='
            f'"{search_substring}"',
        )

        with AllureReporting.add_step(
            f'Create checklist "{self.TEST_NAME}_inactive" for test',
        ):
            response = checklists_client.create_checklist(
                checklist_name=f'{self.TEST_NAME}_inactive',
                machine_id=test_data.get('created_machine_id_1'),
                task_id=[test_data.get('new_task_id')],
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            Assert.response_status(response.status_code, 201)
            checklist = response.json()
            created_checklist_id = checklist.get('checklist_id')
            logger.info(
                f'Checklist created: {created_checklist_id}',
            )

        except AssertionError:
            logger.error('Failed to create checklist for test')
            pytest.fail('Checklist creation failed')

        with AllureReporting.add_step(
            f'Deactivate checklist {created_checklist_id}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=created_checklist_id,
                status=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        try:
            Assert.response_status(response.status_code, 200)
            logger.info(f'Checklist {created_checklist_id} deactivated')
        except AssertionError:
            logger.error('Failed to deactivate checklist')
            pytest.fail('Checklist deactivation failed')

        with AllureReporting.add_step(
            'Search inactive checklists with status=false',
        ):
            response = checklists_client.search_checklists(
                q=self.TEST_NAME,
                status=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify inactive checklist found'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.is_not_empty(checklists)

                found_inactive = any(
                    self.TEST_NAME.lower() in checklist.get(
                        'checklist_name').lower()
                    for checklist in checklists
                )

                Assert.is_true(found_inactive)
                logger.info('Inactive checklist found in search results')

                for checklist in checklists:
                    Assert.equal(checklist.get('status'), False)

            except AssertionError:
                logger.error('Inactive checklist not found')
                pytest.fail('Expected to find inactive checklist')

        with AllureReporting.add_step(
            'Search active checklists with status=true',
        ):
            response = checklists_client.search_checklists(
                q=self.TEST_NAME,
                status=True,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify inactive checklist not in active',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()

                found_inactive_active = any(
                    self.TEST_NAME.lower() in checklist.get(
                        'checklist_name').lower()
                    for checklist in checklists
                )

                Assert.is_false(found_inactive_active)
                logger.info('Inactive checklist not found in active search')

                for checklist in checklists:
                    Assert.equal(checklist.get('status'), True)

            except AssertionError:
                logger.error('Inactive checklist found in active search')
                pytest.fail(
                    'Inactive checklist should not be in active search',
                )

            finally:
                if created_checklist_id:
                    with AllureReporting.add_step(
                        f'Cleanup - delete checklist '
                        f'{created_checklist_id}',
                    ):
                        response = checklists_client.delete_checklist(
                            created_checklist_id,
                        )
                        AllureReporting.attach_response(response.status_code)

                        Assert.response_status(response.status_code, 204)
                        logger.info(
                            f'Checklist {created_checklist_id} deleted '
                            f'(cleanup)',
                        )

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-034: Search checklists with q shorter than 2 chars')
    @pytest.mark.negative
    def test_search_checklists_q_too_short(self, checklists_client):

        logger.info('>>> TEST: Search checklists with q="a" (too short)')

        with AllureReporting.add_step('Search with q="a"'):
            response = checklists_client.search_checklists(q='a')
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify 400 error'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for q too short')
            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for q too short, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-035: Search checklists with empty q')
    @pytest.mark.negative
    def test_search_checklists_q_empty(self, checklists_client):

        logger.info('>>> TEST: Search checklists with q=""')

        with AllureReporting.add_step('Search with q=""'):
            response = checklists_client.search_checklists(q='')
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify 400 error'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for q empty')
            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for q empty, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-036: Search checklists with non-existent substring')
    @pytest.mark.positive
    def test_search_checklists_no_results(self, checklists_client):

        non_existent_query = 'nonexistent_xyz_123'

        logger.info(
            f'>>> TEST: Search checklists with non-existent q='
            f'"{non_existent_query}"',
        )

        with AllureReporting.add_step(
            f'Search with q="{non_existent_query}"',
        ):
            response = checklists_client.search_checklists(
                q=non_existent_query,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify empty results'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.is_empty(checklists)
                logger.info('Received empty results for non-existent query')

            except AssertionError:
                logger.error(
                    f'Expected empty results for q="{non_existent_query}"',
                )
                pytest.fail(
                    f'Expected empty array for non-existent query, '
                    f'got {len(checklists)} results',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Search checklists')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-037: Search checklists with limit exceeded')
    @pytest.mark.positive
    def test_search_checklists_limit_exceeded(
            self, checklists_client, test_data,
    ):

        checklist_name = test_data.get('checklist_name')
        search_substring = checklist_name[:5]

        logger.info(
            '>>> TEST: Search checklists with limit=100 (exceeds max)',
        )

        with AllureReporting.add_step(
            'Search with limit=100',
        ):
            response = checklists_client.search_checklists(
                q=search_substring,
                limit=100,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify limit applied'):
            try:
                Assert.response_status(response.status_code, 200)

                checklists = response.json()
                Assert.less_than(len(checklists), 51)
                logger.info(
                    f'Limit applied: got {len(checklists)} checklists '
                    f'(max 50)',
                )

            except AssertionError:
                logger.error('Limit validation failed')
                pytest.fail('Server should limit results to 50')

        logger.info('<<< TEST PASSED')
