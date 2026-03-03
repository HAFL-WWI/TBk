# -*- coding: utf-8 -*-
# *************************************************************************** #
#
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
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterFile,
    QgsProcessingParameterFeatureSink,
    QgsProcessingException,
    QgsVectorLayer
)
import processing


class TBkPostprocessImportWIS2WebCSV(QgsProcessingAlgorithm):

    INPUT_STANDS = "INPUT_STANDS"
    INPUT_CSV = "INPUT_CSV"
    OUTPUT = "OUTPUT"

    # ---------------------------------------------------------
    # PARAMETERS
    # =========================================================
    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_STANDS,
                self.tr("Stand map (must contain field 'ID')"),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_CSV,
                self.tr("WIS.2 Web CSV (must contain 'standID')"),
                extension="csv"
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Stand map with WIS.2 Web attributes"),
                type=QgsProcessing.TypeVectorAnyGeometry
            )
        )

    # ---------------------------------------------------------
    # MAIN PROCESSING
    # =========================================================
    def processAlgorithm(self, parameters, context, model_feedback):

        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # --- Step 1: Validate inputs
        feedback.setCurrentStep(0)

        stand_layer = self.parameterAsVectorLayer(
            parameters, self.INPUT_STANDS, context
        )

        if stand_layer is None:
            raise QgsProcessingException("Invalid stand layer")

        stand_fields = stand_layer.fields().names()
        id_field = next((f for f in stand_fields if f.lower() == "id"), None)

        if id_field is None:
            raise QgsProcessingException(
                "Stand layer must contain field 'ID' (case insensitive)"
            )

        csv_path = self.parameterAsFile(
            parameters, self.INPUT_CSV, context
        )

        uri = (
            f"file:///{csv_path}"
            "?type=csv"
            "&detectTypes=yes"
            "&geomType=none"
            "&subsetIndex=no"
            "&watchFile=no"
        )

        csv_layer = QgsVectorLayer(uri, "wis2web_csv", "delimitedtext")

        if not csv_layer.isValid():
            raise QgsProcessingException("CSV could not be loaded")

        # Case-insensitive lookup of standID field
        csv_fields = csv_layer.fields().names()
        stand_id_field = next(
            (f for f in csv_fields if f.lower() == "standid"),
            None
        )

        if stand_id_field is None:
            raise QgsProcessingException(
                "CSV must contain field 'standID' (case insensitive)"
            )

        # --- Step 2: Join attribute table
        feedback.setCurrentStep(1)

        feedback.pushInfo("Joining CSV table (standID → ID)")

        alg_params = {
            "INPUT": stand_layer,
            "FIELD": id_field,
            "INPUT_2": csv_layer,
            "FIELD_2": stand_id_field,
            "FIELDS_TO_COPY": [
                "ddom",
                "age",
                "growingStockVolume",
                "TngUrg01_ha",
                "TngUrg01_m3",
                "TngUrg02_ha",
                "TngUrg02_m3",
                "TngUrg03_ha",
                "TngUrg03_m3",
                "rngUrgP0ha",
                "rngUrgP1ha",
                "rngUrgP2ha",
                "rngUrgP3ha",
                "rngPriP1ha",
                "rngPriP2ha",
                "rngPriP3ha",
            ],
            "METHOD": 1,  # first matching feature only (1:1)
            "DISCARD_NONMATCHING": False,
            "PREFIX": "",
            "OUTPUT": parameters[self.OUTPUT],
        }

        outputs["Join"] = processing.run(
            "native:joinattributestable",
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True,
        )

        results[self.OUTPUT] = outputs["Join"]["OUTPUT"]

        return results

    # ---------------------------------------------------------
    # METADATA
    # =========================================================

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk WIS.2 Web import CSV'

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
        return TBkPostprocessImportWIS2WebCSV()
