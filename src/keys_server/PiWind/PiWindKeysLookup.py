# -*- coding: utf-8 -*-

__all__ = [
  'PiWindKeysLookup'
] 

# Python 2 standard library imports
import io
import logging
import os

try:
     from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

# Python 2 non-standard library imports
import pandas as pd
import six

from shapely.geometry import (
    Point,
    MultiPoint,
)

# Imports from Oasis core repos + subpackages or modules within keys_server
from oasislmf.keys.lookup import OasisBaseKeysLookup
from oasislmf.utils.exceptions import OasisException
from oasislmf.utils.log import oasis_log
from oasislmf.utils.peril import PERIL_ID_WIND
from oasislmf.utils.status import (
    KEYS_STATUS_FAIL,
    KEYS_STATUS_NOMATCH,
    KEYS_STATUS_SUCCESS,
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
        # Model peril ID - the lookup instance should certainly know the peril ID associated
        # with the model, hence the instance variable. For multiple perils this can be stored
        # as a tuple
        self.peril_id = PERIL_ID_WIND

        # Keys server config parser - reads the keys server INI file path, which should exist
        # in the same place as this file
        self.config = ConfigParser()

        # Keys server/lookup INI file path
        self.keys_server_ini_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'KeysServer.ini')
        if not os.path.exists(self.keys_server_ini_file_path):
            raise OasisException()

        #
        self.config.read(self.keys_server_ini_file_path)

        # Set keys data directory to be the value passed in via the constructor, or if this does not exist
        # the value found in the keys server INI file which should exist in the same directory as this file
        # - raise an `OasisException` if none of these exist
        self.keys_data_directory = keys_data_directory if keys_data_directory else self.config.get('Default', 'KEYS_DATA_DIRECTORY')

        if not keys_data_directory:
            raise OasisException('No keys data directory specified - expected a valid path via the class constructor or keys server INI file')
        
        # Pass keys data directory, supplier, model ID/name and version to super class
        super(self.__class__, self).__init__(
            self.keys_data_directory,
            supplier,
            model_name,
            model_version
        )

        # Load the area perils dictionary file into a dict
        self.area_perils_file_path = os.path.join(self.keys_data_directory, self.config.get('Keys Data', 'AREA_PERILS_FILE'))
        with io.open(self.area_perils_file_path, 'r', encoding='utf-8') as f:
            ap_df = pd.read_csv(f, float_precision='high')
            ap_df = ap_df.where(ap_df.notnull(), None)
            ap_df.columns = ap_df.columns.str.lower()
            
            # Area perils lookup dictionary - keys are tuples of lat/lon coordinates for polygon vertices
            # and values are contained in a dictionary containing the polygon (`shapely.geometry.MultiPoint`)
            # represented by the vertices and the area peril ID associated with that polygon
            self.area_perils = {
                tuple((it['lat{}'.format(i)], it['lon{}'.format(i)]) for i in range(1, 5)):{
                    'polygon':MultiPoint(tuple((it['lat{}'.format(i)], it['lon{}'.format(i)]) for i in range(1, 5))).convex_hull,
                    'area_peril_id': int(it['area_peril_id'])
                }
                for _, it in ap_df.iterrows()
            }

        # Load the vulnerability dictionary file into a dict
        self.vulnerabilities_file_path = os.path.join(self.keys_data_directory, self.config.get('Keys Data', 'VULNERABILITIES_FILE'))
        with io.open(self.vulnerabilities_file_path, 'r', encoding='utf-8') as f:
            vln_df = pd.read_csv(f, float_precision='high')
            vln_df = vln_df.where(vln_df.notnull(), None)
            vln_df.columns = vln_df.columns.str.lower()
            
            # Vulnerabilities dictionary - keys are coverage/class 1 tuples and values are vulnerability IDs
            self.vulnerabilities = {
                (int(it['coverage']), it['class_1']):int(it['vulnerability_id'])
                for _, it in vln_df.iterrows()
            }

    def get_area_peril_id(self, loc_it):
        """
        Area peril lookup method for an individual item, which could be a dict or a
        Pandas series.
        """
        apst = KEYS_STATUS_NOMATCH
        apmsg = 'No area peril match'
        apid = None

        if not (-90 <= float(loc_it['lat']) <= 90 and -180 <= float(loc_it['lon']) <= 180):
            apst = KEYS_STATUS_FAIL
            apmsg = "Invalid lat/lon"
        else:
            ap = [apit['area_peril_id'] for apit in six.itervalues(self.area_perils) if apit['polygon'].intersects(Point(loc_it['lat'],loc_it['lon']))]
            if ap:
                apst = KEYS_STATUS_SUCCESS
                apid = ap[0]
                apmsg = "Successful area peril match {}".format(ap[0])

        return {'area_peril_status': apst, 'area_peril_id': apid, 'area_peril_message': apmsg}

    def get_vulnerability_id(self, loc_it):
        """
        Vulnerability lookup method for an individual item, which could be a dict or a
        Pandas series.
        """
        vlnst = KEYS_STATUS_NOMATCH
        vlnmsg = 'No vulnerability match'
        vlnid = None

        vln = [vlnid for (coverage, class_1), vlnid in six.iteritems(self.vulnerabilities) if coverage == loc_it['coverage'] and class_1 == loc_it['class_1']]
        if vln:
            vlnst = KEYS_STATUS_SUCCESS
            vlnid = vln[0]
            vlnmsg = "Successful vulnerability match {}".format(vln[0])

        return {'vulnerability_status': vlnst, 'vulnerability_id': vlnid, 'vulnerability_message': vlnmsg}

    @oasis_log()
    def process_locations(self, loc_df):
        """
        Process location rows - passed in as a pandas dataframe.

        NOTE: Does not return anything, but generates lookup dicts/records using `yield`.
        This method is designed to be a Python generator.
        """
        
        # Main loop over location items in locations dataframe
        for _, loc_it in loc_df.iterrows():

            # Initial area peril lookup values
            apst = KEYS_STATUS_NOMATCH
            apmsg = 'No area peril match'
            apid = None

            # Initial vulnerability lookup values
            vlnst = KEYS_STATUS_NOMATCH
            vlnmsg = 'No vulnerability match'
            vlnid = None

            # Combined (area peril and vulnerability) status and message
            cmbst = KEYS_STATUS_NOMATCH
            cmbmsg = '{}, {}'.format(apmsg, vlnmsg)
            
            # Area peril lookup for location item - could be done via function call to get_area_peril_id
            # but it is faster to avoid function calls in a `for` loop if possible
            if not (-90 <= float(loc_it['lat']) <= 90 and -180 <= float(loc_it['lon']) <= 180):
                apst = KEYS_STATUS_FAIL
                apmsg = "Invalid lat/lon"
            else:
                ap = [apit['area_peril_id'] for apit in six.itervalues(self.area_perils) if apit['polygon'].intersects(Point(loc_it['lat'],loc_it['lon']))]
                if ap:
                    apst = KEYS_STATUS_SUCCESS
                    apid = ap[0]
                    apmsg = "Successful area peril match {}".format(ap[0])

            # Vulnerablity lookup for location item - could be done via function call to get_vulnerability_id
            # but it is faster to avoid function calls in a `for` loop if possible
            vln = [vlnid for (coverage, class_1), vlnid in six.iteritems(self.vulnerabilities) if coverage == loc_it['coverage'] and class_1 == loc_it['class_1']]
            if vln:
                vlnst = KEYS_STATUS_SUCCESS
                vlnid = vln[0]
                vlnmsg = "Successful vulnerability match {}".format(vln[0])

            # Set combined status
            if apst == KEYS_STATUS_SUCCESS and vlnst == KEYS_STATUS_SUCCESS:
                cmbst = KEYS_STATUS_SUCCESS
            elif apst == KEYS_STATUS_FAIL or vlnst == KEYS_STATUS_FAIL:
                cmbst = KEYS_STATUS_FAIL

            # Set combined message
            cmbmsg = '{}, {}'.format(apmsg, vlnmsg)

            # Generate lookup record
            yield {
                "id": loc_it['id'],
                "peril_id": self.peril_id,
                "coverage": loc_it['coverage'],
                "area_peril_id": apid,
                "vulnerability_id": vlnid,
                "message": cmbmsg,
                "status": cmbst
            }
