# *************************************************************************** #
# Post processing step for stand maps: Merge similar neighbouring stands
#
# Authors: Attilio Benini, Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
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
import processing
from PyQt5.QtCore import QMetaType

from tbk_qgis.tbk.general.tbk_utilities import *
import pandas as pd
from datetime import timedelta
import time

# Substep narration only (file/console at DEBUG); joins the "Merge similar neighbours" logger
# stream set up by tool_merge_similar_neighbours.py, the only caller of this function.
log = logging.getLogger('Merge similar neighbours')


def merge_similar_neighbours(shape_in_path, shape_out_path, min_area_m2, min_hdom_diff_rel, max_iterations=5):
    """
    TBk post-process. Merge small stands into their most similar neighbour.

    Iterates up to max_iterations times. Each pass:
      - builds a neighbour table,
      - selects small stands (< min_area_m2) with a similar classified neighbour
        (hdom relative difference < min_hdom_diff_rel, shared border length > 0),
      - when multiple neighbours qualify, picks the one with the longest shared border,
      - dissolves each selected stand into its chosen neighbour.
    Stops early when no more candidates are found.

    area_m2 is recalculated after each pass so that subsequent passes use the
    correct sizes of previously merged stands.
    """

    log.debug("--------------------------------------------")
    log.debug("START MERGE similar neighbours...")
    log.debug(f"min_area_m2: {min_area_m2}  min_hdom_diff_rel: {min_hdom_diff_rel}")

    output_file = {"stands_merged": shape_out_path}

    layer = QgsVectorLayer(shape_in_path, "stands_to_be_merged", "ogr")

    any_merges = False

    for iteration in range(max_iterations):
        # add fid_input as a stable per-pass unique identifier
        param = {'INPUT': layer, 'FIELD_NAME': 'fid_input', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        layer = processing.run("native:fieldcalculator", param)["OUTPUT"]

        # ---- Build neighbour table ----
        log.debug(f"Pass {iteration + 1}: building neighbour table...")
        start_time = time.time()

        feature_dict = {f.id(): f for f in layer.getFeatures()}
        index = QgsSpatialIndex()
        for f in feature_dict.values():
            index.addFeature(f)

        neighbours_tmp = []
        for f in feature_dict.values():
            geom = f.geometry()
            src_fid = f["fid_input"]
            src_hdom = f["hdom"]
            src_type = f["type"]
            src_area_m2 = f["area_m2"]
            for intersecting_id in index.intersects(geom.boundingBox()):
                intersecting_f = feature_dict[intersecting_id]
                if f != intersecting_f and not intersecting_f.geometry().disjoint(geom):
                    nbr_fid = intersecting_f["fid_input"]
                    nbr_hdom = intersecting_f["hdom"]
                    nbr_type = intersecting_f["type"]
                    nbr_area_m2 = intersecting_f["area_m2"]
                    length = -1
                    if intersecting_f.geometry().intersects(geom):
                        isct = intersecting_f.geometry().intersection(geom)
                        length = isct.length()
                    neighbours_tmp.append([-1, src_fid, nbr_fid, src_hdom, nbr_hdom,
                                           src_type, nbr_type, src_area_m2, nbr_area_m2, length, -1])

        neighbour_layer = QgsVectorLayer('None', 'Neighbours', 'memory')
        neighbour_layer.startEditing()
        provider = neighbour_layer.dataProvider()
        provider.addAttributes([
            QgsField("OID", QMetaType.Int),
            QgsField("src_FID", QMetaType.Int),
            QgsField("nbr_FID", QMetaType.Int),
            QgsField("src_hdom", QMetaType.Int),
            QgsField("nbr_hdom", QMetaType.Int),
            QgsField("src_type", QMetaType.QString, len=50),
            QgsField("nbr_type", QMetaType.QString, len=50),
            QgsField("src_area_m2", QMetaType.Int),
            QgsField("nbr_area_m2", QMetaType.Int),
            QgsField("LENGTH", QMetaType.Double, len=10, prec=3),
            QgsField("NODE_COUNT", QMetaType.Int),
        ])
        neighbour_layer.updateFields()
        feats = []
        for n in neighbours_tmp:
            feat = QgsFeature()
            feat.setAttributes(n)
            feats.append(feat)
        provider.addFeatures(feats)
        neighbour_layer.commitChanges()

        cols = [f.name() for f in neighbour_layer.fields()]
        datagen = ([f[col] for col in cols] for f in neighbour_layer.getFeatures())
        df = pd.DataFrame.from_records(data=datagen, columns=cols)
        log.debug(f"  neighbour table done: {str(timedelta(seconds=(time.time() - start_time)))}")

        # ---- Select merge candidates ----
        df["src_hdom"] = pd.to_numeric(df["src_hdom"], errors="coerce")
        df["nbr_hdom"] = pd.to_numeric(df["nbr_hdom"], errors="coerce")
        df["hdom_diff_rel"] = (df.src_hdom - df.nbr_hdom).abs() / df.src_hdom

        i_dissolve = ((df.src_area_m2 < min_area_m2) &
                      (df.hdom_diff_rel < min_hdom_diff_rel) &
                      (df.LENGTH > 0) &
                      (df.nbr_type == "classified"))
        df_sub = df[i_dissolve]

        # When multiple neighbours qualify, pick the one with the longest shared border
        if not df_sub.empty:
            df_sub = df_sub.loc[df_sub.groupby("src_FID")["LENGTH"].idxmax()]

        # Don't merge into a stand that is itself being merged (prevents cascading geometry overlap)
        df_sub = df_sub[~df_sub["nbr_FID"].isin(df_sub["src_FID"])]

        if df_sub.empty:
            param = {'INPUT': layer, 'COLUMN': ['fid_input'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
            layer = processing.run("native:deletecolumn", param)["OUTPUT"]
            break

        any_merges = True
        nbr_fid_unique = list(df_sub["nbr_FID"].unique())
        src_fid_unique = list(df_sub["src_FID"].unique())
        log.debug(f"  Pass {iteration + 1}: merging {len(src_fid_unique)} stands into "
                  f"{len(nbr_fid_unique)} targets...")
        start_time = time.time()

        # ---- Dissolve each target group ----
        l = [None] * (len(nbr_fid_unique) + 1)
        l_fid_merged = [None] * len(nbr_fid_unique)

        for i in range(len(nbr_fid_unique)):
            nbr_fid = nbr_fid_unique[i]
            src_fid = list(df_sub[df_sub['nbr_FID'] == nbr_fid]["src_FID"])
            fid_inputs = [nbr_fid] + src_fid
            exp = '"fid_input" IN (' + ', '.join(map(str, fid_inputs)) + ')'

            param = {'INPUT': layer, 'EXPRESSION': exp, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            stands_i = processing.run("native:extractbyexpression", param)["OUTPUT"]
            l_fid_merged[i] = stands_i.aggregate(QgsAggregateCalculator.ArrayAggregate, "fid")[0]

            # sort by area descending so the largest stand's attributes are kept by dissolve
            param = {'INPUT': stands_i, 'EXPRESSION': '$area', 'ASCENDING': False, 'NULLS_FIRST': False,
                     'OUTPUT': 'TEMPORARY_OUTPUT'}
            stands_i = processing.run("native:orderbyexpression", param)["OUTPUT"]

            param = {'INPUT': stands_i, 'FIELD': [], 'SEPARATE_DISJOINT': False, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            dissolve_i = processing.run("native:dissolve", param)["OUTPUT"]

            param = {'INPUT': dissolve_i, 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                     'FIELD_PRECISION': 0, 'FORMULA': '1', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            l[i] = processing.run("native:fieldcalculator", param)["OUTPUT"]

        fid_merged = sum(l_fid_merged, [])
        exp = '"fid" NOT IN (' + ', '.join(map(str, fid_merged)) + ')'
        param = {'INPUT': layer, 'EXPRESSION': exp, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        not_dissolved = processing.run("native:extractbyexpression", param)["OUTPUT"]

        param = {'INPUT': not_dissolved, 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        l[-1] = processing.run("native:fieldcalculator", param)["OUTPUT"]

        param = {'LAYERS': l, 'CRS': None, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        stands_merged = processing.run("native:mergevectorlayers", param)["OUTPUT"]

        # overwrite fid with unique sequential values
        param = {'INPUT': stands_merged, 'FIELD_NAME': 'fid', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        stands_merged = processing.run("native:fieldcalculator", param)["OUTPUT"]

        # drop columns added by mergevectorlayers and the per-pass fid_input
        param = {'INPUT': stands_merged, 'COLUMN': ['layer', 'path', 'fid_input'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
        stands_merged = processing.run("native:deletecolumn", param)["OUTPUT"]

        # recalculate area_m2 so subsequent passes use the correct size of merged stands
        param = {'INPUT': stands_merged, 'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '$area', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        layer = processing.run("native:fieldcalculator", param)["OUTPUT"]

        log.debug(f"  pass done: {str(timedelta(seconds=(time.time() - start_time)))}")

    # ---- Save final result ----
    if any_merges:
        # Update area_m2 one final time and write to output path
        param = {'INPUT': layer, 'FIELD_NAME': 'area_m2', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '$area', 'OUTPUT': output_file["stands_merged"]}
        processing.run("native:fieldcalculator", param)
    else:
        log.debug("No stands to merge")
        param = {'INPUT': layer, 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '0', 'OUTPUT': output_file["stands_merged"]}
        processing.run("native:fieldcalculator", param)

    log.debug("DONE: merge similar neighbours")
    return output_file
