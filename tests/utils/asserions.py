from typing import Any, Optional


class AssertionError(Exception):
    """Custom assertion error"""

    pass


class Assert:
    """Custom assertion helper class"""

    @staticmethod
    def equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert that actual equals expected"""

        if actual != expected:
            msg = message or f'Expected {expected}, but got {actual}'
            raise AssertionError(msg)

    @staticmethod
    def not_equal(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert that actual does not equal expected"""

        if actual == expected:
            msg = (
                message
                or f'Expected not equal to {expected}, but got {actual}'
            )

            raise AssertionError(msg)

    @staticmethod
    def is_true(condition: bool, message: Optional[str] = None):
        """Assert that condition is True"""

        if not condition:
            msg = message or 'Expected condition to be True'
            raise AssertionError(msg)

    @staticmethod
    def is_false(condition: bool, message: Optional[str] = None):
        """Assert that condition is False"""

        if condition:
            msg = message or 'Expected condition to be False'
            raise AssertionError(msg)

    @staticmethod
    def is_none(value: Any, message: Optional[str] = None):
        """Assert that value is None"""

        if value is not None:
            msg = message or f'Expected None, but got {value}'
            raise AssertionError(msg)

    @staticmethod
    def is_not_none(value: Any, message: Optional[str] = None):
        """Assert that value is not None"""

        if value is None:
            msg = message or 'Expected not None'
            raise AssertionError(msg)

    @staticmethod
    def is_empty(value: Any, message: Optional[str] = None):
        """
        Assert that value is empty
        (None, empty string, empty list, empty dict)
        """

        if value is not None and value != '' and value != [] and value != {}:
            msg = message or f'Expected empty value, but got {value}'
            raise AssertionError(msg)

    @staticmethod
    def is_not_empty(value: Any, message: Optional[str] = None):
        """
        Assert that value is not empty
        (not None, not empty string, not empty list, not empty dict)
        """

        if value is None or value == '' or value == [] or value == {}:
            msg = message or f'Expected non-empty value, but got {value}'
            raise AssertionError(msg)

    @staticmethod
    def contains(container: Any, item: Any, message: Optional[str] = None):
        """Assert that container contains item"""

        if item not in container:
            msg = message or f'Expected {item} to be in {container}'
            raise AssertionError(msg)

    @staticmethod
    def not_contains(container: Any, item: Any, message: Optional[str] = None):
        """Assert that container does not contain item"""

        if item in container:
            msg = message or f'Expected {item} not to be in {container}'
            raise AssertionError(msg)

    @staticmethod
    def is_instance(obj: Any, cls: type, message: Optional[str] = None):
        """Assert that object is instance of class"""

        if not isinstance(obj, cls):
            msg = message or f'Expected {obj} to be instance of {cls}'
            raise AssertionError(msg)

    @staticmethod
    def has_key(data: dict, key: str, message: Optional[str] = None):
        """Assert that dictionary has key"""

        if key not in data:
            msg = message or f"Expected key '{key}' in {list(data.keys())}"
            raise AssertionError(msg)

    @staticmethod
    def response_status(
            status_code: int, expected: int, message: Optional[str] = None,
    ):
        """Assert response status code"""

        if status_code != expected:
            msg = message or f'Expected status {expected}, got {status_code}'
            raise AssertionError(msg)

    @staticmethod
    def has_length(
            collection: Any, expected: int, message: Optional[str] = None,
    ):
        """Assert that collection has expected length"""

        actual_length = len(collection)
        if actual_length != expected:
            msg = message or f'Expected length {expected}, got {actual_length}'
            raise AssertionError(msg)

    @staticmethod
    def greater_than(
            actual: Any, expected: Any, message: Optional[str] = None,
    ):
        """Assert that actual is greater than expected"""

        if actual <= expected:
            msg = message or f'Expected {actual} > {expected}'
            raise AssertionError(msg)

    @staticmethod
    def less_than(actual: Any, expected: Any, message: Optional[str] = None):
        """Assert that actual is less than expected"""

        if actual >= expected:
            msg = message or f'Expected {actual} < {expected}'
            raise AssertionError(msg)
