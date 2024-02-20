"""
Model exported as python.
Name : 2023-11-13_tbk_extract_perimeter_minimal
Group : TBk
With QGIS : 32811
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class _tbk_extract_perimeter_minimal(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        #--- load mandatory parameters
        self.addParameter(QgsProcessingParameterVectorLayer('extraction_perimeter', 'Extraction Perimeter', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('raster_extraction_buffer', 'Raster extraction buffer', type=QgsProcessingParameterNumber.Double, defaultValue=10))
        self.addParameter(QgsProcessingParameterFile('tbk_folder', 'TBk Folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=None))

        tbk_root = self.parameterAsString(parameters, 'tbk_folder', context)


        #--- load or generate paths to files
        self.addParameter(QgsProcessingParameterVectorLayer('tbk_bestandeskarte', 'TBk_Bestandeskarte', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('local_densities', 'local_densities', optional=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('vhm_10m', 'vhm_10m', optional=True, defaultValue=None))

        #--- output parameter
        self.addParameter(QgsProcessingParameterFile('output_folder', 'Output Folder', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Vhm_10m_extracted', 'vhm_10m_extracted', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Tbk_bestandeskarte_extracted', 'TBk_Bestandeskarte_extracted', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Local_densities_extracted', 'local_densities_extracted', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, model_feedback)
        results = {}
        outputs = {}

        # Create spatial index
        alg_params = {
            'INPUT': parameters['tbk_bestandeskarte']
        }
        outputs['CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Create spatial index
        alg_params = {
            'INPUT': parameters['local_densities']
        }
        outputs['CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['CreateSpatialIndex']['OUTPUT'],
            'INTERSECT': parameters['extraction_perimeter'],
            'PREDICATE': [0],  # intersect
            'OUTPUT': parameters['Tbk_bestandeskarte_extracted']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Tbk_bestandeskarte_extracted'] = outputs['ExtractByLocation']['OUTPUT']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Buffer+Dissolve stands for raster
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': parameters['raster_extraction_buffer'],
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByLocation']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferdissolveStandsForRaster'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Buffer+Dissolve stands for vector
        alg_params = {
            'DISSOLVE': True,
            'DISTANCE': 0.0001,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['ExtractByLocation']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['BufferdissolveStandsForVector'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Clip raster by mask layer
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': parameters['vhm_10m'],
            'KEEP_RESOLUTION': False,
            'MASK': outputs['BufferdissolveStandsForRaster']['OUTPUT'],
            'MULTITHREADING': False,
            'NODATA': None,
            'OPTIONS': '',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'TARGET_EXTENT': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': parameters['Vhm_10m_extracted']
        }
        outputs['ClipRasterByMaskLayer'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Vhm_10m_extracted'] = outputs['ClipRasterByMaskLayer']['OUTPUT']

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['CreateSpatialIndex']['OUTPUT'],
            'INTERSECT': outputs['BufferdissolveStandsForVector']['OUTPUT'],
            'PREDICATE': [6],  # are within
            'OUTPUT': parameters['Local_densities_extracted']
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Local_densities_extracted'] = outputs['ExtractByLocation']['OUTPUT']
        return results

    def name(self):
        return '2023-11-13_tbk_extract_perimeter_minimal'

    def displayName(self):
        return '2023-11-13_tbk_extract_perimeter_minimal'

    def group(self):
        return 'TBk'

    def groupId(self):
        return 'TBk'

    def createInstance(self):
        return _tbk_extract_perimeter_minimal()
