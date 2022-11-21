import pytest
import os
import requests
from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# See: https://github.com/pytest-docker-compose/pytest-docker-compose

from oasislmf.platform.client import APIClient
from oasislmf.computation.run.platform import PlatformGet, PlatformRun, PlatformList, PlatformRunInputs 

pytest_plugins = ["docker_compose"]


# Invoking this fixture: 'function_scoped_container_getter' starts all services
@pytest.fixture(scope="function")
def wait_for_api(function_scoped_container_getter):

    #"""Wait for the api from my_api_service to become responsive"""
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504])

    request_session.mount('http://', HTTPAdapter(max_retries=retries))
    service = function_scoped_container_getter.get("server").network_info[0]
    api_url = f"http://{service.hostname}:{service.host_port}"

    assert request_session.get(f"{api_url}/healthcheck/")
    
    api_session = APIClient(api_url=api_url)
    return api_session, api_url



#def test__show_api_state(wait_for_api):
#    print(PlatformList().run())

def test__control_set(wait_for_api):
    """The Api is now verified good to go and tests can interact with it"""

    file_path = os.path.dirname(os.path.realpath(__file__))
    loc_file = f"{file_path}/inputs/SourceLocOEDPiWind10.csv"
    acc_file = f"{file_path}/inputs/SourceAccOEDPiWind.csv"
    inf_file = f"{file_path}/inputs/SourceReinsInfoOEDPiWind.csv"
    scp_file = f"{file_path}/inputs/SourceReinsScopeOEDPiWind.csv"
    settings = f"{file_path}/ci/RI_analysis_settings.json"
    

    import ipdb; ipdb.set_trace()
    api_session, api_url = wait_for_api
    PlatformRun(**{"analysis_settings_json": settings, "oed_location_csv": loc_file}).run()
    


