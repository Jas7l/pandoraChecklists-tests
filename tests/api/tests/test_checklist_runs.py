import allure
import pytest
from datetime import datetime, timedelta

from tests.utils.allure_helper import AllureReporting
from tests.utils.asserions import Assert, AssertionError
from tests.utils.logger import get_logger

logger = get_logger(__name__)


def get_test_data(
        checklist_runs_client,
        checklists_client,
        machines_client,
        areas_client,
        employees_client,
):
    test_data = {
        'run_id': None,
        'run_machine_id': None,
        'run_employee_id': None,
        'run_checklist_id': None,
        'run_result_status': None,
        'run_started_at': None,

        'employee_badge': None,
        'employee_id': None,
        'checklist_id': None,
        'checklist_task_ids': None,

        'created_machine_id': None,
        'area_id': None,
    }

    logger.info('Fetching first checklist run from API')
    response = checklist_runs_client.get_checklist_runs_list(limit=1, offset=0)
    Assert.response_status(response.status_code, 200)

    runs = response.json()
    Assert.is_not_empty(runs)
    run = runs[0]

    test_data['run_id'] = run.get('run_id')
    test_data['run_machine_id'] = run.get('machine_id')
    test_data['run_employee_id'] = run.get('started_by_employee_id')
    test_data['run_checklist_id'] = run.get('checklist_id')
    test_data['run_result_status'] = run.get('result_status')
    test_data['run_started_at'] = run.get('started_at')

    logger.info(
        f'Run loaded: ID={test_data["run_id"]}, '
        f'Checklist ID={test_data["run_checklist_id"]}',
    )

    logger.info('Fetching first employee for badge')
    response = employees_client.get_employees_list(limit=1, offset=0)
    Assert.response_status(response.status_code, 200)

    employees = response.json()
    Assert.is_not_empty(employees)
    employee = employees[0]

    test_data['employee_badge'] = employee.get('employee_badge')
    test_data['employee_id'] = employee.get('employee_id')

    logger.info(
        f'Employee loaded: ID={test_data["employee_id"]}, '
        f'Badge={test_data["employee_badge"]}',
    )

    logger.info('Fetching area for machine creation')
    response = areas_client.get_areas_list(limit=1, offset=0, is_active=True)
    Assert.response_status(response.status_code, 200)

    areas = response.json()
    Assert.is_not_empty(areas)
    area_id = areas[0].get('area_id')
    test_data['area_id'] = area_id
    logger.info(f'Area loaded: ID={area_id}')

    logger.info('Creating test machine')
    response = machines_client.create_machine(
        machine_name='Test Run Machine',
        area_id=area_id,
    )
    Assert.response_status(response.status_code, 201)
    machine = response.json()
    test_data['created_machine_id'] = machine.get('machine_id')

    logger.info(f'Machine created: ID={test_data["created_machine_id"]}')

    source_checklist_id = test_data['run_checklist_id']

    logger.info(f'Copying checklist {source_checklist_id} to new machine')
    response = checklists_client.copy_checklist(
        source_checklist_id=source_checklist_id,
        target_machine_id=test_data['created_machine_id'],
    )
    Assert.response_status(response.status_code, 201)

    copied_checklist = response.json()
    test_data['checklist_id'] = copied_checklist.get('checklist_id')
    test_data['checklist_task_ids'] = copied_checklist.get('task_id', [])

    logger.info(
        f'Checklist copied: ID={test_data["checklist_id"]}, '
        f'Task IDs={test_data["checklist_task_ids"]}',
    )

    return test_data


@allure.epic('API Tests')
@allure.feature('Checklist Runs API')
@pytest.mark.api
@pytest.mark.checklist_runs
class TestChecklistRunsAPI:

    TEST_INVALID_ID = 9999999
    TEST_INVALID_BADGE = 88888888
    TEST_INVALID_STATUS = 'invalid_status'
    TEST_LIMIT = 10
    TEST_OFFSET = 0

    @pytest.fixture(scope='class')
    def test_data(
            self,
            checklist_runs_client,
            checklists_client,
            machines_client,
            areas_client,
            employees_client,
    ):
        data = get_test_data(
            checklist_runs_client,
            checklists_client,
            machines_client,
            areas_client,
            employees_client,
        )
        yield data

        if data.get('checklist_id'):
            checklists_client.delete_checklist(data['checklist_id'])
            logger.info(
                f'Checklist {data["checklist_id"]} deleted (cleanup)',
            )
        if data.get('created_machine_id'):
            machines_client.delete_machine(data['created_machine_id'])
            logger.info(
                f'Machine {data["created_machine_id"]} deleted (cleanup)',
            )

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-001: Get checklist runs list')
    @pytest.mark.positive
    def test_get_checklist_runs_list(self, checklist_runs_client):

        logger.info(
            f'>>> TEST: Get checklist runs list with limit={self.TEST_LIMIT}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs list with limit={self.TEST_LIMIT}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                limit=self.TEST_LIMIT,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify response'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                Assert.is_not_empty(runs)
                Assert.less_than(len(runs), self.TEST_LIMIT + 1)
                logger.info(f'Retrieved {len(runs)} checklist runs')
            except AssertionError:
                logger.error('Failed to get checklist runs list')
                pytest.fail('Checklist runs list response is empty or invalid')

        with AllureReporting.add_step('Verify run fields'):
            run = runs[0]

            try:
                Assert.has_key(run, 'run_id')
                Assert.has_key(run, 'checklist_id')
                Assert.has_key(run, 'machine_id')
                Assert.has_key(run, 'employee')
                Assert.has_key(run, 'result_status')
                Assert.has_key(run, 'tasks')
                Assert.has_key(run, 'started_at')
                Assert.has_key(run, 'finished_at')
                logger.info(
                    f'Run fields verified for ID={run.get("run_id")}',
                )
            except AssertionError:
                logger.error('Run missing required fields')
                pytest.fail(
                    'Run object missing required fields',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-002: Get checklist run by id')
    @pytest.mark.positive
    def test_get_checklist_run_by_id(self, checklist_runs_client, test_data):

        run_id = test_data.get('run_id')
        logger.info(f'>>> TEST: Get checklist run by ID={run_id}')

        with AllureReporting.add_step(f'Get checklist run by ID: {run_id}'):
            response = checklist_runs_client.get_checklist_runs_list(
                run_id=run_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify run data'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                Assert.has_length(runs, 1)

                run = runs[0]
                Assert.equal(run.get('run_id'), run_id)

                logger.info(
                    f'Run verified: ID={run_id}, '
                    f'Checklist ID={run.get("checklist_id")}',
                )
            except AssertionError:
                logger.error(f'Run data mismatch for ID={run_id}')
                pytest.fail(
                    f'Run with ID {run_id} not found or data mismatch',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-003: Get checklist run by invalid id')
    @pytest.mark.negative
    def test_get_checklist_run_by_invalid_id(self, checklist_runs_client):

        logger.info(
            f'>>> TEST: Get checklist'
            f' run by invalid ID={self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklist run by invalid ID: {self.TEST_INVALID_ID}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                run_id=self.TEST_INVALID_ID,
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
                    'Expected empty response for invalid run ID '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-004: Get checklist runs by machine_id')
    @pytest.mark.positive
    def test_get_checklist_runs_by_machine_id(
            self, checklist_runs_client, test_data,
    ):

        machine_id = test_data.get('run_machine_id')
        logger.info(f'>>> TEST: Get checklist runs by machine_id={machine_id}')

        with AllureReporting.add_step(
            f'Get checklist runs by machine_id={machine_id}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                machine_id=machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify runs by machine'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                Assert.is_not_empty(runs)

                for run in runs:
                    Assert.equal(run.get('machine_id'), machine_id)

                logger.info(
                    f'Found {len(runs)} runs for machine_id={machine_id}',
                )
            except AssertionError:
                logger.error(
                    f'No runs found for machine_id={machine_id}',
                )
                pytest.fail(
                    f'Expected runs for machine_id={machine_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-005: Get checklist runs by invalid machine_id')
    @pytest.mark.negative
    def test_get_checklist_runs_by_invalid_machine_id(
            self, checklist_runs_client,
    ):

        logger.info(
            f'>>> TEST: Get checklist runs by invalid machine_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by invalid machine_id={self.TEST_INVALID_ID}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
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

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-006: Get checklist runs by employee_id')
    @pytest.mark.positive
    def test_get_checklist_runs_by_employee_id(
            self, checklist_runs_client, test_data,
    ):

        employee_id = test_data.get('run_employee_id')
        logger.info(
            f'>>> TEST: Get checklist runs by employee_id={employee_id}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by employee_id={employee_id}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                employee_id=employee_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify runs by employee'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                Assert.is_not_empty(runs)

                for run in runs:
                    Assert.equal(
                        run.get('started_by_employee_id'),
                        employee_id,
                    )

                logger.info(
                    f'Found {len(runs)} runs for employee_id={employee_id}',
                )
            except AssertionError:
                logger.error(
                    f'No runs found for employee_id={employee_id}',
                )
                pytest.fail(
                    f'Expected runs for employee_id={employee_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-007: Get checklist runs by invalid employee_id')
    @pytest.mark.negative
    def test_get_checklist_runs_by_invalid_employee_id(
            self, checklist_runs_client,
    ):

        logger.info(
            f'>>> TEST: Get checklist runs by invalid employee_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by invalid employee_id='
            f'{self.TEST_INVALID_ID}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                employee_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid employee_id',
        ):
            try:
                Assert.response_status(response.status_code, 200)
                Assert.is_empty(response.json())
                logger.info('Received empty response for invalid employee_id')
            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'employee_id={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid employee_id '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-008: Get checklist runs by checklist_id')
    @pytest.mark.positive
    def test_get_checklist_runs_by_checklist_id(
            self, checklist_runs_client, test_data,
    ):

        checklist_id = test_data.get('run_checklist_id')
        logger.info(
            f'>>> TEST: Get checklist runs by checklist_id={checklist_id}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by checklist_id={checklist_id}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                checklist_id=checklist_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify runs by checklist'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                Assert.is_not_empty(runs)

                for run in runs:
                    Assert.equal(run.get('checklist_id'), checklist_id)

                logger.info(
                    f'Found {len(runs)} runs for checklist_id={checklist_id}',
                )
            except AssertionError:
                logger.error(
                    f'No runs found for checklist_id={checklist_id}',
                )
                pytest.fail(
                    f'Expected runs for checklist_id={checklist_id}, '
                    f'but got empty or invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-009: Get checklist runs by invalid checklist_id')
    @pytest.mark.negative
    def test_get_checklist_runs_by_invalid_checklist_id(
            self, checklist_runs_client,
    ):

        logger.info(
            f'>>> TEST: Get checklist runs by invalid checklist_id='
            f'{self.TEST_INVALID_ID}',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by invalid checklist_id='
            f'{self.TEST_INVALID_ID}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                checklist_id=self.TEST_INVALID_ID,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify empty response for invalid checklist_id',
        ):
            try:
                Assert.response_status(response.status_code, 200)
                Assert.is_empty(response.json())
                logger.info('Received empty response for invalid checklist_id')
            except AssertionError:
                logger.error(
                    f'Unexpected response for invalid '
                    f'checklist_id={self.TEST_INVALID_ID}',
                )
                pytest.fail(
                    'Expected empty response for invalid checklist_id '
                    f'{self.TEST_INVALID_ID}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-010: Get checklist runs by result_status')
    @pytest.mark.parametrize('result_status', ['ok', 'failed'])
    @pytest.mark.positive
    def test_get_checklist_runs_by_result_status(
            self, checklist_runs_client, result_status,
    ):

        logger.info(
            f'>>> TEST: Get checklist runs by result_status="{result_status}"',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by result_status="{result_status}"',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                result_status=result_status,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify runs by status'):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()

                for run in runs:
                    Assert.equal(run.get('result_status'), result_status)

                logger.info(
                    f'Found {len(runs)} runs with status="{result_status}"',
                )
            except AssertionError:
                logger.error(
                    f'No runs found for result_status="{result_status}"',
                )
                pytest.fail(
                    f'Expected runs for result_status="{result_status}", '
                    f'but got invalid response',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-011: Get checklist runs by invalid result_status')
    @pytest.mark.negative
    def test_get_checklist_runs_by_invalid_result_status(
            self, checklist_runs_client,
    ):

        logger.info(
            f'>>> TEST: Get checklist runs by invalid result_status='
            f'"{self.TEST_INVALID_STATUS}"',
        )

        with AllureReporting.add_step(
            f'Get checklist runs by invalid result_status='
            f'"{self.TEST_INVALID_STATUS}"',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                result_status=self.TEST_INVALID_STATUS,
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
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for invalid result_status, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-012: Get checklist runs by date_from')
    @pytest.mark.positive
    def test_get_checklist_runs_by_date_from(
            self, checklist_runs_client, test_data,
    ):

        logger.info('>>> TEST: Get checklist runs by date_from')

        started_at = test_data.get('run_started_at')
        created_date = datetime.fromisoformat(
            started_at.replace('Z', '+00:00'),
        )
        date_from_dt = created_date + timedelta(days=1)
        date_from = date_from_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        with AllureReporting.add_step(
            f'Get checklist runs by date_from={date_from}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                date_from=date_from,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify date_from filter excludes test run',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                run_id = test_data.get('run_id')

                for run in runs:
                    run_started_at = run.get('started_at')
                    Assert.is_not_none(run_started_at)
                    Assert.not_equal(run.get('run_id'), run_id)

                logger.info(
                    f'Run {run_id} correctly excluded by date_from filter',
                )
            except AssertionError:
                logger.error('date_from filter did not exclude test run')
                pytest.fail(
                    f'Expected run {run_id} to be excluded by date_from',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Get checklist runs list')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-013: Get checklist runs by date_to')
    @pytest.mark.positive
    def test_get_checklist_runs_by_date_to(
            self, checklist_runs_client, test_data,
    ):

        logger.info('>>> TEST: Get checklist runs by date_to')

        started_at = test_data.get('run_started_at')
        created_date = datetime.fromisoformat(
            started_at.replace('Z', '+00:00'),
        )
        date_to_dt = created_date - timedelta(days=1)
        date_to = date_to_dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        with AllureReporting.add_step(
            f'Get checklist runs by date_to={date_to}',
        ):
            response = checklist_runs_client.get_checklist_runs_list(
                date_to=date_to,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step(
            'Verify date_to filter excludes test run',
        ):
            try:
                Assert.response_status(response.status_code, 200)

                runs = response.json()
                run_id = test_data.get('run_id')

                for run in runs:
                    run_started_at = run.get('started_at')
                    Assert.is_not_none(run_started_at)
                    Assert.not_equal(run.get('run_id'), run_id)

                logger.info(
                    f'Run {run_id} correctly excluded by date_to filter',
                )
            except AssertionError:
                logger.error('date_to filter did not exclude test run')
                pytest.fail(
                    f'Expected run {run_id} to be excluded by date_to',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-014: Create checklist run with all tasks ok')
    @pytest.mark.positive
    def test_create_checklist_run_all_ok(
            self, checklist_runs_client, machines_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run with all tasks ok')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')
        machine_id = test_data.get('created_machine_id')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids
        ]

        with AllureReporting.add_step(
            f'Create run for checklist {checklist_id} with all tasks ok',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify created run'):
            try:
                Assert.response_status(response.status_code, 201)

                run = response.json()

                Assert.equal(run.get('checklist_id'), checklist_id)
                Assert.equal(run.get('result_status'), 'ok')
                Assert.equal(run.get('status'), 'completed')

                tasks_response = run.get('tasks', [])
                Assert.has_length(tasks_response, len(tasks))

                for task in tasks_response:
                    Assert.equal(task.get('is_ok'), True)
                    Assert.has_key(task, 'task_id')

                logger.info(
                    f'Run created with status=ok, '
                    f'checklist_id={checklist_id}',
                )
            except AssertionError:
                logger.error('Failed to create checklist run')
                pytest.fail(
                    f'Run creation failed for checklist {checklist_id}',
                )

        with AllureReporting.add_step(
            f'Verify machine {machine_id} status is ok',
        ):
            response = machines_client.get_machines_list(
                machine_id=machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machine status'):
            try:
                Assert.response_status(response.status_code, 200)

                machines = response.json()
                Assert.has_length(machines, 1)

                machine = machines[0]
                Assert.equal(machine.get('status'), 'ok')

                logger.info(
                    f'Machine {machine_id} status updated to: ok',
                )
            except AssertionError:
                logger.error(
                    f'Machine {machine_id} status should be ok',
                )
                pytest.fail(
                    'Expected machine status to be ok after successful run',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        'API-TC-015: Create checklist run with invalid employee_badge',
    )
    @pytest.mark.negative
    def test_create_checklist_run_invalid_badge(
            self, checklist_runs_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Create checklist run with invalid badge='
            f'{self.TEST_INVALID_BADGE}',
        )

        checklist_id = test_data.get('checklist_id')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids
        ]

        with AllureReporting.add_step(
            f'Create run with'
            f' invalid employee_badge={self.TEST_INVALID_BADGE}',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=self.TEST_INVALID_BADGE,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 404)
                logger.info('Received expected 404 error for invalid badge')
            except AssertionError:
                logger.error(
                    f'Expected 404 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 404 error for invalid employee_badge, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-016: Create checklist run with missing task')
    @pytest.mark.negative
    def test_create_checklist_run_missing_task(
            self, checklist_runs_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run with missing task')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids[:-1]
        ]

        with AllureReporting.add_step(
            f'Create run with missing task (only {len(tasks)} of '
            f'{len(task_ids)} tasks)',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for missing task')
            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for missing task, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-017: Create checklist run with duplicate task')
    @pytest.mark.negative
    def test_create_checklist_run_duplicate_task(
            self, checklist_runs_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run with duplicate task')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids
        ]
        tasks.append({'task_id': task_ids[0], 'is_ok': True})

        with AllureReporting.add_step(
            f'Create run with duplicate task (task {task_ids[0]} twice)',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
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
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for duplicate task, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-018: Create checklist run with invalid task_id')
    @pytest.mark.negative
    def test_create_checklist_run_invalid_task(
            self, checklist_runs_client, test_data,
    ):

        logger.info(
            f'>>> TEST: Create checklist run with invalid task_id='
            f'{self.TEST_INVALID_ID}',
        )

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids
        ]
        tasks.append({'task_id': self.TEST_INVALID_ID, 'is_ok': True})

        with AllureReporting.add_step(
            f'Create run with invalid task_id={self.TEST_INVALID_ID}',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for invalid task')
            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for invalid task_id, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-019: Create checklist run with missing is_ok field')
    @pytest.mark.negative
    def test_create_checklist_run_missing_is_ok(
            self, checklist_runs_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run with missing is_ok field')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_ids[0]},
        ]
        for task_id in task_ids[1:]:
            tasks.append({'task_id': task_id, 'is_ok': True})

        with AllureReporting.add_step(
            f'Create run with missing is_ok field for task {task_ids[0]}',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify error response'):
            try:
                Assert.response_status(response.status_code, 400)
                logger.info('Received expected 400 error for missing is_ok')
            except AssertionError:
                logger.error(
                    f'Expected 400 error, got {response.status_code}',
                )
                pytest.fail(
                    f'Expected 400 error for missing is_ok field, '
                    f'got status {response.status_code}',
                )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title('API-TC-020: Create checklist run for inactive checklist')
    @pytest.mark.negative
    def test_create_checklist_run_inactive_checklist(
            self, checklist_runs_client, checklists_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run for inactive checklist')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids
        ]

        with AllureReporting.add_step(
            f'Deactivate checklist {checklist_id}',
        ):
            response = checklists_client.patch_checklist(
                checklist_id=checklist_id,
                status=False,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify checklist deactivated'):
            try:
                Assert.response_status(response.status_code, 200)

                checklist = response.json()
                Assert.equal(checklist.get('checklist_id'), checklist_id)
                Assert.equal(checklist.get('status'), False)
                logger.info(f'Checklist {checklist_id} deactivated')
            except AssertionError:
                logger.error('Failed to deactivate checklist')
                pytest.fail(f'Checklist {checklist_id} deactivation failed')

        try:
            with AllureReporting.add_step(
                f'Create run for inactive checklist {checklist_id}',
            ):
                response = checklist_runs_client.create_checklist_run(
                    checklist_id=checklist_id,
                    employee_badge=employee_badge,
                    tasks=tasks,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify error response'):
                try:
                    Assert.response_status(response.status_code, 400)
                    logger.info(
                        'Received expected 400 error for inactive checklist',
                    )
                except AssertionError:
                    logger.error(
                        f'Expected 400 error, got {response.status_code}',
                    )
                    pytest.fail(
                        f'Expected 400 error for inactive checklist, '
                        f'got status {response.status_code}',
                    )

        finally:
            with AllureReporting.add_step(
                f'Reactivate checklist {checklist_id}',
            ):
                response = checklists_client.patch_checklist(
                    checklist_id=checklist_id,
                    status=True,
                )
                AllureReporting.attach_response(
                    response.status_code,
                    response.json(),
                )

            with AllureReporting.add_step('Verify checklist reactivated'):
                try:
                    Assert.response_status(response.status_code, 200)

                    checklist = response.json()
                    Assert.equal(checklist.get('checklist_id'), checklist_id)
                    Assert.equal(checklist.get('status'), True)
                    logger.info(f'Checklist {checklist_id} reactivated')
                except AssertionError:
                    logger.error('Failed to reactivate checklist')
                    pytest.fail(
                        f'Checklist {checklist_id} reactivation failed',
                    )

        logger.info('<<< TEST PASSED')

    @allure.story('Create checklist run')
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title(
        'API-TC-021: Create checklist'
        ' run with failed task - machine goes to accident',
    )
    @pytest.mark.positive
    def test_create_checklist_run_with_failed_task(
            self, checklist_runs_client, machines_client, test_data,
    ):

        logger.info('>>> TEST: Create checklist run with failed task')

        checklist_id = test_data.get('checklist_id')
        employee_badge = test_data.get('employee_badge')
        task_ids = test_data.get('checklist_task_ids')
        machine_id = test_data.get('created_machine_id')

        tasks = [
            {'task_id': task_id, 'is_ok': True}
            for task_id in task_ids[:-1]
        ]
        tasks.append({
            'task_id': task_ids[-1],
            'is_ok': False,
            'comment': 'Test failure',
        })

        with AllureReporting.add_step(
            f'Create run with failed task {task_ids[-1]}',
        ):
            response = checklist_runs_client.create_checklist_run(
                checklist_id=checklist_id,
                employee_badge=employee_badge,
                tasks=tasks,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify run with failed status'):
            try:
                Assert.response_status(response.status_code, 201)

                run = response.json()

                Assert.equal(run.get('checklist_id'), checklist_id)
                Assert.equal(run.get('result_status'), 'failed')
                Assert.equal(run.get('status'), 'completed')

                tasks_response = run.get('tasks', [])
                Assert.has_length(tasks_response, len(tasks))

                last_task = tasks_response[-1]
                Assert.equal(last_task.get('is_ok'), False)
                Assert.equal(last_task.get('comment'), 'Test failure')

                logger.info(
                    f'Run created with result_status=failed, '
                    f'checklist_id={checklist_id}',
                )
            except AssertionError:
                logger.error('Failed to create checklist run with failed task')
                pytest.fail(
                    f'Run creation failed for checklist {checklist_id}',
                )

        with AllureReporting.add_step(
            f'Verify machine {machine_id} status is accident',
        ):
            response = machines_client.get_machines_list(
                machine_id=machine_id,
            )
            AllureReporting.attach_response(
                response.status_code,
                response.json(),
            )

        with AllureReporting.add_step('Verify machine status'):
            try:
                Assert.response_status(response.status_code, 200)

                machines = response.json()
                Assert.has_length(machines, 1)

                machine = machines[0]
                Assert.equal(machine.get('status'), 'accident')

                logger.info(
                    f'Machine {machine_id} status updated to: accident',
                )
            except AssertionError:
                logger.error(
                    f'Machine {machine_id} status should be accident',
                )
                pytest.fail(
                    'Expected machine status to be accident after failed run',
                )

        logger.info('<<< TEST PASSED')
