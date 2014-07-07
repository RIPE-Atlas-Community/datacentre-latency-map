var map;
var center = new L.LatLng(52,4);

var marker_defaults = {
    radius: 8,
    fillColor: "#e07800",
    color: "#eee",
    weight: 1,
    opacity: 1,
    fillOpacity: 0.5
   };

var color_scale = d3.scale.linear()
      .domain([-100, 0, 100])
      .range(["red", "white", "green"]);

var opacity_scale = d3.scale.linear()
      .domain([-100, 0, 100])
      .range([1,0,1]);

function onEachFeature( feature, layer ) {
         var txt = '<table>';
         for (fe in feature.properties) {
            if (fe == 'rtts') { continue }
            if (fe == 'asn_v4' || fe == 'asn_v6') {
               asn = feature.properties[fe];
               txt += '<tr><td>' + fe + 
                  '</td><td><a href="https://stat.ripe.net/' + asn + '">'+ asn +'</a></td></tr>';
            } else {
               txt += '<tr><td>' + fe + '</td><td>' + feature.properties[fe] + '</td></tr>';
            }
         }
         for (msm_id in feature.properties.rtts) {
            // @@ msm_id => hostname / symbolic name
            txt += '<tr><td>' + msm_id + '</td><td>' + feature.properties.rtts[msm_id] + 'ms</td></tr>';
         }
         txt += '</table>';
         layer.bindPopup( txt );
};

function initmap() {
	// set up the map
	map = new L.Map('map');
	
   function project(x) {
      var point = map.latLngToLayerPoint(new L.LatLng(x[1], x[0]));
      return [point.x, point.y];
   };
	map.setView(center,2);
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {attribution: osmAttrib});		
	map.addLayer(osm);

   /*
   var blackmarble = L.tileLayer('http://{s}.tiles.earthatlas.info/black-marble/{z}/{x}/{y}.png', {
      attribution: 'Map imagery by <a href="http://www.nasa.gov/mission_pages/NPP/news/earth-at-night.html">NASA Earth Observatory/NOAA NGDC</a>',
      maxZoom: 6
   });
	map.addLayer(blackmarble);
   */

   var svg = d3.select(map.getPanes().overlayPane).append("svg"),
   g = svg.append("g").attr("class", "leaflet-zoom-hide");

      
   L.geoJson(geodata,{ 
      pointToLayer: function( feature, latlng) {
         var marker_opts = marker_defaults;
         var show_mark = 0;
         /* hack */
         if ( typeof feature.properties.rtts  == "object" ) {
            rtts = feature.properties.rtts;
            eval( sfo_rtt = rtts['1040115'] );
            eval( iad_rtt = rtts['1040118'] );
            eval( ams_rtt = rtts['1040120'] );
            mcolor='black';
            var mborder=0;
            if ( ams_rtt < iad_rtt && ams_rtt < sfo_rtt ) { mcolor = 'orange'; if (ams_rtt > 150) { mborder=1 } }
            if ( iad_rtt < ams_rtt && iad_rtt < sfo_rtt ) { mcolor = 'green'; if (iad_rtt > 150) { mborder=1 } }
            if ( sfo_rtt < ams_rtt && sfo_rtt < iad_rtt ) { mcolor = 'blue'; if ( sfo_rtt > 150) { mborder=1 } }
            marker_opts['fillColor'] = mcolor;
            if (mborder != 0 ) {
               marker_opts['color'] = 'red';
               marker_opts['weight'] = 3;
            } else {
               marker_opts['color'] = 'white';
               marker_opts['weight'] = 1;
            }
         }
         return L.circleMarker(latlng, marker_opts);
      },
      onEachFeature: onEachFeature
   } ).addTo(map)
}
