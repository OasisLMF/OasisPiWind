import pytest
import os
import requests
from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import tarfile
import glob


#https://github.com/OasisLMF/OasisLMF/blob/be0e4bff8f80176576e308e7b87e7359b6e961f0/tests/pytools/gulmc/test_gulmc.py


from oasislmf.platform.client import APIClient
from oasislmf.computation.run.platform import PlatformGet, PlatformRun, PlatformList, PlatformRunInputs, PlatformRunLosses

pytest_plugins = ["docker_compose"]
file_path = os.path.dirname(os.path.realpath(__file__))

# Invoking this fixture: 'function_scoped_container_getter' starts all services
# See: https://github.com/pytest-docker-compose/pytest-docker-compose
@pytest.fixture(scope='module')
def wait_for_api(module_scoped_container_getter):

    #"""Wait for the api from my_api_service to become responsive"""
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504])

    request_session.mount('http://', HTTPAdapter(max_retries=retries))
    service = module_scoped_container_getter.get("server").network_info[0]
    api_url = f"http://{service.hostname}:{service.host_port}"

    assert request_session.get(f"{api_url}/healthcheck/")
    
    api_session = APIClient(api_url=api_url)
    return api_session, api_url


@pytest.fixture(scope='module')
def control_set(wait_for_api):
    """The Api is now verified good to go and tests can interact with it"""

    # load test data 
    test_params = {
        "analysis_settings_json": f"{file_path}/ci/RI_analysis_settings.json", 
        "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
        "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
        "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.csv",
        "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.csv"
    }
    expected_dir = f'{{file_path}}/ci/expected/control_set/'
    
    # generate inputs / losses 
    api_session, api_url = wait_for_api
    test_params['analysis_id'] = PlatformRunInputs(**test_params).run()
    PlatformRunLosses(**test_params).run()  

    # download output tar file 
    output_tar = f'{file_path}/result/control-set.tar.gz'
    api_session.analyses.output_file.download(test_params['analysis_id'], output_tar)
    
    # list files in output and return 
    output = tarfile.open(output_tar)
    file_list = [member for member in output.getmembers() if member.isfile()]
    output.close()

    return output_tar, expected_dir
    

# https://stackoverflow.com/questions/2018512/reading-tar-file-contents-without-untarring-it-in-python-script
# ipdb> tar = tarfile.open(output_tar)
# ipdb> f=tar.extractfile(file_list[2])
# ipdb> f.read()

# ipdb> file_list[2].path
# 'output/gul_S1_aalcalc.csv'

# ipdb> file_list[2].isfile()
# True


#file_list = glob.glob(f"{file_path}/ci/expected/control_set/output/*")

file_list = glob.glob(f"{file_path}/ci/expected/control_set/output/*")
@pytest.mark.parametrize("test_file", file_list)
def test_control_set(control_set, test_file):
    import ipdb; ipdb.set_trace()
    print (control_set)
    


#def test_output_match(test__run_control_set):
#    import ipdb; ipdb.set_trace()
#    file_list, output_tar = test__run_control_set
#
#    test_file
