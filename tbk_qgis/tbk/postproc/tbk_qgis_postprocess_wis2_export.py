# -*- coding: utf-8 -*-

#######################################################################
# Export a generated stand map for WIS.2
#
# Author: Hannes Horneber, BFH-HAFL
#######################################################################

"""
/***************************************************************************
 TBk - Toolkit for the generation of forest stand maps
 ***************************************************************************/
"""

__author__ = 'Berner Fachhochschule BFH-HAFL'
__date__ = '2024-02-20'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import time
from datetime import datetime, timedelta
import logging, logging.handlers
import sys
import osgeo.gdal as gdal
import osgeo.ogr as ogr
import osgeo.osr as osr

import math

import numpy as np
from scipy import ndimage

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterDefinition,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsCoordinateReferenceSystem,
                       QgsApplication)
import processing

from tbk_qgis.tbk.utility.tbk_utilities import *


class TBkPostprocessWIS2Export(QgsProcessingAlgorithm):
    """
    This algorithm takes a stand map and exports it for WIS2.
    """

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # ------- Define Constants -------#
    # Constants used to refer to parameters and outputs.

    # They will be used when calling the algorithm from another algorithm, or when  calling from the QGIS console.

    # Directory containing the input files
    OUTPUT_ROOT = "output_root"
    OUTPUT = "OUTPUT"

    # inputs
    STANDS = "stands"
    FOREST_SITES = "forest_sites"

    DEFAULT_SITE_CATEOGRY = "default_site_category"
    FIELD_FOREST_SITE_CATEGORY = "field_forest_site_category"
    FIELD_P100 = "field_p100"
    FIELD_P120 = "field_p120"
    FIELD_P140 = "field_p140"
    FIELD_P160 = "field_p160"
    FIELD_P390 = "field_p390"
    FIELD_P410 = "field_p410"
    FIELD_P420 = "field_p420"
    FIELD_P430 = "field_p430"
    FIELD_P440 = "field_p440"
    FIELD_P800 = "field_p800"

    DELETE_TMP = "delete_tmp"
    CREATE_WIS2_SUBFOLDER = "create_wis2_subfolder"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # ------- Add Algorithm Parameters -------#
        # Parameters with default values

        # input stand map
        self.addParameter(QgsProcessingParameterFeatureSource(self.STANDS,
                                                              self.tr("Stand map to be exported"),
                                                              [QgsProcessing.TypeVectorPolygon]))

        # output folder
        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_ROOT,
                                                     self.tr(
                                                         "Output folder (export will be named: wis2_stands_export_YYYYMMDD-HHMM.xml)"),
                                                     behavior=QgsProcessingParameterFile.Folder,
                                                     fileFilter='All Folders (*.*)', defaultValue=None,
                                                     optional=True))
        # forest site categories (field)
        self.addParameter(QgsProcessingParameterString(self.FIELD_FOREST_SITE_CATEGORY,
                                                       self.tr(
                                                           "Field Name of site category (either in stand map or in layer with forest sites - provide below)"),
                                                       optional=True))
        # forest site categories (layer)
        self.addParameter(QgsProcessingParameterFeatureSource(self.FOREST_SITES,
                                                              self.tr("Layer with Forest sites (Waldstandorte)"),
                                                              [QgsProcessing.TypeVectorPolygon],
                                                              optional=True))

        # --- Advanced Parameters
        self.addAdvancedParameter(QgsProcessingParameterString(self.DEFAULT_SITE_CATEOGRY,
                                                               self.tr(
                                                                   "Default site category (will be used when no field/layer is provided or if field is 0 / empty / NULL)"),
                                                               defaultValue="7a"))

        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P100,
                                                               self.tr("p100 tree species Field Name\n" +
                                                                       "If none provided, NH will be used."),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P120,
                                                               self.tr("p120 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P140,
                                                               self.tr("p140 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P160,
                                                               self.tr("p160 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P390,
                                                               self.tr("p390 tree species Field Name\n" +
                                                                       "If none provided, 100 - NH will be used."),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P410,
                                                               self.tr("p410 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P420,
                                                               self.tr("p420 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P430,
                                                               self.tr("p430 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P440,
                                                               self.tr("p440 tree species Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P800,
                                                               self.tr("p800 tree species Field Name"),
                                                               optional=True))

        self.addAdvancedParameter(QgsProcessingParameterBoolean(self.CREATE_WIS2_SUBFOLDER,
                                                                self.tr("Create subfolder wis2_export."),
                                                                defaultValue=True))
        self.addAdvancedParameter(QgsProcessingParameterBoolean(self.DELETE_TMP,
                                                                self.tr("Delete temporary files"),
                                                                defaultValue=True))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # ------- INIT Algorithm -------#

        feedback.pushInfo("====================================================================")
        feedback.pushInfo("START PROCESSING")
        start_time = time.time()
        feedback.pushInfo("====================================================================")

        # --- get input parameters
        stands_layer = self.parameterAsVectorLayer(parameters, self.STANDS, context)
        stands_layer_source = str(self.parameterAsVectorLayer(parameters, self.STANDS, context).source())
        feedback.pushInfo(f"Using stands:\n {stands_layer_source}\n"
                          f"with fields:\n {stands_layer.fields().names()}\n")

        siteCategory_layer = self.parameterAsVectorLayer(parameters, self.FOREST_SITES, context)

        default_site_category = str(self.parameterAsString(parameters, self.DEFAULT_SITE_CATEOGRY, context))
        field_forest_site_category = str(self.parameterAsString(parameters, self.FIELD_FOREST_SITE_CATEGORY, context))
        field_p100 = str(self.parameterAsString(parameters, self.FIELD_P100, context))
        field_p120 = str(self.parameterAsString(parameters, self.FIELD_P120, context))
        field_p140 = str(self.parameterAsString(parameters, self.FIELD_P140, context))
        field_p160 = str(self.parameterAsString(parameters, self.FIELD_P160, context))
        field_p390 = str(self.parameterAsString(parameters, self.FIELD_P390, context))
        field_p410 = str(self.parameterAsString(parameters, self.FIELD_P410, context))
        field_p420 = str(self.parameterAsString(parameters, self.FIELD_P420, context))
        field_p430 = str(self.parameterAsString(parameters, self.FIELD_P430, context))
        field_p440 = str(self.parameterAsString(parameters, self.FIELD_P440, context))
        field_p800 = str(self.parameterAsString(parameters, self.FIELD_P800, context))

        delete_tmp = self.parameterAsBoolean(parameters, self.DELETE_TMP, context)
        tmp_joined_layer = ""
        create_wis2_subfolder = self.parameterAsBoolean(parameters, self.CREATE_WIS2_SUBFOLDER, context)

        # --- get/generate output parameters
        output_root = self.parameterAsString(parameters, self.OUTPUT_ROOT, context)
        if not output_root or output_root == "":
            # generate output root from input source layer
            output_root = os.path.dirname(stands_layer_source)  ## directory of file
            feedback.pushInfo(f"No output folder provided, using directory of stand map input.")

        if create_wis2_subfolder:
            output_folder = os.path.join(output_root, "wis2_export")  # can be used to create subfolder by default
            feedback.pushInfo(f"Creating subdirectory wis2_export.")
            ensure_dir(output_folder)
        else:
            output_folder = output_root
            ensure_dir(output_folder)

        feedback.pushInfo(f"Output folder:\n{output_folder}\n")

        currentDatetime = datetime.now().strftime("%Y%m%d-%H%M")
        output_xml = os.path.join(output_folder, ("wis2_stands_export_" + currentDatetime + ".xml"))

        # --- check and join siteCategory_layer
        if (not siteCategory_layer):
            # case 1 and 2: no join layer present
            if (not field_forest_site_category) or field_forest_site_category == "":
                # case 1: no join layer and no site category field -> fall back to default
                feedback.pushInfo(
                    "No layer or field for site categories provided.\n" +
                    f"Site categories will be set to default {default_site_category}")
                field_forest_site_category = ""
            else:
                # case 2: no join layer but site category field provided -> (try) to read site category from TBk
                # check if field really exists
                if not stands_layer.fields().indexFromName(field_forest_site_category) == -1:
                    # case 2a: field found
                    print(f"Using site categories from stands layer (field: {field_forest_site_category})")
                    feedback.pushInfo(
                        f"Using site categories from stands layer (field: {field_forest_site_category})")
                else:
                    # case 2b: field not found
                    print("Field for site categories provided but can't be found in stands layer.\n" +
                          f"Site categories will be set to default {default_site_category}")
                    feedback.pushWarning(
                        "Field for site categories provided but can't be found in stands layer.\n" +
                        f"Site categories will be set to default {default_site_category}")
                    field_forest_site_category = ""
        else:
            # case 3 and 4: join layer present
            # get layer source
            siteCategory_layer_source = str(
                self.parameterAsVectorLayer(parameters, self.FOREST_SITES, context).source())

            # check if category field is present
            if (not field_forest_site_category) or field_forest_site_category == "":
                # case 3: Join layer but no join field name provided -> no join possible without field name
                print("Layer for site categories provided, but no field name for site categories.\n"
                      "No join possible without field name\n"
                      f"Use one of the present names: {siteCategory_layer.fields().names()}\n"
                      f"Site categories will be set to default {default_site_category}")
                feedback.pushWarning(
                    "Layer for site categories provided, but no field name for site categories.\n"
                    "No join possible without field name\n"
                    f"Use one of the present names: {siteCategory_layer.fields().names()}\n"
                    f"Site categories will be set to default {default_site_category}")
                field_forest_site_category = ""
            else:
                # case 4: Join layer and join field provided -> join
                feedback.pushInfo(f"Extracting forest sites (field name: {field_forest_site_category}) from layer")
                feedback.pushInfo(siteCategory_layer_source)

                tmp_joined_layer = os.path.join(output_folder,
                                                ("wis2_stands_with_site_categories_" + currentDatetime + ".gpkg"))

                # append site categories to stand map (spatial join) and write tmp file
                processing.run("native:joinattributesbylocation", {'INPUT': QgsProcessingFeatureSourceDefinition(
                    stands_layer_source,
                    selectedFeaturesOnly=False, featureLimit=-1,
                    flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck,
                    geometryCheck=QgsFeatureRequest.GeometryNoCheck), 'PREDICATE': [0],
                    'JOIN': QgsProcessingFeatureSourceDefinition(
                        siteCategory_layer_source,
                        selectedFeaturesOnly=False, featureLimit=-1,
                        flags=QgsProcessingFeatureSourceDefinition.FlagOverrideDefaultGeometryCheck,
                        geometryCheck=QgsFeatureRequest.GeometryNoCheck),
                    'JOIN_FIELDS': [field_forest_site_category], 'METHOD': 2,
                    'DISCARD_NONMATCHING': False, 'PREFIX': 'siteCategory_',
                    'OUTPUT': tmp_joined_layer})

                feedback.pushInfo("Successfully extracted forest sites.\n" +
                                  f"Joined layer saved as {tmp_joined_layer}")

                # TODO 1: check&inform if NULL values are present (will be set to default)
                # TODO 2: give option to use either provided site category (if present and not NULL) or joined one

                # use joined layer as stands layer
                stands_layer = QgsVectorLayer(tmp_joined_layer)
                field_forest_site_category = "siteCategory_" + field_forest_site_category

        # ------- MAIN PROCESSING -------#
        # write stands to XML
        print(f"\nExport to XML file:\n {output_xml}\n")
        feedback.pushInfo(f"\nExport to XML file:\n {output_xml}\n")
        i = 0
        with open(output_xml, 'a') as xml_file:

            xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            xml_file.write(
                '<dataroot xmlns:od="urn:schemas-microsoft-com:officedata" generated="' + currentDatetime + '">\n')
            xml_file.write('\n')

            provider = stands_layer.dataProvider()
            # iterate over each stand and write attributes
            for f in stands_layer.getFeatures():
                # print('load stand ' + str(f["ID"]))
                # print(str(f["area_m2"]))

                # remove stands without geometry
                if (f["area_m2"] == NULL):
                    print(' > skip stand ' + str(f["ID"]) + ': area is NULL')
                    feedback.pushInfo('skip stand ' + str(f["ID"]) + ': area is NULL')
                else:
                    # main processing of valid stand
                    i = i + 1  # count outputs
                    # print('processing stand ' + str(f["ID"]))
                    # feedback.pushInfo('processing stand ' + str(f["ID"]))

                    xml_file.write('<Stand>\n')

                    xml_file.write('\t<ID>' + str(f["ID"]) + '</ID>\n')
                    xml_file.write('\t<area>' + str(f["area_m2"]) + '</area>\n')
                    xml_file.write('\t<DG_default>' + str(f["DG"]) + '</DG_default>\n')

                    # TODO replace DG NULL with 1 (?)
                    # DG: set to 1 if 0/NULL
                    if not f["DG"]:
                        xml_file.write('\t<DG>' + str(1) + '</DG>\n')
                    else:
                        xml_file.write('\t<DG>' + str(f["DG"]) + '</DG>\n')

                    # hdom: set hdom = 0 to 1
                    if (f["hdom"] == 0):
                        xml_file.write('\t<hdom>' + str(1) + '</hdom>\n')
                    else:
                        xml_file.write('\t<hdom>' + str(f["hdom"]) + '</hdom>\n')

                    xml_file.write('\t<ddom>' + str(0) + '</ddom>\n')
                    xml_file.write('\t<age>' + str(0) + '</age>\n')

                    # TREE SPECIES: if field is provided, take field, else use NH
                    if field_p100 == "":
                        p100 = f["NH"]
                    else:
                        p100 = f[(field_p100)]

                    if field_p120 == "":
                        p120 = 0
                    else:
                        p120 = f[(field_p120)]

                    if field_p140 == "":
                        p140 = 0
                    else:
                        p140 = f[(field_p140)]

                    if field_p160 == "":
                        p160 = 0
                    else:
                        p160 = f[(field_p160)]

                    if field_p390 == "":
                        p390 = 0
                    else:
                        p390 = f[(field_p390)]

                    if field_p410 == "":
                        p410 = 100 - f["NH"]
                    else:
                        p410 = f[(field_p410)]

                    if field_p420 == "":
                        p420 = 0
                    else:
                        p420 = f[(field_p420)]

                    if field_p430 == "":
                        p430 = 0
                    else:
                        p430 = f[(field_p430)]

                    if field_p440 == "":
                        p440 = 0
                    else:
                        p440 = f[(field_p440)]

                    if field_p800 == "":
                        p800 = 0
                    else:
                        p800 = f[(field_p800)]

                    # check whether tree species proportions add up to 100, otherwise scale up:
                    #TODO come up with solution (e.g. scale/normalize values to 100)
                    sum_tree_species = p100 + p120 + p140 + p160 + p390 + p410 + p420 + p430 + p440 + p800
                    if not (sum_tree_species == 100):
                        feedback.pushWarning(
                            ' > stand ' + str(f["ID"]) + f': tree species proportions add up to {sum_tree_species}%')
                        print(' > stand ' + str(f["ID"]) + f': tree species proportions add up to {sum_tree_species}%')

                    # write tree species proportions to XML
                    xml_file.write('\t<p100>' + str(p100) + '</p100>\n')
                    xml_file.write('\t<p120>' + str(p120) + '</p120>\n')
                    xml_file.write('\t<p140>' + str(p140) + '</p140>\n')
                    xml_file.write('\t<p160>' + str(p160) + '</p160>\n')
                    xml_file.write('\t<p390>' + str(p390) + '</p390>\n')
                    xml_file.write('\t<p410>' + str(p410) + '</p410>\n')
                    xml_file.write('\t<p420>' + str(p420) + '</p420>\n')
                    xml_file.write('\t<p430>' + str(p430) + '</p430>\n')
                    xml_file.write('\t<p440>' + str(p440) + '</p440>\n')
                    xml_file.write('\t<p800>' + str(p800) + '</p800>\n')


                    # SITE CATEGORY: use default if no field is provided
                    if field_forest_site_category == "":
                        xml_file.write('\t<siteCategory>' + default_site_category + '</siteCategory>\n')
                    else:
                        # replace NULL / 0 values with Default value
                        if not f[(field_forest_site_category)]:
                            xml_file.write('\t<siteCategory>' + default_site_category + '</siteCategory>\n')
                        else:
                            xml_file.write(
                                '\t<siteCategory>' + str(f[(field_forest_site_category)]) + '</siteCategory>\n')

                    xml_file.write('</Stand>\n\n')
            # close data tag
            xml_file.write('</dataroot>')

        print(f"\nExported {i} stands")
        feedback.pushInfo(f"\nExported {i} stands")

        # ------- WRAPUP -------#
        # TODO this doesn't work since the file isn't closed
        # if delete_tmp and not tmp_joined_layer == "":
        #     print(f"Attempting to delete temporary files")
        #     feedback.pushInfo(f"Delete temporary files: \n {tmp_joined_layer}")
        #     if os.path.exists(tmp_joined_layer):
        #         os.remove(tmp_joined_layer)

        feedback.pushInfo("====================================================================")
        feedback.pushInfo("FINISHED")
        feedback.pushInfo("TOTAL PROCESSING TIME: %s (h:min:sec)" % str(timedelta(seconds=(time.time() - start_time))))
        feedback.pushInfo("====================================================================")

        return {self.OUTPUT: output_folder}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk WIS2 export'

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
        return TBkPostprocessWIS2Export()
