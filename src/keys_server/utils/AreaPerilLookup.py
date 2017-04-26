__all__ = ['AreaPerilLookup']

# (c) 2013-2016 Oasis LMF Ltd.  Software provided for early adopter evaluation only.
'''
Area peril lookup.
'''
import csv
import logging

from shapely.geometry import (
    Point,
    MultiPoint,
)

import oasis_utils


class AreaPerilLookup(object):
    '''
    Functionality to perform an area peril lookup.
    '''

    def __init__(self, areas_file=None):
        self._lookup_data = []

        if areas_file:
            with open(areas_file, 'r') as f:
                dr = csv.DictReader(f)
                for r in dr:
                    self._lookup_data.append(
                        (
                            int(r['AREA_PERIL_ID']),
                            MultiPoint(
                                tuple((float(r['LAT{}'.format(i)]),float(r['LON{}'.format(i)])) for i in range(1, 5))
                            ).convex_hull
                        )
                    )                


    def set_lookup_data(self, data):
        '''
        Set the lookup data.
        Args:
            data: the lookup data.
        '''
        self._lookup_data = []
        for rec in data:
            self._lookup_data.append(
                (rec['id'], MultiPoint(rec['points']).convex_hull)
            )


    def validate_lat(self, lat):
        '''
        Check that a string or number is a valid latitude.
        Args:
            s (string or number): the latitude
        Returns:
            True if string is a valid latitude, False otherwise
        '''
        return -90 <= lat <= 90


    def validate_lon(self, lon):
        '''
        Check that a string or number is a valid longitude.
        Args:
            s (string or number): the longitude
        Returns:
            True if string is a valid longitude, False otherwise
        '''
        return -180 <= lon <= 180


    def do_lookup_location(self, location):
        '''
        Perform a lookup on a specified location.
        Args:
            location: the location to lookup.
        Return:
            Lookup result
        '''
        logging.debug("Looking up location.")
        
        status = oasis_utils.KEYS_STATUS_NOMATCH
        area_peril_id = None
        message = ''

        lat = location['lat']
        lon = location['lon']

        if not self.validate_lat(lat) & self.validate_lon(lon):
            status = oasis_utils.KEYS_STATUS_FAIL
            area_peril_id = None
            message = "Invalid lat/lon"
        else:
            loc_point = Point(lat, lon)
            for (cell_area_peril_id, cell) in self._lookup_data:
                if cell.intersects(loc_point):
                    area_peril_id = cell_area_peril_id
                    status = oasis_utils.KEYS_STATUS_SUCCESS
                    break

        return {
            'status': status,
            'area_peril_id': area_peril_id,
            'message': message
        }
