"""
Model exported as python.
Name : model
Group : 
With QGIS : 31611
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class KeepFields(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('Inputlayer', 'Input layer', defaultValue=None))
        self.addParameter(QgsProcessingParameterField('Fieldstokeep', 'Fields to keep', type=QgsProcessingParameterField.Any, parentLayerParameterName='Inputlayer', allowMultiple=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('KeptFields', 'Kept fields', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}

        input_layer = self.parameterAsVectorLayer(parameters, "Inputlayer", context)
        fields_to_keep = self.parameterAsFields(parameters, 'Fieldstokeep', context)
        
        all_fields = input_layer.fields().names()
        
        drop_fields = [field for field in all_fields if field not in fields_to_keep]

        # Drop field(s)
        alg_params = {
            'COLUMN': drop_fields,
            'INPUT': parameters['Inputlayer'],
            'OUTPUT': parameters['KeptFields']
        }
        outputs['DropFields'] = processing.run('qgis:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['KeptFields'] = outputs['DropFields']['OUTPUT']
        return results

    def name(self):
        return 'keepFields'

    def displayName(self):
        return 'Keep fields'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return KeepFields()
