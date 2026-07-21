from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tests.utils.logger import get_logger
import json

logger = get_logger(__name__)


class BaseApiClient:
    """Base API client"""

    def __init__(self, base_url, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create new session with retry strategy"""

        session = requests.Session()

        retry_kwargs = dict(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
        )
        allowed = ['HEAD', 'GET', 'OPTIONS']
        try:
            retry_strategy = Retry(**retry_kwargs, allowed_methods=allowed)
        except TypeError:
            retry_strategy = Retry(**retry_kwargs, method_whitelist=allowed)

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def _log_request(self, method: str, url: str, **kwargs):
        """Log request"""

        logger.info(f'>>> {method} {url}')
        if 'json' in kwargs:
            logger.debug(
                f"Request body: {json.dumps(kwargs['json'], indent=2)}",
            )
        if 'data' in kwargs:
            logger.debug(f"Request data: {kwargs['data']}")

    def _log_response(self, response: requests.Response):
        """Log response"""

        logger.info(f'<<< {response.status_code} {response.url}')
        try:
            logger.debug(
                f'Response body: {json.dumps(response.json(), indent=2)}',
            )
        except Exception:
            logger.debug(f'Response body: {response.text}')

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """Execute GET request"""

        url = f'{self.base_url}{endpoint}'
        self._log_request('GET', url, params=params)
        response = self.session.get(
            url, params=params, timeout=self.timeout, **kwargs,
        )
        self._log_response(response)

        return response

    def post(
            self,
            endpoint: str,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[Any] = None,
            **kwargs,
    ) -> requests.Response:
        """Execute POST request"""

        url = f'{self.base_url}{endpoint}'
        self._log_request('POST', url, json=json, data=data)
        response = self.session.post(
            url, json=json, data=data, timeout=self.timeout, **kwargs,
        )
        self._log_response(response)

        return response

    def put(
            self,
            endpoint: str,
            json: Optional[Dict[str, Any]] = None,
            **kwargs,
    ) -> requests.Response:
        """Execute PUT request"""

        url = f'{self.base_url}{endpoint}'
        self._log_request('PUT', url, json=json)
        response = self.session.put(
            url, json=json, timeout=self.timeout, **kwargs,
        )
        self._log_response(response)

        return response

    def patch(
            self,
            endpoint: str,
            json: Optional[Dict[str, Any]] = None,
            **kwargs,
    ) -> requests.Response:
        """Execute PATCH request"""

        url = f'{self.base_url}{endpoint}'
        self._log_request('PATCH', url, json=json)
        response = self.session.patch(
            url, json=json, timeout=self.timeout, **kwargs,
        )
        self._log_response(response)

        return response

    def delete(
            self,
            endpoint: str,
            **kwargs,
    ) -> requests.Response:
        """Execute DELETE request"""

        url = f'{self.base_url}{endpoint}'
        self._log_request('DELETE', url)
        response = self.session.delete(
            url, timeout=self.timeout, **kwargs,
        )
        self._log_response(response)

        return response

    def close(self):
        """Close session"""

        self.session.close()
        logger.info('Session closed')
