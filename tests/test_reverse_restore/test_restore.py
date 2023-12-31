import logging
import pytest
import requests

from utils.pytest_utils import _assert_resource_available
from utils.pytest_utils import _calculate_reversed_expected_result_str
from utils.pytest_utils import _long_list_generator
from utils.pytest_utils import containerized_app_resrouce

class TestClassRestoreApi:
    """
    Grouping tests based on API endpoing - /restore test coverage
    """
    def test_restore_api_sanity(self, containerized_app_resrouce):
        logging.info(f'Sanity validation for contenerized_app with properties of ---> {containerized_app_resrouce}')
        reverse_api_path = containerized_app_resrouce.resource_api[0]
        restore_api_path = containerized_app_resrouce.resource_api[1]
        reverse_url = containerized_app_resrouce.get_test_url(api_path=reverse_api_path)
        restore_url = containerized_app_resrouce.get_test_url(api_path=restore_api_path)
        _assert_resource_available(reverse_url)
        _assert_resource_available(restore_url)
        # step1 -> populate /reverse with known data -> preperation
        logging.info(f'executing test against: {restore_url}')
        list_size = 100
        tested_input_str = _long_list_generator(list_size)
        expected_reverse_result = _calculate_reversed_expected_result_str(tested_input_str)
        request_data = {'in': tested_input_str}
        reverse_response = requests.get(reverse_url, params=request_data)
        reverse_response_dict = reverse_response.json()
        reverse_actual_result = reverse_response_dict.get('result')
        logging.info(f'Validating status code of: {reverse_url}')
        assert reverse_response.status_code == 200
        logging.info(f'Validating expected result of: {reverse_url}')
        assert reverse_actual_result == expected_reverse_result
        # step2 -> same data should be retrieved from /restore
        restore_response = requests.get(restore_url)
        logging.info(f'Validating status code of: {restore_response}')
        assert restore_response.status_code == 200
        restore_response_dict = restore_response.json()
        restore_actual_result = restore_response_dict.get('result')
        logging.info(f'Validating expected result of: {restore_url}')
        logging.warning('potential race condition ---> if another request sent at same time to /reverse ---> it may override cahced value')
        assert reverse_actual_result == expected_reverse_result

    def test_restore_api_no_last_value(self, containerized_app_resrouce):
        url = "http://localhost:5000/not_existing_api"
        response = requests.head(url)
        assert response.status_code != 200

