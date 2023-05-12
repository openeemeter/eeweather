#!/bin/bash

DATA_DIR=${1:-data}

mkdir -p $DATA_DIR

# download and install CA climate zone raw data
wget -N https://community.esri.com/ccqpr47374/attachments/ccqpr47374/coordinate-reference-systemsforum-board/1814/1/CA_Building_Standards_Climate_Zones.zip -P $DATA_DIR -q --show-progress
unzip -q -o $DATA_DIR/CA_Building_Standards_Climate_Zones.zip -d $DATA_DIR

# reproject to ESRI Shapefile
ogr2ogr -q -f "ESRI Shapefile" -t_srs EPSG:4326 $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp $DATA_DIR/CA_Building_Standards_Climate_Zones.shp

# convert to geojson
mapshaper -quiet -i $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp -o format=geojson $DATA_DIR/CA_Building_Standards_Climate_Zones.json

# clean up
rm -f $DATA_DIR/CA\ Building\ Standards\ Climate\ Zones.lyr
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.cpg
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.dbf
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.prj
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.sbn
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.sbx
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.shp
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.shp.xml
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.shx
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones.zip
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.dbf
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.prj
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shp
rm -f $DATA_DIR/CA_Building_Standards_Climate_Zones_reprojected.shx
