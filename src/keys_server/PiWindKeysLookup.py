__all__ = [
  'PiWindKeysLookup'
] 

# Python 2 standard library imports
import csv
import io
import logging
import os

# Python 2 non-standard library imports
import pandas as pd

# Imports from Oasis core repos + subpackages or modules within keys_server
from oasis_utils import (
    oasis_utils,
    oasis_log_utils,
)

from oasis_keys_lookup import BaseKeysLookup

from utils import (
    AreaPerilLookup,
    VulnerabilityLookup,
)


class PiWindKeysLookup(BaseKeysLookup):
    """
    PiWind keys lookup.
    """

    _LOCATION_RECORD_META = {
        'id': {'csv_header': 'ID', 'csv_data_type': int, 'validator': oasis_utils.to_int, 'desc': 'Location ID'},
        'lon': {'csv_header': 'LON', 'csv_data_type': float, 'validator': oasis_utils.to_float, 'desc': 'Longitude'},
        'lat': {'csv_header': 'LAT', 'csv_data_type': float, 'validator': oasis_utils.to_float, 'desc': 'Latitude'},
        'coverage': {'csv_header': 'COVERAGE', 'csv_data_type': int, 'validator': oasis_utils.to_int, 'desc': 'Coverage'},
        'class_1': {'csv_header': 'CLASS_1', 'csv_data_type': str, 'validator': oasis_utils.to_string, 'desc': 'Class #1'},
        'class_2': {'csv_header': 'CLASS_2', 'csv_data_type': str, 'validator': oasis_utils.to_string, 'desc': 'Class #2'}
    }


    @oasis_log_utils.oasis_log()
    def __init__(
        self,
        keys_data_directory=os.path.join(os.sep, 'var', 'oasis', 'keys_data'),
        supplier='OasisLMF',
        model_name='PiWind',
        model_version='0.0.0.1'
    ):
        """
        Initialise the static data required for the lookup.
        """
        super(self.__class__, self).__init__(
            keys_data_directory,
            supplier,
            model_name,
            model_version
        )

        self.area_peril_lookup = AreaPerilLookup(areas_file=os.path.join(self.keys_data_directory, 'area_peril_dict.csv'))
        self.vulnerability_lookup = VulnerabilityLookup(vulnerabilities_file=os.path.join(self.keys_data_directory, 'vulnerability_dict.csv'))

    
    @oasis_log_utils.oasis_log()
    def process_locations(self, loc_data):
        """
        Read in raw location rows from request CSV data and generate
        exposure records. This is the main method to override in each model
        keys lookup class. Other methods inherited from the superclass
        BaseKeysLookup can also be used, please refer to the source:
        
        https://github.com/OasisLMF/oasis_keys_lookup/blob/master/BaseKeysLookup.py
        """
        loc_df = pd.read_csv(io.StringIO(loc_data))

        for i in range(len(loc_df)):
            exposure_rec = dict()
            exposure_rec['peril_id'] = oasis_utils.PERIL_ID_WIND
            
            loc_rec = self._get_location_record(loc_df.loc[i])

            exposure_rec['id'] = loc_rec['id']
            exposure_rec['coverage'] = loc_rec['coverage']

            loc_area_peril_rec = self.area_peril_lookup.do_lookup_location(loc_rec)
            exposure_rec['area_peril_id'] = loc_area_peril_rec['area_peril_id']

            loc_vuln_peril_rec = self.vulnerability_lookup.do_lookup_location(loc_rec)
            exposure_rec['vulnerability_id'] = loc_vuln_peril_rec['vulnerability_id']

            if loc_area_peril_rec['status'] == loc_vuln_peril_rec['status'] == oasis_utils.KEYS_STATUS_SUCCESS:
                exposure_rec['status'] = oasis_utils.KEYS_STATUS_SUCCESS
            elif (
                loc_area_peril_rec['status'] == oasis_utils.KEYS_STATUS_FAIL or
                loc_vuln_peril_rec['status'] == oasis_utils.KEYS_STATUS_FAIL
            ):
                exposure_rec['status'] = oasis_utils.KEYS_STATUS_FAIL
                exposure_rec['message'] = '{}, {}'.format(
                    loc_area_peril_rec['message'],
                    loc_vuln_peril_rec['message']
                )
            else:
                exposure_rec['status'] = oasis_utils.KEYS_STATUS_NOMATCH
                exposure_rec['message'] = 'No area peril or vulnerability match'

            yield exposure_rec


    def _get_location_record(self, loc_item):
        """
        Construct a location record (dict) from the location item, which in this
        case is a row in a Pandas dataframe.
        """
        meta = self._LOCATION_RECORD_META
        return dict(
            (
                k,
                meta[k]['validator'](loc_item[meta[k]['csv_header']])
            ) for k in meta
        )
