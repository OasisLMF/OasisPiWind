import pathlib
import pandas as pd

class ExposurePreAnalysis:
    """
    Example of custum module called by oasislmf/model_preparation/ExposurePreAnalysis.py
    """

    def __init__(self, raw_oed_location_csv, oed_location_csv, exposure_pre_analysis_setting, **kwargs):
        self.raw_oed_location_csv = raw_oed_location_csv
        self.oed_location_csv = oed_location_csv
        self.exposure_pre_analysis_setting = exposure_pre_analysis_setting


    def run(self):
        file_ext = pathlib.Path(self.raw_oed_location_csv).suffix[1:].lower()
        file_type = 'parquet' if file_ext in ['parquet', 'pq'] else 'csv'
        pd_read_func = getattr(pd, f"read_{file_type}")

        panda_df = pd_read_func(self.raw_oed_location_csv, memory_map=True)
        panda_df['BuildingTIV_new'] = panda_df['BuildingTIV'] * self.exposure_pre_analysis_setting['BuildingTIV_multiplyer']
        pd_write_func =  getattr(panda_df, f"to_{file_type}")
        pd_write_func(self.oed_location_csv, index=False)
