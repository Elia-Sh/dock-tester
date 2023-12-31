#!/usr/bin/env python3
import argparse
import logging
from logging.handlers import RotatingFileHandler
import json
from xml.dom.minidom import parse
import os
from pprint import pformat
import pytest
import requests

from utils.docker_handler import DokerHandler
from utils.config_handler import ConfigHandler


def main(cmd_args):
    """
    entry point, uses arguments provided via command line,
    abstracting pytest and docker implenations,
    providing a simple to cmd utility 
    """
    utility_name = os.path.splitext(os.path.basename(__file__))[0]
    framework_confing_dict = {
        'junint_file_name': 'results_junit.xml',
        'fail-safety': True,
        'verbose_mode': True,
        'open_pdb_on_test_failure': True,
        'logfile_path': f'logs/{utility_name}.log',
        'mount_local_volume': False     #future feature
    }
    setup_logger(framework_confing_dict)
    logging.info('Welcome to docker experimental testing framework')
    app_config_json = read_config_file()

    if cmd_args.stop_container_app == True:
        stop_container_app(app_config_json)
    if cmd_args.start_container_app == True:
        start_container_app(app_config_json)
    if cmd_args.list_tests:
        list_existing_tests(cmd_args.list_tests)
    if cmd_args.run_tests:
        run_tests(cmd_args.run_tests, framework_confing_dict, app_config_json)
    if cmd_args.add_new_test:
        add_new_test()
    if cmd_args.list_last_result:
        list_last_result(framework_confing_dict)
    if cmd_args.publish_last_result:
        publish_junit(framework_confing_dict)
### end main() ###




def setup_logger(test_framework_confing_dict):
    # future improvement - logs rotation, based on file size,
    # i.e logfile.1.log, logfile.2.log, etc
    logfile_path = test_framework_confing_dict.get('logfile_path')
    logs_directory_path = os.path.abspath(os.path.dirname(logfile_path))
    os.makedirs(logs_directory_path, exist_ok=True)
    log_formatter =    logging.Formatter('%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d %(message)s',
                                  datefmt='%Y%m%d.%H:%M:%S')
    stream_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                                  datefmt='%Y%m%d.%H:%M:%S')
    #Setup File handler
    # file_handler = logging.FileHandler(logfile_path)
    max_log_file_size_bytes = 10 * 1000 * 1000   # 10 MB
    file_handler = RotatingFileHandler(logfile_path, 
        maxBytes=max_log_file_size_bytes, backupCount=10)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    #Setup Stream Handler (i.e. console)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.INFO)

    #Get our logger
    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    #Add both Handlers
    app_log.addHandler(file_handler)
    app_log.addHandler(stream_handler)


def execute_self_test(params_params):
    """
    Future feature - 
    examples for self-test potential provided functionality - 
        - check if docker host is reachable
        - check if requierments installed
        - check if app_config is valid
        - check if framework_config is valid
    """
    logging.info(f'Running self-test')


def publish_junit(config_dict):
    junint_file_name = config_dict.get('junint_file_name')
    url = 'http://localhost/reporting-system/v1/publish-latest'
    files = {'file': open(junint_file_name, 'rb')}
    try:
        response = requests.post(url, files=files)
    except requests.exceptions.ConnectionError as ex:
        logging.error(f'Was not able to publish: {junint_file_name} to: {url}')
        exit(1)
    return response.text
    

def read_config_file():
    app_config_dict = ConfigHandler.get_config_from_dockerfile()
    logging.info(f'app_config_dict: {app_config_dict}')
    return app_config_dict


def list_existing_tests(tests_directories_str = ''):
    logging.info('pytest --collect-only')
    retcode = pytest.main(['--collect-only', tests_directories_str])


def list_last_result(test_framerwork_config={}):
    results_file_name = test_framerwork_config.get('junint_file_name')
    logging.info(f'listing last results from: {results_file_name}')
    if not os.path.isfile(results_file_name):
        logging.error(f'was not able find file: {results_file_name}')
        exit(1)
    summery_dict = {}
    testcases_results_summary_list = []
    with open(results_file_name) as file:
        xml_minioom_obj = parse(file)
        summery_obj = xml_minioom_obj.getElementsByTagName('testsuite').pop()
        summery_dict = dict(summery_obj.attributes.items())
        test_cases_xml_list = xml_minioom_obj.getElementsByTagName('testcase')
        for testcase_xml_obj in test_cases_xml_list:
            name_attr = testcase_xml_obj.attributes.get('name')
            test_result_dict = {
                'testcase_name': name_attr.value,
                'testcase_pass': True
            }
            if testcase_xml_obj.hasChildNodes():
                # simple indicator for failure in junit XML
                test_result_dict['testcase_pass'] = False
            testcases_results_summary_list.append(test_result_dict)
    if summery_dict:
        logging.info(summery_dict)
        logging.info(f'summary of tests -\n{pformat(testcases_results_summary_list)}')
    else:
        logging.error(f'was not able to parse testuite in junit result: {results_file_name}')
        exit(1)


def start_container_app(app_config):
    image_name = app_config.get('tested_resource_name')
    logging.info(f'Starting container app ---> using image {image_name}')
    new_container_obj = DokerHandler.start_container(app_config)
    container_name = new_container_obj.name
    container_id = new_container_obj.id[:12]
    logging.info(f'Started new container ---> name: {container_name}, id: {container_id}')


def stop_container_app(app_config, cleanup=False):
    image_name = app_config.get('tested_resource_name')
    containers_list = DokerHandler.get_containers_list(image_name)
    if not containers_list:
        logging.info(f'No containers found for app with image: {image_name}')
    elif len(containers_list) > 1:
        logging.info(f'Detected {len(containers_list)} containers for app: {image_name}')
        DokerHandler.stop_container(image_name=image_name)
    else:
        logging.info(f'Stopping single instance of: {image_name}')
        container_name = containers_list.pop().name
        DokerHandler.stop_container(container_name=container_name)    
    if cleanup:
        # import ipdb; ipdb.set_trace()
        logging.info(f'will delete stopped containers: {image_name}')
        DokerHandler.cleanup(app_config)


def test_setup(app_config):
    image_name = app_config.get('tested_resource_name')
    containers_list = DokerHandler.get_containers_list(image_name=image_name)
    if not containers_list:
        logging.info(f'No containers found for app with image: {image_name}')
        start_container_app(app_config)
    else:
        logging.info(f'Found existing containers for app with image: {image_name}, reusing')


def test_teardown(app_config, test_framerwork_config, pytest_return_code_enum):
    stop_app_on_tests_failure_bool = test_framerwork_config.get('fail-safety')
    if pytest_return_code_enum == 1:
        logging.warning(f'pytest return code: {repr(pytest_return_code_enum)}')
        if stop_app_on_tests_failure_bool:
            logging.warning('Fail-Safety: Stopping app on tests failure')
            stop_container_app(app_config)
        else:
            logging.warning(f'fail-safe disabled in framework config, not stopping container')
    elif pytest_return_code_enum == 0:
        logging.info('no failures detected, no need to stop app, keep rocking')


def run_tests(pytest_predicates='',
        test_framerwork_config={},
        app_config={}):
    """
    A pytest predicate can be:
        * tests_directory
        * marker
        * testFile::testsClass::TestFunction
        * debug (i.e -x)
    """
    test_setup(app_config)
    results_file_name = test_framerwork_config.get('junint_file_name')
    open_pdb_on_test_failure = test_framerwork_config.get('open_pdb_on_test_failure')
    verbose_mode = test_framerwork_config.get('verbose_mode')
    logging.info(f'Running tests, pytest_predicates: {pytest_predicates}')
    pytest_args_list = [f'--junitxml={results_file_name}', pytest_predicates]
    if open_pdb_on_test_failure:
        # used for troubleshooting test failures
        pytest_args_list.insert(0,'-x')
        pytest_args_list.insert(0,'--pdb')
    if verbose_mode:
        pytest_args_list.insert(0,'-rA')
    retcode = pytest.main(pytest_args_list)
    if retcode != 0:
        logging.warning('TESTS FAILED, see pytest log for more details.')
    test_teardown(app_config, test_framerwork_config, retcode)


def add_new_test():
    """
    Future feature - 
        1. creates a new "test_component" in tests dir
        2. contents of new dir will be pytest base test skeleton with:
        2.1. tested resource definition, represted by class name TestedResource - a.k.a actor
        2.2. and a basic test class which name prefixed with "TestClass" and user provided suffix 
    """
    logging.info(f'Adding a new test into tests dir')
    raise NotImplemented


### command line arguments parser ###
parser = argparse.ArgumentParser()
args_group = parser.add_mutually_exclusive_group()
args_group.add_argument('--start-container-app', '-s',
    action='store_true',
    help='start tested app.py container')
args_group.add_argument('--stop-container-app', '-k',
    action='store_true',
    help='stop tested app.py container')
args_group.add_argument('--list-tests',
    nargs='?', const='./tests', type=str,
    help='lists existing pytest tests')
args_group.add_argument('--list-last-result' ,action='store_true',
    help='list last execution from junit xml')
args_group.add_argument('--publish-last-result' ,action='store_true',
    help='list last execution from junit xml')
args_group.add_argument('--add-new-test', nargs=1,
    help='Add new test class')
args_group.add_argument('--run-tests', nargs='?', const='./tests',
    help='execute tests')


if __name__ == "__main__":
    # Fully Supported commands:
        # start_app
        # stop_app
        # list_tests
        # list_last_result
        # run_tests
        # publish_junit
    # dev commands -> implemented, not exposed
        # rebuild image from Dockerfile
        # cleanup -> for stopped app containers
    # Future extensions
        # add test
        # self-test
    cmd_args = parser.parse_args()
    if not any(vars(cmd_args).values()):
        parser.print_help()
        exit(0)
    main(cmd_args)
