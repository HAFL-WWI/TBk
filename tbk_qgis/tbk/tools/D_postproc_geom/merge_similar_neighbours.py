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

import os
import subprocess
import sys

from qgis import core
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QVariant
from qgis.utils import iface
from qgis.core import QgsProject
import processing
from qgis.core import *

from tbk_qgis.tbk.general.tbk_utilities import *

import numpy as np
import pandas as pd
from datetime import timedelta
import time


def merge_similar_neighbours(working_root, shape_in_path, shape_out_path, min_area_m2, min_hdom_diff_rel, del_tmp=True):
    """
    TBk post-process. Prepare polygons to dissolve by specific criterias.
    Used to combine small polygons with similar neighbours.

    :param working_root:
    :param shape_in_path:
    :param shape_out_path:
    :param min_area_m2:
    :param min_hdom_diff_rel:
    :param del_tmp:
    :return:
    """

    print("--------------------------------------------")
    print("START MERGE similar neighbours...")
    print("min_area_m2: ", min_area_m2, " min_hdom_diff_rel: ", min_hdom_diff_rel)

    # load stands to be merged
    simplified_layer = QgsVectorLayer(shape_in_path, "stands_to_be_merged", "ogr")
    # QgsProject.instance().addMapLayer(simplified_layer)

    # add fid_input as unique identifier of input features (simplified stands)
    param = {'INPUT': simplified_layer, 'FIELD_NAME': 'fid_input', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
             'FIELD_PRECISION': 0,
             'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
    algoOutput = processing.run("native:fieldcalculator", param)
    simplified_layer = algoOutput["OUTPUT"]

    ########################################
    # Approximate the arcpy Neighbours tool
    # Code basing on https://www.qgistutorials.com/en/docs/find_neighbour_polygons.html

    print("Make internally used neighbours table...")
    start_time = time.time()

    # Create memory layer
    neighbourLayer = QgsVectorLayer('None', 'Neighbours', 'memory')

    # Create a dictionary of all features
    feature_dict = {f.id(): f for f in simplified_layer.getFeatures()}

    # Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.addFeature(f)

    neighbours_tmp = []

    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        geom = f.geometry()

        oid = -1
        src_FID = f["fid_input"]
        src_hdom = f["hdom"]
        src_type = f["type"]
        src_area_m2 = f["area_m2"]
        node_count = -1

        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighbouring features.
        intersecting_ids = index.intersects(geom.boundingBox())

        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]

            # For our purpose we consider a feature as 'neighbour' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbour.
            if (f != intersecting_f and
                    not intersecting_f.geometry().disjoint(geom)):
                nbr_FID = intersecting_f["fid_input"]
                nbr_hdom = intersecting_f["hdom"]
                nbr_type = intersecting_f["type"]
                nbr_area_m2 = intersecting_f["area_m2"]
                lngth = -1
                if (intersecting_f.geometry().touches(geom) or intersecting_f.geometry().intersects(geom)):
                    isct = intersecting_f.geometry().intersection(geom)
                    lngth = isct.length()
                # Add a feature with attributes (and without geometry) to populate the 3 fields

                # print([objectid,src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
                neighbours_tmp.append(
                    [oid, src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2,
                     nbr_area_m2, lngth, node_count])

    # Begin editing memory layer and create 3 fields
    neighbourLayer.startEditing()
    provider = neighbourLayer.dataProvider()
    provider.addAttributes([QgsField("OID", QVariant.Int),
                            QgsField("src_FID", QVariant.Int),
                            QgsField("nbr_FID", QVariant.Int),
                            QgsField("src_hdom", QVariant.Int),
                            QgsField("nbr_hdom", QVariant.Int),
                            QgsField("src_type", QVariant.String),
                            QgsField("nbr_type", QVariant.String),
                            QgsField("src_area_m2", QVariant.Int),
                            QgsField("nbr_area_m2", QVariant.Int),
                            QgsField("LENGTH", QVariant.Double),
                            QgsField("NODE_COUNT", QVariant.Int)])
    neighbourLayer.updateFields()

    for n in neighbours_tmp:
        attr = neighbourLayer.dataProvider()
        feat = QgsFeature()
        # print([objectid,src_FID, nbr_FID, src_hdom, nbr_hdom, src_type, nbr_type, src_area_m2, nbr_area_m2, lngth, node_count])
        feat.setAttributes(n)
        attr.addFeatures([feat])
        # print(feat)

        neighbourLayer.commitChanges()

    # list all column names of table neighbourLayer
    cols = [f.name() for f in neighbourLayer.fields()]
    # print(cols)
    # a generator to yield one row at a time
    datagen = ([f[col] for col in cols] for f in neighbourLayer.getFeatures())
    # make pandas data.frame
    df = pd.DataFrame.from_records(data=datagen, columns=cols)
    # print(df.head())
    # save table neighbourLayer as .csv
    # df.to_csv(os.path.join(working_root, "neighbour.csv"), index=False)

    # print('Processing neighbours complete.')
    end_time = time.time()
    print("Neighbours table execution time: " + str(timedelta(seconds=(end_time - start_time))))

    print("Do actual merger of similar neighbours ...")
    start_time = time.time()

    # select small polygons with possible neighbour to dissolve
    df["hdom_diff_rel"] = (df.src_hdom - df.nbr_hdom).abs() / df.src_hdom
    i_dissolve = ((df.src_area_m2 < min_area_m2) &
                  (df.hdom_diff_rel < min_hdom_diff_rel) &
                  (df.LENGTH > 0) &
                  (df.nbr_type == "classified"))
    df_sub = df[i_dissolve]

    # remove polygons with multiple dissolve options. Too complicate. Could for example lead to similar and adjcent large polygons -> confusing.
    df_sub_counts = df_sub.groupby(["src_FID"])["OID"].count().reset_index()
    df_sub = df_sub[df_sub["src_FID"].isin(df_sub_counts[df_sub_counts["OID"] == 1]["src_FID"])]

    # keep only polygons having polygons as merge partners, which themselves are NOT among the polygons to be merged -->
    # avoid generating dissolved geometries, which overlap with each other
    df_sub = df_sub[df_sub["nbr_FID"].isin(df_sub["src_FID"]) == False]

    if len(df_sub.index) > 0:  # merge stands only if necessary
        if (len(df_sub) == len(df_sub.src_FID.unique())):
            print("Merging objects not unique!")

        # unique nbr_FID from subset of neighbours table
        nbr_FID_unique = list(set(list(df_sub["nbr_FID"])))

        # list with empty placeholder for each merged feature + 1 placeholder for all the other features
        l = [None] * (len(nbr_FID_unique) + 1)

        # list with empty placeholder for each merged feature to collect fids of original geometries
        l_fid_merged = [None] * len(nbr_FID_unique)

        # unique scr_FID from subset of neighbours table
        src_FID_unique = list(set(list(df_sub["src_FID"])))
        print(len(src_FID_unique), "polygons to dissolve!")

        for i in range(len(nbr_FID_unique)):
            # select adjacent stands, which will be dissolved into a single surface
            nbr_FID = nbr_FID_unique[i]
            src_FID = list(df_sub[df_sub['nbr_FID'] == nbr_FID]["src_FID"])
            fid_inputs = [nbr_FID] + src_FID
            exp = '"fid_input" IN (' + ', '.join(map(str, fid_inputs)) + ')'
            param = {'INPUT': simplified_layer, 'EXPRESSION': exp, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:extractbyexpression", param)
            stands_i = algoOutput["OUTPUT"]

            # save original fids of stands, which will be merged below, in list
            l_fid_merged[i] = stands_i.aggregate(QgsAggregateCalculator.ArrayAggregate, "fid")[0]

            # sort selected stands by area (largest 1st) --> 1st feature's attributes are kept when dissolved
            param = {'INPUT': stands_i, 'EXPRESSION': '$area', 'ASCENDING': False, 'NULLS_FIRST': False,
                     'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:orderbyexpression", param)
            stands_i = algoOutput["OUTPUT"]

            # dissolved into a single surface
            param = {'INPUT': stands_i, 'FIELD': [], 'SEPARATE_DISJOINT': False, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:dissolve", param)
            dissovle_i = algoOutput["OUTPUT"]

            # add column merged = 1 (meaning dissolved geometry)
            param = {'INPUT': dissovle_i, 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                     'FIELD_PRECISION': 0,
                     'FORMULA': '1', 'OUTPUT': 'TEMPORARY_OUTPUT'}
            algoOutput = processing.run("native:fieldcalculator", param)
            l[i] = algoOutput["OUTPUT"]  # replace empty placeholder in list

        # turn nested list with fids of merged simplified into a flat list
        fid_merged = sum(l_fid_merged, [])

        # gather all not dissolved features in a single layer and ...
        exp = '"fid" NOT IN (' + ', '.join(map(str, fid_merged)) + ')'
        param = {'INPUT': simplified_layer, 'EXPRESSION': exp, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:extractbyexpression", param)

        # ... add column merged = 0 (meaning not dissolved geometry) to this layer ...
        param = {'INPUT': algoOutput["OUTPUT"], 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '0', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        l[len(l) - 1] = algoOutput["OUTPUT"]  # ... and finally replace last empty placeholder with this layer

        # merge listed layers with dissolved and not dissolved features
        param = {'LAYERS': l, 'CRS': None, 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:mergevectorlayers", param)
        stands_merged = algoOutput["OUTPUT"]

        # overwrite fid of with unique values in order make certain that all features are exportable
        param = {'INPUT': stands_merged, 'FIELD_NAME': 'fid', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
                 'FORMULA': '@row_number', 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:fieldcalculator", param)
        stands_merged = algoOutput["OUTPUT"]

        # drop attribute layer, path (added by native:mergevectorlayers) & and 'fid_input' (unique identifier of input
        # features / simplified stands) finally save layer
        param = {'INPUT': stands_merged, 'COLUMN': ['layer', 'path', 'fid_input'], 'OUTPUT': shape_out_path}
        algoOutput = processing.run("native:deletecolumn", param)

    else:  # no stands to merge
        print("No stands to merge")

        # drop 'fid_input' (unique identifier of input features / simplified stands) finally save layer
        param = {'INPUT': simplified_layer, 'COLUMN': ['fid_input'], 'OUTPUT': 'TEMPORARY_OUTPUT'}
        algoOutput = processing.run("native:deletecolumn", param)

        # add column merged = 0 (meaning not dissolved geometry) to all simplified stands ...
        param = {'INPUT': algoOutput["OUTPUT"], 'FIELD_NAME': 'merged', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0,
                 'FIELD_PRECISION': 0, 'FORMULA': '0', 'OUTPUT': shape_out_path}
        algoOutput = processing.run("native:fieldcalculator", param)
        # ... and save them as merged stands

    end_time = time.time()
    print("Actual merger of similar neighbours execution time: " + str(timedelta(seconds=(end_time - start_time))))


    return shape_out_path
