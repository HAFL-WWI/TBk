# -*- coding: utf-8 -*-
# *************************************************************************** #
# Create raster hdom diff (difference VHM - hdom) to indicate how strong areas of a stand deviate from hdom.
# Also creates a point layer from VHM_10 m (for visualization purposes)
#
# Model exported as python.
# Name : TBk: hdom diff
# Group : TBk
# With QGIS : 33404
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

import os

from PyQt5.QtCore import QCoreApplication
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterFeatureSink
import processing
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_processing_algorithm_toolsG import TBkProcessingAlgorithmToolG

class TBkPostprocessHdomDiff(TBkProcessingAlgorithmToolG):

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer('tbk_bestandesgrenzen', 'TBk: Bestandesgrenzen', defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterLayer('vhm_10m', 'VHM_10m ', defaultValue=None))
        self.addParameter(
            QgsProcessingParameterRasterDestination('diff_hdom_vhm', 'Output diff_hdom_vhm.tif', createByDefault=True,
                                                    defaultValue=''))
        self.addParameter(
            QgsProcessingParameterFeatureSink('vhm_10m_points', 'Output VHM_10m_points.gpkg', type=QgsProcessing.TypeVectorPoint,
                                              createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}
        # to get a usable source path, the param needs to be extracted
        params = self._extract_context_params(parameters, context)

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
        outputs['RasterizeHdom_new'] = processing.run('gdal:rasterize', alg_params, context=context, feedback=feedback,
                                                      is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}


        if not os.path.exists(params.diff_hdom_vhm):
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
                'OUTPUT': params.diff_hdom_vhm
            }
            outputs['RasterCalculator'] = processing.run('gdal:rastercalculator', alg_params, context=context,
                                                         feedback=feedback, is_child_algorithm=True)
            results['diff_hdom_vhm'] = outputs['RasterCalculator']['OUTPUT']
        else:
            feedback.pushWarning(f"Output already exists: {params.diff_hdom_vhm}. Skipping.")
            results['diff_hdom_vhm'] = params.diff_hdom_vhm

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Raster pixels to points
        # Note: vhm_10m_points is a QgsProcessingParameterFeatureSink, which asMap()/
        # _extract_context_params() does not resolve to a concrete destination path (unlike
        # the diff_hdom_vhm raster destination above) - it must be read via
        # parameterAsOutputLayer(), matching the working pattern in tool_merge_stand_maps.py.
        #
        # Check the *expected* destination for pre-existence before calling
        # parameterAsOutputLayer() at all - not after. vhm_10m_points.gpkg is a shared,
        # non-per-run cache (see tool_mainTBk.py/_regionwise.py) that's typically already there
        # by the time this runs, and parameterAsOutputLayer()'s sink resolution has been
        # observed to itself fail/return a bogus scratch path in that case (found 2026-09-04:
        # "Could not create layer <name>_<uuid>_points.gpkg ... sqlite3_open failed" - reproduced
        # both single-run and with a second TBk instance running concurrently, and even with the
        # exact same bogus filename/UUID recurring across separate runs, so this isn't lock
        # contention and isn't a freshly-random scratch name either - something in sink
        # resolution itself is unreliable here. Reading back parameters['vhm_10m_points'] isn't
        # safe either: by the time processAlgorithm() sees it, the Processing framework may have
        # already normalized it away from the plain string the caller passed (that was tried
        # 2026-09-04 and still hit the same bogus path). Instead, recompute the expected path
        # the same way every real caller does - from parameters['vhm_10m'], used as a raw string
        # elsewhere in this function (e.g. two lines above) - so this check never depends on
        # sink resolution at all. If the real destination already exists on disk, there's no
        # need to touch sink resolution - or GDAL/OGR - at all: just skip, exactly as the
        # "already exists" branch below always intended.
        expected_vhm_10m_points_path = os.path.splitext(parameters['vhm_10m'])[0] + "_points.gpkg"
        if os.path.exists(expected_vhm_10m_points_path):
            feedback.pushWarning(f"Output already exists: {expected_vhm_10m_points_path}. Skipping.")
            results['vhm_10m_points'] = expected_vhm_10m_points_path
            return results

        vhm_10m_points_path = self.parameterAsOutputLayer(parameters, 'vhm_10m_points', context)
        if not os.path.exists(vhm_10m_points_path):
            alg_params = {
                'FIELD_NAME': 'VHM_10m',
                'INPUT_RASTER': parameters['vhm_10m'],
                'RASTER_BAND': 1,
                'OUTPUT': vhm_10m_points_path
            }
            outputs['RasterPixelsToPoints'] = processing.run('native:pixelstopoints', alg_params, context=context,
                                                         feedback=feedback, is_child_algorithm=True)
            results['vhm_10m_points'] = outputs['RasterPixelsToPoints']['OUTPUT']
        else:
            feedback.pushWarning(f"Output already exists: {vhm_10m_points_path}. Skipping.")
            results['vhm_10m_points'] = vhm_10m_points_path
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

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkPostprocessHdomDiff()
