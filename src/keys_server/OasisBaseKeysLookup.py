__all__ = [
    'OasisBaseKeysLookup'
]

import logging
import os

from oasis_utils import (
    oasis_utils,
    oasis_log_utils,
)

class OasisBaseKeysLookup(object):
    """
    A base class / interface that serves a template for model-specific keys
    lookup classes.

    """

    @oasis_log_utils.oasis_log()
    def __init__(
        self,
        keys_data_directory=os.path.join(os.sep, 'var', 'oasis', 'keys_data'),
        supplier=None,
        model_name=None,
        model_version=None
    ):
        """
        Class constructor
        """
        self.keys_data_directory = keys_data_directory
        self.supplier = supplier
        self.model_name = model_name
        self.model_version = model_version


    @oasis_log_utils.oasis_log()
    def process_locations(self, loc_data, mime_type=oasis_utils.MIME_TYPE_CSV):
        """
        Read in raw location rows from request data and generate exposure
        records. The request content MIME type is assumed to be CSV, but can be
        explicitly set to JSON by the caller.
        """
        pass


    def _get_location_record(self, raw_loc_item):
        """
        Returns a dict of standard location keys and values based on
        a raw location item, which could be a Pandas or Geopandas dataframe
        row or a string representing a line from a CSV file, or a list or
        tuple.
        """
        pass


    def _get_area_peril_id(self, record):
        """
        Get the area peril ID for a particular location record.
        """
        return oasis_utils.UNKNOWN_ID, "Not implemented"


    def _get_vulnerability_id(self, record):
        """
        Get the vulnerability ID for a particular location record.
        """
        return oasis_utils.UNKNOWN_ID-1, "Not implemented"


    @oasis_log_utils.oasis_log()
    def _get_area_peril_ids(self, loc_data, include_context=True):
        """
        Generates area peril IDs in two modes - if include_context is
        True (default) it will generate location records/rows including
        the area peril IDs, otherwise it will generate pairs of location
        IDs and the corresponding area peril IDs.
        """
        pass


    @oasis_log_utils.oasis_log()
    def _get_vulnerability_ids(self, loc_data, include_context=True):
        """
        Generates vulnerability IDs in two modes - if include_context is
        True (default) it will generate location records/rows including
        the area peril IDs, otherwise it will generate pairs of location
        IDs and the corresponding vulnerability IDs.
        """
        pass


    def _get_lookup_success(self, ap_id, vul_id):
        """
        Determine the status of the keys lookup.
        """
        status = oasis_utils.KEYS_STATUS_SUCCESS
        if ap_id == oasis_utils.UNKNOWN_ID or vul_id == oasis_utils.UNKNOWN_ID:
            status = oasis_utils.KEYS_STATUS_NOMATCH
        return status

