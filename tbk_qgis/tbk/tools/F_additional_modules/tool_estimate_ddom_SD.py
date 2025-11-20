# -*- coding: utf-8 -*-
# *************************************************************************** #
# Based on hdom, NH (mixture degree) and a forest site with a bonity class
# the ddom (dominant breast height diameter) is estimated (and in extension the
# SD = stade de developpement/stage of development (DE Entwicklungsstufe))
#
# Model exported as python.
# Name : TBk ddom and SD estimate
# Group : TBk
# With QGIS : 34008
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
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFeatureSink
import processing

from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_processing_algorithm_toolsF import TBkProcessingAlgorithmToolF


class TBkDdomSDEstimate(TBkProcessingAlgorithmToolF):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            'stand_map_features', 'Stand map features',
            types=[QgsProcessing.TypeVectorAnyGeometry],
            defaultValue=None))

        self.addParameter(QgsProcessingParameterField(
            'stand_map_forestsite_field', 'Stand map: ForestSite field',
            type=QgsProcessingParameterField.Any,
            parentLayerParameterName='stand_map_features',
            allowMultiple=False, defaultValue=None))

        self.addParameter(QgsProcessingParameterFile(
            'forestsitebonclass_key',
            'ForestSite–BonClass Key (optional, CSV file)',
            extension='csv',
            optional=True,
            behavior=QgsProcessingParameterFile.File,
            defaultValue=None
        ))

        self.addParameter(QgsProcessingParameterFeatureSink(
            'StandMapWithDdomAndSd', 'Stand map with ddom and SD',
            type=QgsProcessing.TypeVectorAnyGeometry,
            createByDefault=True, supportsAppend=True,
            defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}

        # --- ----------------------------------------------------
        # 1 Handle ForestSite–BonClass key input (CSV / layer / default)

        key_path = self.parameterAsFile(parameters, 'forestsitebonclass_key', context)

        if not key_path:
            # No file provided — use default from plugin directory
            plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # tbk_qgis root
            key_path = os.path.join(plugin_dir, 'tbk', 'postproc', 'resources', 'ForestSite_BonClass_key_BE.csv')
            feedback.pushInfo(f"Using default ForestSite–BonClass key from: {key_path}")
        else:
            feedback.pushInfo(f"Using user-specified ForestSite–BonClass key: {key_path}")

        if not os.path.exists(key_path):
            raise QgsProcessingException(f"ForestSite–BonClass key file not found: {key_path}")

        # Detect delimiter automatically
        with open(key_path, 'r', encoding='utf-8-sig') as f:
            header_line = f.readline()
        delimiter = ';' if ';' in header_line and ',' not in header_line else ','

        uri = f'file:///{key_path}?type=csv&detectTypes=yes&geomType=none&delimiter={delimiter}'
        forestsitebonclass_key = QgsVectorLayer(uri, 'ForestSite_BonClass_key', 'delimitedtext')

        if not forestsitebonclass_key.isValid():
            raise QgsProcessingException(f"Failed to load ForestSite–BonClass key from: {key_path}")

        feedback.pushInfo(f"Loaded key layer with fields: {[f.name() for f in forestsitebonclass_key.fields()]}")

        # --- ----------------------------------------------------
        # 2 Join attributes by field value
        feedback.pushInfo("Joining attributes by ForestSite value...")

        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['stand_map_forestsite_field'],
            'FIELDS_TO_COPY': 'BonClass',
            'FIELD_2': 'ForestSite',
            'INPUT': parameters['stand_map_features'],
            'INPUT_2': forestsitebonclass_key,
            'METHOD': 1,  # Take attributes of the first matching feature only
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }

        outputs['JoinAttributesByFieldValue'] = processing.run(
            'native:joinattributestable', alg_params,
            context=context, feedback=feedback, is_child_algorithm=True
        )

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # --- ----------------------------------------------------
        # 3️ Calculate ddom_estimated

        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'ddom_estimated',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,  # Integer
            'FORMULA': (
                'if("hdom" = 0, 0, '
                'if("NH">50, '
                'if("BonClass" = 1, 3.6303*ln("hdom")^5 - 30.318*ln("hdom")^4 + 90.489*ln("hdom")^3 - 110.26*ln("hdom")^2 + 49.747*ln("hdom") + 1.3889, '
                'if("BonClass" = 2, -0.00004*"hdom"^4 + 0.0047*"hdom"^3 -0.1489*"hdom"^2 + 2.934*"hdom" - 2.295, '
                '1.4611*ln("hdom")^4 - 8.7695*ln("hdom")^3 + 19.05*ln("hdom")^2 - 8.5983*ln("hdom"))), '
                'if("BonClass" = 1, 5.6023*ln("hdom")^3 - 21.583*ln("hdom")^2 + 24.945*ln("hdom") + 0.8036, '
                'if("BonClass" = 2, 4.4724*ln("hdom")^3 - 17.999*ln("hdom")^2 + 23.043*ln("hdom") + 0.5375, '
                '3.7027*ln("hdom")^3 - 15.203*ln("hdom")^2 + 21.037*ln("hdom") + 0.3938))))'
            ),
            'INPUT': outputs['JoinAttributesByFieldValue']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }

        outputs['CalculateDdom_estimated'] = processing.run(
            'native:fieldcalculator', alg_params,
            context=context, feedback=feedback, is_child_algorithm=True
        )

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # --- ----------------------------------------------------
        # 4 Calculate SD class (1–6)
        alg_params = {
            'FIELD_LENGTH': 0,
            'FIELD_NAME': 'SD',
            'FIELD_PRECISION': 0,
            'FIELD_TYPE': 1,
            'FORMULA': (
                'if("hdom" < 10 OR "ddom_estimated" < 10, 1, '
                'if("ddom_estimated" <= 20, 2, '
                'if("ddom_estimated" <= 30, 3, '
                'if("ddom_estimated" <= 40, 4, '
                'if("ddom_estimated" <= 50, 5, 6)))))'
            ),
            'INPUT': outputs['CalculateDdom_estimated']['OUTPUT'],
            'OUTPUT': parameters['StandMapWithDdomAndSd']
        }

        outputs['CalculateSd_16'] = processing.run(
            'native:fieldcalculator', alg_params,
            context=context, feedback=feedback, is_child_algorithm=True
        )

        results['StandMapWithDdomAndSd'] = outputs['CalculateSd_16']['OUTPUT']
        return results

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess ddom SD estimate'

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
        return TBkDdomSDEstimate()
