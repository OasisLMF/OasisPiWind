import pytest
import os
import requests
from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import tarfile
import glob

from unittest import TestCase
from parametrize import parametrize
import pandas as pd 
from pandas.testing import assert_frame_equal

from oasislmf.platform.client import APIClient
from oasislmf.computation.run.platform import PlatformRunInputs, PlatformRunLosses
#from oasislmf.utils.data import print_dataframe, get_dataframe



pytest_plugins = ["docker_compose"]
file_path = os.path.dirname(os.path.realpath(__file__))



# Invoking this fixture: 'function_scoped_container_getter' starts all services
# See: https://github.com/pytest-docker-compose/pytest-docker-compose
#"""Wait for the api from my_api_service to become responsive"""
@pytest.fixture(scope='module')
def wait_for_api(module_scoped_container_getter):

    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504])

    request_session.mount('http://', HTTPAdapter(max_retries=retries))
    service = module_scoped_container_getter.get("server").network_info[0]
    api_url = f"http://{service.hostname}:{service.host_port}"
    assert request_session.get(f"{api_url}/healthcheck/")
    return APIClient(api_url=api_url)



# Attach the oasislmf api client to each test class 
# https://stackoverflow.com/a/50135020
@pytest.fixture(autouse=True, scope='class')
def _class_server_conn(request, wait_for_api):
    request.cls.api = wait_for_api
    

class ControlSet(TestCase):
    expected_files = glob.glob(f"{file_path}/ci/expected/control_set/output/*")
    loss_generated = False

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/control_set/'
        cls.results_tar = f'{file_path}/result/control-set.tar.gz'
        # Control set 
        cls.params = {
            "analysis_settings_json": f"{file_path}/ci/RI_analysis_settings.json", 
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.csv",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.csv"
        }

    
    def setUp(self): 
        if not ControlSet.loss_generated:
            # clear any prev results 
            if os.path.isfile(self.results_tar):
                os.remove(self.results_tar)

            # run loss analysis and download output tar
            self.params['analysis_id'] = PlatformRunInputs(**self.params).run()
            PlatformRunLosses(**self.params).run()  
            self.api.analyses.output_file.download(self.params['analysis_id'], self.results_tar)

    def test_loss_output_generated(self):
        analysis_id = self.params.get('analysis_id')
        self.assertEqual(self.api.analyses.status(analysis_id), 'RUN_COMPLETED')
        assert(os.path.isfile(self.results_tar))
        ControlSet.loss_generated = True
        
    def _result_from_tar(self, result_file):
        tar_key = result_file.replace(self.expected_dir,'')
        with tarfile.open(self.results_tar) as tar:
            return pd.read_csv(tar.extractfile(tar_key))

    def _expect_from_dir(self, result_file): 
        return pd.read_csv(result_file)

    @parametrize("filename", ControlSet.expected_files)
    def test_output_file(self, filename):
        df_result = self._result_from_tar(filename)
        df_expect = self._expect_from_dir(filename)
        assert_frame_equal(df_result, df_expect)



      
class case_0(ControlSet):    
    expected_files = glob.glob(f"{file_path}/ci/expected/0_case/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{{file_path}}/ci/expected/0_case/'
        cls.results_tar = f'{file_path}/result/0_case.tar.gz'
        cls.params = {
            "analysis_settings_json": f"{file_path}/ci/GUL_analysis_settings.json", 
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
        }



class case_1(ControlSet):    
    expected_files = glob.glob(f"{file_path}/ci/expected/1_case/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{{file_path}}/ci/expected/1_case/'
        cls.results_tar = f'{file_path}/result/1_case.tar.gz'
        cls.params = {
            "analysis_settings_json": f"{file_path}/ci/FM_analysis_settings.json", 
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
        }
