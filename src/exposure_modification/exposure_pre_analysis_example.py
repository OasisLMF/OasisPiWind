class ExposurePreAnalysis:
    """
    Example of custum module called by oasislmf/model_preparation/ExposurePreAnalysis.py
    Exposure pre analysis modules need to modify exposure_data object (mostly probably the dataframes) to have an effect
    """

    def __init__(self, exposure_data, exposure_pre_analysis_setting, **kwargs):
        self.exposure_data = exposure_data
        self.exposure_pre_analysis_setting = exposure_pre_analysis_setting

    def run(self):
        """example of adding a new column to exposure_data.location.dataframe"""
        panda_df= self.exposure_data.location.dataframe
        panda_df['BuildingTIV_new'] = panda_df['BuildingTIV'] * self.exposure_pre_analysis_setting['BuildingTIV_multiplyer']
