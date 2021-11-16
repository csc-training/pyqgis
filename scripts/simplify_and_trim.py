proj_layers = QgsProject.instance().mapLayers()
original_layer = list(proj_layers.values())[0]

# list where the features of the new layer will be gathered
simplified_feat_list = []

# used in simplification
tolerance_level = 5000

# looping through features of the the layer
for input_order, feat in enumerate(original_layer.getFeatures()):
    # original geometry
    geometry = feat.geometry()
    simplified = geometry.simplify(tolerance_level)
    
    #attrs = feat.attributes()
    trimmed_attributes = [feat['name'], feat['pop']]
    
    # creating a new feature that shares the same input order but new geometry
    feat = QgsFeature(input_order)
    feat.setGeometry(simplified)
    feat.setAttributes(trimmed_attributes)

    # adding all the features to a list
    simplified_feat_list.append(feat)

# making sure the CRS is the same in both layers
layer_crs = original_layer.sourceCrs().authid()
geometry_type = QgsWkbTypes.displayString(original_layer.wkbType())

# creating the new vector layer as a temporary (memory) layer
simplified_layer = QgsVectorLayer('{0}?crs={1}'.format(geometry_type, layer_crs), 
                "Simplified_{0}_{1}".format(original_layer.sourceName(), str(tolerance_level)), "memory")
provider = simplified_layer.dataProvider()

# add fields
provider.addAttributes([QgsField("name", QVariant.String),
                    QgsField("pop",  QVariant.Int)])
simplified_layer.updateFields()
# adding all the features to it
provider.addFeatures(simplified_feat_list)

#check the layer is valid
if simplified_layer.isValid():
    # inserting the new layer to the project
    QgsProject.instance().addMapLayer(simplified_layer)
else:
    print("Faulty layer")