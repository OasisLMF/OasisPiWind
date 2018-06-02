# -*- coding: utf-8 -*-

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
from oasislmf.keys.lookup import OasisBaseKeysLookup
from oasislmf.utils.log import oasis_log
from oasislmf.utils.peril import PERIL_ID_WIND
from oasislmf.utils.status import (
    KEYS_STATUS_FAIL,
    KEYS_STATUS_NOMATCH,
    KEYS_STATUS_SUCCESS,
)
from oasislmf.utils.values import (
    to_int,
    to_float,
    to_string,
)

from .utils import (
    AreaPerilLookup,
    VulnerabilityLookup,
)


class PiWindKeysLookup(OasisBaseKeysLookup):
    """
    PiWind keys lookup.
    """

    @oasis_log()
    def __init__(self, keys_data_directory=None, supplier='OasisLMF', model_name='PiWind', model_version=None):
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

    
    @oasis_log()
    def process_locations(self, loc_df):
        """
        Process location rows - passed in as a pandas dataframe.
        """
        aplookup = self.area_peril_lookup.do_lookup_location
        vlookup = self.vulnerability_lookup.do_lookup_location

        for _, it in loc_df.iterrows():
            rec = it.to_dict()

            area_peril_rec = aplookup(rec)

            vuln_peril_rec = vlookup(rec)

            status = message = ''

            if area_peril_rec['status'] == vuln_peril_rec['status'] == KEYS_STATUS_SUCCESS:
                status = KEYS_STATUS_SUCCESS
            elif (
                area_peril_rec['status'] == KEYS_STATUS_FAIL or
                vuln_peril_rec['status'] == KEYS_STATUS_FAIL
            ):
                status = KEYS_STATUS_FAIL
                message = '{}, {}'.format(
                    area_peril_rec['message'],
                    vuln_peril_rec['message']
                )
            else:
                status = KEYS_STATUS_NOMATCH
                message = 'No area peril or vulnerability match'

            yield {
                "id": rec['id'],
                "peril_id": PERIL_ID_WIND,
                "coverage": rec['coverage'],
                "area_peril_id": area_peril_rec['area_peril_id'],
                "vulnerability_id": vuln_peril_rec['vulnerability_id'],
                "message": message,
                "status": status
            }
