import os
import glob
import pytest

from parametrize import parametrize
from .modelcheck import TestOasisModel


# analysis settings files
file_path = os.path.dirname(os.path.realpath(__file__))
GUL = os.path.join(file_path, 'ci', 'GUL_analysis_settings.json')
IL = os.path.join(file_path, 'ci', 'FM_analysis_settings.json')
RI = os.path.join(file_path, 'ci', 'RI_analysis_settings.json')
ORD_CSV = os.path.join(file_path, 'ci', 'ORD_csv_analysis_settings.json')
ORD_PQ = os.path.join(file_path, 'ci', 'ORD_parquet_analysis_settings.json')


class control_set(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            params = {
                "analysis_settings_json": RI,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
                'oed_info_csv': os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.csv'),
                'oed_scope_csv': os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.csv')
            })

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_0(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            params = {
                "analysis_settings_json": GUL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_1(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            params = {
                "analysis_settings_json": IL,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_2(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_2,
            params = {
                "analysis_settings_json": IL,
                'oed_location_csv': os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind.csv'),
                'oed_accounts_csv': os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_3(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_3,
            params = {
                "analysis_settings_json": IL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10Type2Ded.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWindType2Ded.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_4(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_4,
            params = {
                "analysis_settings_json": IL,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10Type2Lim.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWindType2Lim.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_5(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_5,
            params = {
                "analysis_settings_json": ORD_CSV,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.csv'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.csv'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.csv'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.csv'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_6(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_6,
            params = {
                "analysis_settings_json": ORD_PQ,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_7(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_7,
            params = {
                "analysis_settings_json": ORD_CSV,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)


class case_8(TestOasisModel):
    exp_dir =  os.path.join(file_path, 'ci', 'expected', __qualname__)
    exp_files = glob.glob(f"{exp_dir}/output/*")

    @classmethod
    def setUpClass(cls):
        super().setUpClass(
            expected_dir = exp_case_8,
            params = {
                "analysis_settings_json": ORD_PQ,
                "oed_location_csv": os.path.join(file_path, 'inputs', 'SourceLocOEDPiWind10.parquet'),
                "oed_accounts_csv": os.path.join(file_path, 'inputs', 'SourceAccOEDPiWind.parquet'),
                "oed_info_csv":  os.path.join(file_path, 'inputs', 'SourceReinsInfoOEDPiWind.parquet'),
                "oed_scope_csv": os.path.join(file_path, 'inputs', 'SourceReinsScopeOEDPiWind.parquet'),
            }
        )

    @parametrize("filename", exp_files)
    def test_output_file(self, filename):
        self._check_output(filename)
