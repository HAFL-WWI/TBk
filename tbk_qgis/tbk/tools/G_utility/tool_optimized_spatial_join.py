# -*- coding: utf-8 -*-
# *************************************************************************** #
# Perform a spatial join, converting to singlepart geometries and indexing before
#
# Model exported as python.
# Name : Append Attribute (singlepart + index)
#
# (C) Hannes Horneber (BFH-HAFL)
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
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterFeatureSink,
    QgsProcessingMultiStepFeedback,
)
import processing
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_processing_algorithm_toolsG import TBkProcessingAlgorithmToolG
import time  # ← added


class OptimizedSpatialJoin(TBkProcessingAlgorithmToolG):
    # -----------------------------------------
    # PARAMETER KEYS
    # =========================================
    P_LAYER_A = "layer_to_join_attribute_on"
    P_LAYER_B = "attribute_layer"
    P_FIELDS = "fields_to_join"
    P_PREFIX = "joined_attributes_prefix"
    P_OUTPUT = "OUTPUT"

    P_SINGLEPART = "convert_to_singlepart_before_join"
    P_FIXGEOM = "fix_geometries_before_join"
    P_CLIP = "clip_before_join"

    # -----------------------------------------
    # ALGORITHM SETUP
    # =========================================
    def initAlgorithm(self, config=None):

        # Main join target (layer A)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.P_LAYER_A,
                "Layer to join attribute on",
                types=[QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # Attribute source (layer B)
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.P_LAYER_B,
                "Attribute Layer",
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

        # Fields to join
        self.addParameter(
            QgsProcessingParameterField(
                self.P_FIELDS,
                "Fields to Join",
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.P_LAYER_B,
                allowMultiple=True,
                defaultValue=["Code"]
            )
        )

        # Prefix
        self.addParameter(
            QgsProcessingParameterString(
                self.P_PREFIX,
                "Joined Attributes Prefix",
                optional=True,
                defaultValue=""
            )
        )

        # toggle singlepart conversion
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.P_SINGLEPART,
                "Convert attribute layer to singlepart before join",
                defaultValue=False
            )
        )

        # toggle fix geometries conversion
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.P_FIXGEOM,
                "Fix geometries on attribute layer before join",
                defaultValue=False
            )
        )

        # toggle bounding-box clipping option
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.P_CLIP,
                "Clip attribute layer B to extent of layer A (bounding-box)",
                defaultValue=True
            )
        )

        # Output
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.P_OUTPUT,
                "Output with attribute",
                createByDefault=True,
                type=QgsProcessing.TypeVectorAnyGeometry
            )
        )

    # -----------------------------------------
    # MAIN LOGIC
    # =========================================
    def processAlgorithm(self, parameters, context, model_feedback):

        feedback = QgsProcessingMultiStepFeedback(10, model_feedback)
        results = {}

        t0 = time.perf_counter()
        last = t0

        def _tick(label):
            nonlocal last
            now = time.perf_counter()
            feedback.pushInfo(f"{label}: \t\t      {now - last:.3f}s (total {now - t0:.3f}s)")
            last = now

        # PARAMETERS
        layer_A = self.parameterAsVectorLayer(parameters, self.P_LAYER_A, context)
        layer_B = self.parameterAsVectorLayer(parameters, self.P_LAYER_B, context)

        fields_to_join = parameters[self.P_FIELDS]
        prefix = parameters[self.P_PREFIX]

        do_singlepart = self.parameterAsBoolean(parameters, self.P_SINGLEPART, context)
        do_clip = self.parameterAsBoolean(parameters, self.P_CLIP, context)
        do_fixgeom = self.parameterAsBoolean(parameters, self.P_FIXGEOM, context)

        # -----------------------------------------
        # SECTION 1: PREPARE LAYER A (target)
        # =========================================

        # --- STEP 1: ensure spatial index on A
        feedback.setCurrentStep(0)
        if layer_A.dataProvider().hasSpatialIndex() == 2:
            feedback.pushInfo(f"{layer_A.name()}: Spatial index already exists")
            input_A = layer_A.source()
        else:
            feedback.pushInfo(f"Creating spatial index for {layer_A.name()}")
            res = processing.run(
                "native:createspatialindex",
                {"INPUT": parameters[self.P_LAYER_A]},
                context=context,
                feedback=feedback,
                is_child_algorithm=True
            )
            input_A = res["OUTPUT"]
        _tick("Step 1 (Index A)")

        # -----------------------------------------
        # SECTION 2: PREPARE LAYER B (attribute source)
        # =========================================
        prepared_B = parameters[self.P_LAYER_B]

        # --- STEP 2: multipart → singlepart (optional)
        feedback.setCurrentStep(1)
        if do_singlepart:
            feedback.pushInfo("Converting attribute layer B to singlepart…")
            res = processing.run(
                "native:multiparttosingleparts",
                {"INPUT": prepared_B, "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT},
                context=context, feedback=feedback, is_child_algorithm=True
            )
            prepared_B = res["OUTPUT"]
            _tick("Step 2 (Singlepart B)")
        else:
            feedback.pushInfo("skip Step 2 (Singlepart disabled)")

        # --- STEP 3: fix geometries
        feedback.setCurrentStep(2)
        if do_fixgeom:
            feedback.pushInfo("Fixing geometries…")
            res = processing.run(
                "native:fixgeometries",
                {"INPUT": prepared_B, "METHOD": 1, "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT},
                context=context, feedback=feedback, is_child_algorithm=True
            )
            prepared_B = res["OUTPUT"]
            _tick("Step 3 (Fix geometries)")
        else:
            feedback.pushInfo("skip Step 3 (Fix geometries disabled)")

        # --- STEP 4: bounding-box clip (optional)
        feedback.setCurrentStep(3)
        if do_clip:
            feedback.pushInfo("Clipping attribute layer B to bounding box of A…")
            res_box = processing.run(
                "native:polygonfromlayerextent",
                {"INPUT": layer_A, "ROUND_TO": 0, "OUTPUT": "TEMPORARY_OUTPUT"},
            )
            temp_bbox = res_box["OUTPUT"]

            res_clip = processing.run(
                "native:clip",
                {"INPUT": prepared_B, "OVERLAY": temp_bbox, "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT},
                context=context, feedback=feedback, is_child_algorithm=True
            )
            prepared_B = res_clip["OUTPUT"]
            _tick("Step 4 (Clip B)")
        else:
            feedback.pushInfo("skip Step 3 (Bounding-box clipping disabled")

        # --- STEP 5: ensure spatial index on B
        feedback.setCurrentStep(4)
        res = processing.run(
            "native:createspatialindex",
            {"INPUT": prepared_B},
            context=context, feedback=feedback, is_child_algorithm=True
        )
        indexed_B = res["OUTPUT"]
        _tick("Step 5 (Index B)")

        # -----------------------------------------
        # SECTION 3: SPATIAL JOIN
        # =========================================

        feedback.setCurrentStep(5)
        feedback.pushInfo("Running spatial join (largest overlap)…")

        res = processing.run(
            "native:joinattributesbylocation",
            {
                "INPUT": input_A,
                "JOIN": indexed_B,
                "JOIN_FIELDS": fields_to_join,
                "PREDICATE": [0],  # intersects
                "METHOD": 2,  # largest overlap (1:1)
                "DISCARD_NONMATCHING": False,
                "PREFIX": prefix,
                "OUTPUT": parameters[self.P_OUTPUT],
            },
            context=context, feedback=feedback, is_child_algorithm=True
        )
        _tick("Step 6 (Spatial join)")

        feedback.pushInfo(f"TOTAL TIME Optimized spatial Join: {time.perf_counter() - t0:.3f}s")

        results[self.P_OUTPUT] = res["OUTPUT"]
        return results

    # -----------------------------------------
    # METADATA
    # =========================================

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Optimized Spatial Join'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Spatial Join that optimizes the performance before joining. Converts the secondary join layer to singlepart and adds spatial indices for both layers, ensuring a better performance on the join.</p></body></html></p>
<h2>Input parameters</h2>
<h3>Layer to join attribute on</h3>
<p>Main join layer</p>
<h3>Attribute Layer</h3>
<p>Secondary join layer (with attributes to append to main layer)</p>
<h2>Outputs</h2>
<h3>Output with Attribute</h3>
<p>Main layer with joined attributes from secondary layer.</p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm author: Hannes Horneber @ BFH-HAFL (2024)</p></body></html>"""

    def createInstance(self):
        return OptimizedSpatialJoin()
