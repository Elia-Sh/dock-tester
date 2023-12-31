import logging
import pytest
import requests

from utils.pytest_utils import _assert_resource_available
from utils.pytest_utils import _calculate_reversed_expected_result_str
from utils.pytest_utils import _long_list_generator
from utils.pytest_utils import containerized_app_resrouce


class TestClassApiRas:
    """
    RAS - Reliability, availability and serviceability
    """
    def test_restart_containerized_app_process(self):
        """
        kill process of running app in container
        * relevant to /restore -> will have empty cache
        """
        pass

    def test_restart_containerized_app(self):
        """
        scale horizontally or failover app to new container ->
        * relevant to /restore -> will have empty cache
        * also relevant to scaling applicating -> for example start app on two containers simultaneously
        """
        pass

    def test_upgrades(self):
        """
        Upgrade can be defined in multiple ways - 
            api changes
            schema/config changes
        * hot upgrade?
        * how long it takes to accomplish the upgrade -
        * rollbascks in case of disaster
        """
        pass