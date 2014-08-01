#!/usr/bin/env python

##
## Grabs all probes information from atlas.ripe.net that are later used to process data.
##

import json
import urllib2
from pprint import pprint 

all_probes_url = 'https://atlas.ripe.net/api/v1/probe/?limit=0'

url_fh = urllib2.urlopen( all_probes_url )
prb_info = json.load( url_fh )
url_fh.close()

for prb_id in prb_info['objects']:
   print "%s %0.4f %0.4f %s %s %s" % ( prb_id['id'], prb_id['latitude'], prb_id['longitude'], prb_id['asn_v4'], prb_id['asn_v6'], prb_id['country_code'] ) 

