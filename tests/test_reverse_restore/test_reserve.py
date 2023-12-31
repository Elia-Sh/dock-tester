import logging
import pytest
import requests

from utils.pytest_utils import _assert_resource_available
from utils.pytest_utils import _calculate_reversed_expected_result_str
from utils.pytest_utils import _long_list_generator
from utils.pytest_utils import containerized_app_resrouce


class TestClassReverseApi:
    """
    Grouping tests based on API - for /reverse endpoint
    """
    def test_reverse_api_sanity(self, containerized_app_resrouce):
        logging.info(f'Sanity validation for contenerized_app with properties of ---> {containerized_app_resrouce}')
        reverse_api_path = containerized_app_resrouce.resource_api[0] # this is reverse API
        url = containerized_app_resrouce.get_test_url(api_path=reverse_api_path)
        logging.info(f'executing test against: {url}')
        _assert_resource_available(url)
        tested_input = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        # note explicit definition of expected_reult for "sanity",
        # -> in order not to rely on external component for "recalculation" of expected result
        expected_result = 'elit. adipiscing consectetur amet, sit dolor ipsum Lorem' # explicit definition 
        request_data = {'in': tested_input}
        response = requests.get(url, params=request_data)
        response_dict = response.json()
        actual_result = response_dict.get('result')
        logging.info('Validating status code of request')
        assert response.status_code == 200
        logging.info('Comparing expected result to result from endpoint')
        assert actual_result == expected_result

    def test_reverse_algorithm(self, containerized_app_resrouce):
        reverse_api_path = containerized_app_resrouce.resource_api[0] # this is reverse API
        url = containerized_app_resrouce.get_test_url(api_path=reverse_api_path)
        logging.info(f'executing test against: {url}')
        _assert_resource_available(url)
        relaxed_list_sizes = [0, 1, 42, 149]   # bigger values covered in performace section
        for list_size in relaxed_list_sizes:
            tested_input_str = _long_list_generator(list_size)
            logging.info(f'Validating reverse of object with {list_size} elements ')
            expected_result = _calculate_reversed_expected_result_str(tested_input_str)
            request_data = {'in': tested_input_str}
            response = requests.get(url, params=request_data)
            response_dict = response.json()
            actual_result = response_dict.get('result')
            logging.info('Validating status code of request')
            assert response.status_code == 200
            logging.info('Comparing expected result to result from endpoint')
            assert actual_result == expected_result

        logging.info('Validating reverse of empty string')
        empty_input_request_data = {'in': ''}
        expected_result = ''
        response = requests.get(url, params=empty_input_request_data)
        response_dict = response.json()
        actual_result = response_dict.get('result')
        logging.info('Validating status code of request')
        assert response.status_code == 200
        logging.info('Comparing expected result to result from endpoint')
        assert actual_result == expected_result

    def test_not_valid_input_format(self, containerized_app_resrouce):
        reverse_api_path = containerized_app_resrouce.resource_api[0] # this is reverse API
        url = containerized_app_resrouce.get_test_url(api_path=reverse_api_path)
        negative_input_str = "[['asfasfaf', ['asfasf']],{asfasf}', \\\'asfasf\\\2`']"
        negative_input_expected_result = _calculate_reversed_expected_result_str(negative_input_str)
        logging.info(f'testing {negative_input_str} against: {url}')
        logging.info('since input is still a string, but with unexpected chars, it can be reversed')
        logging.info('expecting - request success')
        request_data_negative_input_str = {'in': negative_input_str}
        response_negative_input = requests.get(url,params=request_data_negative_input_str)
        result_negative_input = response_negative_input.json().get('result')
        assert response_negative_input.status_code == 200
        logging.info('Comparing expected result to result from endpoint')
        assert result_negative_input == negative_input_expected_result

        logging.info(f'testing incorrecrt query parameter against: {url}')
        request_data_incorrect_param = {'foobar': 'this is not "in" query parameter'}
        response_incorrect_param = requests.get(url,params=request_data_incorrect_param)
        result_negative_input = response_incorrect_param.json().get('result')
        assert response_incorrect_param.status_code == 200
        logging.info('Comparing expected result to result from endpoint')
        assert result_negative_input == '', 'use of foobar as query parameter implictly states in=""'

    def test_not_existing_api(self, containerized_app_resrouce):
        url_root = containerized_app_resrouce.get_test_url(api_path='')
        not_existing_urls_list = [url_root, f'{url_root}notexistingurl']
        for url in not_existing_urls_list:
            logging.info(f'executing test against: {url}')
            response = requests.get(url)
            assert response.status_code == 404

    def test_not_supported_crud(self, containerized_app_resrouce):
        not_supported_operations_list = ['POST', 'PUT', 'DELETE']
        reverse_api_path = containerized_app_resrouce.resource_api[0] # this is reverse API
        url = containerized_app_resrouce.get_test_url(api_path=reverse_api_path)
        logging.info(f'executing test against: {url}')
        for request_method in not_supported_operations_list:
            logging.info(f'testing method: {request_method}')
            response = requests.request(request_method, url)
            assert response.status_code == 405

