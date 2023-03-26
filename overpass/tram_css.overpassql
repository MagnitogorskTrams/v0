[out:json];

(
  node["public_transport"="stop_position"]["tram"="yes"]({{bbox}});
  node["railway"="tram_stop"]({{bbox}});
  way["railway"="tram"]({{bbox}});
  //relation["route"="tram"]({{bbox}});
);
out body;
>;
out qt;
{{style: /* http://wiki.openstreetmap.org/wiki/Overpass_turbo/MapCSS */

node
{ color:silver; fill-color:silver; opacity:0.1; }

way[railway=tram]
{ color:#FF6200; }

way[railway=tram][tracks=2]
{ color:red; }

way[railway=tram][lanes=2]
{ color:red; }

way[railway=tram][service=yard]
{ color:navy; opacity:0.3; }

way[railway=tram][service=spur]
{ color:navy; opacity:0.3; }

node[railway=tram_stop]
{ color:red; fill-color:yellow; opacity:1; }

node[public_transport=stop_position]
{ color:red; fill-color:white; opacity:0.5; }

node[public_transport=stop_position][tram=yes]
{ color:green; fill-color:lime; opacity:1; }

node[fixme]
{ color:red; fill-color:black; opacity:1; }

}}
