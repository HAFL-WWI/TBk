# -*- coding: utf-8 -*-
# *************************************************************************** #
# Calculate the change between two TBk versions (development of dg_layer).
# Model exported as python.
# Name : TBk development DG (28m) extent intersect
# Group : TBk
# With QGIS : 33405
#
# Authors: Hannes Horneber (BFH-HAFL)
# *************************************************************************** #
"""
/***************************************************************************
    TBk: Toolkit Bestandeskarte (QGIS Plugin)
    Toolkit for the generating and processing forest stand maps
    Copyright (C) 2025 BFH-HAFL (hannes.horneber@bfh.ch, christian.rosset@bfh.ch)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 ***************************************************************************/
"""
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from PyQt5.QtCore import QCoreApplication
from qgis._core import QgsProcessingParameterNumber, QgsProcessingParameterDefinition
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing
from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_processing_algorithm_toolsF import TBkProcessingAlgorithmToolF


class TBkPostprocessOSChange(TBkProcessingAlgorithmToolF):

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

        parameter = QgsProcessingParameterNumber('thresh_hdom', 'hdom: Stands >= hdom are considered for TBk change',
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=25.0)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber('thresh_hdiff',
                                                 'Negative height difference (in m) after which an area is considered cleared.',
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=7.0)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

    # --- Process Algorithm
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        feedback.pushInfo("\n#------- Calculate OS change -------#")
        # Raster calculator expression represents a binary table with for cases
        # A = old, B = new; A: 0 if not there, 10 if there, B: 0 if not there, 1 if there.
        # 1 = no upper layer (previously no upper layer and still no upper layer)
        # 2 = increase (previously no upper layer, new upper layer)
        # 11 = decrease (previously upper layer, new no upper layer)
        # 12 = maintain (previously upper layer, still upper layer)
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
        outputs['change_DG'] = processing.run('gdal:rastercalculator', alg_params, context=context,
                                              feedback=feedback, is_child_algorithm=True)
        results['change_DG'] = outputs['change_DG']['OUTPUT']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        feedback.pushInfo("\n#-------Rasterize hdom_new -------#")
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

        feedback.pushInfo("\n#-------Rasterize hdom_old -------#")
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

        feedback.pushInfo("\n#------- Calculate cleared areas (change_OS_hdom) -------#")
        # Raster calculator expression represents five cases
        # cases C see change_DG (1, 2, 11, 12)
        # case 100: hdom_old >= hdom_thresh AND hdom_diff >= thresh_diff
        #
        # Expression breakdown: inner part X = (C + (100 * D)) * E)
        # C: change_DG cases (1, 2, 11, 12) for all non cleared stands (higher than thresh_hdom)
        # add 100 (= case 100) multiplied with condition D (hdom_old - hdom_new >= thresh_hdiff)
        # multiplied with condition E (hdom_old >= thresh_hdom), whole term gets to 0 if hdom_old < thresh_hdom
        # min(X,100) : floors values to 100 since results of term X can be > 100
        #
        # examples: with thresh_hdom = 25 and thresh_diff = 7
        # hdom_old = 40, hdom_new = 12, DG_dev = xy -> case 100, cleared since strong reduction of hdom in large stand
        # hdom_old = 25, hdom_new = 19, DG_dev = xy -> case change_DG xy, not sufficient reduction to be considered cleared
        # hdom_old = 24, hdom_new = x, DG_dev = y -> 0, (old) stand not high enough to be considered
        alg_formula = f"minimum((C + (100 * ((A - B) >= {parameters['thresh_hdiff']}))) * (A >= {parameters['thresh_hdom']}), 100)"
        alg_params = {
            'BAND_A': 1,  # hdom_old
            'BAND_B': 1,  # hdom_new
            'BAND_C': 1,  # DG_dev
            'BAND_D': None,
            'BAND_E': None,
            'BAND_F': None,
            'EXTRA': '--extent=intersect',
            'FORMULA': alg_formula,
            'INPUT_A': outputs['RasterizeHdom_old']['OUTPUT'],
            'INPUT_B': outputs['RasterizeHdom_new']['OUTPUT'],
            'INPUT_C': outputs['change_DG']['OUTPUT'],
            'INPUT_D': None,
            'INPUT_E': None,
            'INPUT_F': None,
            'NO_DATA': None,
            'OPTIONS': 'COMPRESS=DEFLATE --co PREDICTOR=2 --co ZLEVEL=9',
            'PROJWIN': None,
            'RTYPE': 0,  # Byte
            'OUTPUT': parameters['change_DG_hdom']
        }
        outputs['change_DG_hdom'] = processing.run('gdal:rastercalculator', alg_params, context=context,
                                                   feedback=feedback, is_child_algorithm=True)
        results['change_DG_hdom'] = outputs['change_DG_hdom']['OUTPUT']

        feedback.pushInfo("\n#------- DONE -------#\n")
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

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPostprocessOSChange()
