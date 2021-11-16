# defining input parameters

# path to the NUTS3 layer
input_layer_path = 'C:/Users/tatu/pyqgis_practical/data/practical_data.gpkg|layername=NUTS3_FIN_pop'
tolerance = 5000
# list of field names to keep
fields_to_keep = ['name', 'pop']

simplified_layer = processing.run("native:simplifygeometries", 
              {'INPUT':input_layer_path,
               'METHOD':0,
               'TOLERANCE':tolerance,
               'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'] # NOTICE THAT THE LAYER IS IMMEDIATELY FETCHED FROM THE DICT

processing.runAndLoadResults("native:retainfields", 
               {'INPUT':simplified_layer,
                'FIELDS':fields_to_keep,
                'OUTPUT':'TEMPORARY_OUTPUT'})