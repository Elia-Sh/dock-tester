import logging
import pytest
import requests
from faker import Faker

from .docker_handler import DokerHandler
from .config_handler import ConfigHandler


class TestedResource:
    """
    A Model representing tested element, constructed during runtime,
    based on app_config, passed via fixture to test cases
    """
    __test__ = False
    image_name=''
    resource_api = ''
    exposed_ports = ''
    def __init__(self):
        resource_config = ConfigHandler.get_config_from_dockerfile(silent=True)
        if not resource_config.values():
            logging.error('Error getting app config')
            raise ConnectionError('Failure reading app configuration')
        self.image_name = resource_config.get('tested_resource_name')
        self.exposed_ports = resource_config.get('exposed_ports')
        self.resource_api = resource_config.get('tested_apis_list')
    def get_test_url(self, schema='http', hostname='127.0.0.1', api_path=''):
        api_url = f'{schema}://{hostname}:{self.exposed_ports}/{api_path}'
        return api_url
    def __str__(self):
        return f'image_name: {self.image_name}, exposed_ports: {self.exposed_ports}, resource_api: {self.resource_api}'



@pytest.fixture(scope='session', autouse=True)
def containerized_app_resrouce():
    """
    pytest fixture to pass app_config model to tests
    """
    logging.info("pytest app resource setup")
    tested_resource = TestedResource()
    containers_list = DokerHandler.get_containers_list(image_name=tested_resource.image_name)
    if not containers_list:
        no_app_container_error_message = \
            'app_resource: was not able to find containers for: {}'.format(tested_resource.image_name)
        logging.info(no_app_container_error_message)
        logging.info('hint -> maybe rebuild image')
        raise Exception(no_app_container_error_message)
    container_test_resource = containers_list.pop()
    latest_image_sha = DokerHandler.get_latest_image_shasum(tested_resource.image_name)
    container_image_sha = container_test_resource.image.id
    if not latest_image_sha == container_image_sha:
        logging.warning(f'app container for: {tested_resource.image_name} is not latest version')
        logging.warning(f'container image sha: {container_image_sha};')
        logging.warning(f'latest image sha: {latest_image_sha}')
    yield tested_resource
    logging.info("pytest app resource teardown")


def _assert_resource_available(api_str = ''):
    assert api_str, 'api_str is the tested resource, cant be empty'
    response = requests.head(api_str)
    assert response.status_code == 200


def _long_list_generator(list_len=0):
    """
    Helper method to generate dummy data
    """
    if list_len == 0:
        long_list_str = ''
    else:
        fake = Faker()
        long_list_str = fake.sentence(nb_words=list_len, variable_nb_words=False)
    return long_list_str

def _calculate_reversed_expected_result(a_list_of_elements=[]):
    """
    Helper method for abstraction expected resultsand future proofing api changes 
    
    note the limiting ability to calculate expected results,
    in future this task may-be offloaded to dedicated compute node
    """
    # simple case for /reverse API endpoint -
    assert type(a_list_of_elements) == list
    reversed_list = a_list_of_elements[::-1]
    return reversed_list

def _calculate_reversed_expected_result_str(elemts_str='') -> str:
    """
    string wrapper
    """
    a_list_of_elements = elemts_str.split()
    reversed_list = _calculate_reversed_expected_result(a_list_of_elements)
    reversed_str = ' '.join(reversed_list)
    return reversed_str

    