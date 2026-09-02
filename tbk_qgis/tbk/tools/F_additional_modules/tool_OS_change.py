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

        parameter = QgsProcessingParameterNumber('thresh_hdom_split',
                                                 'hdom: threshold (in m) separating tall (Baumholz) from low (Jungwuchs) '
                                                 'stands for clearing classification',
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=14.0)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber('frac_full',
                                                 'Stands where new hdom drops below this fraction of old hdom are '
                                                 'considered fully cleared.',
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=1.0 / 3)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

        parameter = QgsProcessingParameterNumber('frac_partial',
                                                 'Stands (with old hdom above thresh_hdom_split) where new hdom drops '
                                                 'below this fraction (but stays above frac_full) of old hdom are '
                                                 'considered partially cleared.',
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=2.0 / 3)
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(parameter)

        self._add_gdal_create_options_parameter()

    # --- Process Algorithm
    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}
        gdal_create_options = self.parameterAsString(parameters, self.GDAL_CREATE_OPTIONS, context)

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
            'OPTIONS': gdal_create_options,
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
        # Raster calculator distinguishes three clearing cases based on old hdom (A) and new hdom (B),
        # relative to the old hdom, falling back to the change_DG cases (C: 1, 2, 11, 12) otherwise.
        # 99  = partially cleared: A > thresh_hdom_split AND new hdom retains between frac_full and frac_partial of A
        # 100 = fully cleared (Baumholz): A > thresh_hdom_split AND new hdom drops below frac_full of A
        # 101 = fully cleared (Jungwuchs): A < thresh_hdom_split AND new hdom drops below frac_full of A
        #
        # examples: with thresh_hdom_split = 14, frac_full = 1/3, frac_partial = 2/3
        # hdom_old = 40, hdom_new = 10 -> case 100, fully cleared tall stand
        # hdom_old = 40, hdom_new = 20 -> case 99, partially cleared tall stand (dropped to half)
        # hdom_old = 10, hdom_new = 2  -> case 101, fully cleared low stand
        # hdom_old = 40, hdom_new = 35 -> case change_DG, not sufficient reduction to be considered cleared
        thresh_hdom_split = parameters['thresh_hdom_split']
        frac_full = parameters['frac_full']
        frac_partial = parameters['frac_partial']
        cond_partial = f"(A>{thresh_hdom_split})*(B>=({frac_full})*A)*(B<({frac_partial})*A)"
        cond_full_tall = f"(A>{thresh_hdom_split})*(B<({frac_full})*A)"
        cond_full_low = f"(A<{thresh_hdom_split})*(B<({frac_full})*A)"
        alg_formula = (f"({cond_partial}*99 + {cond_full_tall}*100 + {cond_full_low}*101"
                       f" + (1-({cond_partial}+{cond_full_tall}+{cond_full_low}))*C)")
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
            'OPTIONS': gdal_create_options,
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
