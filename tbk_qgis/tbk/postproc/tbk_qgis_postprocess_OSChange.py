"""
Calculate the change between two TBk versions (development of dg_layer).

Model exported as python.
Name : TBk development DG (28m) extent intersect
Group : TBk
With QGIS : 33405
"""
from qgis.PyQt.QtCore import QCoreApplication
from qgis._core import QgsProcessingParameterNumber, QgsProcessingParameterDefinition
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

class TBkPostprocessOSChange(QgsProcessingAlgorithm):

    # --- Init Algorithm: Add Parameters
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer('TBknewBestandesgrenzen', 'TBk new: Bestandesgrenzen', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterLayer('TBknewDGBestand', 'TBk new: DG Bestand', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterVectorLayer('TBkoldBestandesgrenzen', 'TBk old: Bestandesgrenzen', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterLayer('TBkoldDGBestand', 'TBk old: DG Bestand', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterDestination('change_DG',
                                                    'Output change_DG: \nRaster indicating whether upper layer has changed',
                                                    createByDefault=True, defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterDestination('change_DG_hdom',
                                                    'Output change_DG_hdom: \nRaster indicating whether upper layer or hdom has changed (upper layer cleared) in stands >= hdom',
                                                    createByDefault=True, defaultValue=None))

        parameter = QgsProcessingParameterNumber('hdom', 'hdom: Stands >= hdom are considered for TBk change',
                                                 type=QgsProcessingParameterNumber.Type.Integer, defaultValue=28)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber('thresh_hdiff',
                                                 'Negative height difference (in m) after which an area is considered cleared.',
                                                 type=QgsProcessingParameterNumber.Type.Integer, defaultValue=5)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.Flag.FlagAdvanced)
        self.addParameter(parameter)

    # --- Process Algorithm
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Raster calculator
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': None,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '--extent=intersect',
            'FORMULA': '(A*10 + B) + 1',
            'INPUT_A': parameters['TBkoldDGBestand'],
            'INPUT_B': parameters['TBknewDGBestand'],
            'INPUT_C': None,
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': 'COMPRESS=DEFLATE --co PREDICTOR=2 --co ZLEVEL=9',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': parameters['change_DG']
        }
        outputs['RasterCalculator'] = processing.run('gdal:rastercalculator', alg_params, context=context,
                                                     feedback=feedback, is_child_algorithm=True)
        results['change_DG'] = outputs['RasterCalculator']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Rasterize hdom_new
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 5,  # Float32
            'EXTENT': parameters['TBknewDGBestand'],
            'EXTRA': '',
            'FIELD': 'hdom',
            'HEIGHT': 1.5,
            'INIT': None,
            'INPUT': parameters['TBknewBestandesgrenzen'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,  # Georeferenced units
            'WIDTH': 1.5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizeHdom_new'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback,
                                                      is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Rasterize hdom_old
        alg_params = {
            'BURN': 0,
            'DATA_TYPE': 0,  # Byte
            'EXTENT': parameters['TBknewDGBestand'],
            'EXTRA': '',
            'FIELD': 'hdom',
            'HEIGHT': 1.5,
            'INIT': None,
            'INPUT': parameters['TBkoldBestandesgrenzen'],
            'INVERT': False,
            'NODATA': 0,
            'OPTIONS': '',
            'UNITS': 1,  # Georeferenced units
            'WIDTH': 1.5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RasterizeHdom_old'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback,
                                                      is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Raster calculator
        alg_formula = f'minimum((C + (100 * logical_and(B < {parameters["hdom"] - parameters["thresh_hdiff"]}, A >= {parameters["hdom"]}))) * (A >= {parameters["hdom"]}), 100)'
        alg_params = {
            'BAND_A': 1,
            'BAND_B': 1,
            'BAND_C': 1,
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '--extent=intersect',
            'FORMULA': alg_formula,
            'INPUT_A': outputs['RasterizeHdom_old']['OUTPUT'],
            'INPUT_B': outputs['RasterizeHdom_new']['OUTPUT'],
            'INPUT_C': outputs['RasterCalculator']['OUTPUT'],
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': 'COMPRESS=DEFLATE --co PREDICTOR=2 --co ZLEVEL=9',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': parameters['change_DG_hdom']
        }
        outputs['RasterCalculator'] = processing.run('gdal:rastercalculator', alg_params, context=context,
                                                     feedback=feedback, is_child_algorithm=True)
        results['change_DG_hdom'] = outputs['RasterCalculator']['OUTPUT']
        return results

    # --- Set Name/ID/Group
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess OS Change'

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
        return TBkPostprocessOSChange()
