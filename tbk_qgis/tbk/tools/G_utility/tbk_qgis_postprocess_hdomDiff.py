"""
Create raster hdom diff (difference VHM - hdom) to indicate how strong areas of a stand deviate from hdom.
Also creates a point layer from VHM_10 m (for visualization purposes)

Model exported as python.

Name : TBk: hdom diff
Group : TBk
With QGIS : 33404
"""
from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing

"""
/***************************************************************************
 TBk - Toolkit for the generation of forest stand maps
 ***************************************************************************/
"""

class TBkPostprocessHdomDiff(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('tbk_bestandesgrenzen', 'TBk: Bestandesgrenzen', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('vhm_10m', 'VHM_10m ', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Diff_hdom_vhm', 'diff_hdom_vhm', createByDefault=True, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('Vhm_10m_points', 'vhm_10m_points', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # Rasterize hdom_new
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': parameters['vhm_10m'],
            'EXTRA': '',
            'FIELD': 'hdom',
            'HEIGHT': 10,
            'INIT': None,
            'INPUT': parameters['tbk_bestandesgrenzen'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,  # Georeferenced units
            'USE_Z': False,
            'WIDTH': 10,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizeHdom_new'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Raster calculator
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '--extent=intersect',
            'FORMULA': 'B - A',
            'INPUT_A': parameters['vhm_10m'],
            'INPUT_B': outputs['RasterizeHdom_new']['OUTPUT'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': '',
            'PROJWIN': None,
            'RTYPE': 1,  # Int16
            'OUTPUT': parameters['Diff_hdom_vhm']
        }
        outputs['RasterCalculator'] = processing.run('gdal:rastercalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Diff_hdom_vhm'] = outputs['RasterCalculator']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Raster pixels to points
        alg_params = {
            'FIELD_NAME': 'VHM_10m',
            'INPUT_RASTER': parameters['vhm_10m'],
            'RASTER_BAND': 1,
            'OUTPUT': parameters['Vhm_10m_points']
        }
        outputs['RasterPixelsToPoints'] = processing.run('native:pixelstopoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Vhm_10m_points'] = outputs['RasterPixelsToPoints']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess Hdom diff'

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
        return '2 TBk Postprocessing'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'postproc'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPostprocessHdomDiff()
