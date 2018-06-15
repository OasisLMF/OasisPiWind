# -*- coding: utf-8 -*-

__all__ = [
  'PiWindKeysLookup'
] 

# Python 2 standard library imports
import io
import logging
import os

from collections import OrderedDict

try:
     from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

# Python 2 non-standard library imports
import pandas as pd
import six

from rtree.core import RTreeError
from rtree.index import Index

from shapely.geometry import MultiPoint

# Imports from Oasis core repos + subpackages or modules within `keys_server` subpackage
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

        # Load keys server and lookup settings from INI file
        self.keys_server_ini_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'KeysServer.ini')
        if not os.path.exists(self.keys_server_ini_file_path):
            raise OasisException()

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

        # Create an RTree index with the area peril entries - index entries are
        #
        #    (area peril ID, area polygon bounds)
        #
        # pairs. Also store as a dict - entries are
        #
        #    (area peril ID, area peril entry dict)
        #
        # pairs.
        self.area_perils_fp = os.path.join(self.keys_data_directory, self.config.get('Lookup', 'AREA_PERILS_FILE'))

        with io.open(self.area_perils_fp, 'r', encoding='utf-8') as f:
            ap_df = pd.read_csv(f, float_precision='high')

        ap_df.dropna(subset=ap_df.columns, inplace=True)
        ap_df.columns = ap_df.columns.str.lower()
        ap_df['index'] = list(range(len(ap_df)))
        ap_df['area_peril_id'] = ap_df['area_peril_id'].apply(int)
        ap_df['area_peril_id'] = ap_df['area_peril_id'].astype(object)

        self.area_perils = {}

        def _ap_idx_entries():
            for _, ap in ap_df.iterrows():
                apid = ap['area_peril_id']
                self.area_perils[apid] = ap.to_dict()
                poly = MultiPoint(tuple((float(ap['lon{}'.format(i)]),float(ap['lat{}'.format(i)])) for i in range(1, 5))).convex_hull
                yield (apid, poly.bounds, None)

        self.area_perils_idx = Index(_ap_idx_entries())

        # Create a vulnerabilities ordered dict - entries are 
        #
        #    ((coverage type, class 1), vulnerabilty ID)
        #
        # pairs. The reason for making this dict ordered (by ID, ascending) is
        # that it is used directly for the vulnerabilty ID lookup, whereas
        # the area peril ID lookup uses the RTree index, which imposes its
        # order internally.
        self.vulnerabilities_fp = os.path.join(self.keys_data_directory, self.config.get('Lookup', 'VULNERABILITIES_FILE'))

        with io.open(self.vulnerabilities_fp, 'r', encoding='utf-8') as f:
            vln_df = pd.read_csv(f, float_precision='high')

        vln_df.dropna(subset=vln_df.columns, inplace=True)
        vln_df.columns = vln_df.columns.str.lower()
        vln_df['index'] = list(range(len(vln_df)))
        vln_df['coverage'] = vln_df['coverage'].apply(int)
        vln_df['vulnerability_id'] = vln_df['vulnerability_id'].apply(int)
        vln_df['coverage'] = vln_df['coverage'].astype(object)
        vln_df['vulnerability_id'] = vln_df['vulnerability_id'].astype(object)

        self.vulnerabilities = OrderedDict(
            [
                ((it['coverage'],it['class_1']), it['vulnerability_id'])
                for _, it in vln_df.iterrows()
            ]
        )

    def lookup_area_peril(self, loc_item):
        """
        Area peril lookup for an individual item, which could be a dict or a
        Pandas series.
        """
        lon = loc_item['lon']
        lat = loc_item['lat']

        ap_lookup = lambda loc_id, apst, apid, apmsg: {
            'id': loc_id,
            'area_peril_status': apst,
            'area_peril_id': apid,
            'area_peril_message': apmsg
        }

        try:
            lon = float(lon)
            lat = float(lat)
            if not ((-180 <= lon <= 180) and (-90 <= lat <= 90)):
                raise ValueError('lon/lat out of bounds')
        except (ValueError, TypeError) as e:
            return ap_lookup(loc_item['id'], KEYS_STATUS_FAIL, None, 'Area peril lookup: invalid lon/lat ({}, {}) - {}'.format(lon, lat, str(e)))

        apst = KEYS_STATUS_NOMATCH
        apmsg = 'No area peril match'
        apid = None
        point = lon, lat

        try:
            apid = list(self.area_perils_idx.intersection(point))[0]
        except IndexError:
            try:
                apid = list(self.area_perils_idx.nearest(point))[0]
            except IndexError:
                pass
        except RTreeError as e:
            return ap_lookup(loc_item['id'], KEYS_STATUS_FAIL, None, str(e))
        else:
            apst = KEYS_STATUS_SUCCESS
            apmsg = 'Successful area peril lookup: {}'.format(apid)

        return ap_lookup(loc_item['id'], apst, apid, apmsg)

    def lookup_vulnerability(self, loc_item):
        """
        Vulnerability lookup for an individual item, which could be a dict or a
        Pandas series.
        """
        coverage = loc_item['coverage']
        class_1 = loc_item['class_1']

        vln_lookup = lambda loc_id, vlnst, vlnid, vlnmsg: {
            'id': loc_id,
            'vulnerability_status': vlnst,
            'vulnerability_id': vlnid,
            'vulnerability_message': vlnmsg
        }

        try:
            int(coverage) and str(class_1)
        except (TypeError, ValueError):
            return vln_lookup(loc_item['id'], KEYS_STATUS_FAIL, None, 'Vulnerability lookup: invalid location coverage or class 1')

        vlnst = KEYS_STATUS_NOMATCH
        vlnmsg = 'No vulnerability match'
        vlnid = None

        try:
            vlnid = self.vulnerabilities[(loc_item['coverage'], loc_item['class_1'])]
        except KeyError:
            pass
        else:
            vlnst = KEYS_STATUS_SUCCESS
            vlnmsg = 'Successful vulnerability lookup: {}'.format(vlnid)

        return vln_lookup(loc_item['id'], vlnst, vlnid, vlnmsg)

    def lookup_status(self, loc_item):
        """
        Gets the combined area peril and vulnerability lookup status and message
        """
        apst = loc_item['area_peril_status']
        apmsg = loc_item['area_peril_message']

        vlnst = loc_item['vulnerability_status']
        vlnmsg = loc_item['vulnerability_message']

        cmbst = KEYS_STATUS_NOMATCH
        cmbmsg = '{}; {}'.format(apmsg, vlnmsg)

        if apst == vlnst == KEYS_STATUS_SUCCESS:
            cmbst = KEYS_STATUS_SUCCESS
        elif apst == KEYS_STATUS_FAIL or vlnst == KEYS_STATUS_FAIL:
            cmbst = KEYS_STATUS_FAIL

        return {'status': cmbst, 'message': cmbmsg}

    @oasis_log()
    def process_locations(self, loc_df):
        """
        Process location rows - passed in as a pandas dataframe.

        NOTE: Does not return anything, but generates lookup dicts/records using `yield`.
        This method is designed to be a Python generator.
        """
        for _, it in loc_df.iterrows():
            ap_lookup = self.lookup_area_peril(it)
            apst = ap_lookup['area_peril_status']
            apmsg = ap_lookup['area_peril_message']
            
            vln_lookup = self.lookup_vulnerability(it)
            vlnst = vln_lookup['vulnerability_status']
            vlnmsg = vln_lookup['vulnerability_message']
            
            # Could optionally call the status lookup method, but it is always
            # better to avoid outside function calls in a `for` loop if possible
            status = (
                KEYS_STATUS_SUCCESS if apst == vlnst == KEYS_STATUS_SUCCESS
                else (KEYS_STATUS_FAIL if (apst == KEYS_STATUS_FAIL or vlnst == KEYS_STATUS_FAIL) else KEYS_STATUS_NOMATCH)
            )
            
            message = '{}; {}'.format(apmsg, vlnmsg)

            yield {
                'id': it['id'],
                'peril_id': PERIL_ID_WIND,
                'coverage': it['coverage'],
                'area_peril_id': ap_lookup['area_peril_id'],
                'vulnerability_id': vln_lookup['vulnerability_id'],
                'status': status,
                'message': message
            }
