import pytest
import requests
#from urllib.parse import urljoin
#from urllib3.util.retry import Retry
#from requests.adapters import HTTPAdapter

# See: https://github.com/pytest-docker-compose/pytest-docker-compose

pytest_plugins = ["docker_compose"]


# Invoking this fixture: 'function_scoped_container_getter' starts all services
@pytest.fixture(scope="function")
def wait_for_api(function_scoped_container_getter):
    """Wait for the api from my_api_service to become responsive"""
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[500, 502, 503, 504])
    request_session.mount('http://', HTTPAdapter(max_retries=retries))

    service = function_scoped_container_getter.get("my_api_service").network_info[0]
    api_url = "http://%s:%s/" % (service.hostname, service.host_port)
    assert request_session.get(api_url)
    return request_session, api_url


def test_read_and_write(wait_for_api):
    """The Api is now verified good to go and tests can interact with it"""
    request_session, api_url = wait_for_api
    data_string = 'some_data'
    request_session.put('%sitems/2?data_string=%s' % (api_url, data_string))
    item = request_session.get(urljoin(api_url, 'items/2')).json()
    assert item['data'] == data_string
    request_session.delete(urljoin(api_url, 'items/2'))
