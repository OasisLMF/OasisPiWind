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

# analysis settings files 
GUL = os.path.join(file_path, 'ci', 'GUL_analysis_settings.json')
IL = os.path.join(file_path, 'ci', 'FM_analysis_settings.json')
RI = os.path.join(file_path, 'ci', 'RI_analysis_settings.json')
ORD_CSV = os.path.join(file_path, 'ci', 'ORD_csv_analysis_settings.json') 
ORD_PQ = os.path.join(file_path, 'ci', 'ORD_parquet_analysis_settings.json')

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


class TestPiWind(TestCase):
    expected_files = None

    @classmethod
    def setUpClass(cls):
        cls.results_tar = f'{file_path}/result/base_case.tar.gz'
        cls.params = {
            "analysis_settings_json": f"{file_path}/ci/GUL_analysis_settings.json",
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
        }

        # clear any prev results
        if os.path.isfile(cls.results_tar):
            os.remove(cls.results_tar)
        # run loss analysis and download output tar
        cls.params['analysis_id'] = PlatformRunInputs(**cls.params).run()
        PlatformRunLosses(**cls.params).run()
        cls.api.analyses.output_file.download(cls.params['analysis_id'], cls.results_tar)

    def test_loss_output_generated(self):
        analysis_id = self.params.get('analysis_id')
        self.assertEqual(self.api.analyses.status(analysis_id), 'RUN_COMPLETED')
        assert(os.path.isfile(self.results_tar))

    def _result_from_tar(self, result_file):
        tar_key = result_file.replace(self.expected_dir,'')
        with tarfile.open(self.results_tar) as tar:
            return pd.read_csv(tar.extractfile(tar_key))

    def _expect_from_dir(self, result_file):
        return pd.read_csv(result_file)

    def _compare_output(self, filename):
        df_result = self._result_from_tar(filename)
        df_expect = self._expect_from_dir(filename)
        assert_frame_equal(df_result, df_expect)


class ControlSet(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/control_set/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/control_set/'
        cls.results_tar = f'{file_path}/result/control-set.tar.gz'
        cls.params = {
            "analysis_settings_json": RI
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.csv",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.csv"
        }
        super(case_0, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_0(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_0/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_0/'
        cls.results_tar = f'{file_path}/result/case_0.tar.gz'
        cls.params = {
            "analysis_settings_json": GUL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
        }
        super(case_0, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_1(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_1/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_1/'
        cls.results_tar = f'{file_path}/result/case_1.tar.gz'
        cls.params = {
            "analysis_settings_json": IL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
        }
        super(case_1, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_2(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_2/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_2/'
        cls.results_tar = f'{file_path}/result/case_2.tar.gz'
        cls.params = {
            "analysis_settings_json": IL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
        }
        super(case_2, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_3(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_3/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_3/'
        cls.results_tar = f'{file_path}/result/case.tar.gz'
        cls.params = {
            "analysis_settings_json": IL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10Type2Ded.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWindType2Ded.csv",
        }
        super(case_3, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_4(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_4/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_4/'
        cls.results_tar = f'{file_path}/result/case.tar.gz'
        cls.params = {
            "analysis_settings_json": IL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10Type2Lim.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWindType2Lim.csv",
        }
        super(case_4, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_5(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_5/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_5/'
        cls.results_tar = f'{file_path}/result/case_5.tar.gz'
        cls.params = {
            "analysis_settings_json": ORD_CSV
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.csv",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.csv",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.csv"
        }
        super(case_5, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_6(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_6/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_6/'
        cls.results_tar = f'{file_path}/result/case_6.tar.gz'
        cls.params = {
            "analysis_settings_json": ORD_PQ
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.parquet",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.parquet",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.parquet",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.parquet"
        }
        super(case_6, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_7(TestPiWind):
    expected_files = glob.glob(f"{file_path}/ci/expected/case_7/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_7/'
        cls.results_tar = f'{file_path}/result/case_7.tar.gz'
        cls.params = {
            "analysis_settings_json": ORD_CSV
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.parquet",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.parquet",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.parquet",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.parquet"
        }
        super(case_7, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)



class case_8(TestPiWind):
    __test__ = False  # skip this test until updated
    expected_files = glob.glob(f"{file_path}/ci/expected/case_8/output/*")

    @classmethod
    def setUpClass(cls):
        cls.expected_dir = f'{file_path}/ci/expected/case_8/'
        cls.results_tar = f'{file_path}/result/case_8.tar.gz'
        cls.params = {
            "analysis_settings_json": ORD_PQ
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.parquet",
            "oed_accounts_csv": f"{file_path}/inputs/SourceAccOEDPiWind.parquet",
            "oed_info_csv":  f"{file_path}/inputs/SourceReinsInfoOEDPiWind.parquet",
            "oed_scope_csv": f"{file_path}/inputs/SourceReinsScopeOEDPiWind.parquet"
        }
        super(case_8, cls).setUpClass()

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)
