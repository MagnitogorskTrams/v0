[out:json][timeout:25];
{{geocodeArea:Magnitogorsk}}->.searchArea;
way["railway"="tram"]["service"!="yard"]["service"!="spur"]["service"!="siding"]["service"!="crossover"](area.searchArea);
out body;
>;
out skel;
