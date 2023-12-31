import logging
import pytest
import requests

from utils.pytest_utils import _assert_resource_available
from utils.pytest_utils import _calculate_reversed_expected_result_str
from utils.pytest_utils import _long_list_generator
from utils.pytest_utils import containerized_app_resrouce

class TestClassApiPerformance:
    """
    basic test cases for performace verification
    """
    def test_response_time(self, api_str = ''):
        """
        collects baseline stats for APIs - response latency, meassured in ms or us
        """
        pass

    def test_requests_per_minute(self, api_str = ''):
        """
        collects baseline stats for APIs - requests per minute,
        optinal values for requests_per_minute [1, 10, 100, 1000, ...]
        """
        pass

    def test_max_stress(self, api_str = ''):
        """
        1. max elements in request,
        2. max elements in response
        optinal values for requests_per_minute [1, 10, 100, 1000, ...]
        """
        pass

    def test_uptime(self, api_str = ''):
        """
        collect data for usage of CPU, memory, storage, network throughput, over time,
        interesting data points - 
        [1second, 5seconds, 30seconds, 1minute, 1hour, 3hours, 
            10hours, 24hours, 2days, 10days, 30days, and super strech of months]
        """
        pass

