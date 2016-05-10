#! /bin/sh

echo "Downloading latest RU-CHE.osm.pbf"
curl http://be.gis-lab.info/data/osm_dump/dump/latest/RU-CHE.osm.pbf > RU-CHE.osm.pbf

echo "Importing to DB"
imposm3 import -config config.json -read RU-CHE.osm.pbf -write -overwritecache -connection $PGIS_CONNECTION

echo "Done"

rm ./RU-CHE.osm.pbf
