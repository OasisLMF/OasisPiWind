class MyExposurePreAnalysis:
    """
    Template for a custom exposure pre-analysis module.
    This module is called by ExposurePreAnalysis() in oasislmf/computation/hooks/pre_analysis.py to produce customized outputs.
    In order to have an effect, customized exposure pre-analysis modules need to modify the `exposure_data` instance member
    (mostly typically, its dataframes).
    """

    def __init__(self, exposure_data, exposure_pre_analysis_setting, **kwargs):
        self.exposure_data = exposure_data
        self.exposure_pre_analysis_setting = exposure_pre_analysis_setting

    def run(self):
        """example of adding a new column to exposure_data.location.dataframe"""
        df = self.exposure_data.location.dataframe
        df['BuildingTIV_new'] = df['BuildingTIV'] * self.exposure_pre_analysis_setting['BuildingTIV_multiplyer']
