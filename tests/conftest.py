"""pytest configuration"""

from .modelcheck import wait_for_api, _class_server_conn

def pytest_addoption(parser):
    parser.addoption(
        '--generate-expected', action='store_true', default=False,  # dest='generate_expected',
        help='If True, it generates the expected files instead of running the tests. Default: False.'
    )  
    parser.addoption(
        '--skip-output-cmp', action='store_true', default=False,
        help='If True, only check that output is generated dont compare with exisiting files'
    )  

pytest_plugins = [
    "docker_compose",
]
