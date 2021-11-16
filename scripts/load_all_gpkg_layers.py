# EXAMPLE PATH: define the actual path on your system
gpkg_path = "C:/Users/joker/OneDrive/Mantsa 6. vuosi/Work/PYQGIS-materials/data/practical_data.gpkg" # windows
gpkg_layer = QgsVectorLayer(gpkg_path, "whole_gpkg", "ogr")
# returns a list of strings describing the sublayers
# !!::!! separetes the values
# EXAMPLE: 1!!::!!Paavo!!::!!3027!!::!!MultiPolygon!!::!!geom!!::!!
sub_strings = gpkg_layer.dataProvider().subLayers()

for sub_string in sub_strings:
    layer_name = sub_string.split(gpkg_layer.dataProvider().sublayerSeparator())[1]
    uri = "{0}|layername={1}".format(gpkg_path, layer_name)
    # Create layer
    sub_vlayer = QgsVectorLayer(uri, layer_name, 'ogr')
    # Add layer to map
    if sub_vlayer.isValid():
        QgsProject.instance().addMapLayer(sub_vlayer)
    else:
        print("Can't add layer", layer_name)