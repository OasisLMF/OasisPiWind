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
        panda_df = pd.read_csv(self.raw_oed_location_csv, memory_map=True)
        import ipdb; ipdb.set_trace()
        panda_df['BuildingTIV'] = panda_df['BuildingTIV'] * self.exposure_pre_analysis_setting['BuildingTIV_multiplyer']
        panda_df.to_csv(self.oed_location_csv, index=False)
