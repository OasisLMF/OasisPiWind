"""pytest configuration"""

from os import getenv
from .modelcheck import wait_for_api, _class_server_conn


def pytest_addoption(parser):
    parser.addoption(
        '--generate-expected', action='store_true', default=False,  # dest='generate_expected',
        help='If True, it generates the expected files instead of running the tests. Default: False.',
    )
    parser.addoption(
        '--api-version', type=str, default=getenv('WORKER_API_VER', default='v1'), 
        help='Set the OasisAPI clients api version [v1, v2]' 
    )  

pytest_plugins = [
    "docker_compose",
]
