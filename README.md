Datacentre-latency-map
======================

This is a first prototype of a datacentre latency map using RIPE Atlas.

It consists of:
* A script to start measurements: **start_measurements.py**
* A script to pull measurement data from RIPE Atlas and visualise it: **process.py**

Workflow
========

To start using this, one would need:
* A RIPE Atlas account with enough credits to run measurements, and an api-key for that, stored in **~/.atlas/auth**
* A configuration file for the measurements **conf.yaml** , an example configuration is available in **conf.yaml.example**.
* After running **start_measurements.py**, a summary of measurement metadata is written to **msm.json** in the local directory.
* Once measurements are actually done (allow some 10-15 minutes for that), one can process the measurement data with **process.pl**. **process.pl** needs a local **all-probes.geoloc.txt** file (example format in **all-probes.geoloc.txt.example**), with RIPE Atlas probe IDs, with lat,lon,v4ASN,v6ASN and country information. **process.pl** will create a ./map/geodata.js javascript file which has the relevant measurement data in a geojson-compatible format.
* Point a browser at ./map/map.html to see the result.


