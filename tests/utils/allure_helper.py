import allure
from typing import Any, Dict, Optional
import json


class AllureReporting:
    """Allure reporting helper class."""

    @staticmethod
    def attach_request(
            method: str,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            payload: Optional[Dict[str, Any]] = None,
    ):
        """Attach API request to Allure report"""

        full_url = url
        if params:
            param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            full_url = f'{url}?{param_string}'

        request_info = f'{method} {full_url}'

        if params:
            request_info += (
                f'\n\nQuery Parameters:'
                f'\n{json.dumps(params, indent=2, ensure_ascii=False)}',
            )

        if payload:
            request_info += (
                f'\n\nRequest Body:'
                f'\n{json.dumps(payload, indent=2, ensure_ascii=False)}',
            )

        allure.attach(request_info, 'API Request', allure.attachment_type.TEXT)

    @staticmethod
    def attach_response(
            status_code: int, response_body: Optional[Dict[str, Any]] = None,
    ):
        """Attach API response to Allure report"""

        response_info = f'Status Code: {status_code}\n'
        if response_body:
            response_info += (
                f'\nResponse Body:\n{json.dumps(response_body, indent=2)}'
            )

        allure.attach(
            response_info, 'api_response', allure.attachment_type.TEXT,
        )

    @staticmethod
    def attach_screenshot(screenshot_path: str, name: str = 'screenshot'):
        """Attach screenshot to Allure report"""

        with open(screenshot_path, 'rb') as file:
            allure.attach.file(
                file,
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )

    @staticmethod
    def add_step(title: str):
        """Add step to Allure report"""

        return allure.step(title)

    @staticmethod
    def attach_log(log_content: str, name: str = 'log'):
        """Attach log file to Allure report"""

        allure.attach(log_content, name, allure.attachment_type.TEXT)
