# (c) 2013-2016 Oasis LMF Ltd.  Software provided for early adopter evaluation only.
import csv
import urllib2
import json
import gzip
import os
# Not supported in cygwin
#import psutil
import argparse
import sys

class LookupClient(object):
    """
    Example lookup client for calling the PiWind lookup service and
    manipulating the response data.

    There is code to illustrate there approaches:
    1.) Posting the location data as CSV.
    2.) Posting the location data as JSON.
    3.) Batch posting the location data as JSON. This allows large location files to be
        handled without loading too much data into memory.
    """

    #_LOOKUP_URL = "http://localhost:50000/oasis/piwind/v1.0/lookup"
    #_lookup_url = "http://10.1.0.190/oasis/piwind/v1.0/lookup"
    #_exposure_file = os.path.abspath(os.path.join('utils', "exposure.csv"))

    _lookup_url = ""
    _exposure_file = ""

    _STATUS_SUCCESS = "success"
    _STATUS_FAIL = "fail"
    _STATUS_NOMATCH = "nomatch"

    def __init__(self, filename, url):
        self._exposure_file = filename
        self._lookup_url = url

    def do_lookup_json(self):
        """
        Do a lookup using a json request.
        """
        locations = list()
        with open(self._exposure_file, 'r') as csvfile:
            exposure_reader = csv.reader(csvfile, lineterminator='\n')
            for row in exposure_reader:
                locations.append({"id": int(row[0]), "lat": float(row[1]), "lon": float(row[2])})

        all_location_count = 0
        success_location_count = 0
        nomatch_location_count = 0
        fail_location_count = 0

        all_location_count = 0
        success_location_count = 0
        nomatch_location_count = 0
        fail_location_count = 0
        for location in self.lookup_locations(locations):
            all_location_count = all_location_count + 1
            if location['status'] == self._STATUS_SUCCESS:
                success_location_count = success_location_count + 1
            elif location['status'] == self._STATUS_NOMATCH:
                nomatch_location_count = nomatch_location_count + 1
            elif location['status'] == self._STATUS_FAIL:
                fail_location_count = fail_location_count + 1

        #process = psutil.Process(os.getpid())
        #print '{:,} locations : {:,} bytes'.format(len(locations), process.memory_info().rss)

        print '{:,} locations'.format(all_location_count)
        print '{0:.2f}% success'.format(100 * success_location_count/all_location_count)
        print '{0:.2f}% fail'.format(100 * fail_location_count/all_location_count)
        print '{0:.2f}% no match'.format(100 * nomatch_location_count/all_location_count)

    def do_lookup_json_batched(self):
        """
        Do a batched lookup using a json request.
        """
        batch_size = 1000

        all_location_count = 0
        success_location_count = 0
        nomatch_location_count = 0
        fail_location_count = 0

        locations = list()
        with open(self._exposure_file, 'r') as csvfile:
            exposure_reader = csv.reader(csvfile, lineterminator='\n')
            
            # Skip the header
            next(exposure_reader)

            count = 0
            for row in exposure_reader:
                locations.append({
                    "id": int(row[0]), "lat": float(row[1]), "lon": float(row[2]),
                    "class_1": row[3], "class_2": row[4], "coverage": row[5]})
                count = count + 1
                if count % batch_size == 0:
                    for location in self.lookup_locations(locations):
                        all_location_count = all_location_count + 1
                        if location['status'] == self._STATUS_SUCCESS:
                            success_location_count = success_location_count + 1
                        elif location['status'] == self._STATUS_NOMATCH:
                            nomatch_location_count = nomatch_location_count + 1
                        elif location['status'] == self._STATUS_FAIL:
                            fail_location_count = fail_location_count + 1
                    #process = psutil.Process(os.getpid())
                    #print '{:,} locations : {:,} bytes'.format(count, process.memory_info().rss)
                    del locations[:]

        for location in self.lookup_locations(locations):
            all_location_count = all_location_count + 1
            if location['status'] == self._STATUS_SUCCESS:
                success_location_count = success_location_count + 1
            elif location['status'] == self._STATUS_NOMATCH:
                nomatch_location_count = nomatch_location_count + 1
            elif location['status'] == self._STATUS_FAIL:
                fail_location_count = fail_location_count + 1

        #process = psutil.Process(os.getpid())
        #print '{:,} locations : {:,} bytes'.format(count, process.memory_info().rss)

        print '{:,} locations'.format(all_location_count)
        print '{0:.2f}% success'.format(100.0 * success_location_count/all_location_count)
        print '{0:.2f}% fail'.format(100.0 * fail_location_count/all_location_count)
        print '{0:.2f}% no match'.format(100.0 * nomatch_location_count/all_location_count)

    def lookup_locations(self, locations):
        '''
        Do a lookup on a set of locations.
        '''
        req = urllib2.Request(self._lookup_url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsondata = json.dumps(locations)
        jsondataasbytes = jsondata.encode('utf-8')
        req.add_header('Content-Length', len(jsondataasbytes))
        response = urllib2.urlopen(req, jsondataasbytes)
        return json.loads(gzip.zlib.decompress(response.read()).decode('utf-8'))

    def do_lookup_csv(self):
        """
        Do a lookup using a csv request.
        """

        with open(self._exposure_file, 'r') as exposure_file:
            csv_data = exposure_file.read()

        csv_data_bytes = csv_data.encode()

        req = urllib2.Request(self._lookup_url)
        req.add_header('Content-Type', 'text/csv; charset=utf-8')
        req.add_header('Content-Length', len(csv_data_bytes))
        response = urllib2.urlopen(req, data=csv_data_bytes)

        locations = json.loads(gzip.zlib.decompress(response.read()).decode('utf-8'))

        all_location_count = 0
        success_location_count = 0
        nomatch_location_count = 0
        fail_location_count = 0
        for location in locations:
            all_location_count = all_location_count + 1
            if location['status'] == self._STATUS_SUCCESS:
                success_location_count = success_location_count + 1
            elif location['status'] == self._STATUS_NOMATCH:
                nomatch_location_count = nomatch_location_count + 1
            elif location['status'] == self._STATUS_FAIL:
                fail_location_count = fail_location_count + 1

        #process = psutil.Process(os.getpid())
        #print '{:,} locations : {:,} bytes'.format(len(locations), process.memory_info().rss)

        print '{:,} locations'.format(all_location_count)
        print '{0:.2f}% success'.format(100 * success_location_count/all_location_count)
        print '{0:.2f}% fail'.format(100 * fail_location_count/all_location_count)
        print '{0:.2f}% no match'.format(100 * nomatch_location_count/all_location_count)

    def do_lookup_csv_to_stdout(self):
        """
        Do a lookup using a csv request.
        """
        with open(self._exposure_file, 'r') as exposure_file:
            csv_data = exposure_file.read()

        csv_data_bytes = csv_data.encode()

        req = urllib2.Request(self._lookup_url)
        req.add_header('Content-Type', 'text/csv; charset=utf-8')
        req.add_header('Content-Length', len(csv_data_bytes))
        response = urllib2.urlopen(req, data=csv_data_bytes)
        
        sys.stdout.write(gzip.zlib.decompress(response.read()))

#
# Invoke lookup from command line.
#
if __name__ = '__main__':
    parser = argparse.ArgumentParser(description='Run a Pi Wind v1.0 exposure lookup.')
    parser.add_argument('-URL', metavar='URL', type=str, help='The lookup server URL.', required=True)
    parser.add_argument('exposure_file', metavar='exposure_file', type=str, help='The exposure data file.')
    args = parser.parse_args()

    # Check exposure file
    lookup_client = LookupClient(args.exposure_file, args.URL)
    lookup_client.do_lookup_csv_to_stdout()