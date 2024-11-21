"""


Model exported as python.
Name : Append Attribute (singlepart + index)
Group :
With QGIS : 33404
"""
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class OptimizedSpatialJoin(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterVectorLayer('layer_to_join_attribute_on', 'Layer to join attribute on',
                                                            defaultValue=None))
        self.addParameter(
            QgsProcessingParameterVectorLayer('attribute_layer', 'attribute Layer', types=[QgsProcessing.SourceType.TypeVectorPolygon],
                                              defaultValue=None))
        self.addParameter(
            QgsProcessingParameterFeatureSink('output_with_attribute', 'Output with attribute', optional=True,
                                              type=QgsProcessing.SourceType.TypeVectorAnyGeometry, createByDefault=True,
                                              defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(
            QgsProcessingParameterField('fields_to_join', 'Fields to Join', type=QgsProcessingParameterField.DataType.Any,
                                        parentLayerParameterName='attribute_layer', allowMultiple=True,
                                        defaultValue='Code'))
        self.addParameter(
            QgsProcessingParameterString('joined_attributes_prefix', 'Joined Attributes Prefix', multiLine=False,
                                         defaultValue='VegZone_'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(5, model_feedback)
        results = {}
        outputs = {}

        layer_to_join_on = self.parameterAsVectorLayer(parameters, 'layer_to_join_attribute_on', context)
        if (layer_to_join_on.dataProvider().hasSpatialIndex() == 2):
            print(f'The {layer_to_join_on.name()} has spatial index')
            input_layer1_join_attributes_by_location = str(layer_to_join_on.source())
        else:
            # Indexed Input
            print(f'Creating spatial index for {layer_to_join_on}')

            alg_params = {
                'INPUT': parameters['layer_to_join_attribute_on']
            }
            outputs['IndexedInput'] = processing.run('native:createspatialindex', alg_params, context=context,
                                                     feedback=feedback, is_child_algorithm=True)
            input_layer1_join_attributes_by_location = outputs['IndexedInput']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Multipart to singleparts
        alg_params = {
            'INPUT': parameters['attribute_layer'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['MultipartToSingleparts'] = processing.run('native:multiparttosingleparts', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Fix geometries that were created by single part algorithm
        alg_params = {
            'INPUT': outputs['MultipartToSingleparts']['OUTPUT'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Indexed Singlepart AttributeLayer
        alg_params = {
            'INPUT': outputs['FixGeometries']['OUTPUT']
        }
        outputs['IndexedSinglepartAttributeLayer'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}



        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': input_layer1_join_attributes_by_location,
            'JOIN': outputs['IndexedSinglepartAttributeLayer']['OUTPUT'],
            'JOIN_FIELDS': parameters['fields_to_join'],
            'METHOD': 2,  # Take attributes of the feature with largest overlap only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': parameters['joined_attributes_prefix'],
            'OUTPUT': parameters['output_with_attribute']
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params,
                                                             context=context, feedback=feedback,
                                                             is_child_algorithm=True)
        results['OutputWithAttribute'] = outputs['JoinAttributesByLocation']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Optimized Spatial Join'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        # return self.tr(self.groupId())
        return 'X Utility'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'utility'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Spatial Join that optimizes the performance before joining. Converts the secondary join layer to singlepart and adds spatial indices for both layers, ensuring a better performance on the join.</p></body></html></p>
<h2>Input parameters</h2>
<h3>Layer to join attribute on</h3>
<p>Main join layer</p>
<h3>Attribute Layer</h3>
<p>Secondary join layer (with attributes to append to main layer)</p>
<h2>Outputs</h2>
<h3>Output with Attribute</h3>
<p>Main layer with joined attributes from secondary layer.</p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm author: Hannes Horneber @ BFH-HAFL (2024)</p></body></html>"""

    def createInstance(self):
        return OptimizedSpatialJoin()
