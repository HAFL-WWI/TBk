# -*- coding: utf-8 -*-
# *************************************************************************** #
# Prepare VHM raster and / or MG raster as input for TBk.
#
# Authors: Attilio Benini (BFH-HAFL)
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

import os  # os is used below, so make sure it's available in any case
import time
from datetime import datetime, timedelta
import glob
import math

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterString,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterNumber,
    QgsProcessingParameterDefinition,
    QgsProcessingException,
    QgsProcessingParameterField
)

import processing

from tbk_qgis.tbk.utility.tbk_utilities import *

from .pre_processing_helper import PreProcessingHelper


class TBkPrepareMaskAlgorithm(QgsProcessingAlgorithm):

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # --- Parameters (Class) ---

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # input
    MASK = "mask"

    # output
    OUTPUT = 'OUTPUT'

    # --- Advanced Parameters (Class) ---

    # advanced params
    # dissolve geometries (polygons & multipolygon)
    DISSOLVE = "dissolve"
    # dissolve field(s)
    DISSOLVE_FIELDS = "dissolve_fields"
    # replacement of attribute name fid, if fid is among dissolve field(s)
    FID_ORIGINAL = "fid_original"
    # return single parts (only polygons / no multipolygons)
    RETURN_SINGLE_PARTS = "return_single_parts"
    # min area polygon / multipolygon to keep (m^2)
    MIN_AREA = "min_area"
    # maximum hole-size within polygon / multipolygon (m^2)
    MAX_HOLE_SIZE_TO_REMOVE = "max_hole_size_to_remove"
    # min width of returned (multi-)polygons
    MIN_WIDTH = "min_width"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # --- Parameters (Tool UI) ---

        # input
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.MASK,
                self.tr("Input mask"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        # --- Advanced Parameters (Tool UI) ---

        # dissolve polygons / multipolygon
        parameter = QgsProcessingParameterBoolean(
            self.DISSOLVE,
            self.tr("Dissolve geometries"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # dissolve field(s)
        parameter = QgsProcessingParameterField(
            self.DISSOLVE_FIELDS,
            self.tr('Dissolve field(s)'),
            type=QgsProcessingParameterField.Any,
            parentLayerParameterName='mask',
            allowMultiple=True,
            optional=True
        )
        self.addAdvancedParameter(parameter)

        # replacement of attribute name fid, if fid is among dissolve field(s)
        parameter = QgsProcessingParameterString(
            self.FID_ORIGINAL,
            self.tr("Replacement of attribute name fid, if fid is among dissolve field(s)"),
            defaultValue="fid_original"
        )
        self.addAdvancedParameter(parameter)

        # return single parts (only polygons / no multipolygons)
        parameter = QgsProcessingParameterBoolean(
            self.RETURN_SINGLE_PARTS,
            self.tr("Return single-part geometries (no multi-polygons)"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # min area polygon / multipolygon to keep (m^2)
        parameter = QgsProcessingParameterNumber(
            self.MIN_AREA,
            self.tr(
                "Minimum area of returned (multi-)polygons (m^2)"
                "\nIf set to 0 no (multi-)polygons with actual surfaces get dropped"
            ),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=100
        )
        self.addAdvancedParameter(parameter)

        # maximum hole-size within polygon / multipolygon (m^2)
        parameter = QgsProcessingParameterNumber(
            self.MAX_HOLE_SIZE_TO_REMOVE,
            self.tr(
                "Maximum area of holes to be removed within returned (multi-)polygons (m^2)"
                "\nIf set to 0 no holes get removed / filled"
            ),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=10
        )
        self.addAdvancedParameter(parameter)

        # min width of returned (multi-)polygons
        parameter = QgsProcessingParameterNumber(
            self.MIN_WIDTH,
            self.tr(
                "Minimum width of returned (multi-)polygons (m)"
                "\nIf set to 0 no dropping of (multi-)polygons due to minimum width."
            ),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=10
        )
        self.addAdvancedParameter(parameter)

        # output layer
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Processed mask')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # --- Init Parameters

        # input
        mask = str(self.parameterAsVectorLayer(parameters, self.MASK, context).source())

        # advanced parameters
        # dissolve polygons / multipolygon
        dissolve = self.parameterAsBool(parameters, self.DISSOLVE, context)
        # min area polygon / multipolygon to keep (m^2)

        # dissolve field(s)
        dissolve_fields = self.parameterAsStrings(parameters, self.DISSOLVE_FIELDS, context)

        # replacement of attribute name fid, if fid among dissolve field(s)
        fid_original = str(self.parameterAsString(parameters, self.FID_ORIGINAL, context))

        # return single parts (only polygons / no multipolygons)
        return_single_parts = self.parameterAsBool(parameters, self.RETURN_SINGLE_PARTS, context)

        min_area = self.parameterAsInt(parameters, self.MIN_AREA, context)
        if min_area < 0:
            raise QgsProcessingException(
                "Minimum area of returned (multi-)polygons must be >= 0. If set to 0 no (multi-)polygons with actual surfaces get dropped."
            )

        # maximum hole-size within polygon / multipolygon (m^2)
        max_hole_size_to_remove = self.parameterAsInt(parameters, self.MAX_HOLE_SIZE_TO_REMOVE, context)
        if max_hole_size_to_remove < 0:
            raise QgsProcessingException(
                "Maximum hole-size within returned (multi-)polygons must be >= 0. If set to 0 no holes get removed / filled."
            )

        # min width of returned (multi-)polygons
        min_width = self.parameterAsInt(parameters, self.MIN_WIDTH, context)
        if min_width < 0:
            raise QgsProcessingException(
                "Minimum width of returned (multi-)polygons must be >= 0. If set to 0 no dropping of (multi-)polygons due to minimum width."
            )

        # output layer
        output = str(self.parameterAsOutputLayer(parameters, self.OUTPUT, context))

        # --- Process mask
        start_time = time.time()

        # remove M & Z- dimensions (if existing)
        param = {'INPUT': mask, 'DROP_M_VALUES': True, 'DROP_Z_VALUES': True, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:dropmzvalues", param)
        mask_ = algoOutput["OUTPUT"]

        # fix geometries
        param = {'INPUT': mask_, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fixgeometries", param)
        mask_ = algoOutput["OUTPUT"]

        # remove NULL- and empty geometries
        param = {'INPUT': mask_, 'REMOVE_EMPTY': True, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:removenullgeometries", param)
        mask_ = algoOutput["OUTPUT"]

        # select geometries with min. area > 0
        param = {'INPUT': mask_, 'EXPRESSION': '$area > 0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        mask_ = algoOutput["OUTPUT"]

        # buffer with zero in order to eliminate geometry types like (multi-)surface resp. turn them into (multi-)polygon
        param = {
            'INPUT': mask_,
            'DISTANCE': 0,  # buffer with zero
            'SEGMENTS': 5,
            'END_CAP_STYLE': 0,
            'JOIN_STYLE': 0,
            'MITER_LIMIT': 2,
            'DISSOLVE': False,
            'SEPARATE_DISJOINT': False,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        algoOutput = processing.run("native:buffer", param)
        mask_ = algoOutput["OUTPUT"]

        # after buffering fix geometries once again
        param = {'INPUT': mask_, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fixgeometries", param)
        mask_ = algoOutput["OUTPUT"]

        # once again: select polygons / multipolygons with min. area > 0
        param = {'INPUT': mask_, 'EXPRESSION': '$area > 0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        mask_ = algoOutput["OUTPUT"]

        if dissolve:
            # if fid among dissolve field(s) ...
            if 'fid' in dissolve_fields:
                # ... save fid under attribute name giving hint that refers to original fid (default fid_original)
                param = {
                    'INPUT': mask_,
                    'FIELD_NAME': fid_original,
                    'FIELD_TYPE': 1,
                    'FIELD_LENGTH': 0,
                    'FIELD_PRECISION': 0,
                    'FORMULA': ' "fid" ',
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
                algoOutput = processing.run("native:fieldcalculator", param)
                mask_ = algoOutput["OUTPUT"]
                # ... and replace fid listed among dissolve fields by attribute name of the copied fid
                dissolve_fields[dissolve_fields == 'fid'] = fid_original

            param = {'INPUT': mask_, 'FIELD': dissolve_fields, 'SEPARATE_DISJOINT': False, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:dissolve", param)
            mask_ = algoOutput["OUTPUT"]

        # only keep fid & if used dissolve fields as attribute(s)
        fields_to_keep = ['fid'] + dissolve_fields
        param = {'INPUT': mask_, 'FIELDS': fields_to_keep, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:retainfields", param)
        mask_ = algoOutput["OUTPUT"]

        # remove holes smaller maximum hole-size
        if max_hole_size_to_remove > 0:
            param = {'INPUT': mask_, 'MIN_AREA': max_hole_size_to_remove, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:deleteholes", param)
            mask_ = algoOutput["OUTPUT"]

        if return_single_parts:
            param = {'INPUT': mask_, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:multiparttosingleparts", param)
            mask_ = algoOutput["OUTPUT"]

        if min_width > 0:
            # add unique tmp. id
            param = {'INPUT': mask_, 'FIELD_NAME': 'tmp_id', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                     'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:fieldcalculator", param)
            mask_ = algoOutput["OUTPUT"]

            # shrink mask / negative buffering ...
            param = {
                'INPUT': mask_,
                'DISTANCE': -(min_width / 2),  # ... with min. width / 2
                'SEGMENTS': 5,
                'END_CAP_STYLE': 0,
                'JOIN_STYLE': 0,
                'MITER_LIMIT': 2,
                'DISSOLVE': False,
                'SEPARATE_DISJOINT': False,
                'OUTPUT': 'TEMPORARY_OUTPUT'
            }
            algoOutput = processing.run("native:buffer", param)
            mask_shrunk = algoOutput["OUTPUT"]

            # reduce shrunk mask to actual surfaces
            param = {'INPUT': mask_shrunk, 'EXPRESSION': '$area > 0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            mask_shrunk = algoOutput["OUTPUT"]

            # list of tmp_id of (multi-)polygons having min. width
            tmp_id_with_min_width = [f['tmp_id'] for f in mask_shrunk.getFeatures()]

            # select (multi-)polygons with min. width
            expr = '"tmp_id" IN (' + ', '.join(map(str, tmp_id_with_min_width)) + ')'
            param = {'INPUT': mask_, 'EXPRESSION': expr, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            mask_ = algoOutput["OUTPUT"]

            # drop attribute tmp_id
            param = {'INPUT': mask_, 'COLUMN': ['tmp_id'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:deletecolumn", param)
            mask_ = algoOutput["OUTPUT"]

        # select (multi-)polygons with min. area size
        if min_area == 0:
            expr = '$area > 0'
        else:
            expr = '$area >= ' + str(min_area)
        param = {'INPUT': mask_, 'EXPRESSION': expr, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        mask_ = algoOutput["OUTPUT"]

        # overwrite fid with unique values ...
        # ... in order export all (multi-)polygons properly without complains and not just the 1st one
        param = {
            'INPUT': mask_,
            'FIELD_NAME': 'fid',
            'FIELD_TYPE': 1,
            'FIELD_LENGTH': 0,
            'FIELD_PRECISION': 0,
            'FORMULA': '@row_number + 1',  # add 1 --> start with 1 instead of 0
            'OUTPUT': output
        }
        algoOutput = processing.run("native:fieldcalculator", param)
        mask_ = algoOutput["OUTPUT"]

        # finished
        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" %
                          str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: mask_}

    # --- Algorithm ID, Name

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk prepare mask'

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
        return '0 TBk preprocessing tools'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'preproc'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Processes a geometry set including at least one geometry having a surface to a ready to use (muti-)polygon layer as mask input for <b><i>TBk</i></b>’s preprocessing algorithm <b><i>TBk prepare VHM (and MG)</i></b> resp. as perimeter input for <b><i>TBk</i></b>’s main algorithm <b><i>Generate BK</i></b>.</p></body></html></p>

<h2>Input parameters</h2>
<h3>Input mask</h3>
<p>Geometry set including one or more geometries having surfaces. Geometry types <i>polygon</i>, <i>mutipolygon</i>, <i>surface</i>, <i>mulitsurface</i> and <i>geometrycollection</i> are applicable. Commonly, <i>.gbd</i> do not work as input. Best practice is to save a layer of interest located in a <i>.gbd</i> as <i>.gpkg</i> and then to use that as input.</p>

<h2>Advanced parameters</h2>
<h3>Dissolve geometries</h3>
<p>Check box: default True.</p>
<h3>Dissolve field(s)</h3>
<p>Optional list of strings / attribute names of input, which causes dissolving of features belonging to the same class. Only applied if <i>Dissolve geometries</i> is True / checked.</p>
<h3>Replacement of attribute name fid, if fid is among dissolve field(s)</h3>
<p>string: default <i>fid_original</i></p>
<h3>Return single-part geometries (no multi-polygons)</h3>
<p>Check box: default True.</p>
<h3>Minimum area of returned (multi-)polygons</h3>
<p>integer / [m&sup2;]: default 100m&sup2;. If set to 0 no (multi-)polygons with actual surfaces get dropped.</p>
<h3>Maximum area of holes to be removed within returned (multi-)polygons</h3>
<p>integer / [m&sup2;]: default 10m&sup2;. If set to 0 no holes get removed / filled.</p>
<h3>Minimum width of returned (multi-)polygons</h3>
<p>integer / [m]: default 10m. If set to 0 no dropping of (multi-)polygons due to minimum width.</p>

<h2>Outputs</h2>
<h3>Proecessed mask</h3>
<p>Geometry set consisting only of geometry types <i>polygon</i> and/or <i>mutipolygon</i> and dimensions X and Y, meaning that Z and M dimensions are not inherited from the input. Each returned geometry is associated with newly created unique <i>fid</i>. If <i>Dissolve geometries</i> is applied and attributes are selected as <i>Dissolve field(s)</i> these attributes are returned additionally to the <i>fid</i>. If the input’s <i>fid</i> is among the selected <i>Dissolve field(s)</i>, it is return as attribute named accordingly to the advanced parameter <i>Replacement of attribute name fid</i>. Any other attribute is dropped.

<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm author: Attilio Benini, @ BFH-HAFL (2025)</p></body></html>"""

    def createInstance(self):
        return TBkPrepareMaskAlgorithm()