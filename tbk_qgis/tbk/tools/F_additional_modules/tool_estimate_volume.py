# -*- coding: utf-8 -*-
# *************************************************************************** #
# Based on hdom, DG and NH the volume (dominant breast height diameter) is estimated.
#
# Name : TBk V estimate
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
from qgis._core import QgsProcessingException, QgsVectorLayer, QgsProcessingParameterFile
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterFeatureSink
import processing

from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_processing_algorithm_toolsF import TBkProcessingAlgorithmToolF


class TBkVEstimate(TBkProcessingAlgorithmToolF):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            'stand_map_features', 'Stand map features with hdom, DG and NH attributes',
            types=[QgsProcessing.TypeVectorAnyGeometry],
            defaultValue=None))

        self.addParameter(QgsProcessingParameterFile(
            'V_estimator_stratification_CSV',
            'File with Volume Estimator specification (optional, CSV file)',
            extension='csv',
            optional=True,
            behavior=QgsProcessingParameterFile.File,
            defaultValue=None
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            'stand_map_with_V', 'Stand map with V',
            type=QgsProcessing.TypeVectorAnyGeometry,
            createByDefault=True, supportsAppend=True,
            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # --- ----------------------------------------------------
        # 1 Handle V_estimator_stratification_CSV input (CSV / layer / default)

        key_path = self.parameterAsFile(parameters, 'V_estimator_stratification_CSV', context)

        if not key_path:
            # No file provided — use default from plugin directory
            plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # tbk_qgis root
            key_path = os.path.join(plugin_dir, 'tbk', 'postproc', 'resources', 'VolumeEstimation_Stratification_FR.csv')
            feedback.pushInfo(f"Using default Volume Estimator from: {key_path}")
        else:
            feedback.pushInfo(f"Using user-specified Volume Estimator: {key_path}")

        if not os.path.exists(key_path):
            raise QgsProcessingException(f"Volume Estimator CSV file not found: {key_path}")

        # Detect delimiter automatically
        with open(key_path, 'r', encoding='utf-8-sig') as f:
            header_line = f.readline()
        delimiter = ';' if ';' in header_line and ',' not in header_line else ','

        uri = f'file:///{key_path}?type=csv&detectTypes=yes&geomType=none&delimiter={delimiter}'
        V_estimator_stratification_CSV = QgsVectorLayer(uri, 'V_estimator_stratification_CSV', 'delimitedtext')

        if not V_estimator_stratification_CSV.isValid():
            raise QgsProcessingException(f"Failed to load ForestSite–BonClass key from: {key_path}")

        feedback.pushInfo(f"Loaded key layer with fields: {[f.name() for f in V_estimator_stratification_CSV.fields()]}")

        # --- ----------------------------------------------------
        # 2 Determine V based on attributes
        interval_rules = []

        for f in V_estimator_stratification_CSV.getFeatures():
            def parse_interval(text):
                text = text.strip().replace('"', '')
                # Format is "[a;b[" or "[a;b]"
                left_inc = text.startswith('[')
                right_inc = text.endswith(']')
                nums = text[1:-1].split(';')
                lo = float(nums[0]) if nums[0] != '' else None
                hi = float(nums[1]) if nums[1] != '' else None
                return lo, hi, left_inc, right_inc

            h_lo, h_hi, _, _ = parse_interval(f['hdom'])
            dg_lo, dg_hi, _, _ = parse_interval(f['DG'])
            nh_lo, nh_hi, _, _ = parse_interval(f['NH'])

            mean_V = f['mean_V_3_strates']

            interval_rules.append((
                h_lo, h_hi,
                dg_lo, dg_hi,
                nh_lo, nh_hi,
                (round(mean_V / 10 ) * 10) if mean_V is not None else 0
            ))

        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'Volume_estimated',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': (
                    'CASE ' +
                    ''.join([
                        f'WHEN "hdom" >= {h_min} AND "hdom" < {h_max} AND '
                        f'"DG" >= {dg_min} AND "DG" < {dg_max} AND '
                        f'"NH" >= {nh_min} AND "NH" < {nh_max} '
                        f'THEN {vol} '
                        for (h_min, h_max, dg_min, dg_max, nh_min, nh_max, vol)
                        in interval_rules
                    ]) +
                    'END'
            ),
            'INPUT': parameters['stand_map_features'],
            'OUTPUT': parameters['stand_map_with_V']
        }

        outputs['calculated_V'] = processing.run(
            'native:fieldcalculator', alg_params,
            context=context, feedback=feedback, is_child_algorithm=True
        )

        results['stand_map_with_V'] = outputs['calculated_V']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess V estimate'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return TBkVEstimate()
