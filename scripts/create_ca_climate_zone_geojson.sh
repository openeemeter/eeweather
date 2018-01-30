#!/bin/bash

DATA_DIR=${1:-data}

mkdir -p $DATA_DIR

# download and install CA climate zone raw data
wget -N http://www.energy.ca.gov/maps/renewable/CA_Building_Standards_Climate_Zones.zip -P $DATA_DIR -q --show-progress
unzip -q -o $DATA_DIR/CA_Building_Standards_Climate_Zones.zip -d $DATA_DIR

# reproject to ESRI Shapefile
ogr2ogr -q -f "ESRI Shapefile" -t_srs EPSG:4326 $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp $DATA_DIR/CA_Building_Standards_Climate_Zones.shp

# convert to geojson
mapshaper -quiet -i $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp -o format=geojson $DATA_DIR/CA_Building_Standards_Climate_Zones.json

# clean up
rm $DATA_DIR/CA\ Building\ Standards\ Climate\ Zones.lyr
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.cpg
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.dbf
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.prj
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.sbn
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.sbx
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.shp
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.shp.xml
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.shx
rm $DATA_DIR/CA_Building_Standards_Climate_Zones.zip
rm $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.dbf
rm $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.prj
rm $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp
rm $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shx
