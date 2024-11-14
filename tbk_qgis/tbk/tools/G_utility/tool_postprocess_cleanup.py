"""
Removes small areas (< 100 m2) and areas without geometry.
Also fixes geometries and removes duplicates in the stand ID field.

Model exported as python.
Name : TBk Cleanup
Group : TBk
With QGIS : 33404
"""
from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterFeatureSink
import processing
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_processing_algorithm_toolsG import TBkProcessingAlgorithmToolG

"""
/***************************************************************************
 TBk - Toolkit for the generation of forest stand maps
 ***************************************************************************/
"""

__author__ = 'Berner Fachhochschule BFH-HAFL'
__date__ = '2024-02-20'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'


class TBkPostprocessCleanup(TBkProcessingAlgorithmToolG):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer('input_stand_map', 'TBk Bestandeskarte', defaultValue=None))

        self.addParameter(QgsProcessingParameterFeatureSink('output_stand_map_clean', 'TBk Bestandeskarte clean',
                                                            type=QgsProcessing.TypeVectorAnyGeometry,
                                                            createByDefault=True, supportsAppend=True,
                                                            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Extract area_m2 > 100
        alg_params = {
            'EXPRESSION': '"area_m2" >= 100',
            'INPUT': parameters['input_stand_map'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractArea_m2100'] = processing.run('native:extractbyexpression', alg_params, context=context,
                                                      feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Extract "area_m2" IS NOT NULL
        alg_params = {
            'EXPRESSION': '"area_m2" IS NOT NULL',
            'INPUT': outputs['ExtractArea_m2100']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractArea_m2IsNotNull'] = processing.run('native:extractbyexpression', alg_params, context=context,
                                                            feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': outputs['ExtractArea_m2IsNotNull']['OUTPUT'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context,
                                                  feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Add autoincremental field
        alg_params = {
            'FIELD_NAME': 'ID_1',
            'GROUP_FIELDS': [''],
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'MODULUS': 0,
            'SORT_ASCENDING': True,
            'SORT_EXPRESSION': '"ID"',
            'SORT_NULLS_FIRST': False,
            'START': 1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AddAutoincrementalField'] = processing.run('native:addautoincrementalfield', alg_params,
                                                            context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Drop field ID
        alg_params = {
            'COLUMN': ['ID'],
            'INPUT': outputs['AddAutoincrementalField']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFieldId'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback,
                                                is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Rename field ID_1 -> ID
        alg_params = {
            'FIELD': 'ID_1',
            'INPUT': outputs['DropFieldId']['OUTPUT'],
            'NEW_NAME': 'ID',
            'OUTPUT': parameters['output_stand_map_clean']
        }
        results['OUTPUT'] = processing.run('native:renametablefield', alg_params, context=context,
                                                      feedback=feedback, is_child_algorithm=True)

        # outputs['RenameFieldId_1Id'] = results['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess Cleanup'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPostprocessCleanup()
