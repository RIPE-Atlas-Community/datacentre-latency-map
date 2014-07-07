#!/usr/bin/env python
import yaml
import json
import os
import sys
import time
import urllib2

config_file = "./conf.yaml"
msm_info=[]
msm_info_file="./msm.json"

MSM_START_OFFSET=600 # 5 minutes
MSM_SPACING=90 # how far apart to do measurements

### AUTH
authfile = "%s/.atlas/auth" % os.environ['HOME']
if not os.path.exists(authfile):
    print >>sys.stderr, ("Authentication file %s not found" % authfile)
    sys.exit(1)
auth = open(authfile)
KEY = auth.readline()[:-1]
auth.close()
KEY.rstrip()
### END AUTH

MSM_URL = "https://atlas.ripe.net/api/v1/measurement/?key=%s" % KEY

class JsonRequest(urllib2.Request):
    def __init__(self, url):
        urllib2.Request.__init__(self, url)
        self.add_header("Content-Type", "application/json")
        self.add_header("Accept", "application/json")

with open(config_file) as f:
   config = yaml.safe_load( f )

def start_measure( hostname, af ):
   now=int(time.time())
   msm_def = {
      "definitions": [
         {
            'target': hostname,
            'af': af,
            'description': "%s / IPv%d (4x a day, 16pkt)" % (hostname, af),
            'type': 'ping',
            'resolve_on_probe': True,
            'interval': 86400/4, # 4x a day
            'packets': 16
         }
      ],
      "probes": [
         { 'requested': -1,
           'type': 'area',
           'value': 'WW'
         }
      ], 
      'start_time': now+MSM_START_OFFSET
   }
   json_data = json.dumps( msm_def )
   msm_req = JsonRequest(MSM_URL)
   try:
      msm_conn = urllib2.urlopen(msm_req, json_data)
   except urllib2.HTTPError as e:
        print >>sys.stderr, ("Fatal error when reading results: %s" % e.read())
        sys.exit(1)
   # Now, parse the answer
   msm_meta = json.load(msm_conn)
   msm_id = msm_meta["measurements"][0]
   msm_chunk = {
         'msm_id': msm_id,
         'af': af,
         'hostname': hostname
   }
   print(msm_chunk)
   msm_info.append( msm_chunk )
   time.sleep( MSM_SPACING )
   return msm_chunk

lb_hostname = config['loadbalancer']['hostname']   
for af in [4,6]:
   start_measure( lb_hostname, af)

for dc in config['datacenters']:
   dc_hostname = dc['hostname']
   for af in [4,6]:
      start_measure( dc_hostname, af)

with open( msm_info_file, 'w' ) as outfile:
   outfile.write( json.dumps( msm_info , indent=2 ) )
