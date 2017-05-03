# (c) 2013-2016 Oasis LMF Ltd.  Software provided for early adopter evaluation only.
import os
import csv

EXPOSURE_FILE = "exposure_dict.csv"
AREA_PERIL_LOOKUP_FILE = "area_peril_dict.csv"
VULNERABILITY_LOOKUP_FILE = "vulnerability_dict.csv"

def create_test_exposure(
        number_of_locations=50000,
        min_lat=50, max_lat=60, grid_lat_dim=100,
        min_lon=-9, max_lon=2, grid_lon_dim=100):
    '''
    Create a test exposure data file for locations within a specified grid.
    Args:
        number_of_locations: the number of locations
        min_lat: the minimum latitude of the grid
        max_lat: the maximum latitude of the grid 
        grid_lat_dim: the latitudal dimension of the grid
        min_lon: the minimum longitude of the grid
        max_lon: the maximum longitude of the grid
        grid_lon_dim: the longitudinal dimension of the grid
    '''

    if os.path.exists(EXPOSURE_FILE):
        os.remove(EXPOSURE_FILE)

    with open(EXPOSURE_FILE, 'w') as csvfile:
        exposure_writer = csv.writer(csvfile, lineterminator='\n')
        for exposure_id in range(1, number_of_locations + 1):
            lat = round(
                min_lat + (((max_lat - min_lat)/grid_lat_dim) * exposure_id % grid_lat_dim), 2)
            lon = round(
                min_lon + (((max_lon - min_lon)/grid_lon_dim) * exposure_id % grid_lon_dim), 2)
            exposure_writer.writerow([exposure_id, lat, lon])

def create_area_peril_lookup_data(
        min_lat=50, max_lat=60,
        grid_lat_dim=100,
        min_lon=-9, max_lon=2,
        grid_lon_dim=100):
    '''
    Create test area peril lokup data file for a specified grid.
    Args:
        min_lat: the minimum latitude of the grid
        max_lat: the maximum latitude of the grid
        grid_lat_dim: the latitudal dimension of the grid
        min_lon: the minimum longitude of the grid
        max_lon: the maximum longitude of the grid
        grid_lon_dim: the longitudinal dimension of the grid
    '''
    if os.path.exists(AREA_PERIL_LOOKUP_FILE):
        os.remove(AREA_PERIL_LOOKUP_FILE)

    with open(AREA_PERIL_LOOKUP_FILE, 'w') as csvfile:
        exposure_writer = csv.writer(csvfile, lineterminator='\n')
        for area_peril_id in range(1, grid_lat_dim * grid_lon_dim + 1):
            lat1 = round(min_lat + (((max_lat - min_lat)/grid_lat_dim) * area_peril_id), 2)
            lon1 = round(min_lon + (((max_lon - min_lon)/grid_lon_dim) * area_peril_id), 2)
            lat2 = round(min_lat + (((max_lat - min_lat)/grid_lat_dim) * (area_peril_id + 1)), 2)
            lon2 = round(min_lon + (((max_lon - min_lon)/grid_lon_dim) * area_peril_id), 2)
            lat3 = round(min_lat + (((max_lat - min_lat)/grid_lat_dim) * area_peril_id), 2)
            lon3 = round(min_lon + (((max_lon - min_lon)/grid_lon_dim) * (area_peril_id + 1)), 2)
            lat4 = round(min_lat + (((max_lat - min_lat)/grid_lat_dim) * (area_peril_id + 1)), 2)
            lon4 = round(min_lon + (((max_lon - min_lon)/grid_lon_dim) * (area_peril_id + 1)), 2)

            exposure_writer.writerow(
                [area_peril_id, lat1, lon1, lat2, lon2, lat3, lon3, lat4, lon4])

print "Generating test data"
print "Generating exposure"
create_test_exposure()
print "Generating AreaPeril lookup data"

create_area_peril_lookup_data(
    number_of_area_perils=100, min_lat=-0.9176515, max_lat=-0.9176515 + 0.0606651,
    grid_lat_dim=10,
    min_lon=52.7339933, max_lon=52.7339933 + 0.0606651,
    grid_lon_dim=10)

print "Generating Vulnerability lookup data"
# TODO
print "Done"
