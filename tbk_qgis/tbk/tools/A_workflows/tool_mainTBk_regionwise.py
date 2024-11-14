# todo: set header
import os

import processing
import logging
from collections import ChainMap

from qgis._core import QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeature, QgsProject, QgsWkbTypes, QgsProcessing

from tbk_qgis.tbk.general.tbk_utilities import getVectorSaveOptions
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours_algorithm import \
    TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch_algorithm import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calculate_crown_coverage_algorithm import \
    TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion_algorithm import \
    TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_update_stand_attributes_algorithm import \
    TBkUpdateStandAttributesAlgorithm
from tbk_qgis.tbk.tools.G_utility.tool_postprocess_merge_stand_maps import TBkPostprocessMergeStandMaps

from osgeo import ogr

from tbk_qgis.tbk.tools.E_postproc_attributes.tool_append_attributes_algorithm import TBkAppendStandAttributesAlgorithm

ogr.UseExceptions()  # To avoid warnings, though this isn't necessary in future versions.


class TBkAlgorithmRegionwise(TBkProcessingAlgorithmToolA):
    """
    todo
    """
    # array containing the algorithms to use
    algorithms = [
        TBkStandDelineationAlgorithm(),
        TBkSimplifyAndCleanAlgorithm(),
        TBkMergeSimilarNeighboursAlgorithm(),
        TBkClipToPerimeterAndEliminateGapsAlgorithm(),
        TBkCalculateCrownCoverageAlgorithm(),
        TBkAddConiferousProportionAlgorithm(),
        TBkUpdateStandAttributesAlgorithm()
    ]

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # Initialisation config used to adapt the output root UI description
        init_config = {'output_root': {'name': "output_root", 'description': "Output folder"}}

        # init all used algorithm and add their parameters to parameters list
        for alg in self.algorithms:
            alg.initAlgorithm(init_config)
            alg_params = alg.parameterDefinitions()
            alg_params_dict = {p.name(): p for p in alg_params}
            params.append(alg_params_dict)

        # parameters chain map used as a simple way to avoid duplicate parameter
        params_chain = ChainMap(*params)

        unique_param_definitions = list(params_chain.values())
        for param in unique_param_definitions:
            if param.name() != 'working_root':
                self.addParameter(param.clone())

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # --- OVERWRITE FLAG for testing/debugging
        overwrite = False

        # Handle the working root and temp output folder
        output_root = parameters["output_root"]

        # set logger
        self._configure_logging(output_root, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # *************************************** #
        # --- *  Main Region-wise Processing * ---#
        # *************************************** #
        log.info('TBk Starting Region-wise Processing')

        # Load the perimeter vector layer from the path stored in parameters
        perimeter_layer = QgsVectorLayer(parameters["perimeter"], "perimeter", "ogr")
        if not perimeter_layer.isValid():
            raise Exception(f"Invalid perimeter layer: {perimeter_layer.source()}")
        num_regions = perimeter_layer.featureCount()
        log.info(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")
        print(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")

        # Create subfolder "regions" within output_root
        regions_dir = os.path.join(output_root, 'regions')
        os.makedirs(regions_dir, exist_ok=True)

        # Loop over each feature in the perimeter layer
        log.info(f"Processing single regions")
        # list for storing all results
        region_stand_maps = []
        region_ID_prefix = []
        for feature in perimeter_layer.getFeatures():
            # --- Setup
            region_name = feature["region"]  # Adjust attribute name if different
            region_root_dir = os.path.join(regions_dir, region_name)
            region_base_data_dir = os.path.join(region_root_dir, 'base_data_preprocessed')
            os.makedirs(region_base_data_dir, exist_ok=True)
            print(f"\n--------------------------------")
            print(f"--- Processing Region {region_name} ---")
            print(f"--------------------------------")
            print(f"to {region_base_data_dir}")

            # --- Create buffered perimeter feature layer
            buffered_feature_layer = QgsVectorLayer(f"Polygon?crs={perimeter_layer.crs().authid()}", "buffered_mask",
                                                    "memory")
            buffered_feature = QgsFeature()
            buffered_feature.setGeometry(feature.geometry().buffer(10, 5))
            buffered_feature_layer.dataProvider().addFeature(buffered_feature)
            buffered_feature_layer.updateExtents()
            # Add the buffered layer to the map registry (otherwise it isn't found)
            QgsProject.instance().addMapLayer(buffered_feature_layer)

            # Construct output file path for the clipped rasters
            vhm_10m_clipped = os.path.join(region_base_data_dir, 'VHM_10m.tif')
            mg_10m_clipped = os.path.join(region_base_data_dir, 'MG_10m.tif')
            print(f"Clipping VHM10m / Coniferous raster with buffered perimeter")

            if overwrite or not os.path.exists(vhm_10m_clipped):
                # Clip VHM with buffered mask
                processing.run("gdal:cliprasterbymasklayer", {
                    'INPUT': parameters["vhm_10m"],
                    'MASK': QgsProcessingFeatureSourceDefinition(
                        buffered_feature_layer.source(),
                        selectedFeaturesOnly=False,
                        featureLimit=1,
                        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                    ),
                    'OUTPUT': vhm_10m_clipped
                })

            if overwrite or not os.path.exists(mg_10m_clipped):
                # Clip Coniferous raster with buffered perimeter
                processing.run("gdal:cliprasterbymasklayer", {
                    'INPUT': parameters["coniferous_raster_for_classification"],
                    'MASK': QgsProcessingFeatureSourceDefinition(
                        buffered_feature_layer.source(),
                        selectedFeaturesOnly=False,
                        featureLimit=1,
                        geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                    ),
                    'OUTPUT': mg_10m_clipped
                })

            # --- Remove buffered layer from registry and delete it
            QgsProject.instance().removeMapLayer(buffered_feature_layer.id())
            buffered_feature_layer = None  # Ensures layer is dereferenced

            # Construct the output path for the vector file (GeoPackage)
            output_vector = os.path.join(region_base_data_dir, f'perimeter_{region_name}.gpkg')

            if overwrite or not os.path.exists(output_vector):
                # Create and populate the single-feature layer
                perimeter_single_feature = QgsVectorLayer(f"Polygon?crs={perimeter_layer.crs().authid()}",
                                                          f"perimeter_{region_name}", "memory")
                perimeter_single_feature_data = perimeter_single_feature.dataProvider()
                perimeter_single_feature_data.addAttributes(perimeter_layer.fields())
                perimeter_single_feature.updateFields()
                perimeter_single_feature_data.addFeature(feature)

                # Commit changes to the layer before saving
                perimeter_single_feature.commitChanges()

                # Save the single feature layer to the GeoPackage
                ctc = QgsProject.instance().transformContext()
                error = QgsVectorFileWriter.writeAsVectorFormatV3(
                    perimeter_single_feature,  # The memory layer
                    output_vector,  # output file path
                    ctc,  # CRS
                    getVectorSaveOptions('GPKG', 'utf-8')
                )

                # Check for errors
                if error != QgsVectorFileWriter.NoError:
                    print(f"Error while saving {output_vector}: {error}")
                else:
                    print(f"Successfully saved {region_name} perimeter to {output_vector}")

            # --- Configure parameters for region

            # copy parent parameters and adjust only those relevant for the region
            parameters_region = parameters.copy()
            parameters_region["config_file"] = ""
            parameters_region["perimeter"] = output_vector
            parameters_region["vhm_10m"] = vhm_10m_clipped
            parameters_region["coniferous_raster_for_classification"] = mg_10m_clipped
            parameters_region["output_root"] = region_root_dir
            parameters_region["working_root"] = os.path.join(region_root_dir, 'bk_process')
            parameters_region["result_dir"] = region_root_dir
            # todo: some of these paths are still hardcoded, need to be dynamic
            parameters_region["output_stand_delineation"] = os.path.join(region_root_dir, 'bk_process',
                                                                         'stand_boundaries.gpkg')
            # --- Run Stand Delineation
            if overwrite or not os.path.exists(parameters_region["output_stand_delineation"]):
                print(f"STAND DELINEATION: \n{parameters_region['perimeter']}")
                results_stand_delineation = processing.run(TBkStandDelineationAlgorithm(), parameters_region,
                                                           context=context, feedback=feedback)
            else:
                print(f"Skipped STAND DELINEATION, file already exists (overwrite = False)")

            parameters_region["input_to_simplify"] = parameters_region["output_stand_delineation"]
            parameters_region["output_simplified"] = os.path.join(region_root_dir, 'bk_process',
                                                                  'stands_simplified.gpkg')
            # --- Simplify and eliminate
            if overwrite or not os.path.exists(parameters_region["output_simplified"]):
                print(f"SIMPLIFY & CLEAN: \n{parameters_region['input_to_simplify']}")
                results_simplify = processing.run(TBkSimplifyAndCleanAlgorithm(), parameters_region,
                                                  context=context, feedback=feedback)
            else:
                print(f"Skipped SIMPLIFY & CLEAN, file already exists (overwrite = False)")

            parameters_region["input_to_clip"] = parameters_region["output_simplified"]
            parameters_region["output_clipped"] = os.path.join(region_root_dir, 'bk_process', 'stands_clipped.gpkg')

            # --- Clip & Singlepart
            if overwrite or not os.path.exists(parameters_region["output_clipped"]):
                print(f"CLIP: \n{parameters_region['input_to_clip']}")
                results_clipped = processing.run(TBkClipToPerimeterAndEliminateGapsAlgorithm(), parameters_region,
                                                 context=context, feedback=feedback)
            else:
                print(f"Skipped CLIP, file already exists (overwrite = False)")

            # --- Merge
            parameters_region["input_to_merge"] = parameters_region["output_clipped"]
            parameters_region["output_merged"] = os.path.join(region_root_dir, 'bk_process', 'stands_merged.gpkg')

            if overwrite or not os.path.exists(parameters_region["output_merged"]):
                print(f"MERGE: \n{parameters_region['input_to_merge']}")
                algOutput = processing.run(TBkMergeSimilarNeighboursAlgorithm(), parameters_region,
                                           context=context, feedback=feedback)
            else:
                print(f"Skipped MERGE, file already exists (overwrite = False)")

            # --- Eliminate second pass
            parameters_region["input_to_simplify_2"] = parameters_region["output_merged"]
            parameters_region["output_simplified_2"] = os.path.join(region_root_dir, 'bk_process',
                                                                    'stands_simplified_2.gpkg')
            # remove small and elongated polygons
            # expression = f"with_variable('shape_index', $area / ($perimeter^2) * 100, " \
            #              f"($area < {parameters_region['min_area_m2']})" \
            #              f"OR (shape_index < 1.5 AND $area < ({parameters_region['min_area_m2']} + 500) AND \"hdom\" < 10)" \
            #              f"OR (shape_index < 2.05 AND $area < ({parameters_region['min_area_m2']} + 500) AND \"type\" = 'remainder')" \
            #              f"OR (shape_index < 2.2 AND \"type\" = 'remainder')"
            expression = f"with_variable('shape_index', $area / ($perimeter^2) * 100, " \
                         f"($area < {parameters_region['min_area_m2']}) " \
                         f"OR (@shape_index < 1.5 AND $area < ({parameters_region['min_area_m2']} + 500) AND hdom < 10) " \
                         f"OR (@shape_index < 2.05 AND $area < ({parameters_region['min_area_m2']} + 500) AND type = 'remainder') " \
                         f"OR (@shape_index < 2.2 AND type = 'remainder'))"

            if overwrite or not os.path.exists(parameters_region["output_simplified_2"]):
                print(f"Second ELIMINATE pass: \n{parameters_region['output_simplified_2']}")
                # Select by area_attribute
                alg_params = {
                    'EXPRESSION': expression,
                    'INPUT': algOutput['OUTPUT'],
                    'METHOD': 0,  # creating new selection
                }
                algOutput = processing.run('qgis:selectbyexpression', alg_params, context=context,
                                           feedback=feedback, is_child_algorithm=True)

                # processing.run("native:saveselectedfeatures", {
                #     'INPUT': algOutput['OUTPUT'],
                #     'OUTPUT': 'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/regions/test_select.gpkg'})

                # Eliminate selected polygons
                alg_params = {
                    'INPUT': algOutput['OUTPUT'],
                    'MODE': 2,  # Largest Common Boundary
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }
                algOutput = processing.run('qgis:eliminateselectedpolygons', alg_params,
                                           context=context, feedback=feedback,
                                           is_child_algorithm=True)
                # Field calculator
                alg_params = {
                    'FIELD_LENGTH': 0,
                    'FIELD_NAME': "area_m2",
                    'FIELD_PRECISION': 0,
                    'FIELD_TYPE': 0,  # Decimal (double)
                    'FORMULA': '$area',
                    'INPUT': algOutput['OUTPUT'],
                    'OUTPUT': parameters_region["output_simplified_2"]
                }
                algOutput = processing.run('native:fieldcalculator', alg_params, context=context,
                                           feedback=feedback, is_child_algorithm=True)
            else:
                print(f"Skipped second eliminate, file already exists (overwrite = False)")

            # --- Cleanup
            parameters_region["input_to_clean"] = parameters_region["output_simplified_2"]
            parameters_region["output_clean"] = os.path.join(region_root_dir, 'bk_process', 'stands_clean.gpkg')

            if overwrite or not os.path.exists(parameters_region["output_clean"]):
                algOutput = processing.run("TBk:TBk postprocess Cleanup",
                                           {'input_stand_map': parameters_region["input_to_clean"],
                                            'output_stand_map_clean': parameters_region["output_clean"]})
            else:
                print(f"Skipped cleanup, file already exists (overwrite = False)")

            # --- Collect regions and ID/name
            region_stand_maps.append(parameters_region["output_clean"])
            region_ID_prefix.append(feature["region"])
            print(f"--------------------------------")
            print(f"--- completed {region_ID_prefix} ---")
            print(f"--------------------------------\n\n")

        # --- -------------------------------- ---#

        # --- Merge
        print(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"Layer results per region: \n{region_stand_maps}")

        # write to working dir for compatibility with the following tools
        os.makedirs(os.path.join(output_root, 'bk_process'), exist_ok=True)
        merged = os.path.join(output_root, 'bk_process', 'stands_clipped.gpkg')
        # merged = os.path.join(output_root, 'bk_process', 'tbk_regions_merged.gpkg')
        # merged = os.path.join(regions_dir, 'tbk_regions_merged.gpkg')
        # if overwrite or not os.path.exists(parameters_region["output_simplified_2"]):
        if True or not os.path.exists(parameters_region["output_simplified_2"]):
            print(f"Now merging into one single Stand Map")
            processing.run("TBk:TBk postprocess merge stand maps", {
                'tbk_map_layers': region_stand_maps,
                'id_prefix': 2,  # '2' corresponds to the "custom" option
                'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
                'OUTPUT': merged
            })

            processing.run("TBk:TBk postprocess merge stand maps", {'tbk_map_layers': [
                'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/regions/A/bk_process/stands_merged.gpkg|layername=stands_merged',
                'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/regions/B/bk_process/stands_merged.gpkg|layername=stands_merged',
                'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/regions/C/bk_process/stands_merged.gpkg|layername=stands_merged'],
                                                                    'id_prefix': 0, 'custom_prefix_list': '',
                                                                    'OUTPUT': 'TEMPORARY_OUTPUT'})
        else:
            print(f"Skipped Region merge, file already exists (overwrite = False)")

        # *************************************** #
        # ---   ***  TBk Attributierung    *** ---#
        # *************************************** #

        # prepare for running multiple tbk algorithms
        parameters["result_dir"] = output_root
        parameters["working_dir"] = os.path.join(output_root, 'bk_process')
        parameters["input_to_attribute"] = os.path.join(output_root, 'bk_process', 'tmp', 'stands_attributed_tmp.gpkg')
        parameters["output_attributed"] = os.path.join(output_root, 'bk_process', 'stands_attributed.gpkg')

        algorithms_attributation = [
            TBkCalculateCrownCoverageAlgorithm(),
            TBkAddConiferousProportionAlgorithm(),
            TBkUpdateStandAttributesAlgorithm(),
            TBkAppendStandAttributesAlgorithm()
        ]

        # run remaining algorithms
        for alg in algorithms_attributation:
            # print("->------------------------------------------")
            result = processing.run(alg, parameters, context=context, feedback=feedback)
            print(f"{result}")
            print("----------------------------------------->|-\n")

        print("\n--------------------------------------------")
        print("\n--- Final cleanup and appends ---")
        finalize_TBk(result['OUTPUT'], os.path.join(output_root, 'TBk_Bestandeskarte.gpkg'))
        print("--------------------------------------------")

        print(f"\n---------------------------------")
        print(f"--- COMPLETED REGION-WISE TBk ---")
        print(f"---------------------------------\n")
        return {}

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkAlgorithmRegionwise()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate BK Regionwise'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')


from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsVectorFileWriter, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeature, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant

import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeature, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant


def finalize_TBk(input_layer, output_layer):
    # remove unnecessary fields and change order
    processing.run("native:refactorfields", {
        'INPUT': input_layer,
        'FIELDS_MAPPING': [
            {'alias': '', 'comment': '', 'expression': '"fid"', 'length': 0, 'name': 'fid', 'precision': 0,
             'sub_type': 0, 'type': 4, 'type_name': 'int8'},
            {'alias': '', 'comment': '', 'expression': '"ID"', 'length': 0, 'name': 'ID', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"hmax"', 'length': 0, 'name': 'hmax', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"hdom"', 'length': 0, 'name': 'hdom', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG"', 'length': 0, 'name': 'DG', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"NH"', 'length': 0, 'name': 'NH', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"area_m2"', 'length': 0, 'name': 'area_m2', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_ks"', 'length': 0, 'name': 'DG_ks', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_us"', 'length': 0, 'name': 'DG_us', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_ms"', 'length': 0, 'name': 'DG_ms', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_os"', 'length': 0, 'name': 'DG_os', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG_ueb"', 'length': 0, 'name': 'DG_ueb', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"struktur"', 'length': 0, 'name': 'struktur',
             'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"tbk_typ"', 'length': 0, 'name': 'tbk_typ', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"ID_meta"', 'length': 0, 'name': 'ID_meta', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"ID_pre_merge"', 'length': 0, 'name': 'ID_pre_merge',
             'precision': 0, 'sub_type': 0, 'type': 4, 'type_name': 'int8'},
            {'alias': '', 'comment': '', 'expression': '"VegZone_Code"', 'length': 0, 'name': 'VegZone_Code',
             'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'}],
        'OUTPUT': 'TEMPORARY_OUTPUT'})

    processing.run("native:fieldcalculator", {
        'INPUT': 'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/bk_process/tmp/TBk_Bestandeskarte_vegZone3.gpkg|layername=TBk_Bestandeskarte_vegZone3',
        'FIELD_NAME': 'PH_STRUCTURE', 'FIELD_TYPE': 1, 'FIELD_LENGTH': 0, 'FIELD_PRECISION': 0,
        'FORMULA': 'if("VegZone_Code" IN (-1, 0, 1, 2, 4, 5), \r\n    if("NH">50,\r\n        if("hdom">=26, \r\n            if("DG_os" + "DG_ueb" >= 45, \r\n                if("DG_ms" >= 35,\r\n                4,\r\n                    if("DG_ms">=25,\r\n                        if("DG_us" >=20,\r\n                            3,\r\n                            2\r\n                        ),\r\n                        if("DG_ms">=15,\r\n                            if("DG_us">=10,\r\n                                2,\r\n                                1\r\n                            ),\r\n                            if("DG_us">=10,\r\n                                1,\r\n                                0\r\n                            )\r\n                        )\r\n                    )\r\n                ),\r\n                5\r\n            ), \r\n            if("hdom">18,\r\n                -1, \r\n                if("hdom">10,\r\n                    -2,\r\n                    -3\r\n                )\r\n            )\r\n        ),\r\n        if("hdom">=23, \r\n            if("DG_os" + "DG_ueb" >= 45, \r\n                if("DG_ms" >= 35,\r\n                    4,\r\n                    if("DG_ms">=25,\r\n                        if("DG_us" >=20,\r\n                            3,\r\n                            2\r\n                        ),\r\n                        if("DG_ms">=15,\r\n                            if("DG_us">=10,\r\n                                2,\r\n                                1\r\n                            ),\r\n                            if("DG_us">=10,\r\n                                1,\r\n                                0\r\n                            )\r\n                        )\r\n                    )\r\n                ),\r\n            5), \r\n            if("hdom">16,\r\n                -1, \r\n                if("hdom">9,\r\n                    -2,\r\n                    -3\r\n                )\r\n            )\r\n        )\r\n    ),\r\n    if ("VegZone_Code" IN (6, 7),\r\n        if("NH">50,\r\n            if("hdom">=23, \r\n                if("DG_os" + "DG_ueb" >= 45, \r\n                    if("DG_ms" >= 35,\r\n                    4,\r\n                        if("DG_ms">=25,\r\n                            if("DG_us" >=20,\r\n                                3,\r\n                                2\r\n                            ),\r\n                            if("DG_ms">=15,\r\n                                if("DG_us">=10,\r\n                                    2,\r\n                                    1\r\n                                ),\r\n                                if("DG_us">=10,\r\n                                    1,\r\n                                    0\r\n                                )\r\n                            )\r\n                        )\r\n                    ),\r\n                    5\r\n                ), \r\n                if("hdom">16,\r\n                    -1, \r\n                    if("hdom">9,\r\n                        -2,\r\n                        -3\r\n                    )\r\n                )\r\n            ),\r\n            if("hdom">=19, \r\n                if("DG_os" + "DG_ueb" >= 45, \r\n                    if("DG_ms" >= 35,\r\n                        4,\r\n                        if("DG_ms">=25,\r\n                            if("DG_us" >=20,\r\n                                3,\r\n                                2\r\n                            ),\r\n                            if("DG_ms">=15,\r\n                                if("DG_us">=10,\r\n                                    2,\r\n                                    1\r\n                                ),\r\n                                if("DG_us">=10,\r\n                                    1,\r\n                                    0\r\n                                )\r\n                            )\r\n                        )\r\n                    ),\r\n                5), \r\n                if("hdom">13,\r\n                    -1, \r\n                    if("hdom">7,\r\n                        -2,\r\n                        -3\r\n                    )\r\n                )\r\n            )\r\n        ),\r\n        if("VegZone_Code" IN (8),\r\n            if("NH">50,\r\n                if("hdom">=19, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                        4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                        5\r\n                    ), \r\n                    if("hdom">13,\r\n                        -1, \r\n                        if("hdom">7,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                ),\r\n                if("hdom">=16, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                            4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                    5), \r\n                    if("hdom">11,\r\n                        -1, \r\n                        if("hdom">6,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                )\r\n            ),\r\n            if("NH">50,\r\n                if("hdom">=16, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                        4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                        5\r\n                    ), \r\n                    if("hdom">11,\r\n                        -1, \r\n                        if("hdom">6,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                ),\r\n                if("hdom">=13, \r\n                    if("DG_os" + "DG_ueb" >= 45, \r\n                        if("DG_ms" >= 35,\r\n                            4,\r\n                            if("DG_ms">=25,\r\n                                if("DG_us" >=20,\r\n                                    3,\r\n                                    2\r\n                                ),\r\n                                if("DG_ms">=15,\r\n                                    if("DG_us">=10,\r\n                                        2,\r\n                                        1\r\n                                    ),\r\n                                    if("DG_us">=10,\r\n                                        1,\r\n                                        0\r\n                                    )\r\n                                )\r\n                            )\r\n                        ),\r\n                    5), \r\n                    if("hdom">9,\r\n                        -1, \r\n                        if("hdom">5,\r\n                            -2,\r\n                            -3\r\n                        )\r\n                    )\r\n                )\r\n            )\r\n        )\r\n    )\r\n)\r\n\r\n',
        'OUTPUT': output_layer})

def merge_layers_with_composite_id(vector_paths, region_ids, output_path):
    """
    Merges multiple vector layers into a single layer, adding a composite ID.

    Parameters:
        vector_paths (list): List of paths to the vector layers to be merged.
        region_ids (list): List of region IDs corresponding to each vector layer.
        output_path (str): Path to save the merged output layer.
    """

    # Verify inputs
    if len(vector_paths) != len(region_ids):
        raise ValueError("The number of region IDs must match the number of vector paths.")

    # Remove existing output file if it exists
    if os.path.exists(output_path):
        os.remove(output_path)

    # Create an empty memory layer for merging
    crs = QgsProject.instance().crs()  # Assume all layers share project CRS
    merged_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "merged_layer", "memory")
    merged_data_provider = merged_layer.dataProvider()

    # Fields to include in the merged layer
    merged_data_provider.addAttributes([
        QgsField("ID", QVariant.String),
        QgsField("ID_inRegion", QVariant.String)
    ])
    merged_layer.updateFields()

    # Iterate through each vector layer and region ID
    for path, region_id in zip(vector_paths, region_ids):
        # Attempt to load the layer
        layer = QgsVectorLayer(path, "temp_layer", "ogr")

        if not layer.isValid():
            print(f"Error: Could not load the layer from path: {path}")
            continue  # Skip this layer if it couldn't be loaded

        # Ensure the original layer has an "ID" field
        if "ID" not in [field.name() for field in layer.fields()]:
            print(f"Warning: Layer at {path} does not contain an 'ID' field. Skipping this layer.")
            continue

        # Process features and add them to the merged layer
        for feature in layer.getFeatures():
            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())

            # Set the composite ID and original ID fields
            original_id = feature["ID"]
            new_feature.setAttributes([
                f"{region_id}_{original_id}",  # Composite ID (ID field)
                original_id  # Original ID (ID_inRegion field)
            ])

            merged_data_provider.addFeature(new_feature)

    # Define output options and write the merged layer to a file
    output_options = QgsVectorFileWriter.SaveVectorOptions()
    output_options.driverName = "GPKG"
    output_options.fileEncoding = "UTF-8"
    output_options.layerName = "stands_regions_merged"  # Explicit layer name

    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        merged_layer,
        output_path,
        QgsProject.instance().transformContext(),
        output_options
    )

    # Check for errors during the write operation
    if error == QgsVectorFileWriter.NoError:
        print(f"Successfully saved merged layer to {output_path}")
    else:
        print(f"Error: Could not save merged layer to {output_path}. Error code: {error}")
