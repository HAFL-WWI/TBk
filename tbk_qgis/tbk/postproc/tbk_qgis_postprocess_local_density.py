# -*- coding: utf-8 -*-
# *************************************************************************** #
# Determine local density zones in forest stands based on a canopy cover layer (DG).
#
# Authors: Attilio Benini, Alexandra Erbach, Hannes Horneber (BFH-HAFL)
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
import math

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterMatrix,
                       QgsProcessingException,
                       QgsProcessingParameterString,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsApplication)
import processing

from tbk_qgis.tbk.utility.tbk_utilities import *


class TBkPostprocessLocalDensity(QgsProcessingAlgorithm):

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # Directory containing the input files
    PATH_TBk_INPUT = "path_tbk_input"

    OUTPUT = "OUTPUT"

    # Use forest mixture degree / coniferous raster to calculate density zone mean?
    MG_USE = "mg_use"

    # Forest mixture degree / coniferous raster to calculate density zone mean
    MG_INPUT = "mg_input"

    # advanced parameters

    # TBk input file name (string)
    TBK_INPUT_FILE = "tbk_input_file"
    # suffix for output files (string)
    OUTPUT_SUFFIX = "output_suffix"
    # input table for local density classes (matrix as one-dimensional list)
    TABLE_DENSITY_CLASSES = "table_density_classes"
    # determine whether DG is calculated for all layers (KS, US, MS, OS, UEB) (boolean)
    CALC_ALL_DG = "calc_all_dg"
    # minimum size for dense/sparse "clumps" (m^2)
    MIN_SIZE_CLUMP = "min_size_clump"
    # minimum size for stands to apply calculation of local densities (m^2)
    MIN_SIZE_STAND = "min_size_stand"
    # threshold for minimal holes within local density polygons (m^2)
    HOLES_THRESH = "holes_thresh"
    # method to remove thin parts and details of zones by minus / plus buffering (boolean)
    BUFFER_SMOOTHING = "buffer_smoothing"
    # buffer distance of buffer smoothing (m)
    BUFFER_SMOOTHING_DIST = "buffer_smoothing_dist"
    # save unclipped local densities as layer / .gpkg  (boolean)
    SAVE_UNCLIPPED = "save_unclipped"
    # grid cell size for grouping stands (km)
    GRID_CELL_SIZE = "grid_cell_size"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Folder for algo input/output
        self.addParameter(
            QgsProcessingParameterFile(
                self.PATH_TBk_INPUT,
                self.tr("Folder with TBk results"),
                behavior=QgsProcessingParameterFile.Folder,
                fileFilter='All Folders (*.*)',
                defaultValue=None
            )
        )

        # Use forest mixture degree / coniferous raster to calculate density zone mean?
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.MG_USE,
                self.tr("Use forest mixture degree (coniferous raster)?"),
                defaultValue=True
            )
        )

        # Forest mixture degree / coniferous raster to calculate density zone mean
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.MG_INPUT,
                self.tr("Forest mixture degree (coniferous raster) 10m input (.tif)"),
                optional=True
            )
        )

        # TBk input file name (string)
        parameter = QgsProcessingParameterString(
            self.TBK_INPUT_FILE,
            self.tr("Name of TBk-map-file (.gpkg) included in folder with TBk results"),
            defaultValue='TBk_Bestandeskarte.gpkg'  # output of Generate TBk
        )
        self.addAdvancedParameter(parameter)

        # suffix for output files (string)
        parameter = QgsProcessingParameterString(
            self.OUTPUT_SUFFIX,
            self.tr(
                "Suffix added to names of output files (.gpkg)"
                "\n(different suffixes prevent overwriting)"
            ),
            optional=True
        )
        self.addAdvancedParameter(parameter)

        # input table for local density classes (matrix as one-dimensional list)
        parameter = QgsProcessingParameterMatrix(
            self.TABLE_DENSITY_CLASSES,
            self.tr(
                "Table to define classes of local densities"
                "\nclass: unique class name"
                "\nmin DG [%]: minimal percentage of degree of cover"
                "\nmin DG [%]: maximal percentage of degree of cover"
                "\nradius of circular moving window applied on the degree of cover raster [m]"
            ),
            hasFixedNumberRows=False,
            headers=['class', 'min DG [%]', 'max DG [%]', 'radius of circular moving window [m]'],
            defaultValue=[
                1, 85, 100, 7,
                2, 60, 85, 14,
                3, 40, 60, 14,
                4, 25, 40, 14,
                5, 0, 25, 7,
                12, 60, 100, 14
            ]
        )
        self.addAdvancedParameter(parameter)

        # determine whether DG is calculated for all layers (KS, US, MS, OS, UEB) (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.CALC_ALL_DG,
            self.tr("Calculate mean with zonal statistics for all DG layers (KS, US, MS, OS, UEB)"),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # minimum size for dense/sparse "clumps" (m^2)
        parameter = QgsProcessingParameterNumber(
            self.MIN_SIZE_CLUMP,
            self.tr("Minimum size for 'clumps' of local densities (m^2)"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=1200
        )
        self.addAdvancedParameter(parameter)

        # minimum size for stands to apply calculation of local densities (m^2)
        parameter = QgsProcessingParameterNumber(
            self.MIN_SIZE_STAND,
            self.tr("Minimum size for stands to apply calculation of local densities (m^2)"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=1200
        )
        self.addAdvancedParameter(parameter)

        # threshold for minimal holes within local density polygons (m^2)
        parameter = QgsProcessingParameterNumber(
            self.HOLES_THRESH,
            self.tr("Threshold for minimal holes within local density polygons (m^2)"),
            type=QgsProcessingParameterNumber.Integer,
            defaultValue=400
        )
        self.addAdvancedParameter(parameter)

        # method to remove thin parts and details of zones by minus / plus buffering (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.BUFFER_SMOOTHING,
            self.tr(
                "Remove thin parts and details of density zones by minus / plus buffering."
                "\nIf unchecked, no buffer smoothing is applied."
            ),
            defaultValue=True
        )
        self.addAdvancedParameter(parameter)

        # buffer distance of buffer smoothing (m)
        parameter = QgsProcessingParameterNumber(
            self.BUFFER_SMOOTHING_DIST,
            self.tr(
                "Buffer distance of buffer smoothing (m)."
                "\nIf set to 0, no buffer smoothing is applied."
            ),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=7
        )
        parameter.setMetadata({'widget_wrapper': {'decimals': 2}})
        self.addAdvancedParameter(parameter)

        # save unclipped local densities as layer / .gpkg  (boolean)
        parameter = QgsProcessingParameterBoolean(
            self.SAVE_UNCLIPPED,
            self.tr("Save unclipped local densities as layer / .gpkg (having suffix '_unclipped') "),
            defaultValue=False
        )
        self.addAdvancedParameter(parameter)

        # grid cell size for grouping stands (km)
        parameter = QgsProcessingParameterNumber(
            self.GRID_CELL_SIZE,
            self.tr(
                "Grid cell size for grouping stands by their x_min & y_min overlapping (km)."
                "\n(used for iterative intersection of stands and local densities)"
            ),
            type=QgsProcessingParameterNumber.Double,
            defaultValue=3
        )
        parameter.setMetadata({'widget_wrapper': {'decimals': 3}})
        self.addAdvancedParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        path_tbk_input = self.parameterAsString(parameters, self.PATH_TBk_INPUT, context)
        path_output = os.path.join(path_tbk_input, "local_densities")
        ensure_dir(path_output)

        # boolean input: Use forest mixture degree / coniferous raster to calculate density zone mean?
        mg_use = self.parameterAsBool(parameters, self.MG_USE, context)

        # raster input: forest mixture degree / coniferous raster to calculate density zone mean
        if mg_use:
            try:
                mg_input = str(self.parameterAsRasterLayer(parameters, self.MG_INPUT, context).source())
                if not os.path.splitext(mg_input)[1].lower() in (".tif", ".tiff"):
                    raise QgsProcessingException("mg_input must be TIFF file")
            except:
                raise QgsProcessingException(
                    'if "Use forest mixture degree / coniferous raster" is True, mg_input must be TIFF file')

        # TBk input file name (string)
        tbk_input_file = self.parameterAsString(parameters, self.TBK_INPUT_FILE, context)

        # suffix for output files (string)
        output_suffix = self.parameterAsString(parameters, self.OUTPUT_SUFFIX, context)

        # input table for local density classes (matrix as one-dimensional list)
        table_density_classes = self.parameterAsMatrix(parameters, self.TABLE_DENSITY_CLASSES, context)
        if len(table_density_classes) % 4 != 0:
            raise QgsProcessingException("Invalid value for table_density_classes: list must contain a multiple of 4 elements.")
        # nuber of density classes
        n_cl = int(len(table_density_classes) / 4)

        # gather and check names of density classes
        cl_names = []
        for i in range(n_cl):
            cl_i = str(table_density_classes[i * 4])
            if cl_i == '':
                raise QgsProcessingException('Empty string ("") among names of DG-density-classes. Only strings with length >= 1 are valid names.')
            else:
                cl_i = cl_i.replace(' ', '_')
                if cl_i in cl_names:
                    raise QgsProcessingException('"' + cl_i + '" is a duplicate among the names of DG-density-classes. Valid names must be unique. Note that under the hood " " is replaced by "_".')
                else:
                    cl_names.append(cl_i)

        # function to check whether string is a number
        def is_number(x):
            try:
                float(x)
                return True
            except ValueError:
                return False

        # gather and check min-values of density classes
        cl_min = []
        for i in range(n_cl):
            min_i = str(table_density_classes[i * 4 + 1])
            if is_number(min_i):
                min_i = float(min_i)
                if min_i < 0 or min_i >= 100:
                    raise QgsProcessingException('The min of DG-class "' + cl_names[i] + '" is set to ' + str(min_i) + ', which is outside of the range valid: 0 >= min < 100.')
                else:
                    cl_min.append(float(min_i))
            else:
                raise QgsProcessingException('The min of DG-class "' + cl_names[i] + '" is set to "' + str(min_i) + '". But it must be a number (0 >= min < 100).')

        # gather and check max-values of density classes
        cl_max = []
        for i in range(n_cl):
            max_i = str(table_density_classes[i * 4 + 2])
            if is_number(max_i):
                max_i = float(max_i)
                if max_i <= 0 or max_i > 100:
                    raise QgsProcessingException('The max of DG-class "' + cl_names[i] + '" is set to ' + str(max_i) + ', which is outside of the range valid: 0 > max =< 100.')
                else:
                    cl_max.append(float(max_i))
            else:
                raise QgsProcessingException('The max of DG-class "' + cl_names[i] + '" is set to "' + str(max_i) + '". But it must be a number (0 >= max < 100).')

        # check whether min-value < max-value of density classes
        for i in range(n_cl):
            if cl_min[i] >= cl_max[i]:
                raise QgsProcessingException('The min and max of DG-class "' + cl_names[i] + '" are set to ' + str(cl_min[i]) + ' resp. to ' + str(cl_max[i]) + '. But min < max must be true.')

        # gather and check values for radii of moving windows
        cl_radius = []
        for i in range(n_cl):
            radius_i = str(table_density_classes[i * 4 + 3])
            if is_number(radius_i):
                radius_i = float(radius_i)
                if radius_i <= 0:
                    raise QgsProcessingException('The radius of circular moving window for DG-class "' + cl_names[i] + '" is set to ' + str(radius_i) + '. But it must be a positive number [m].')
                else:
                    cl_radius.append(float(radius_i))
            else:
                raise QgsProcessingException('The radius of circular moving window for DG-class "' + cl_names[i] + '" is set to "' + str(radius_i) + '". But it must be a positive number [m].')

        # determine whether DG is calculated for all layers (KS, US, MS, OS, UEB) (boolean)
        calc_all_dg = self.parameterAsBool(parameters, self.CALC_ALL_DG, context)

        # minimum size for dense/sparse "clumps" (m^2)
        min_size_clump = self.parameterAsInt(parameters, self.MIN_SIZE_CLUMP, context)

        # minimum size for stands to apply calculation of local densities (m^2)
        min_size_stand = self.parameterAsInt(parameters, self.MIN_SIZE_STAND, context)

        # threshold for minimal holes within local density polygons (m^2)
        holes_thresh = self.parameterAsInt(parameters, self.HOLES_THRESH, context)

        # method to remove thin parts and details of zones by minus / plus buffering (boolean)
        buffer_smoothing = self.parameterAsBool(parameters, self.BUFFER_SMOOTHING, context)

        # buffer distance of buffer smoothing (m)
        buffer_smoothing_dist = self.parameterAsDouble(parameters, self.BUFFER_SMOOTHING_DIST, context)

        # save unclipped local densities as layer / .gpkg  (boolean)
        save_unclipped = self.parameterAsBool(parameters, self.SAVE_UNCLIPPED, context)

        # grid cell size for grouping stands (km)
        grid_cell_size = self.parameterAsDouble(parameters, self.GRID_CELL_SIZE, context)

        start_time = time.time()

        # lump together density classes
        den_classes = []
        for i in range(n_cl):
            den_classes.append(
                {
                    "class": cl_names[i],    # string / as is
                    "min": cl_min[i] / 100,  # [0%, 100%] --> [0, 1]
                    "max": cl_max[i] / 100,  # [0%, 100%] --> [0, 1]
                    "radius": cl_radius[i]   # > 0 [m] / as is
                }
            )
        # for i in den_classes: print(i)

        path_dg = os.path.join(path_tbk_input, "dg_layers/dg_layer.tif")

        path_dg_ks = os.path.join(path_tbk_input, "dg_layers/dg_layer_ks.tif")
        path_dg_us = os.path.join(path_tbk_input, "dg_layers/dg_layer_us.tif")
        path_dg_ms = os.path.join(path_tbk_input, "dg_layers/dg_layer_ms.tif")
        path_dg_os = os.path.join(path_tbk_input, "dg_layers/dg_layer_os.tif")
        path_dg_ueb = os.path.join(path_tbk_input, "dg_layers/dg_layer_ueb.tif")

        path_stands = os.path.join(path_tbk_input, tbk_input_file)

        stands_all = QgsVectorLayer(path_stands, 'Stands', 'ogr')
        # add fid (--> fid_stand) as unique identifier for later joins to original stands
        param = {'INPUT': stands_all, 'FIELD_NAME': 'fid_stand', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 10,
                 'FIELD_PRECISION': 0, 'FORMULA': ' "fid" ', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        stands_all = algoOutput["OUTPUT"]

        # load dg raster "DG" (Hauptschicht = hs = DG_OS + DG_UEB)
        dg = QgsRasterLayer(path_dg)

        res_dg = dg.rasterUnitsPerPixelY()

        # load other DG rasters (needed only to determine DGs per zone)
        if calc_all_dg:
            dg_ks = QgsRasterLayer(path_dg_ks)
            dg_us = QgsRasterLayer(path_dg_us)
            dg_ms = QgsRasterLayer(path_dg_ms)
            dg_os = QgsRasterLayer(path_dg_os)
            dg_ueb = QgsRasterLayer(path_dg_ueb)

        # helper functions (start with f_)

        # helper function to save intermediate vector data & tables
        def f_save_as_gpkg(input, name, path=path_output):
            # if type(input) == str:
            #    input = QgsVectorLayer(input, '', 'ogr')
            path_ = os.path.join(path, name + ".gpkg")
            ctc = QgsProject.instance().transformContext()
            QgsVectorFileWriter.writeAsVectorFormatV3(input, path_, ctc, getVectorSaveOptions('GPKG', 'utf-8'))

        # select stands with min. area size
        feedback.pushInfo("select stands with area > " + str(min_size_stand) + "m^2 ...")
        param = {'INPUT': stands_all, 'EXPRESSION': '$area > ' + str(min_size_stand), 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        stands = algoOutput["OUTPUT"]

        # reduce attributes
        col_names = ['fid_stand', 'ID', 'DG']
        if calc_all_dg:
            col_names_rest = ['DG_ks', 'DG_us', 'DG_ms', 'DG_os', 'DG_ueb', 'NH', 'hdom']
        else:
            col_names_rest = ['NH', 'hdom']
        col_names[len(col_names):] = col_names_rest
        if not mg_use:
            col_names.remove('NH')
        param = {'INPUT': stands, 'FIELDS': col_names, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:retainfields", param)
        stands = algoOutput["OUTPUT"]

        # suffix attribute columns with _stand
        for col in col_names[1:]:  # 1st of col_names = fid_stand = tmp. id is not suffixed a 2nd time!
            param = {'INPUT': stands, 'FIELD': col, 'NEW_NAME': col + '_stand', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:renametablefield", param)
            stands = algoOutput["OUTPUT"]

        # recalculate stand area
        param = {'INPUT': stands, 'FIELD_NAME': 'area_stand', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 10, 'FIELD_PRECISION': 0,
                 'FORMULA': 'round($area)', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        stands = algoOutput["OUTPUT"]

        # check attributes of selected stands
        # print("attributes of selected stands:")
        # for field in stands.fields(): print(field.name(), field.typeName())

        # add neighbour size for circular mowing window (must be odd)
        def get_size(radius, res = res_dg):
            size = math.floor(radius / res * 2)
            if size % 2 == 0:
                size = size + 1
            return(size)

        for i in den_classes: i["size"] = get_size(i["radius"])
        # for i in den_classes: print(i)

        # for each unique neighbouring size gather corresponding radii in a list
        focal_dg_layers_feedback = {}
        for i in den_classes:
            if not str(i["size"]) in focal_dg_layers_feedback:
                focal_dg_layers_feedback[str(i["size"])] = [i["radius"]]
            else:
                focal_dg_layers_feedback[str(i["size"])].append(i["radius"])

        # make feedback messages with specific information for each unique neighbouring size
        for i in focal_dg_layers_feedback:
            all_radii = sorted(list(set(focal_dg_layers_feedback[i])))
            all_radii = [str(r) + 'm' for r in all_radii]
            if (len(all_radii) == 1):
                text_radii = "radius " + all_radii[0]
            else:
                text_radii = "radii " + ', '.join(all_radii[:-1]) + " and " + all_radii[-1]
            focal_dg_layers_feedback[i] = (
                    "apply to dg_layer raster layer (degree of cover) focal statistic " +
                    "with circular moving window having neighbour size " +
                    str(i) +
                    " which corresponds to " +
                    text_radii +
                    " ..."
            )

        # dict for focal layers (for each unique neighbour size one layer)
        focal_dg_layers = {}
        for i in den_classes:
            if not str(i["size"]) in focal_dg_layers:
                feedback.pushInfo(focal_dg_layers_feedback[str(i["size"])])
                param = {'input': dg, 'selection': dg, 'method': 0, 'size': i["size"], 'gauss': None, 'quantile': '',
                         '-c': True, '-a': False, 'weight': '', 'output': 'TEMPORARY_OUTPUT', 'GRASS_REGION_PARAMETER': None,
                         'GRASS_REGION_CELLSIZE_PARAMETER': 0, 'GRASS_RASTER_FORMAT_OPT': '', 'GRASS_RASTER_FORMAT_META': ''}
                algoOutput = processing.run("grass7:r.neighbors", param)
                focal_dg_layers[str(i["size"])] = QgsRasterLayer(algoOutput["output"])
        # check
        # for i in focal_dg_layers:
        #     print(i)
        #     param = {'INPUT': focal_dg_layers[str(i)], 'BAND': None}
        #     res_i = processing.run("native:rasterlayerproperties", param)['PIXEL_HEIGHT']
        #     print(res_i)

        # list to gather polygons of oll density classes
        den_polys = []

        for cl in den_classes:
            feedback.pushInfo("polyognize local densities of class " + str(cl["class"]) + " ...")
            # input / parameters for a certain density class
            min = str(cl["min"] - 0.0001)
            max = str(cl["max"] + 0.0001)
            cl_ = str(cl["class"])
            focal_in_use = focal_dg_layers[str(cl["size"])]

            # stats of used focal layer
            focal_stats = focal_in_use.dataProvider().bandStatistics(1, QgsRasterBandStats.All)
            focal_min = focal_stats.minimumValue
            focal_max = focal_stats.maximumValue
            # if range of density class does not overlap with range of values of focal layer continue with next class
            if float(max) <= focal_min or float(min) >= focal_max:
                continue

            # reclassify raster: 1 = within density range, else or no data
            param = {'INPUT_RASTER': focal_in_use, 'RASTER_BAND': 1, 'TABLE': [min, max, '1'], 'NO_DATA': 0,
                     'RANGE_BOUNDARIES': 0, 'NODATA_FOR_MISSING': True, 'DATA_TYPE': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:reclassifybytable", param)
            recl = algoOutput["OUTPUT"]

            # polygonize
            param = {'INPUT': recl, 'BAND': 1, 'FIELD': 'DN', 'EIGHT_CONNECTEDNESS': False, 'EXTRA': '',
                     'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("gdal:polygonize", param)
            polys_cl = algoOutput["OUTPUT"]
            # f_save_as_gpkg(polys_cl, "0_class_" + cl_)

            # add density class as attribute
            param = {'INPUT': polys_cl, 'FIELD_NAME': 'class', 'FIELD_TYPE': 2, 'FIELD_LENGTH': 0,
                     'FIELD_PRECISION': 0, 'FORMULA': "to_string( '" + cl_ + "' )", 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:fieldcalculator", param)
            polys_cl = algoOutput["OUTPUT"]
            # f_save_as_gpkg(polys_cl, "3_class_" + cl_)

            den_polys.append(polys_cl)

        # merge listed layers with density polygons of different classes
        feedback.pushInfo("merge local densities of all classes ...")
        param = {'LAYERS': den_polys, 'CRS': None, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:mergevectorlayers", param)
        den_polys = algoOutput["OUTPUT"]

        # overwrite fid of merged density polygons with unique values ...
        param ={'INPUT': den_polys, 'FIELD_NAME': 'fid', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_polygonized") # ... in order make them exportable without complain and not ...
                                                             # ... just those features inherited form the 1st element of above merged list

        # remove holes smaller than threshold
        if holes_thresh > 0:
            feedback.pushInfo("remove holes < " + str(holes_thresh) + "m^2 ...")
            param = {'INPUT': den_polys, 'MIN_AREA': holes_thresh, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:deleteholes", param)
            den_polys = algoOutput["OUTPUT"]
            # f_save_as_gpkg(den_polys, "den_polys_without_holes")

        # apply buffer smoothing if ...
        if buffer_smoothing and buffer_smoothing_dist != 0:
            feedback.pushInfo(
                'remove thin parts / “buffer smoothing" (buffer dist. = ' +
                str(round(buffer_smoothing_dist ,2)) +
                "m) ..."
            )
            param = {'INPUT': den_polys, 'DISTANCE': -buffer_smoothing_dist, 'SEGMENTS': 5, 'END_CAP_STYLE': 0,
                     'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'DISSOLVE': False, 'SEPARATE_DISJOINT': False,
                     'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:buffer", param)
            den_polys = algoOutput["OUTPUT"]
            # f_save_as_gpkg(den_polys, "den_polys_minus_buffered")
            param = {'INPUT': den_polys, 'DISTANCE': buffer_smoothing_dist + 1.5, 'SEGMENTS': 5, 'END_CAP_STYLE': 0,
                     'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'DISSOLVE': False, 'SEPARATE_DISJOINT': False,
                     'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:buffer", param)
            den_polys = algoOutput["OUTPUT"]
            # f_save_as_gpkg(den_polys, "den_polys_plus_buffered")

        feedback.pushInfo("fix geometries of local densities and selected stands ...")
        param = {'INPUT': den_polys, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fixgeometries", param)
        den_polys = algoOutput["OUTPUT"]
        param = {'INPUT': stands, 'METHOD': 1, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fixgeometries", param)
        stands = algoOutput["OUTPUT"]

        # drop local densities having zero area
        param = {'INPUT': den_polys, 'EXPRESSION': '$area > 0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        den_polys = algoOutput["OUTPUT"]

        # drop attributes DN (added by gdal:polygonize), layer & path (added by native:mergevectorlayers)
        param = {'INPUT': den_polys, 'COLUMN': ['DN', 'layer', 'path'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:deletecolumn", param)
        den_polys = algoOutput["OUTPUT"]

        if save_unclipped:
            feedback.pushInfo("save output: TBk_local_densities_unclipped" + output_suffix + ".gpkg ...")
            # save local densities output
            path_local_den_unclipped_out = os.path.join(path_output, "TBk_local_densities_unclipped" + output_suffix + ".gpkg")
            ctc = QgsProject.instance().transformContext()
            QgsVectorFileWriter.writeAsVectorFormatV3(den_polys, path_local_den_unclipped_out, ctc,
                                                      getVectorSaveOptions('GPKG', 'utf-8'))

        # drop local densities geometries having areas below min. area --> reduce workload for later intersection with stands
        feedback.pushInfo("before intersection: filter out local densities with area < " + str(min_size_clump) + "m^2 ...")
        # print("N of local densities geometries before filtering with min. area: " + str(len(den_polys)))
        param = {'INPUT': den_polys, 'EXPRESSION': '$area > ' + str(min_size_clump), 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        den_polys = algoOutput["OUTPUT"]
        # print("N of local densities geometries after filtering with min. area: " + str(len(den_polys)))
        # f_save_as_gpkg(den_polys, "den_polys_larger_before_intersection")

        feedback.pushInfo("intersection of local densities and selected stands ...")
        # check attribute of selected stands
        # for field in stands.fields(): print(field.name(), field.typeName())
        # list all fields of selected stands (fid is not included!)
        stands_fields = []
        for field in stands.fields():
            stands_fields.append(field.name())
        # print(stands_fields)

        # group selected stands by x_min & y_min intersecting with grid cells (attribute group is not exported)
        grid_width = grid_cell_size * 1000  # [km] --> [m]
        formular = ("concat( ceil(  x_min( $geometry ) / " + str(grid_width) +
                    "), '_', ceil(  y_min( $geometry ) / " + str(grid_width) + "))")
        # print(formular)
        param = {'INPUT': stands, 'FIELD_NAME': 'group', 'FIELD_TYPE': 2, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                 'FORMULA': formular, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        stands = algoOutput["OUTPUT"]
        # f_save_as_gpkg(stands, "stands_grouped")

        # creat spatial index for selected stands
        processing.run("native:createspatialindex", {'INPUT': stands})
        # creat spatial index for local densities
        processing.run("native:createspatialindex", {'INPUT': den_polys})

        # list unique group names
        group_index = stands.fields().indexFromName("group")
        group_unique = list(stands.uniqueValues(group_index))

        # list of placeholders to later insert groupwise intersections of stands & local densities
        l = [None] * len(group_unique)

        # iterate over unique stand groups
        for i in range(len(l)):
            # extract from selected stands those belong to the i-th group
            expression = ' "group"  =  ' + "'" + group_unique[i] + "'"
            # print(expression)
            param = {'INPUT': stands, 'EXPRESSION': expression, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            stands_g = algoOutput["OUTPUT"]
            # print("N stands: " + str(len(stands_g)))

            # make rectangle polygon = extent of stands belonging to the i-th group
            param = {'INPUT': stands_g, 'ROUND_TO': 0, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:polygonfromlayerextent", param)
            rect_g = algoOutput["OUTPUT"]

            # extract local densities overlapping with rectangle (a single & simple polygon / geometry)
            param = {'INPUT': den_polys, 'PREDICATE': [0], 'INTERSECT': rect_g, 'OUTPUT': 'TEMPORARY_OUTPUT'} # 'PREDICATE': [0] --> intersect
            algoOutput = processing.run("native:extractbylocation", param)
            den_polys_g = algoOutput["OUTPUT"]
            # print("N local densities: " + str(len(den_polys_g)))

            # if there aren't any overlapping local densities continue with next group
            if len(den_polys_g) == 0:
                continue

            # intersection stands belong to the i-th group & local densities potentially overlapping
            param = {'INPUT': den_polys_g, 'OVERLAY': stands_g, 'INPUT_FIELDS': ['class'], 'OVERLAY_FIELDS': stands_fields,
                     'OVERLAY_FIELDS_PREFIX': '', 'OUTPUT': 'TEMPORARY_OUTPUT', 'GRID_SIZE': None}
            algoOutput = processing.run("native:intersection", param)
            den_polys_g = algoOutput["OUTPUT"]

            # if intersection has returned no geometries continue with next group
            if len(den_polys_g) == 0:
                continue

            # insert returns of intersection into list
            l[i] = den_polys_g

        # remove None values in list
        l = list(filter(lambda item: item is not None, l))

        # merge groupwise intersections of stands & local densities
        param = {'LAYERS': l, 'CRS': None, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:mergevectorlayers", param)
        den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_intersected")

        # drop attribute layer & path (added by native:mergevectorlayers)
        param = {'INPUT': den_polys, 'COLUMN': ['layer', 'path'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:deletecolumn", param)
        den_polys = algoOutput["OUTPUT"]

        # multi parts --> single parts
        feedback.pushInfo("turn local density multi parts into single parts ...")
        param = {'INPUT': den_polys, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:multiparttosingleparts", param)
        den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_sigle_parts")

        # drop local densities polygons having areas below min. area
        feedback.pushInfo("filter out local densities with area < " + str(min_size_clump) + "m^2 ...")
        param = {'INPUT': den_polys, 'EXPRESSION': '$area > ' + str(min_size_clump), 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)
        den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_larger_than_min_area")

        # calculate area of local densities
        feedback.pushInfo("calculate area of local densities and its ratio to area of stand...")
        param = {'INPUT': den_polys, 'FIELD_NAME': 'area', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 10, 'FIELD_PRECISION': 0,
                 'FORMULA': 'round($area)', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        den_polys = algoOutput["OUTPUT"]

        # calculate ratio of area of local density to area of stand
        param = {'INPUT': den_polys, 'FIELD_NAME': 'area_pct', 'FIELD_TYPE': 0, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                 'FORMULA': 'round($area / area_stand, 2)', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        den_polys = algoOutput["OUTPUT"]

        # resample Mishungsgrad / Nadelholzanteil raster to resolution 1m x 1m within extent of Deckungsgrad (= dg = DG)
        # 'RESAMPLING': 0 --> Nearest Neighbour
        feedback.pushInfo("zonal statistic ...")
        if mg_use:
            param = {'INPUT': mg_input, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'RESAMPLING': 0, 'NODATA': None,
                     'TARGET_RESOLUTION': 1, 'OPTIONS': '', 'DATA_TYPE': 0, 'TARGET_EXTENT': dg.extent(),
                     'TARGET_EXTENT_CRS': None, 'MULTITHREADING': False, 'EXTRA': '', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("gdal:warpreproject", param)
            mg = algoOutput["OUTPUT"]

        # zonal statistics
        if calc_all_dg:
            rasters_4_stats = {'DG': dg, 'DG_ks': dg_ks, 'DG_us': dg_us, 'DG_ms': dg_ms, 'DG_os': dg_os, 'DG_ueb': dg_ueb}
        else:
            rasters_4_stats = {'DG': dg}
        if mg_use:
            rasters_4_stats['NH'] = mg

        for raster in rasters_4_stats:
            # actual zonal stats: 'STATISTICS': [2] --> mean
            param = {'INPUT': den_polys, 'INPUT_RASTER': rasters_4_stats[raster], 'RASTER_BAND': 1,
                     'COLUMN_PREFIX': raster + '_', 'STATISTICS': [2], 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:zonalstatisticsfb", param)
            den_polys = algoOutput["OUTPUT"]
            # get rid attribute suffix _mean
            param = {'INPUT': den_polys, 'FIELD': raster + '_mean', 'NEW_NAME': raster, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:renametablefield", param)
            den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_zonal_stats")

        feedback.pushInfo("calculate local density metrics for overlapping stands ...")
        # group stands in original stands map by using the tmp. id of stands (fid_stand) ...
        group_size = 1000 # (max.) number of stands pick from original stands map for an iterative step
        formular = 'ceil("fid_stand" / ' + str(group_size) + ')'
        param = {'INPUT': stands_all, 'FIELD_NAME': 'fid_stand_group', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
               'FIELD_PRECISION': 0, 'FORMULA': formular, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        stands_all = algoOutput["OUTPUT"]
        # f_save_as_gpkg(stands_all, "stands_all_grouped")
        # ... same procedure with the local densities according
        param = {'INPUT': den_polys, 'FIELD_NAME': 'fid_stand_group', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': formular, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        den_polys = algoOutput["OUTPUT"]
        # f_save_as_gpkg(den_polys, "den_polys_grouped")

        # from by now existing attributes of density polygons aggregate a (long) summary table for each combination of
        # density class & stand
        # - fid_stand: tmp. id of each stand allowing later to join to original stand layer
        # - class:     local density class
        # - area:      total area of a class within a stand [m^2]
        # - area_pct:  ratio of total area (s. above) to area of stand [0, 1]
        # - dg:        mean DG of HS (= DG_OS + DG_UEB) of all subsurface of a class with the same stand [0, 100] (%)
        # - nh:        mean NH  of all subsurface of a class with the same stand [0, 100] (%)
        aggregates = [
            {'aggregate': 'first_value', 'delimiter': ',', 'input': '"fid_stand"', 'length': 0, 'name': 'fid_stand',
             'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'aggregate': 'first_value', 'delimiter': ',', 'input': '"class"', 'length': 0, 'name': 'class',
             'precision': 0, 'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'aggregate': 'sum', 'delimiter': ',', 'input': '"area"', 'length': 0, 'name': 'area', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'aggregate': 'first_value', 'delimiter': ',', 'input': 'round(sum(area) / mean(area_stand), 2)',
             'length': 0, 'name': 'area_pct', 'precision': 0, 'sub_type': 0, 'type': 6,
             'type_name': 'double precision'},
            {'aggregate': 'first_value', 'delimiter': ',', 'input': 'round(sum(DG * area) / sum(area) * 100)',
             'length': 0, 'name': 'dg', 'precision': 0, 'sub_type': 0, 'type': 4, 'type_name': 'integer'}
        ]
        if mg_use:
            aggregates.append(
                {'aggregate': 'first_value', 'delimiter': ',', 'input': 'round(sum(NH * area) / sum(area))',
                 'length': 0, 'name': 'nh', 'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'}
            )

        # all density classes
        all_classes = []
        for cl in den_classes:
            all_classes.append(str(cl["class"]))
        # all value types included in stats on local densities (s. long table above)
        value_types = ['area', 'area_pct', 'dg']
        if mg_use:
            value_types.append('nh')
        # list of new fields for stats on local densities
        new_fields = []
        for cl in all_classes:
            for v in value_types:
                new_fields.append("z" + cl + "_" + v)
        # define new fields / attributes for stands layers generated in below loop
        new_attributes = []
        for i in new_fields:
            if i[-8:] == "area_pct":
                new_attributes.append(QgsField(i, QVariant.Double))
            else:
                new_attributes.append(QgsField(i, QVariant.Int))

        # get unique values from tmp. group id (fid_stand_group) add to original stand map
        fid_stand_group_index = stands_all.fields().indexFromName("fid_stand_group")
        fid_stand_group_index_unique = list(stands_all.uniqueValues(fid_stand_group_index))

        # list of placeholders to later insert groupwise modifications of original stand map
        l_stands_all = [None] * len(fid_stand_group_index_unique)
        # print(len(l_stands_all))

        # groupwise calculation of local density metrics
        for gr in range(len(l_stands_all)):
            # extract geometries belonging to the i-th group ...
            expression = ' "fid_stand_group"  =  ' + str(fid_stand_group_index_unique[gr])
            # print(expression)
            # ... from original stand map
            param = {'INPUT': stands_all, 'EXPRESSION': expression, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            stands_all_g = algoOutput["OUTPUT"]
            # print("N stands: " + str(len(stands_all_g)))
            # ... from local densities
            param = {'INPUT': den_polys, 'EXPRESSION': expression, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            den_polys_g = algoOutput["OUTPUT"]
            # print("N local densities: " + str(len(den_polys_g)))

            # if there are any local densities overlapping with the i-th group of stands ...
            if len(den_polys_g) > 0:
                # 1) table (long format) for each combination of stand and local density class metrics
                param = {'INPUT': den_polys_g, 'OUTPUT': 'TEMPORARY_OUTPUT'}
                algoOutput = processing.run("native:dropgeometries", param)
                param = {
                    'INPUT': algoOutput["OUTPUT"],
                    'GROUP_BY': 'Array( "fid_stand", "class")',
                    'AGGREGATES': aggregates,
                    'OUTPUT': 'TEMPORARY_OUTPUT'
                }
                algoOutput = processing.run("native:aggregate", param)
                statstable_long_g = algoOutput["OUTPUT"]
                # f_save_as_gpkg(statstable_long_g, "statstable_long_g_" + gr)
                # 2) add new attribute to i-th group of stands
                pr = stands_all_g.dataProvider()
                pr.addAttributes(new_attributes)
                stands_all_g.updateFields()
                # 3) populate new attributes with values from (long) summary table
                for f in statstable_long_g.getFeatures():
                    with edit(stands_all_g):
                        for stand in stands_all_g.getFeatures():
                            if stand["fid_stand"] == f["fid_stand"]:
                                for v in value_types:
                                    stand["z" + f["class"] + "_" + v] = f[v]
                            stands_all_g.updateFeature(stand)

            l_stands_all[gr] = stands_all_g

        # merge the groups of stands with complemented local density metrics to 1 layer
        param = {'LAYERS': l_stands_all, 'CRS': None, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:mergevectorlayers", param)
        stands_all = algoOutput["OUTPUT"]
        # f_save_as_gpkg(stands_all, "stands_all_merged")

        feedback.pushInfo("tidy up attributes of local densities ...")
        # sequence fields of local densities for output. note: tmp. id for stands (= fid_stand) is not part of output!
        field_names = ['class', 'ID_stand', 'area', 'area_stand', 'area_pct']
        for raster in rasters_4_stats:
            field_names.append(raster)
            field_names.append(raster + '_stand')
        field_names.append('hdom_stand')
        # print(field_names)

        # get ID_stand's meta data
        ID_stand_field = den_polys.fields()['ID_stand']
        ID_stand_type = ID_stand_field.type()
        ID_stand_type_name = ID_stand_field.typeName()

        # select fields for local-density-output according sequence created above and prettify zonal-stats-attributes
        fields_mapping = []
        for field in field_names:
            if field == 'class':
                type = int(10)
                type_name = 'text'
                exp = '"class"'  # keep as is
            elif field == 'ID_stand':
                type = ID_stand_type  # inherit data type
                type_name = ID_stand_type_name # inherit data type
                exp = '"ID_stand"'  # keep as is
            elif field == 'area_pct':
                type = int(6)
                type_name = 'double precision'
                exp = '"area_pct"'  # keep as is
            elif field == 'NH':
                type = int(2)
                type_name = 'integer'
                exp = 'round("NH")'  # already %-tage
            elif field != 'NH' and field in rasters_4_stats:
                type = int(2)
                type_name = 'integer'
                exp = 'round("' + field + '" * 100)'  # [0, 1] --> [0, 100]%
            else:
                type = int(2)
                type_name = 'integer'
                exp = '' + '"' + field + '"' + ''  # keep as is
            map = {'alias': '', 'comment': '', 'expression': exp, 'length': 0, 'name': field, 'precision': 0,
                   'sub_type': 0, 'type': type, 'type_name': type_name}
            fields_mapping.append(map)
        param = {'INPUT': den_polys, 'FIELDS_MAPPING': fields_mapping, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:refactorfields", param)
        den_polys = algoOutput["OUTPUT"]

        feedback.pushInfo("save output: TBk_local_densities" + output_suffix + ".gpkg ...")
        # save local densities output
        path_local_den_out = os.path.join(path_output, "TBk_local_densities" + output_suffix + ".gpkg")
        ctc = QgsProject.instance().transformContext()
        QgsVectorFileWriter.writeAsVectorFormatV3(den_polys, path_local_den_out, ctc,
                                                  getVectorSaveOptions('GPKG', 'utf-8'))

        feedback.pushInfo("save output: TBk_Bestandeskarte_local_densities" + output_suffix + ".gpkg ...")
        # tmp. id (= fid_stand) and its derivative (fid_stand_group) are not part of output, same goes to attributes
        # added by native:mergevectorlayers (layer, path)!
        col_to_delete = ['fid_stand', 'fid_stand_group', 'layer', 'path']
        param = {'INPUT': stands_all, 'COLUMN': col_to_delete, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:deletecolumn", param)
        stands_all = algoOutput["OUTPUT"]
        # output original stands + local density stats
        path_stands_out = os.path.join(path_output, "TBk_Bestandeskarte_local_densities" + output_suffix + ".gpkg")
        ctc = QgsProject.instance().transformContext()
        QgsVectorFileWriter.writeAsVectorFormatV3(stands_all, path_stands_out, ctc,
                                                  getVectorSaveOptions('GPKG', 'utf-8'))

        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: path_output}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk postprocess local density'

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

    def shortHelpString(self):
        return """<html><body><p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">Detects within polygons of a TBk stand map zones (polygons), which are defined by specific percentual classes of mean degree of cover. Bevor segregating the zones, a focal statistic algorithm with a circular moving window is applied to the binary degree of cover raster (<i>dg_layer</i> / output of <b><i>Generate BK</i></b>). The radius of moving window can be set individually for each class. Thus, setting percentual ranges and radii defines classes of the local densities. Once polygons representing classes of local densities are derived, holes below a minimal area (default 400m&sup2;) are removed from the polygons. Optionally thin parts of the local density zones are removed by a minus / plus buffering (“buffer smoothing”). Finally local densities polygons within stand having an area below a threshold (default 1200m&sup2;) and having themself an area below another threshold (default also 1200m&sup2;) are filtered out.

Some attributes form overlapping stands are inherited by the local densities. The names of these attributes are suffixed with <i>_stand</i>. Further attributes derive from mean values achieved from zonal statistic applied to serval raster layers belonging either to the input or the output of <b><i>TBk</i></b>’s main algorithm <b><i>Generate BK</i></b>. The coniferous raster is the only input and involving it is optional. The zones’ mean of general degree of cover is calculated in any case, while getting the corresponding values from the degree of cover specific to different height ranges (<i>KS</i>, <i>US</i>, <i>MS</i>, <i>OS</i>, <i>UEB</i>) relative to height of the stand’s dominate trees is optional.

To a copy of the TBk stand map attributes with metrics about each local density class detected within a stand are added.</p></body></html></p>

<h2>Input parameters</h2>
<h3>Folder with TBk results</h3>
<p>Path to folder containing returns of <b><i>TBk</i></b>’s main algorithm <b><i>Generate BK</i></b></p>
<h3>Use forest mixture degree (coniferous raster)</h3>
<p>Check box: if checked (default) zonal statistic is applied to forest mixture degree raster layer.</p>
<h3>Forest mixture degree (coniferous raster) 10m input</h3>
<p>Path to forest mixture degree raster layer. Only required if <b><i>Use forest mixture degree ...</i></b> is checked.</p>

<h2>Advanced parameters</h2>
<h3>Name of TBk-map-file (.gpkg) included in folder with TBk results</h3>
<p>File name of the TBk stand map kept in the <i><b>Folder with TBk results</i></b>. By default <i>TBk_Bestandeskarte.gpkg</i>, which is what <b><i>Generate BK</i></b> returns. The default can be replaced by aternatives like <i>TBk_Bestandeskarte_clean.gpkg</i>.</p>
<h3>Suffix added to names of output files (.gpkg)</h3>
<p>String. When generating multiple versions of local densities based on the same TBk map using different suffixes prevents from overwriting previous results as returns are dropped in same folder (<i><b>local_densities</i></b>, s. below <i><b>Outputs</i></b>).</p>
<h3>Table to define classe of local densities</h3>
<p>Matrix with 4 columns to set 1 or multiple classes. By default 6 classes defined.</p>
<h3>Calculate mean with zonal statistics for all DG layers (KS, US, MS, OS, UEB)</h3>
<p>Check box: if checked (default) zonal statistic is applied to all raster with degree of cover specific to different height ranges (<i>KS</i>, <i>US</i>, <i>MS</i>, <i>OS</i>, <i>UEB</i>) relative to height of the stand’s dominate trees.</p>
<h3>Minimum size for 'clumps' of local densities</h3>
<p>integer / [m&sup2;], default 1200m&sup2;</p>
<h3>Minimum size for stands to apply calculation of local densities</h3>
<p>integer / [m&sup2;], default 1200m&sup2;</p>
<h3>Threshold for minimal holes within local density 'clump'</h3>
<p>integer / [m&sup2;], default 400m&sup2;</p>
<h3>Remove thin parts and details of density zones by minus / plus buffering.</h3>
<p>Check box: if checked (default) "buffer smoothing" applied to polygons of local densities.</p>
<h3>Buffer distance of buffer smoothing</h3>
<p>float / [m], default 7m</p>
<h3>Save unclipped local densities as layer / .gpkg.</h3>
<p>Check box: if checked unclipped geometries of local density classes are saved as layer / .gpkg having suffix <i>_unclipped</i>.</p>
<h3>Grid cell size for grouping stands by their x_min & y_min overlapping</h3>
<p>float / [km], default 3km --> 9km&sup2; square cells. This input is used for groupwise / iterative intersection of stands and local densities, thus tackling the run time of intersection exponentially increasing with number of geometries. This parameter is experimental as the optimal cell size is unknown at the time.</p> 

<h2>Outputs</h2>
<h3>local_densities</h3>
<p>A folder placed within the <i><b>Folder with TBk results</i></b> (s. <i><b>Inputs</i></b> above) containing two files:

- <i>TBk_local_densities.gpkg</i>* holding a same named layer with polygons of all density classes.

- <i>TBk_local_densities_unclipped.gpkg</i>* holding a same named layer with polygons of all unclipped density classes (optional s. advanced parameter <i><b>Save unclipped ... </i></b>).

- <i>TBk_Bestandeskarte_local_densities.gpkg</i>* holding a same named layer being a copy of the input TBk stand map having additional attributes with metrics about each local density class detected within the stands.

* Note that the advanced parameter <i><b>Suffix added to ...</i></b> allows to suffix file names.</p>
<p><!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
</style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:8.3pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html></p><br><p align="right">Algorithm author: Attilio Benini @ BFH-HAFL (2024)</p></body></html>"""

    def createInstance(self):
        return TBkPostprocessLocalDensity()
