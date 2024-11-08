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

import qgis.core
import time
from datetime import datetime, timedelta

from qgis.PyQt.QtCore import QCoreApplication
import processing

from tbk_qgis.tbk.general.tbk_utilities import *


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
    DEFAULT_TREE_SPECIES_FIELD = "NH"
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

        self.addAdvancedParameter(QgsProcessingParameterString(self.DEFAULT_TREE_SPECIES_FIELD,
                                                               self.tr(
                                                                   "Default tree species attribute (will be used for Beech (p100) / Fir (p410)\n" +
                                                                   "Will be applied if no other field is provided, the field is not found or if it is NULL)"),
                                                               defaultValue="NH"))

        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P100,
                                                               self.tr("Spruce (Fichte, p100) proportion Field Name\n" +
                                                                       "If none provided, NH will be used."),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P120,
                                                               self.tr("Fir (Tanne, p120) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P140,
                                                               self.tr("Pine (Foehre/Kiefer, p140) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P160,
                                                               self.tr("Larch (Laerche, p160) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P390,
                                                               self.tr("Other Coniferous Trees (p390) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P410,
                                                               self.tr("Beech (Buche, p410) proportion Field Name\n" +
                                                                       "If none provided, 100 - NH will be used."),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P420,
                                                               self.tr("Oak (Eiche, p420) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P430,
                                                               self.tr("Ash (Esche, p430) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P440,
                                                               self.tr("Maple (Ahorn, p440) proportion Field Name"),
                                                               optional=True))
        self.addAdvancedParameter(QgsProcessingParameterString(self.FIELD_P800,
                                                               self.tr("Other broadleaves (p800) proportion Field Name"),
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
        default_tree_species_field = str(self.parameterAsString(parameters, self.DEFAULT_TREE_SPECIES_FIELD, context))
        field_p100 = str(self.parameterAsString(parameters, self.FIELD_P100, context))
        field_p410 = str(self.parameterAsString(parameters, self.FIELD_P410, context))

        field_p120 = str(self.parameterAsString(parameters, self.FIELD_P120, context))
        field_p140 = str(self.parameterAsString(parameters, self.FIELD_P140, context))
        field_p160 = str(self.parameterAsString(parameters, self.FIELD_P160, context))
        field_p390 = str(self.parameterAsString(parameters, self.FIELD_P390, context))
        field_p420 = str(self.parameterAsString(parameters, self.FIELD_P420, context))
        field_p430 = str(self.parameterAsString(parameters, self.FIELD_P430, context))
        field_p440 = str(self.parameterAsString(parameters, self.FIELD_P440, context))
        field_p800 = str(self.parameterAsString(parameters, self.FIELD_P800, context))

        fields_tree_species = [
            str(self.parameterAsString(parameters, self.FIELD_P100, context)),
            str(self.parameterAsString(parameters, self.FIELD_P120, context)),
            str(self.parameterAsString(parameters, self.FIELD_P140, context)),
            str(self.parameterAsString(parameters, self.FIELD_P160, context)),
            str(self.parameterAsString(parameters, self.FIELD_P390, context)),
            str(self.parameterAsString(parameters, self.FIELD_P410, context)),
            str(self.parameterAsString(parameters, self.FIELD_P420, context)),
            str(self.parameterAsString(parameters, self.FIELD_P430, context)),
            str(self.parameterAsString(parameters, self.FIELD_P440, context)),
            str(self.parameterAsString(parameters, self.FIELD_P800, context))
        ]

        fields_pX_tree_species = {
            "p100": str(self.parameterAsString(parameters, self.FIELD_P100, context)),
            "p120": str(self.parameterAsString(parameters, self.FIELD_P120, context)),
            "p140": str(self.parameterAsString(parameters, self.FIELD_P140, context)),
            "p160": str(self.parameterAsString(parameters, self.FIELD_P160, context)),
            "p390": str(self.parameterAsString(parameters, self.FIELD_P390, context)),
            "p410": str(self.parameterAsString(parameters, self.FIELD_P410, context)),
            "p420": str(self.parameterAsString(parameters, self.FIELD_P420, context)),
            "p430": str(self.parameterAsString(parameters, self.FIELD_P430, context)),
            "p440": str(self.parameterAsString(parameters, self.FIELD_P440, context)),
            "p800": str(self.parameterAsString(parameters, self.FIELD_P800, context))
        }

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

                # use joined layer as stands layer
                stands_layer = QgsVectorLayer(tmp_joined_layer)
                field_forest_site_category = "siteCategory_" + field_forest_site_category

        # ------- MAIN PROCESSING -------#

        # --- set tree species fields
        print("Tree Species Fields")
        feedback.pushInfo("Tree Species Fields")

        # if field is provided, check if field exists, else use NH
        for pkey, pfield in fields_pX_tree_species.items():
            # check if provided fields are found, if not set to empty string
            if pfield != "":
                if not stands_layer.fields().indexFromName(pfield) == -1:
                    # case a: field found
                    print(f"For {pkey} use field: {pfield}")
                    feedback.pushInfo(f"For {pkey} use field: {pfield}")
                else:
                    # case b: field not found
                    print(f"Provided field \'{pfield}\' for {pkey} not found and won't be used for tree species.")
                    feedback.pushWarning(
                        f"Provided field \'{pfield}\' for {pkey} not found and won't be used for tree species.")

                    fields_pX_tree_species[pkey] = ""
            else:
                if not pkey == "p100" and not pkey == "p410":
                    # case: no field provided
                    print(f"No field provided for {pkey} (will be set to 0)")
                    feedback.pushInfo(f"No field provided for {pkey} (will be set to 0)")

            # check if p100 / p410 are set, assign default fields if not
            if fields_pX_tree_species[pkey] == "":
                if pkey == "p100":
                    # case b1: p100
                    print(f"Default tree species field will be used for p100: {default_tree_species_field}")
                    feedback.pushWarning(
                        f"Default tree species field will be used for p100: {default_tree_species_field}")
                    fields_pX_tree_species[pkey] = default_tree_species_field
                elif pkey == "p410":
                    # case b2: p410
                    print(f"100 - Default tree species field will be used for p410: 100-{default_tree_species_field}")
                    feedback.pushWarning(
                        f"100 - Default tree species field will be used for p410: 100-{default_tree_species_field}")
                    fields_pX_tree_species[pkey] = default_tree_species_field

        if stands_layer.fields().indexFromName(default_tree_species_field) == -1:
            print(f"Provided default tree species field not found: {default_tree_species_field}\n"
                  "Errors can occur if p100 and p410 have no fields to read from or if NULL values occur in these columns.")
            feedback.pushWarning(f"Provided default tree species field not found: {default_tree_species_field}\n"
                                 "Errors can occur if p100 and p410 have no fields to read from or if NULL values occur in these columns.")

        # --- open XML
        print(f"\nExport to XML file:\n {output_xml}\n")
        feedback.pushInfo(f"\nExport to XML file:\n {output_xml}\n")
        i = 0
        with open(output_xml, 'a') as xml_file:

            xml_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            xml_file.write(
                '<dataroot xmlns:od="urn:schemas-microsoft-com:officedata" generated="' + currentDatetime + '">\n')
            xml_file.write('\n')

            provider = stands_layer.dataProvider()
            # --- iterate over each stand and write attributes
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

                    # --- ID, area, DG, hdom
                    xml_file.write('\t<ID>' + str(f["ID"]) + '</ID>\n')
                    xml_file.write('\t<area>' + str(f["area_m2"]) + '</area>\n')
                    xml_file.write('\t<DG_default>' + str(f["DG"]) + '</DG_default>\n')

                    # DG: set to 1 if 0/NULL
                    if f["DG"] == 0 or f["DG"] == qgis.core.NULL:
                        xml_file.write('\t<DG>' + str(1) + '</DG>\n')
                    else:
                        xml_file.write('\t<DG>' + str(f["DG"]) + '</DG>\n')

                    # hdom: set hdom = 0/NULL to 1
                    if f["hdom"] == 0 or f["hdom"] == qgis.core.NULL:
                        xml_file.write('\t<hdom>' + str(1) + '</hdom>\n')
                    else:
                        xml_file.write('\t<hdom>' + str(f["hdom"]) + '</hdom>\n')

                    xml_file.write('\t<ddom>' + str(0) + '</ddom>\n')
                    xml_file.write('\t<age>' + str(0) + '</age>\n')

                    # --- TREE SPECIES: init with 0
                    pX_tree_species_values = {
                        "p100": 0,  # Fichte
                        "p120": 0,  # Tanne
                        "p140": 0,  # Foehre
                        "p160": 0,  # Laerche
                        "p390": 0,  # Andere Nadelhoelzer
                        "p410": 0,  # Buche
                        "p420": 0,  # Eiche
                        "p430": 0,  # Esche
                        "p440": 0,  # Ahorn
                        "p800": 0  # Andere Laubhoelzer
                    }

                    # init null values flag
                    # used to display a single message if any p-Fields (other than p100/p410) contain NULL values
                    tree_species_null_flag = False

                    # iterate over tree species fields p100 - p800
                    for pkey, pvalue in pX_tree_species_values.items():
                        # check if a field for tree species are set, do nothing otherwise
                        if not fields_pX_tree_species[pkey] == "":
                            # if no tree species fields were set in the beginning, p410 is relying only on the default_tree_species_field
                            # this checks for that case and assigns 100-default_tree_species_field then
                            if (pkey == "p410") and (fields_pX_tree_species[pkey] == default_tree_species_field):
                                if not f[default_tree_species_field] == qgis.core.NULL:
                                    print(
                                        f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL, using {default_tree_species_field}")
                                    pX_tree_species_values[pkey] = 100 - f[default_tree_species_field]
                                else:
                                    print(
                                        f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL. "
                                        f"Default (\'{default_tree_species_field}\') is also NULL, using p100 = 100 / p410 = 0")
                                    pX_tree_species_values[pkey] = 0
                            else:
                                # attempt to read value, if not valid set to default (0 or NH/100 - NH)
                                if not f[fields_pX_tree_species[pkey]] == qgis.core.NULL:
                                    # read and assign anything other than NULL
                                    pX_tree_species_values[pkey] = f[fields_pX_tree_species[pkey]]
                                else:
                                    # fall back to default_tree_species_field
                                    if pkey == "p100":
                                        if not f[default_tree_species_field] == qgis.core.NULL:
                                            print(
                                                f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL, using {default_tree_species_field}")
                                            pX_tree_species_values[pkey] = f[default_tree_species_field]
                                        else:
                                            print(
                                                f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL. "
                                                f"Default (\'{default_tree_species_field}\') is also NULL, using p100 = 100")
                                            pX_tree_species_values[pkey] = 100
                                    elif pkey == "p410":
                                        if not f[default_tree_species_field] == qgis.core.NULL:
                                            print(
                                                f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL, using 100 - {default_tree_species_field}")
                                            pX_tree_species_values[pkey] = 100 - f[default_tree_species_field]
                                        else:
                                            print(
                                                f" > stand {str(f['ID'])}: {pkey} ({fields_pX_tree_species[pkey]}) is NULL. "
                                                f"Default (\'{default_tree_species_field}\') is also NULL, using p410 = 0")
                                            pX_tree_species_values[pkey] = 0
                                    else:
                                        tree_species_null_flag = True

                    if tree_species_null_flag:
                        feedback.pushWarning(f" > stand {str(f['ID'])}: tree species contained NULL values; these were set to 0")
                        print(f" > stand {str(f['ID'])}: tree species contained NULL values; these were set to 0")

                    # check whether tree species proportions add up to 100, otherwise scale up:
                    sum_tree_species = sum(pX_tree_species_values.values())
                    if not (sum_tree_species == 100):
                        feedback.pushWarning(f" > stand {str(f['ID'])}: tree species proportions add up to {sum_tree_species}%: {pX_tree_species_values.values()}")
                        print(f" > stand {str(f['ID'])}: tree species proportions add up to {sum_tree_species}%: {pX_tree_species_values.values()}")

                        if sum_tree_species == 0:
                            feedback.pushWarning(f" >\t: set to p100 = 100: {pX_tree_species_values.values()}")
                            print(f" >\t\t set to p100 = 100: {pX_tree_species_values.values()}")
                        else:
                            # multiply all values by factor
                            pX_tree_species_values.update(
                                (pkey, round(pX_tree_species_values[pkey] * (100 / sum_tree_species))) for pkey in
                                pX_tree_species_values)
                            feedback.pushWarning(
                                f" >\t: updated by factor x{100 / sum_tree_species}: {pX_tree_species_values.values()}")
                            print(
                                f" >\t\t updated by factor x{100 / sum_tree_species}: {pX_tree_species_values.values()}")

                            # make sure it is now 100 by subtraction / addition
                            sum_tree_species = sum(pX_tree_species_values.values())
                            if not (sum_tree_species == 100):
                                for pkey, pvalue in pX_tree_species_values.items():
                                    if pvalue > 0:
                                        feedback.pushWarning(
                                            f" >\t\t rounding caused deviation, adjusting first non-zero value {pkey} by {(sum_tree_species - 100)} to result to 100")
                                        print(
                                            f" >\t\t rounding caused deviation, adjusting first non-zero value {pkey} by {(sum_tree_species - 100)} to result to 100")
                                        pX_tree_species_values[pkey] = pX_tree_species_values[pkey] - (
                                                    sum_tree_species - 100)
                                        break

                    # write tree species fields to XML
                    for pkey, pvalue in pX_tree_species_values.items():
                        xml_file.write('\t<' + pkey + '>' + str(pvalue) + '</' + pkey + '>\n')

                    # --- SITE CATEGORY: use default if no field is provided
                    if field_forest_site_category == "":
                        xml_file.write('\t<siteCategory>' + default_site_category + '</siteCategory>\n')
                    else:
                        # replace NULL / 0 values with Default value
                        if f[(field_forest_site_category)] == "":
                            xml_file.write('\t<siteCategory>' + default_site_category + '</siteCategory>\n')
                        elif f[(field_forest_site_category)] == qgis.core.NULL or \
                                f[(field_forest_site_category)] == 0:
                            feedback.pushWarning(f" > stand {str(f['ID'])}: siteCategory is NULL or 0; will be set to default ({default_site_category})")
                            print(f" > stand {str(f['ID'])}: siteCategory is NULL or 0; will be set to default ({default_site_category})")
                            xml_file.write('\t<siteCategory>' + default_site_category + '</siteCategory>\n')
                        else:
                            xml_file.write('\t<siteCategory>' + str(f[(field_forest_site_category)]) + '</siteCategory>\n')

                    xml_file.write('</Stand>\n\n')
            # --- close data tag
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
