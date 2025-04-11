"""pytest configuration"""

from os import getenv, cpu_count
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
    parser.addoption(
        '--lookup-chunks', type=int, default=getenv('WORKER_LOOKUP_CHUNKS', default=cpu_count()), 
        help='Set the number of lookup chunks (v2 runs only)' 
    )  
    parser.addoption(
        '--analysis-chunks', type=int, default=getenv('WORKER_ANALYSIS_CHUNKS', default=cpu_count()), 
        help='Set the number of analysis chunks (v2 runs only)' 
    )  

pytest_plugins = [
    "docker_compose",
]
