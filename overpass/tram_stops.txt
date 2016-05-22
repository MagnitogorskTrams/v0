[out:json][timeout:25];
{{geocodeArea:Magnitogorsk}}->.searchArea;
(
  (
    node["railway"="tram_stop"](area.searchArea);
    node["tram"="yes"](area.searchArea);
    node["public_transport"="stop_position"](area.searchArea);
  );
  -
  (
    node["bus"="yes"](area.searchArea);
    node["train"="yes"](area.searchArea);
  );
);
out body;
