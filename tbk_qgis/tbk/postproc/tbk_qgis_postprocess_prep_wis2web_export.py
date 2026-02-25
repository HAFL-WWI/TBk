# -*- coding: utf-8 -*-
# *************************************************************************** #
# TBk: Toolkit Bestandeskarte (QGIS Plugin)
# TBk prepare WIS2 web export – Preprocessing Tool
#
# Prepares a stand map (Bestandeskarte) for WIS.2 export.
# Steps:
#   1) hdom: set 0/NULL -> 1
#   2) ID: ensure numeric, assign sequential ints if needed
#   3) ForestSite: join via TBk:Optimized Spatial Join (or default)
#   4) (optional) ConInd/FolInd from NH
#   5) cc0/cc1/cc2: join via TBk:Optimized Spatial Join (or default)
#
# Authors: Hannes Horneber (BFH-HAFL), Copilot assist
# License: AGPL-3.0-or-later
# *************************************************************************** #

import os
from datetime import datetime

import processing
from PyQt5.QtCore import QMetaType

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis._core import QgsProcessingMultiStepFeedback
from qgis.core import (
    QgsApplication,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterFeatureSink,
    QgsProcessingFeatureSourceDefinition,
    QgsProcessingUtils,
    QgsProcessingException,
    QgsFields,
    QgsField,
    QgsFeature,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFeatureRequest,
)


class TBkPrepareWIS2Export(QgsProcessingAlgorithm):
    # -----------------------------------------
    # PARAMETER KEYS
    # =========================================

    INPUT = "input_layer"
    OUTPUT = "OUTPUT"

    # ForestSite
    FORESTSITE_DEFAULT = "forestsite_default"
    FORESTSITE_LAYER = "forestsite_layer"
    FORESTSITE_LAYER_FIELD = "forestsite_layer_field"

    # Coniferous / Deciduous
    USE_CONIFEROUS = "use_coniferous"
    SOURCE_FIELD_NH = "source_field_nh"
    TARGET_FIELD_NH = "target_field_nh"
    TARGET_FIELD_LH = "target_field_lh"

    # VegZones cc0/cc1/cc2
    CC0_DEFAULT = "cc0_default"
    CC0_LAYER = "cc0_layer"
    CC0_LAYER_FIELD = "cc0_layer_field"

    CC1_DEFAULT = "cc1_default"
    CC1_LAYER = "cc1_layer"
    CC1_LAYER_FIELD = "cc1_layer_field"

    CC2_DEFAULT = "cc2_default"
    CC2_LAYER = "cc2_layer"
    CC2_LAYER_FIELD = "cc2_layer_field"

    # -----------------------------------------
    # HELPER FUNCTIONS
    # =========================================

    def _layer_has_field(self, layer: QgsVectorLayer, name: str) -> bool:
        try:
            return name in layer.fields().names()
        except Exception:
            return False

    def _ensure_vector_layer(self, layer_or_id, context):
        """
        Ensures we always return a QgsVectorLayer.
        Accepts either:
          - QgsVectorLayer
          - processing output string (layer id / uri)
        """
        if isinstance(layer_or_id, QgsVectorLayer):
            return layer_or_id

        layer = QgsProcessingUtils.mapLayerFromString(layer_or_id, context)

        if not layer:
            raise QgsProcessingException(f"Could not resolve layer from id/source: {layer_or_id}")

        return layer

    # --- FUNCTION join create_and_apply_default
    def join_create_and_apply_default(self, current, join_layer, join_field,
                                      target_field_name,
                                      target_field_type,  # 1=int, 2=string
                                      default_value, multiply_factor, context, feedback):
        """
        Generic join + field creation logic.

        target_field_type:
            1 = Integer
            2 = String

        multiply_factor (needed for cc):
            1   -> no multiplication
            10  -> multiply joined value by 10
        """

        # ensure layer from TEMPORARY_OUTPUT string
        # to check if target field already exists and drop if yes
        current = self._ensure_vector_layer(current, context)

        if target_field_name in current.fields().names():
            feedback.pushInfo(f"Drop existing field {target_field_name}")
            current = processing.run(
                "native:deletecolumn",
                {
                    "INPUT": current,
                    "COLUMN": [target_field_name],
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                }, context=context, feedback=feedback, is_child_algorithm=True,
            )["OUTPUT"]

        join_expr = None

        # --- Optional Spatial Join
        if join_layer and join_field:
            feedback.pushInfo(f"{target_field_name}: running spatial join")
            current = processing.run(
                "TBk:Optimized Spatial Join",
                {
                    "layer_to_join_attribute_on": current,
                    "attribute_layer": join_layer,
                    "fields_to_join": [join_field],
                    "joined_attributes_prefix": "joined_",
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                }, context=context, feedback=feedback, is_child_algorithm=True,
            )["OUTPUT"]

            joined_name = f"joined_{join_field}"

            # --- ForestSite case (no multiply)
            if multiply_factor == 1:
                current = processing.run(
                    "native:renametablefield",
                    {
                        "INPUT": current,
                        "FIELD": joined_name,
                        "NEW_NAME": target_field_name,
                        "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                    }, context=context, feedback=feedback, is_child_algorithm=True,
                )["OUTPUT"]
            # --- cc case (multiply required)
            else:
                feedback.pushInfo(f"{target_field_name}: multiply joined value by {multiply_factor}")
                expr = f'"{joined_name}" * {multiply_factor}'

                current = processing.run(
                    "native:fieldcalculator",
                    {
                        "INPUT": current,
                        "FIELD_NAME": target_field_name,
                        "FIELD_TYPE": target_field_type,
                        "FIELD_LENGTH": 80 if target_field_type == 2 else 10,
                        "FIELD_PRECISION": 0,
                        "NEW_FIELD": True,
                        "FORMULA": expr,
                        "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                    }, context=context, feedback=feedback, is_child_algorithm=True,
                )["OUTPUT"]

                feedback.pushInfo(f"Drop join field {joined_name} (isn't necessary anymore)")
                current = processing.run(
                    "native:deletecolumn",
                    {
                        "INPUT": current,
                        "COLUMN": [joined_name],
                        "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                    }, context=context, feedback=feedback, is_child_algorithm=True,
                )["OUTPUT"]

        # --- Default fallback (only fill NULLs)
        feedback.pushInfo(f"{target_field_name}: fill in default:{default_value} to missing values.")
        expr = f'coalesce("{target_field_name}", {repr(default_value)})'

        current = processing.run(
            "native:fieldcalculator",
            {
                "INPUT": current,
                "FIELD_NAME": target_field_name,
                "FIELD_TYPE": target_field_type,
                "FIELD_LENGTH": 80 if target_field_type == 2 else 10,
                "FIELD_PRECISION": 0,
                "NEW_FIELD": False,
                "FORMULA": expr,
                "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
            }, context=context, feedback=feedback, is_child_algorithm=True,
        )["OUTPUT"]

        return current

    def addAdvancedParameter(self, parameter):
        from qgis.core import QgsProcessingParameterDefinition
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # -----------------------------------------
    # PARAMETER DEFINITIONS
    # =========================================

    def initAlgorithm(self, config):

        # Input stand map
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Stand map (Bestandeskarte)"),
                [QgsProcessing.TypeVectorPolygon],
            )
        )

        # --- ForestSite params (Advanced)
        self.addParameter(
            QgsProcessingParameterString(
                self.FORESTSITE_DEFAULT,
                self.tr("Forest Site Category (Code, e.g. 7a). Will be used where no Forest Site Layer is available"),
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.FORESTSITE_LAYER,
                self.tr("Forest Site Category layer (will overwrite existing ForestSite field if present)"),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
        self.addParameter(
            QgsProcessingParameterField(
                self.FORESTSITE_LAYER_FIELD,
                self.tr("Forest Site Category field (in layer)"),
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.FORESTSITE_LAYER,
                allowMultiple=False,
                optional=True
            )
        )

        # --- Coniferous / Deciduous
        self.addAdvancedParameter(
            QgsProcessingParameterBoolean(
                self.USE_CONIFEROUS,
                self.tr("Generate tree species columns from NH."
                        "\n(use ONLY WHEN NO TREE SPECIES columns are used! Don't use both.)"),
                defaultValue=False,
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterField(
                self.SOURCE_FIELD_NH,
                self.tr("Field containing coniferous proportion (e.g. NH)"
                        "\n(only used when 'Generate tree species columns' is on)"),
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.INPUT,
                defaultValue="NH",
                allowMultiple=False,
                optional=True
            )
        )

        self.addAdvancedParameter(
            QgsProcessingParameterString(
                self.TARGET_FIELD_NH,
                self.tr("Name of the created field that NH is converted to"
                        "e.g. ConInd for general coniferae or PicAbie for spruce."
                        "\n(only used when 'Generate tree species columns' is on)"),
                defaultValue="ConInd",
                optional=True,
            )
        )

        self.addAdvancedParameter(
            QgsProcessingParameterString(
                self.TARGET_FIELD_LH,
                self.tr("Name of the created field that LH (100 - NH) is used for"
                        "e.g. FolInd for general decidious or FagSylv for beech."
                        "\n(only used when 'Generate tree species columns' is on)"),
                defaultValue="FolInd",
                optional=True,
            )
        )

        # --- VegZones (Advanced): cc0/cc1/cc2

        # ---    cc0 - 2 Layer
        self.addAdvancedParameter(
            QgsProcessingParameterFeatureSource(
                self.CC0_LAYER,
                self.tr("\n\nVegZone Layer cc0 (VegZone 1975)"),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterFeatureSource(
                self.CC1_LAYER,
                self.tr("VegZone Layer cc1 (VegZone 2085 moderate)"),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterFeatureSource(
                self.CC2_LAYER,
                self.tr("VegZone Layer cc2 (VegZone 2085 dry)"),
                [QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        )

        # ---    cc0 - 2 Field
        self.addAdvancedParameter(
            QgsProcessingParameterField(
                self.CC0_LAYER_FIELD,
                self.tr("VegZone field cc0 (in layer) (VegZone 1975)"),
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.CC0_LAYER,
                defaultValue="Code",
                allowMultiple=False,
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterField(
                self.CC1_LAYER_FIELD,
                self.tr("VegZone field cc1 (in layer) (VegZone 2085 moderate)"),
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.CC1_LAYER,
                defaultValue="Code",
                allowMultiple=False,
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterField(
                self.CC2_LAYER_FIELD,
                self.tr("VegZone field cc2 (in layer) (VegZone 2085 dry)"),
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.CC2_LAYER,
                defaultValue="Code",
                allowMultiple=False,
                optional=True
            )
        )

        # ---    cc0 - 2 Default

        self.addAdvancedParameter(
            QgsProcessingParameterNumber(
                self.CC0_DEFAULT,
                self.tr("Default cc0 (VegZone 1975)"),
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterNumber(
                self.CC1_DEFAULT,
                self.tr("Default cc1 (VegZone 2085 moderate)"),
                optional=True
            )
        )
        self.addAdvancedParameter(
            QgsProcessingParameterNumber(
                self.CC2_DEFAULT,
                self.tr("Default cc2 (VegZone 2085 dry)"),
                optional=True
            )
        )

        # Output (single layer; user can choose file or temporary)
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Prepared Stand Map (output)"),
            )
        )

    # -----------------------------------------
    # MAIN PROCESSING
    # =========================================

    def processAlgorithm(self, parameters, context, model_feedback):
        feedback = QgsProcessingMultiStepFeedback(10, model_feedback)
        results = {}

        # Resolve inputs
        stands_src = self.parameterAsSource(parameters, self.INPUT, context)
        stands_vl = self.parameterAsVectorLayer(parameters, self.INPUT, context)

        use_coni = self.parameterAsBoolean(parameters, self.USE_CONIFEROUS, context)
        source_field_nh = self.parameterAsString(parameters, self.SOURCE_FIELD_NH, context)
        target_field_nh = self.parameterAsString(parameters, self.TARGET_FIELD_NH, context)
        target_field_lh = self.parameterAsString(parameters, self.TARGET_FIELD_LH, context)

        forestsite_default = (self.parameterAsString(parameters, self.FORESTSITE_DEFAULT, context) or "7a").strip()
        forestsite_layer = self.parameterAsVectorLayer(parameters, self.FORESTSITE_LAYER, context)
        forestsite_field = self.parameterAsString(parameters, self.FORESTSITE_LAYER_FIELD, context)

        cc0_default = int(round(self.parameterAsDouble(parameters, self.CC0_DEFAULT, context)))
        cc0_layer = self.parameterAsVectorLayer(parameters, self.CC0_LAYER, context)
        cc0_field = self.parameterAsString(parameters, self.CC0_LAYER_FIELD, context)

        cc1_default = int(round(self.parameterAsDouble(parameters, self.CC1_DEFAULT, context)))
        cc1_layer = self.parameterAsVectorLayer(parameters, self.CC1_LAYER, context)
        cc1_field = self.parameterAsString(parameters, self.CC1_LAYER_FIELD, context)

        cc2_default = int(round(self.parameterAsDouble(parameters, self.CC2_DEFAULT, context)))
        cc2_layer = self.parameterAsVectorLayer(parameters, self.CC2_LAYER, context)
        cc2_field = self.parameterAsString(parameters, self.CC2_LAYER_FIELD, context)

        feedback.pushInfo(
            "================================= TBk prepare WIS2 web export =================================")

        # Start chain with original input
        current = stands_vl  # processing accepts layer obj or path; we keep as layer until first algorithm

        # -------------------------------------------
        # Join / apply default (ForestSite, cc0 - 2)
        # ===========================================

        # ForestSite (string, no multiply)
        # cc0 / cc1 / cc2 (integer, multiply *10)
        for name, layer, field, default, data_type, multiply in [
            ("ForestSite", forestsite_layer, forestsite_field, forestsite_default, 2, 1),  # str / no multiply
            ("cc0", cc0_layer, cc0_field, cc0_default, 1, 10),  # int / multiply * 10
            ("cc1", cc1_layer, cc1_field, cc1_default, 1, 10),
            ("cc2", cc2_layer, cc2_field, cc2_default, 1, 10),
        ]:
            # Skip if default is empty AND (layer or field missing)
            if (default in (None, "")) and (not layer or not field):
                feedback.pushInfo(f"{name}: skipped (no default and missing layer/field)")
            else:
                feedback.pushInfo(f"\n{name} processing...")
                current = self.join_create_and_apply_default(
                    current=current,
                    join_layer=layer,
                    join_field=field,
                    target_field_name=name,
                    target_field_type=data_type,
                    default_value=default,
                    multiply_factor=multiply,
                    context=context,
                    feedback=feedback,
                )

        # -----------------------------------------
        # Optional ConInd / FolInd from NH
        # =================================================

        if use_coni:
            feedback.pushInfo(f"\n{source_field_nh} to generate {target_field_nh}/{target_field_lh} columns")

            current = self._ensure_vector_layer(current, context)
            if source_field_nh not in current.fields().names():
                raise QgsProcessingException(
                    f'NH field "{source_field_nh}" not found for {target_field_nh}/{target_field_lh} calculation')

            # ConInd = NH
            current = processing.run(
                "native:fieldcalculator",
                {
                    "INPUT": current,
                    "FIELD_NAME": target_field_nh,
                    "FIELD_TYPE": 1,
                    "FIELD_LENGTH": 10,
                    "FIELD_PRECISION": 0,
                    "NEW_FIELD": True,
                    "FORMULA": f'"{source_field_nh}"',
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )["OUTPUT"]

            # FolInd = 100 - NH
            current = processing.run(
                "native:fieldcalculator",
                {
                    "INPUT": current,
                    "FIELD_NAME": target_field_lh,
                    "FIELD_LENGTH": 10,
                    "FIELD_PRECISION": 0,
                    "NEW_FIELD": True,
                    "FORMULA": f'100 - "{source_field_nh}"',
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                    # "OUTPUT": parameters[self.OUTPUT]
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )["OUTPUT"]

        # -------------------------------------------------
        # Ensure attribute constraints (hdom, ID)
        # =================================================

        # --- Ensure ID field exists and is numeric
        current = self._ensure_vector_layer(current, context)
        id_field = current.fields().field("ID") if "ID" in current.fields().names() else None

        NUMERIC_TYPES = {QVariant.Int, QVariant.LongLong, QVariant.UInt, QVariant.ULongLong, QVariant.Double}
        if id_field is None or id_field.type() not in NUMERIC_TYPES:
            feedback.pushInfo("\nID field missing or not numeric → creating sequential numeric ID")
            current = processing.run(
                "native:fieldcalculator",
                {
                    "INPUT": current,
                    "FIELD_NAME": "ID",
                    "FIELD_TYPE": 1,  # Integer
                    "FIELD_LENGTH": 10,
                    "FIELD_PRECISION": 0,
                    "NEW_FIELD": True,
                    "FORMULA": "@id",  # 1-based sequential ID
                    "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                },
                context=context,
                feedback=feedback,
                is_child_algorithm=True,
            )["OUTPUT"]
        else:
            feedback.pushInfo("\nID field exists and is numeric → keeping existing values")

        # --- Ensure hdom is present and > 0

        # Replace 0 or NULL with 1
        feedback.pushInfo("\nhdom: replacing 0/NULL with 1")
        current = processing.run(
            "native:fieldcalculator",
            {
                "INPUT": current,
                "FIELD_NAME": "hdom",
                "FIELD_TYPE": 1,
                "FIELD_LENGTH": 10,
                "FIELD_PRECISION": 0,
                "NEW_FIELD": False,  # overwrite
                "FORMULA": 'if("hdom" IS NULL OR "hdom" = 0, 1, "hdom")',
                # "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
                "OUTPUT": parameters[self.OUTPUT]
            }, context=context, feedback=feedback, is_child_algorithm=True,
        )["OUTPUT"]

        feedback.pushInfo("\nFinished postprocessing steps: ID, hdom, ConInd/FolInd")

        return {self.OUTPUT: current}

    # -----------------------------------------
    # METADATA
    # =========================================

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    def createInstance(self):
        return TBkPrepareWIS2Export()

    def name(self):
        return "tbk_wis2_web_prep"

    def displayName(self):
        return self.tr("TBk WIS.2 Web prep export (KML)")

    def group(self):
        return "2 TBk Postprocessing"

    def groupId(self):
        return "postproc"
