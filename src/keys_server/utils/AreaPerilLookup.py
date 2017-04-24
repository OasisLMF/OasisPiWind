__all__ = ['AreaPerilLookup']

# (c) 2013-2016 Oasis LMF Ltd.  Software provided for early adopter evaluation only.
'''
AreaPeril lookup.
'''
import logging

from shapely.geometry import (
    Point,
    Polygon,
    MultiPoint,
)

from .LookupStatus import *


class AreaPerilLookup(object):
    '''
    Functionality to perform an AreaPeril lookup.
    '''

    def __init__(self):
        self._lookup_data = []


    def is_number(self, value_to_check):
        '''
        Check that a string is numeric.
        Args:
            s (string): the string to validate
        Returns:
            True if string is numeric, False otherwise
        '''
        try:
            float(value_to_check)
        except ValueError:
            return False
        return True


    def validate_lat(self, lat):
        '''
        Check that a string or number is a valid latitude.
        Args:
            s (string or number): the latitude
        Returns:
            True if string is a valiud latitude, False otherwise
        '''
        if not self.is_number(lat):
            return False
        return (float(lat) >= -90) & (float(lat) <= 90.0)


    def validate_lon(self, lon):
        '''
        Check that a string or number is a valid longitude.
        Args:
            s (string or number): the longitude
        Returns:
            True if string is a valiud longitude, False otherwise
        '''
        if not self.is_number(lon):
            return False
        return (float(lon) >= -180) & (float(lon) <= 180.0)


    def set_lookup_data(self, data):
        '''
        Set the lookup data.
        Args:
            data: the lookup data.
        '''
        for value in data:
            self._lookup_data.append(
                (value['id'], MultiPoint(value['points']).convex_hull)
            )

    def do_lookup_location(self, location):
        '''
        Perform a lookup on a specified location.
        Args:
            location: the location to lookup.
        Return:
            Lookup result
        '''
        logging.debug("Looking up location.", )
        
        status = STATUS_NOMATCH
        area_peril_id = None
        message = None

        lat = location['lat']
        lon = location['lon']

        if not self.validate_lat(lat) & self.validate_lon(lon):
            status = STATUS_FAIL
            area_peril_id = None
            message = "Invalid lat/lon"
        else:
            point = Point(lat, lon)
            for (cell_area_peril_id, cell) in self._lookup_data:
                if cell.intersects(point):
                    area_peril_id = cell_area_peril_id
                    status = STATUS_SUCCESS
                    break

        return {
            'status': status,
            'area_peril_id': area_peril_id,
            'message': message
        }
