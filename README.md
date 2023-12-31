

# Setup
1. git clone and cd into cloned directory
```
git clone git@github.com/elia-sh/dock-tester
cd <dock-tester>
```
2. activate venv
```
python3 -m venv
source venv/bin/activate
```
3. install requierments
```
pip install -r requierments.txt
```


# Usage

* TLDR; Run tests for an API components 
```
./dockt-cli.py --run-test
```

## Definitions
0. `tests` folder contains pytest tests which will be executed against tested element
1. `src` folder contains source code for containerized app providing `/reverse` and `/restore` APIs
2. by parsing dockerfile for arguments and directives,
a description of tested object will be constrcuted in run-time, also known as: `app_config_dict`,
3. this allows decoupling of "test actor", "test bed" and testing framework

example for meaningful defitions in dockerfile, which converted to `app_config_dict`
```
ARG APP_NAME=reverse_words_v1
...
...
EXPOSES 5000
```

## Usage Details
* Starts the and stop containerized tested resource
```
./dockt-cli.py --start-container-app
./dockt-cli.py --stop-container-app
```

* Execute all tests in directory
```
./dockt-cli.py --run-test ./tests
```
* Execute single testcase
```
./dockt-cli.py --run-test ./tests/test_reverse_restore/test_reserve.py::TestClassReverseApi::test_not_supported_crud
```

* Shuts down the application container when test is completed or on error.
example from execution
```
./dockt-cli.py --run-test ./tests

```

* latests tests execution stored result as JUnit file,
```
./dockt-cli.py --run-test
...
...
ls -l results_junit.xml
-rw-r--r-- 1 elia elia 2037 Dec  2 14:53 results_junit.xml
```

* Additionall command line tools -
```
./dockt-cli.py --list-tests
./dockt-cli.py --list-last-result
```  


# Output Examples - 
* _succesful_ test output - 
```
./dockt-cli.py --run-test ./tests
20231202.23:27:49 INFO no failures detected, no need to stop app, keep rocking
```
* _failed_ test output - 
```
./dockt-cli.py --run-test ./tests
FAILED tests/test_reverse_restore/test_reserve.
...

```


# TroubleShooting

Framework utilizes two return codes - `0` for `success` and `1` for `error`,
relying on exceptions handling to correctly handle failures and quit gracefully,
while providing sufficient data via logging - `dockt-cli.log`,
tracebacks and optional pdb cabapilities on test failures

## rebuilding images and starting contenerized apps 
after changing `dockerfile` - which provides the test app,
on `following tests exectuin via cmd, the image will be rebuilt,
and a new container will be deployed,

This is the equivalent to - `
```
docker build -t <image_name> <path_to_docker_file>
docker run -dp 127.0.0.1:5000:5000 <image_name>
```

## debbugging live containers ->
start bash on a running container - 
```
docker exec -it <container_name> bash
```

## query elements
```
docker inspect <element name or ID>
```

## Supported Platforms
```
x86_64 GNU/Linux 6.6.1-arch1-1
Docker 24.0.7
Python 3.11.5
pytest 7.4.3
```