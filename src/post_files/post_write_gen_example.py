class MyPostFileGen:
    """
    Template for a custom exposure pre-analysis module.
    This module is called by ExposurePreAnalysis() in oasislmf/computation/hooks/pre_analysis.py to produce customized outputs.
    In order to have an effect, customized exposure pre-analysis modules need to modify the `exposure_data` instance member
    (mostly typically, its dataframes).
    """

    def __init__(self, exposure_data, post_file_gen_setting, logger, **kwargs):
        self.exposure_data = exposure_data
        self.post_file_gen_setting = post_file_gen_setting
        self.logger = logger

    def run(self):
        self.logger.info("executing the post file gen code")
