#!/bin/bash

DATA_DIR=${1:-data}

mkdir -p $DATA_DIR

# Download and unzip
wget -N http://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_us_zcta510_500k.zip -P $DATA_DIR -q --show-progress
unzip -q -o $DATA_DIR/cb_2016_us_zcta510_500k.zip -d $DATA_DIR

# Convert to GEOJSON - requires mapshaper (https://github.com/mbloch/mapshaper)
mapshaper -quiet -i $DATA_DIR/cb_2016_us_zcta510_500k.shp -o format=geojson $DATA_DIR/cb_2016_us_zcta510_500k.json

# Clean up
rm $DATA_DIR/cb_2016_us_zcta510_500k.cpg
rm $DATA_DIR/cb_2016_us_zcta510_500k.dbf
rm $DATA_DIR/cb_2016_us_zcta510_500k.prj
rm $DATA_DIR/cb_2016_us_zcta510_500k.shp
rm $DATA_DIR/cb_2016_us_zcta510_500k.shp.ea.iso.xml
rm $DATA_DIR/cb_2016_us_zcta510_500k.shp.iso.xml
rm $DATA_DIR/cb_2016_us_zcta510_500k.shp.xml
rm $DATA_DIR/cb_2016_us_zcta510_500k.shx
rm $DATA_DIR/cb_2016_us_zcta510_500k.zip
