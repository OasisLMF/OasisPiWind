#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/oasis")

from oasis_keys_server import APP2 as application
application.secret_key = 'Add your secret key'
