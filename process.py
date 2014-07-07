#!/usr/bin/env python
import sys
import json
import numpy as np
import time
import urllib2
import yaml

## todo: produce single javascript file to include

## fetch from https://atlas.ripe.net/api/v1/measurement/${i}/result/?format=txt

## default start and end (take 3 days of data?)
## @@ make this configurable (cmd-line / cgi? )
END_T = int( time.time() )
START_T = int( END_T - 1*86400 )

OUTPUT_F = "./map/geodata.js";

## read probe info from local file
## load probe locs
PRB_INFO = {}
with open('./all-probes.geoloc.txt') as f:
   f.readline()
   for line in f:
      try:
         line = line.rstrip('\n')
         (prb_id,lat,lon,asn_v4,asn_v6,cc) = line.split('\t')
         prb_id = int( prb_id )
         lat = float(lat)
         lon = float(lon)
         PRB_INFO[prb_id] = {
            'lat': lat,
            'lon': lon,
            'asn_v4': asn_v4,
            'asn_v6': asn_v6,
            'cc': cc
         }
      except: pass

print "%s" % ( PRB_INFO )

## read measurement input from msm.json
MSM_CONF=[]
with open("./msm.json") as fh:
   MSM_CONF = json.load( fh )

MSM_SPEC={}
with open("conf.yaml") as fh:
   MSM_SPEC = yaml.safe_load( fh )

### functions
def process_json_fragment( line, prb_rtts ):
   try:
      data = json.loads( line )
      prb_id = data['prb_id']
      res = data['result']
      ts = data['timestamp']
      for h in res:
         if 'rtt' in h:
            if prb_id in prb_rtts:
               prb_rtts[ prb_id ].append( h['rtt'] )
            else:
               prb_rtts[ prb_id ] = [ h['rtt'] ]
   except:
      pass

def trunc(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    return float( ('%.*f' % (n + 1, f))[:-1] )

### MAIN

for msm in MSM_CONF:
   msm_id = msm['msm_id']
   msm_url = "https://atlas.ripe.net/api/v1/measurement/%s/result/?format=txt&start=%s&stop=%s" % ( msm_id, START_T, END_T )
   print "fetching from msm_url %s" % ( msm_url )
   url_fh = urllib2.urlopen( msm_url )
   prb_rtts = {}
   for line in url_fh:
      try:
         process_json_fragment( line, prb_rtts )
      except:
         pass ### @@ todo be better
   url_fh.close()
   print "calculationg 5th percentile for msm_id:%s" % ( msm_id )
   prb_pct5 = {}
   for prb_id in prb_rtts:
      if prb_id in PRB_INFO:
         sv = np.sort( prb_rtts[ prb_id ] )
         p5_rtt = trunc( np.percentile( sv, 5), 1 )
         if 'rtts' in PRB_INFO[prb_id]:
            PRB_INFO[prb_id]['rtts'][msm_id] = p5_rtt
         else:
            PRB_INFO[prb_id]['rtts'] = { msm_id: p5_rtt }
      else:
         print "No info for prb_id %s " % ( prb_id )

geojson = {
   "type": "FeatureCollection", 
   "features": []
}

for prb_id in PRB_INFO:
   prb_info = PRB_INFO[prb_id]
   lat=None
   lon=None
   rtts={}
   country=None
   asn_v4=None
   asn_v6=None
   try:
      lat = prb_info['lat']
      lon = prb_info['lon']
   except:  # severe enough to not output anything
      print "eeps lat/lon"
      continue
   try:
      rtts = prb_info['rtts']
   except: 
      print "eeps rtts"
      continue
   try:
      country = prb_info['cc']
   except: print "eeps country"
   try:
      asn_v4 = prb_info['asn_v4']
   except: print "eeps asn_v4"
   try:
      asn_v6 = prb_info['asn_v6']
   except: print "eeps asn_v6"
   try:
      geojson['features'].append({
            "geometry": {
                "type": "Point", 
                "coordinates": [
                    lon,lat
                ]
            }, 
            "type": "Feature", 
            "properties": {
                'rtts': rtts,
                'country': country,
                'asn_v4':  asn_v4,
                'asn_v6':  asn_v6,
                'prb_id': prb_id
            }
      });
   except:
      e = sys.exc_info()
      print "eeps for %s (%s)" % ( PRB_INFO[prb_id], e )

with open(OUTPUT_F,'w') as outp_f:
   outp_f.write( "var geodata=%s;" % ( json.dumps( geojson ) ) )


'''
   (ts,rtt) = line.split();
   ts_bin = int( int(ts) / binsize ) * binsize
   rtt = float( rtt )
   if ts_bin in bins:
      bins[ts_bin].append( rtt ) 
   else:
      bins[ts_bin] = [ rtt ]

print "#ts_bin\tavg\tstddev\tmed\tq1\tq3\tp5\tp95"
for ts_bin,values in sorted( bins.items() ):
   sv = np.sort( values )
   avg= np.average( sv )
   stddev = np.std( sv )
   (p5,q1,med,q3,p95) = np.percentile( sv, [5,25, 50 , 75,95])
   print "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % ( ts_bin, avg, stddev, med, q1, q3 , p5, p95)
'''
