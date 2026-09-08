# *************************************************************************** #
# Postprocessing: Clip stand shapefile to exact perimeter and fill gaps.
#
# Authors: Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
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
import logging
import os
import processing
from qgis.core import QgsVectorLayer, QgsProject, QgsVectorFileWriter, QgsProcessingUtils, edit
from tbk_qgis.tbk.general.tbk_utilities import delete_shapefile, delete_geopackage, getVectorSaveOptions, delete_fields

# Substep narration only (file/console at DEBUG); joins the "Clip to perimeter and eliminate
# gaps" logger stream set up by tool_clip_and_patch.py, the only caller of these functions.
log = logging.getLogger('Clip to perimeter and eliminate gaps')


def clip_to_perimeter(working_root,
                      input_to_clip_path,
                      tmp_output_folder,
                      perimeter,
                      del_tmp=True,
                      context=None,
                      feedback=None):
    log.debug("--------------------------------------------")
    log.debug("START Clip to perimeter...")

    # Clip stand and convert to singlepart
    tmp_stands_clipped_path = os.path.join(tmp_output_folder, "stands_clip_tmp.gpkg")
    clipped = clip_vector_layer(input_to_clip_path, perimeter, context=context, feedback=feedback)
    # context isn't shared in this alg call so that subsequent file deletion of results isn't
    # blocked by QGIS (this OUTPUT is a real file, later delete_shapefile()'d by eliminate_gaps())
    processing.run("native:multiparttosingleparts", {
        'INPUT': clipped,
        'OUTPUT': tmp_stands_clipped_path
    }, feedback=feedback)

    return {"stands_clipped": tmp_stands_clipped_path}


def clip_vector_layer(input: str, overlay: str, output='TEMPORARY_OUTPUT', context=None, feedback=None):
    result = processing.run("native:clip", {
        'INPUT': input,
        'OVERLAY': overlay,
        'OUTPUT': output
    }, context=context, feedback=feedback, is_child_algorithm=True)
    # Resolved into an actual layer object (rather than left as the raw context-scoped reference
    # string) so callers can safely pass it on to a *different* processing.run() call that doesn't
    # share our `context` - e.g. because that call's own OUTPUT gets deleted by hand shortly after
    # and must not be resolved through our long-lived context (see clip_to_perimeter() below). A
    # materialized layer object resolves correctly regardless of which context (or none) is used
    # for the next call, whereas the bare reference string only resolves within the context that
    # created it.
    return QgsProcessingUtils.mapLayerFromString(result['OUTPUT'], context)


def clip_vhm_to_perimeter(working_root, tmp_output_folder, vhm_input, perimeter, vhm_output_name):
    log.debug("--------------------------------------------")
    log.debug("START Clip VHM to perimeter...")

    # Clip to forest mask
    vhm_clipped_path = os.path.join(working_root, vhm_output_name)

    param = {'INPUT': vhm_input, 'MASK': perimeter, 'SOURCE_CRS': None, 'TARGET_CRS': None, 'NODATA': None,
             'ALPHA_BAND': False, 'CROP_TO_CUTLINE': True, 'KEEP_RESOLUTION': False,
             'SET_RESOLUTION': False, 'X_RESOLUTION': 0, 'Y_RESOLUTION': 0, 'MULTITHREADING': False,
             'OPTIONS': '', 'DATA_TYPE': 0,
             'EXTRA': '-multi -wm 5000 -co COMPRESS=LZW -co TILED=YES -co BIGTIFF=YES  -wo \"CUTLINE_ALL_TOUCHED=TRUE\"',
             'OUTPUT': vhm_clipped_path}
    processing.run("gdal:cliprasterbymasklayer", param)

    return vhm_clipped_path


def eliminate_gaps(in_shape_path,
                   output_shape_path,
                   tmp_output_folder,
                   perimeter_shape,
                   del_tmp=True,
                   context=None,
                   feedback=None):
    """
    Align tbk shapefile to perimeter (for example Waldmaske AV).
    Idea: If small gaps remain between a defined perimeter and the
    stands shapefile. They need to be merged with the neighboring stand to
    exactly match the perimeter and therefore remove small gap
    """

    log.debug("--------------------------------------------")
    log.debug("START Eliminate gaps...")

    # File names
    gaps_tmp_path = os.path.join(tmp_output_folder, "gaps_tmp.gpkg")
    gaps_single_tmp_path = os.path.join(tmp_output_folder, "gaps_single_tmp.gpkg")
    union_tmp_path = os.path.join(tmp_output_folder, "stands_gaps_union_tmp.gpkg")
    union_tmp_buf_path = os.path.join(tmp_output_folder, "stands_gaps_union_tmp_buf0.gpkg")

    ########################################
    # Find gaps
    # No shared `context` in this block (feedback alone still gives cancellation): these calls
    # read/write real named files (gaps_tmp_path, gaps_single_tmp_path, union_tmp_path,
    # union_tmp_buf_path, in_shape_path) that get delete_shapefile()'d by hand below once del_tmp
    # is set, and resolving them through our long-lived workflow context leaves them locked open
    # under Windows until the whole run's context is torn down - the explicit cleanup then fails
    # with "Permission denied" (verified in isolation: same context -> same lock regardless of
    # is_child_algorithm; no shared context -> no lock).
    log.debug("finding gaps...")
    param = {'INPUT': perimeter_shape, 'OVERLAY': in_shape_path, 'OUTPUT': gaps_tmp_path}
    processing.run("native:difference", param, feedback=feedback)

    ########################################
    # Transform gaps to single part
    log.debug("transform gaps to single part")
    param = {'INPUT': gaps_tmp_path, 'OUTPUT': gaps_single_tmp_path}
    processing.run("native:multiparttosingleparts", param, feedback=feedback)

    ########################################
    # Union with stand layer
    # todo remove Union and replace with a different workflow
    log.debug("union gaps with stands...")
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 1)
    param = {'INPUT': in_shape_path, 'OVERLAY': gaps_single_tmp_path, 'OVERLAY_FIELDS_PREFIX': '',
             'OUTPUT': union_tmp_path}
    processing.run("native:union", param, feedback=feedback)
    processing.ProcessingConfig.setSettingValue('FILTER_INVALID_GEOMETRIES', 2)

    params = {'INPUT': union_tmp_path, 'DISTANCE': 0, 'SEGMENTS': 5, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0,
              'MITER_LIMIT': 2, 'DISSOLVE': False, 'OUTPUT': union_tmp_buf_path}
    processing.run("native:buffer", params, feedback=feedback)

    ########################################
    # Eliminate gaps
    log.debug("eliminate gaps...")
    expression = 'ID IS NULL AND to_int(area($geometry))>0'

    union_layer = QgsVectorLayer(union_tmp_path, "union_tmp", "ogr")
    union_layer.selectByExpression(expression)

    # TODO Does not persist results when writing directly to file
    param = {'INPUT': union_layer, 'MODE': 2, 'OUTPUT': 'TEMPORARY_OUTPUT'}
    algo_output = processing.run("qgis:eliminateselectedpolygons", param, context=context, feedback=feedback,
                                 is_child_algorithm=True)

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(
        QgsProcessingUtils.mapLayerFromString(algo_output['OUTPUT'], context), output_shape_path, ctc,
        getVectorSaveOptions('GPKG', 'utf-8'))

    ########################################
    # Delete gaps not possible to eliminate
    log.debug("delete remaining gaps completely...")
    expression = 'ID IS NULL OR to_int(area($geometry))=0'

    # Delete Fields and keep only major ones
    fields_to_delete = ["ID_2", "GRIDCODE", "FID_stands", "FID_gaps_s", "Id_1", "ORIG_FID"]
    fields_to_keep = ["OBJECTID", "area_m2", "hmax_eff", "hp80", "FID_orig", "ID", "hmax", "hdom", "type"]

    out_layer = QgsVectorLayer(output_shape_path, "union_tmp", "ogr")
    prov = out_layer.dataProvider()
    for field in prov.fields():
        if field.name() not in fields_to_keep:
            fields_to_delete.append(field.name())

    out_layer.selectByExpression(expression)
    if len(out_layer.selectedFeatureIds()) > 0:
        with edit(out_layer):
            out_layer.deleteSelectedFeatures()

    # Delete fields
    delete_fields(out_layer, fields_to_delete)

    log.debug("DONE!")

    # Delete layers
    if del_tmp:
        delete_shapefile(union_tmp_buf_path)
        delete_shapefile(gaps_single_tmp_path)
        delete_shapefile(gaps_tmp_path)
        delete_shapefile(union_tmp_path)
        delete_shapefile(in_shape_path)

    return {"stands_clipped_no_gaps": output_shape_path, }