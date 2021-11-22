from qgis import processing
from qgis.processing import alg
from qgis.core import QgsProject, QgsProperty, QgsAggregateCalculator

# INPUTS ARE DEFINED HERE
@alg(name='polygonToAggregatedPoints', label='Polygons to aggregated points',
     group='examplescripts', group_label='Example scripts')
# 'INPUT' is the recommended name for the main input parameter
@alg.input(type=alg.SOURCE, name='INPUT', label='Input vector layer')
# 'OUTPUT' is the recommended name for the main output parameter
@alg.input(type=alg.VECTOR_LAYER_DEST, name='OUTPUT',
           label='Point output')
@alg.input(type=alg.RASTER_LAYER_DEST, name='RASTER_OUTPUT',
           label='Rasterized output')
@alg.input(type=alg.FIELD, name='VALUE_FIELD', parentLayerParameterName="INPUT",
           label='Value field to scale on')
@alg.input(type=alg.NUMBER, name='SCALE_VALUE', label='Scale value',
           default=10)
@alg.output(type=alg.NUMBER, name='NUMBER_OF_FEATURES',
            label='Number of features processed')
@alg.output(type=alg.NUMBER, name='SUM_OF_FIELD',
            label='Sum of value field')   

def bufferrasteralg(self, parameters, context, feedback, inputs):
    """
    Description of the algorithm.
    (If there is no comment here, you will get an error)
    """
    input_layer = self.parameterAsVectorLayer(parameters,
                                                     'INPUT', context)
    value_field = self.parameterAsString(parameters, 'VALUE_FIELD', context)
    numfeatures = input_layer.featureCount()

    scale_value = self.parameterAsDouble(parameters, 'SCALE_VALUE',
                                            context)
                                            
    points_expression = QgsProperty.fromExpression('round(  "{0}" / {1} )'.format(value_field, str(scale_value)))
    if feedback.isCanceled():
        return {}
    
    # CALCULATING SUM FIELD
    agg_exp = QgsAggregateCalculator.Sum
    aggregation = input_layer.aggregate(aggregate=agg_exp, fieldOrExpression=value_field)
    summed = aggregation[0]

    if feedback.isCanceled():
        return {}
    points_generation = processing.run("native:randompointsinpolygons", 
                        {'INPUT':parameters['INPUT'],
                        'POINTS_NUMBER': points_expression,
                        'MIN_DISTANCE':0,
                        'OUTPUT': parameters['OUTPUT']},
                        context=context,
                        feedback=feedback,
                        is_child_algorithm=True)
                        
    
    if feedback.isCanceled():
        return {}
    
    rasterized_points = processing.run('qgis:rasterize',
                                {'LAYERS': points_generation['OUTPUT'],
                                'EXTENT': points_generation['OUTPUT'],
                                'MAP_UNITS_PER_PIXEL': 500,
                                'OUTPUT': parameters['OUTPUT']
                               },
                               is_child_algorithm=True, context=context,
                               feedback=feedback)

 
    if feedback.isCanceled():
        return {}
    
    results = {'OUTPUT': points_generation['OUTPUT'],
                'RASTER_OUTPUT': rasterized_points['OUTPUT'],
                'NUMBER_OF_FEATURES': numfeatures,
                'SUM_OF_FIELD': summed}
    return results