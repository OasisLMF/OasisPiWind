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
import pandas as pd
from pandas.testing import assert_frame_equal

from oasislmf.platform.client import APIClient
from oasislmf.utils.exceptions import OasisException



# Invoking this fixture: 'function_scoped_container_getter' starts all services
# See: https://github.com/pytest-docker-compose/pytest-docker-compose
#"""Wait for the api from my_api_service to become responsive"""
@pytest.fixture(scope='module')
def wait_for_api(module_scoped_container_getter):
    request_session = requests.Session()
    retries = Retry(total=6,
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
    request.cls.generate_expected = request.config.getoption('--generate-expected', False)


class TestOasisModel(TestCase):
    #__test__ = False
    expected_files = None

    @classmethod
    def setUpClass(cls, expected_dir=None, input_tar=None, results_tar=None, params=None):
        
        # Default
        cls.base_dir = os.path.dirname(os.path.realpath(__file__))
        cls.input_tar = f'{cls.base_dir}/result/input_{cls.__name__}.tar.gz'
        cls.results_tar = f'{cls.base_dir}/result/loss_{cls.__name__}.tar.gz'
        cls.expected_dir = cls.exp_dir
        cls.params = {}

        # SubClass vars
        if expected_dir:
            cls.expected_dir = expected_dir
        if results_tar:
            cls.results_tar = results_tar
        if input_tar:
            cls.input_tar = input_tar
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

        # Download outputs
        cls.api.analyses.input_file.download(cls.analysis_id, cls.input_tar)
        cls.api.analyses.output_file.download(cls.analysis_id, cls.results_tar)

        # Create results if option is set
        cls._generate_expected_results(cls)

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

    def _check_output(self, filename):
        if self.generate_expected:
            pytest.skip(f"Skipping file check, generate_expected={self.generate_expected}")

        df_result = self._result_from_tar(filename)
        df_expect = self._expect_from_dir(filename)
        assert_frame_equal(df_result, df_expect)

    def _generate_expected_results(self):
        if not self.generate_expected:
            return
        else:
            with tarfile.open(self.input_tar) as tar:
                tar.extractall(path=os.path.join(self.expected_dir, 'input'))
            with tarfile.open(self.results_tar) as tar:
                tar.extractall(path=self.expected_dir)

    def test_model_settings(self):
        downloaded_settings = self.api.models.settings.get(self.model_id).json()
        self.assertTrue(downloaded_settings)

    def test_loss_output_generated(self):
        self.assertEqual(self.api.analyses.status(self.analysis_id), 'RUN_COMPLETED')
        assert(os.path.isfile(self.results_tar))

    def test_for_missing_files(self):
        if self.generate_expected:
            pytest.skip(f"Skipping file check, generate_expected={self.generate_expected}")

        # check that all expected files are there in the output tar
        if self.expected_dir:
            with tarfile.open(self.results_tar) as tar:
                results = set([member.path for member in tar.getmembers()])
                expected = set([f.replace(f"{self.expected_dir}/" ,"") for f in  glob.glob(f"{self.expected_dir}/output/*")])
                print(f'result: {results}')
                print(f'expect: {expected}')
                self.assertEqual(expected.difference(results), set())
