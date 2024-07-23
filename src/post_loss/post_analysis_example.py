import logging
import pandas as pd
from io import StringIO
from pathlib import Path

logger = logging.getLogger('oasislmf')
# example output
imperial_march_output = StringIO("""
note, frequency(hz), duration(ms)
A4, 440, 500
A4, 440, 500
A4, 440, 500
F4, 349, 350
C5, 523, 150
A4, 440, 500
F4, 349, 350
C5, 523, 150
A4, 440, 1000
E5, 659, 500
E5, 659, 500
E5, 659, 500
F5, 698, 350
C5, 523, 150
Ab4, 415, 500
F4, 349, 350
C5, 523, 150
A4, 440, 1000
""")

class MyPostAnalysis:
    def __init__(self, model_data_dir=None, model_run_dir=None, user_data_dir=None, analysis_settings_json=None):
        self.model_data_dir = model_data_dir
        self.model_run_dir = model_run_dir
        self.analysis_settings_json = analysis_settings_json

    def run(self):
        logger.info(' -- Running Post Analysis Hook -- ')
        output_path = Path(self.model_run_dir, 'output', 'imperial_march.csv')
        pd_output_data = pd.read_csv(imperial_march_output)
        pd_output_data.to_csv(output_path)
        logger.info(f'Output written to: {output_path}')

