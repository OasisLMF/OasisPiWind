import pytest
import os
import requests
from urllib.parse import urljoin
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import tarfile
import glob
import pathlib
import time
import random

from unittest import TestCase
from parametrize import parametrize
import pandas as pd
from pandas.testing import assert_frame_equal

from oasislmf.platform.client import APIClient


# Test vars
pytest_plugins = ["docker_compose"]
file_path = os.path.dirname(os.path.realpath(__file__))

# Set Oasis Version
#os.environ["SERVER_IMG"] = "coreoasis/api_server"
#os.environ["SERVER_TAG"] = "1.26.4"
#os.environ["WORKER_IMG"] = "coreoasis/model_worker"
#os.environ["WORKER_TAG"] = "1.26.4"
#os.environ["DEBUG"] = "0"

# expected output dirs
exp_case_ctl = os.path.join(file_path, 'ci', 'expected', 'control_set')
exp_case_0 = os.path.join(file_path, 'ci', 'expected', '0_case')
exp_case_1 = os.path.join(file_path, 'ci', 'expected', '1_case')
exp_case_2 = os.path.join(file_path, 'ci', 'expected', '2_case')
exp_case_3 = os.path.join(file_path, 'ci', 'expected', '3_case')
exp_case_4 = os.path.join(file_path, 'ci', 'expected', '4_case')
exp_case_5 = os.path.join(file_path, 'ci', 'expected', '5_case')
exp_case_6 = os.path.join(file_path, 'ci', 'expected', '6_case')
exp_case_7 = os.path.join(file_path, 'ci', 'expected', '7_case')
exp_case_8 = os.path.join(file_path, 'ci', 'expected', '8_case')

# analysis settings files
GUL = os.path.join(file_path, 'ci', 'GUL_analysis_settings.json')
IL = os.path.join(file_path, 'ci', 'FM_analysis_settings.json')
RI = os.path.join(file_path, 'ci', 'RI_analysis_settings.json')
ORD_CSV = os.path.join(file_path, 'ci', 'ORD_csv_analysis_settings.json')
ORD_PQ = os.path.join(file_path, 'ci', 'ORD_parquet_analysis_settings.json')
ALL = os.path.join(file_path, 'ci', 'ALL_output_analysis_settings.json')



class all_outputs(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            params = {
                "analysis_settings_json": ALL,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
                'oed_info_csv': os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.csv'),
                'oed_scope_csv': os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.csv')
            })
    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)



# Invoking this fixture: 'function_scoped_container_getter' starts all services
# See: https://github.com/pytest-docker-compose/pytest-docker-compose
#"""Wait for the api from my_api_service to become responsive"""
@pytest.fixture(scope='module')
def wait_for_api(module_scoped_container_getter):
    request_session = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504, 404])

    try:
        localstack = module_scoped_container_getter.get("localstack-s3").network_info[0]
    except:
        localstack = None

    # Wait for server
    request_session.mount('http://', HTTPAdapter(max_retries=retries))
    server = module_scoped_container_getter.get("server").network_info[0]
    api_url = f"http://{server.hostname}:{server.host_port}"
    assert request_session.get(f"{api_url}/healthcheck/")

    # Wait for localstack (only if in compose file)
    if localstack:
        localstack_url = f"http://{localstack.hostname}:4572/example-bucket"
        assert request_session.get(localstack_url)

    # Wait for Model
    oasis_client = APIClient(api_url=api_url)
    oasis_client.api.mount('http://', HTTPAdapter(max_retries=retries))
    assert oasis_client.models.get(1)
    return oasis_client


# Attach the oasislmf api client to each test class
# https://stackoverflow.com/a/50135020
@pytest.fixture(autouse=True, scope='class')
def _class_server_conn(request, wait_for_api):
    request.cls.api = wait_for_api


class TestPiWind(TestCase):
    #__test__ = False
    expected_files = None

    @classmethod
    def setUpClass(cls, expected_dir=None, results_tar=None, params=None):

        # Default
        cls.expected_dir=None
        cls.results_tar = f'{file_path}/result/base_case.tar.gz'
        cls.params = {
            "analysis_settings_json": GUL,
            "oed_location_csv": f"{file_path}/inputs/SourceLocOEDPiWind10.csv",
        }

        # SubClass vars
        if expected_dir:
            cls.expected_dir = expected_dir
        if results_tar:
            cls.results_tar = results_tar
        if params:
            cls.params = params

        # clear any prev results
        if os.path.isfile(cls.results_tar):
            os.remove(cls.results_tar)

        # Find PiWind's model id
        cls.model_id = cls._get_model_id(cls)

        # Create portfolio
        cls.portfolio_id = cls._create_portfolio(cls)

        cls.analysis_id = cls.api.create_analysis(
            portfolio_id=cls.portfolio_id,
            model_id=cls.model_id,
            analysis_name=cls.__name__,
            analysis_settings_fp=cls.params.get('analysis_settings_json')
        )['id']
        # Run Loss analysis
        cls.api.run_generate(cls.analysis_id)
        cls.api.run_analysis(cls.analysis_id)
        # Download output
        cls.api.analyses.output_file.download(cls.analysis_id, cls.results_tar)

    @classmethod
    def tearDownClass(cls):
        # if a portfolio was created this will cacade delete
        # that and also its linked analysis
        if cls.portfolio_id:
            cls.api.portfolios.delete(cls.portfolio_id)

    def _get_model_id(self, model_search_dict={'model_id': 'PiWind', 'supplier_id': 'OasisLMF'}):
        return self.api.models.search(model_search_dict).json().pop()['id']

    def _create_portfolio(self):
        return self.api.upload_inputs(portfolio_name=self.__name__,
                                      location_fp=self.params.get('oed_location_csv'),
                                      accounts_fp=self.params.get('oed_accounts_csv'),
                                      ri_info_fp=self.params.get('oed_info_csv'),
                                      ri_scope_fp=self.params.get('oed_scope_csv'))['id']

    def _func_to_dataframe(self, filename):
        file_ext = pathlib.Path(filename).suffix[1:].lower()
        file_type = 'parquet' if file_ext in ['parquet', 'pq'] else 'csv'
        return getattr(pd, f"read_{file_type}")

    def _result_from_tar(self, result_file, insensitive_col=True):
        tar_key = result_file.replace(self.expected_dir,'').strip('/')
        pd_read = self._func_to_dataframe(tar_key)

        with tarfile.open(self.results_tar) as tar:
            df = pd_read(tar.extractfile(tar_key))
            if insensitive_col:
                df = df.rename(columns=str.lower)
            return df

    def _expect_from_dir(self, result_file, insensitive_col=True):
        pd_read = self._func_to_dataframe(result_file)
        df = pd_read(result_file)

        if insensitive_col:
            df = df.rename(columns=str.lower)
        return df

    def _compare_output(self, filename):
        df_result = self._result_from_tar(filename)
        df_expect = self._expect_from_dir(filename)
        assert_frame_equal(df_result, df_expect)

    def test_loss_output_generated(self):
        self.assertEqual(self.api.analyses.status(self.analysis_id), 'RUN_COMPLETED')
        assert(os.path.isfile(self.results_tar))

    def test_for_missing_files(self):
        # check that all expected files are there in the output tar
        if self.expected_dir:
            with tarfile.open(self.results_tar) as tar:
                results = set([member.path for member in tar.getmembers()])
                expected = set([f.replace(f"{self.expected_dir}/" ,"") for f in  glob.glob(f"{self.expected_dir}/output/*")])
                print(f'result: {results}')
                print(f'expect: {expected}')
                self.assertEqual(expected.difference(results), set())


class ControlSet(TestPiWind):
    expected_files = glob.glob(f"{exp_case_ctl}/output/*")

    @classmethod
    def setUpClass(cls):
        super(ControlSet, cls).setUpClass(
            expected_dir = exp_case_ctl,
            results_tar = os.path.join(file_path, 'result', 'control-set.tar.gz'),
            params = {
                "analysis_settings_json": RI,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
                'oed_info_csv': os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.csv'),
                'oed_scope_csv': os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.csv')
            })

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_0(TestPiWind):
    expected_files = glob.glob(f"{exp_case_0}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_0, cls).setUpClass(
            expected_dir = exp_case_0,
            results_tar = os.path.join(file_path, 'result', 'case_0.tar.gz'),
            params = {
                "analysis_settings_json": GUL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_1(TestPiWind):
    expected_files = glob.glob(f"{exp_case_1}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_1, cls).setUpClass(
            expected_dir = exp_case_1,
            results_tar = os.path.join(file_path, 'result', 'case_1.tar.gz'),
            params = {
                "analysis_settings_json": IL,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_2(TestPiWind):
    expected_files = glob.glob(f"{exp_case_2}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_2, cls).setUpClass(
            expected_dir = exp_case_2,
            results_tar = os.path.join(file_path, 'result', 'case_2.tar.gz'),
            params = {
                "analysis_settings_json": IL,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_3(TestPiWind):
    expected_files = glob.glob(f"{exp_case_3}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_3, cls).setUpClass(
            expected_dir = exp_case_3,
            results_tar = os.path.join(file_path, 'result', 'case_3.tar.gz'),
            params = {
                "analysis_settings_json": IL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10Type2Ded.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWindType2Ded.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_4(TestPiWind):
    expected_files = glob.glob(f"{exp_case_4}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_4, cls).setUpClass(
            expected_dir = exp_case_4,
            results_tar = os.path.join(file_path, 'result', 'case_4.tar.gz'),
            params = {
                "analysis_settings_json": IL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10Type2Lim.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWindType2Lim.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_5(TestPiWind):
    expected_files = glob.glob(f"{exp_case_5}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_5, cls).setUpClass(
            expected_dir = exp_case_5,
            results_tar = os.path.join(file_path, 'result', 'case_5.tar.gz'),
            params = {
                "analysis_settings_json": ORD_CSV,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.csv'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.csv'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_6(TestPiWind):
    expected_files = glob.glob(f"{exp_case_6}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_6, cls).setUpClass(
            expected_dir = exp_case_6,
            results_tar = os.path.join(file_path, 'result', 'case_6.tar.gz'),
            params = {
                "analysis_settings_json": ORD_PQ,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)


class case_7(TestPiWind):
    expected_files = glob.glob(f"{exp_case_7}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_7, cls).setUpClass(
            expected_dir = exp_case_7,
            results_tar = os.path.join(file_path, 'result', 'case_7.tar.gz'),
            params = {
                "analysis_settings_json": ORD_CSV,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)



class case_8(TestPiWind):
    #__test__ = False  # skip this test until updated
    expected_files = glob.glob(f"{exp_case_8}/output/*")

    @classmethod
    def setUpClass(cls):
        super(case_8, cls).setUpClass(
            expected_dir = exp_case_8,
            results_tar = os.path.join(file_path, 'result', 'case_8.tar.gz'),
            params = {
                "analysis_settings_json": ORD_PQ,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", expected_files)
    def test_output_file(self, filename):
        self._compare_output(filename)
