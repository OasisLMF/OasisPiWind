""" Oasis Model Pytest class

This test class which uses pytest-docker-compose to check an oasis model
vs a set of expected result files.

Test Inputs:
    a docker-compose file that runs the OasisPlatform stack
    the default option is stored in 'pytest.ini' but can be overridden on command line using
    "--docker-compose=./docker-compose.yml"

    An expected files directory for each test class,
    the structure should include two folders
     'input': stores the files from generate oasis files
     'output': stores the files from running a loss analysis

        tests/ci/expected/<test-class-name>
        ├── input
        │   ├── account.csv
        │   ├── correlations.csv
        │   ├── coverages.csv
          ...
        │   ├── location.csv
        │   ├── lookup_config.json
        │   ├── lookup.json
        │   ├── reinsinfo.csv
        │   └── reinsscope.csv
        └── output
            ├── gul_S1_eltcalc.csv
            └── gul_S1_summary-info.csv
"""

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
from requests.exceptions import HTTPError

from oasislmf.platform.client import APIClient
from oasislmf.utils.exceptions import OasisException



@pytest.fixture(scope='module')
def wait_for_api(module_scoped_container_getter, request):
    """
    Fixture that waits for the docker container running the OasisAPI to become responsive.
    see https://github.com/pytest-docker-compose/pytest-docker-compose for details on using
    the `function_scoped_container_getter` object to interact with running docker containers

    Runs only once per pytest execution.

    Returns:
        oasis_client: An instance of the APIClient class from the oasislmf package, this is a python REST client
                      used to make calls to the OasisAPI.
    """
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
    api_ver = request.config.getoption('--api-version', 'v1')
    api_url = f"http://{server.hostname}:{server.host_port}"
    assert request_session.get(f"{api_url}/healthcheck/")

    # Wait for localstack (only if in compose file)
    if localstack:
        localstack_url = f"http://{localstack.hostname}:4572/example-bucket"
        assert request_session.get(localstack_url)

    # Wait for Model
    # First attempt: username/password
    try:
        oasis_client = APIClient(
            api_url=api_url,
            api_ver=api_ver,
            username="admin",
            password="password"
        )
    except HTTPError as e:
        if e.response.status_code not in (400, 401):
            # Raise immediately if it’s not an auth failure
            raise e
        # Second attempt: client ID/secret
        try:
            oasis_client = APIClient(
                api_url=api_url,
                api_ver=api_ver,
                client_id="oasis-Service",
                client_secret="serviceNotSoSecret"
            )
        except HTTPError as e:
            if e.response.status_code in (400, 401):
                raise RuntimeError("Both authentication methods failed (401/400).") from e
            else:
                raise e
    oasis_client.api.mount('http://', HTTPAdapter(max_retries=retries))

    model_headers = {'authorization': f"Bearer {oasis_client.api.tkn_access}"}
    model_url = f"{api_url}/{api_ver}/models/1/"
    assert request_session.get(model_url, headers=model_headers)
    return oasis_client


@pytest.fixture(autouse=True, scope='class')
def _class_server_conn(request, wait_for_api):
    """
    Fixture that attaches the oasislmf API client to each test class.
    Runs for each subclass of TestOasisModel

    Args:
        request: The request object for the test.
        wait_for_api: The wait_for_api fixture.

    Returns:
        None
    """
    request.cls.api = wait_for_api
    request.cls.generate_expected = request.config.getoption('--generate-expected', False)
    request.cls.lookup_chunks = request.config.getoption('--lookup-chunks')
    request.cls.anaysis_chunks = request.config.getoption('--analysis-chunks')


class TestOasisModel(TestCase):
    """
    A unit test class for testing the Oasis model.

    Attributes:
        base_dir (str): The base testing directory.
        input_tar (str): The input tar file path.
        results_tar (str): The results tar file path.
        expected_dir (str): The expected results directory.
        params (dict): The oasislmf.json settings used to all the OasisAPI.
                       Valid keys are from the `oasislmf api run` command
                       [
                         oed_location_csv,
                         oed_accounts_csv,
                         oed_info_csv,
                         oed_scope_csv,
                         analysis_settings_json,
                       ]

    Methods:
        setUpClass(cls, expected_dir=None, input_tar=None, results_tar=None, params=None):
            Sets up the test case.
        tearDownClass(cls):
            Tears down the test case.
        _get_model_id(self, model_search_dict={'model_id': 'PiWind', 'supplier_id': 'OasisLMF'}):
            Gets the model ID.
        _create_portfolio(self):
            Creates a portfolio.
        _func_to_dataframe(self, filename):
            Reads a file and returns a pandas DataFrame.
        _result_from_tar(self, result_file, insensitive_col=True):
            Extracts a tar file and returns a pandas DataFrame.
        _expect_from_dir(self, result_file, insensitive_col=True):
            Reads a file and returns a pandas DataFrame.
        _check_output(self, filename):
            Compares the expected output with the actual output.
        _generate_expected_results(self):
            Generates expected results.
        test_model_settings(self):
            Tests the model settings.
        test_loss_output_generated(self):
            Tests if the loss output is generated.
        test_for_missing_files(self):
            Tests if there are any missing files in the output tar.
    """

    @classmethod
    def setUpClass(cls, expected_dir=None, input_tar=None, results_tar=None, params=None):
        """
        Sets up the test case.

        Args:
            expected_dir (str): The expected directory.
            input_tar (str): The input tar file path.
            results_tar (str): The results tar file path.
            params (dict): The oasislmf settings for the `oasislmf api run` command
        """

        # Default
        cls.base_dir = os.path.dirname(os.path.realpath(__file__))
        cls.input_tar = f'{cls.base_dir}/result/input_{cls.__name__}.tar.gz'
        cls.results_tar = f'{cls.base_dir}/result/loss_{cls.__name__}.tar.gz'
        cls.expected_dir = getattr(cls, 'exp_dir', None)
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

        # skip run if paramters are missing
        if not cls.params:
            pytest.skip(f"Skipping TestClass={cls.__name__}, no input files set in params")

        # Find PiWind's model id
        cls.model_id = cls._get_model_id(cls)

        # test if V2, if yes set chunk sizes based on input (default = number of cpu cores) 
        if cls.api.api_ver.lower() == 'v2':
            chunk_cfg = cls.api.models.chunking_configuration.get(cls.model_id).json()
            chunk_cfg['fixed_lookup_chunks'] = cls.lookup_chunks
            chunk_cfg['fixed_analysis_chunks'] = cls.anaysis_chunks
            cls.api.models.chunking_configuration.post(cls.model_id, chunk_cfg)

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
        """
        Deletes the portfolio and its linked analysis if `portfolio_id` is set.
        """
        if cls.portfolio_id:
            cls.api.portfolios.delete(cls.portfolio_id)

    def _get_model_id(self, model_search_dict={'model_id': 'PiWind', 'supplier_id': 'OasisLMF'}):
        """
        Searches for a model registered with the OasisAPI
        using the supplied search criteria in `model_search_dict` and returns its ID.
        """
        return self.api.models.search(model_search_dict).json().pop()['id']

    def _create_portfolio(self):
        """
        Creates a new portfolio using the specified inputs
        from the classes 'params' attribute and returns its ID.
        """
        return self.api.upload_inputs(portfolio_name=self.__name__,
                                      location_fp=self.params.get('oed_location_csv'),
                                      accounts_fp=self.params.get('oed_accounts_csv'),
                                      ri_info_fp=self.params.get('oed_info_csv'),
                                      ri_scope_fp=self.params.get('oed_scope_csv'))['id']

    def _func_to_dataframe(self, filename):
        """
        Returns a Pandas DataFrame object that is read from the specified file.
        supported file types are 'csv' or 'parquet'

        Args:
            filename (str): The name of the file to read the DataFrame from.

        Returns:
            pd.DataFrame: The DataFrame object read from the file.
        """
        file_ext = pathlib.Path(filename).suffix[1:].lower()
        file_type = 'parquet' if file_ext in ['parquet', 'pq'] else 'csv'
        return getattr(pd, f"read_{file_type}")

    def _result_from_tar(self, result_file, insensitive_col=True):
        """
        Returns a DataFrame object that is read from the specified tar.gz file.
        These are either the generated inputs, or loss outputs tar files
        which are returned from the OasisAPI.

        Args:
            result_file (str): The name of the file to read the DataFrame from in the results tar archive.
            insensitive_col (bool): Whether to make the column names case-insensitive. Defaults to True.

        Returns:
            pd.DataFrame: The DataFrame object read from the file in the results tar archive.
        """
        tar_key = result_file.replace(self.expected_dir,'').strip('/')
        pd_read = self._func_to_dataframe(tar_key)

        with tarfile.open(self.results_tar) as tar:
            df = pd_read(tar.extractfile(tar_key))
            if insensitive_col:
                df = df.rename(columns=str.lower)
            return df

    def _expect_from_dir(self, result_file, insensitive_col=True):
        """
        Returns a DataFrame object that is read from a test's expected results directory.

        Args:
            result_file (str): The name of the file to read the DataFrame from in the expected results directory.
            insensitive_col (bool): Whether to make the column names case-insensitive. Defaults to True.

        Returns:
            pd.DataFrame: The DataFrame object read from the file in the expected results directory.
        """
        pd_read = self._func_to_dataframe(result_file)
        df = pd_read(result_file)

        if insensitive_col:
            df = df.rename(columns=str.lower)
        return df

    def _check_output(self, filename):
        """
        Check the output of the analysis against expected results
        and asserts the two match.

        'df_result' is extracted from the tar file downloaded from
        the OasisAPI's analyses/{id} endpoints

        'df_expect' is read from the tests expected files directory

        Args:
            filename (str): The filename of the output to check.

        Returns:
            None
        """
        if self.generate_expected:
            pytest.skip(f"Skipping file check, generate_expected={self.generate_expected}")

        df_result = self._result_from_tar(filename)
        df_expect = self._expect_from_dir(filename)

        if (('eltcalc' in filename
                and "standard_deviation" in df_result.columns
                and "standard_deviation" in df_expect.columns)
            or (('elt' in filename or 'plt' in filename)
                and "sdloss" in df_result.columns
                and "sdloss" in df_result.columns
            )
        ): # work around for rounding error tolerance in stdev
            stdev_col = "standard_deviation" if "standard_deviation" in df_result.columns else "sdloss"
            res_col = list(set(df_result.columns) - {stdev_col})
            exp_col = list(set(df_expect.columns) - {stdev_col})

            assert_frame_equal(df_result[res_col], df_expect[exp_col])
            assert_frame_equal(df_result[[stdev_col]], df_expect[[stdev_col]], rtol=0.01)
        else:
            assert_frame_equal(df_result, df_expect)

    def _generate_expected_results(self):
        """
        Checks if the flag `--generate-expected` is set, if true then
        regenerates the expected results from the input tar file and results tar files.

        Returns:
            None
        """
        if not self.generate_expected:
            return
        else:
            with tarfile.open(self.input_tar) as tar:
                tar.extractall(path=os.path.join(self.expected_dir, 'input'))
            with tarfile.open(self.results_tar) as tar:
                tar.extractall(path=self.expected_dir)

    def test_model_settings(self):
        """
        Test if the model_settings.json has been successfully POSTed
        to the OasisAPI by the model self registration celery task.

        Asserts that the 'models/{id}/settings' endpoint is not 404 and
        returns JSON data.

        Returns:
            None
        """
        downloaded_settings = self.api.models.settings.get(self.model_id).json()
        self.assertTrue(downloaded_settings)

    def test_loss_output_generated(self):
        """
        Test if the loss output has been generated and asserts that the `analyses/{id}`
        has the status 'RUN_COMPLETED'

        Returns:
            None
        """
        self.assertEqual(self.api.analyses.status(self.analysis_id), 'RUN_COMPLETED')
        assert(os.path.isfile(self.results_tar))

    def test_for_missing_files(self):
        """
        Test for missing files in the output tar file.

        Checks all the listed files between a tests expected directory and generated loss
        results tar. This this is marked as fail if an expected file is not generated in the
        loss outputs

        Returns:
            None
        """
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
