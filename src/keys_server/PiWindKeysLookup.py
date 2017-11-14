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

from .OasisBaseKeysLookup import OasisBaseKeysLookup

from .utils import (
    AreaPerilLookup,
    VulnerabilityLookup,
)


class PiWindKeysLookup(OasisBaseKeysLookup):
    """
    PiWind keys lookup.
    """

    _LOCATION_RECORD_META = {
        'id': {'source_header': 'ID', 'csv_data_type': int, 'validator': oasis_utils.to_int, 'desc': 'Location ID'},
        'lon': {'source_header': 'LON', 'csv_data_type': float, 'validator': oasis_utils.to_float, 'desc': 'Longitude'},
        'lat': {'source_header': 'LAT', 'csv_data_type': float, 'validator': oasis_utils.to_float, 'desc': 'Latitude'},
        'coverage': {'source_header': 'COVERAGE', 'csv_data_type': int, 'validator': oasis_utils.to_int, 'desc': 'Coverage'},
        'class_1': {'source_header': 'CLASS_1', 'csv_data_type': str, 'validator': oasis_utils.to_string, 'desc': 'Class #1'},
        'class_2': {'source_header': 'CLASS_2', 'csv_data_type': str, 'validator': oasis_utils.to_string, 'desc': 'Class #2'}
    }


    @oasis_log_utils.oasis_log()
    def __init__(self, keys_data_directory, supplier, model_name, model_version):
        """
        Initialise the static data required for the lookup.
        """
        super(self.__class__, self).__init__(
            keys_data_directory,
            supplier,
            model_name,
            model_version
        )

        self.area_peril_lookup = AreaPerilLookup(
            areas_file=os.path.join(self.keys_data_directory, 'area_peril_dict.csv')
        ) if keys_data_directory else AreaPerilLookup()
        
        self.vulnerability_lookup = VulnerabilityLookup(
            vulnerabilities_file=os.path.join(self.keys_data_directory, 'vulnerability_dict.csv')
        ) if keys_data_directory else VulnerabilityLookup()

    
    @oasis_log_utils.oasis_log()
    def process_locations(self, loc_df):
        """
        Process location rows - passed in as a pandas dataframe.
        """

        for i in range(len(loc_df)):            
            record = self._get_location_record(loc_df.loc[i])

            area_peril_rec = self.area_peril_lookup.do_lookup_location(record)

            vuln_peril_rec = self.vulnerability_lookup.do_lookup_location(record)

            status = message = ''

            if area_peril_rec['status'] == vuln_peril_rec['status'] == oasis_utils.KEYS_STATUS_SUCCESS:
                status = oasis_utils.KEYS_STATUS_SUCCESS
            elif (
                area_peril_rec['status'] == oasis_utils.KEYS_STATUS_FAIL or
                vuln_peril_rec['status'] == oasis_utils.KEYS_STATUS_FAIL
            ):
                status = oasis_utils.KEYS_STATUS_FAIL
                message = '{}, {}'.format(
                    area_peril_rec['message'],
                    vuln_peril_rec['message']
                )
            else:
                status = oasis_utils.KEYS_STATUS_NOMATCH
                message = 'No area peril or vulnerability match'

            yield {
                "id": record['id'],
                "peril_id": oasis_utils.PERIL_ID_WIND,
                "coverage": record['coverage'],
                "area_peril_id": area_peril_rec['area_peril_id'],
                "vulnerability_id": vuln_peril_rec['vulnerability_id'],
                "message": message,
                "status": status
            }


    def _get_location_record(self, loc_item):
        """
        Construct a location record (dict) from the location item, which in this
        case is a row in a Pandas dataframe.
        """
        meta = self._LOCATION_RECORD_META
        return dict(
            (
                k,
                meta[k]['validator'](loc_item[meta[k]['source_header']])
            ) for k in meta
        )
