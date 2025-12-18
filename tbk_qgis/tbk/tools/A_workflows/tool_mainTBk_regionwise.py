# todo: set header

import processing
import logging
from collections import ChainMap
from osgeo import ogr

from qgis._core import QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeature, QgsProject, QgsProcessingException, QgsProcessingParameterBoolean, \
    QgsProcessingMultiStepFeedback

from tbk_qgis.tbk.general.tbk_utilities import (getVectorSaveOptions, dict_diff)
from tbk_qgis.tbk.general.persistence_utility import (read_dict_from_toml_file)
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours import \
    TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calc_crown_coverage import \
    TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion import \
    TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_append_attributes import TBkAppendStandAttributesAlgorithm
from tbk_qgis.tbk.tools.G_utility.tool_hdom_vhm_diff import TBkPostprocessHdomDiff

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
        TBkAppendStandAttributesAlgorithm()
    ]

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # Initialisation config used to adapt the output root UI description
        init_config = {
            # Indicates the tool is running in a standalone or modularized context in the initAlgorithm() method
            'is_standalone_context': False,
        }
        params = []

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

        parameter = QgsProcessingParameterBoolean('create_subdir_time', "Create subfolder with timestamp",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # --- OVERWRITE FLAG for testing/debugging

        overwrite = False
        # overwrite = True
        merge_bk_process = True

        # --- Setup parameters/config, dir and logging

        # read configuration file path
        config_path = parameters['config_file']
        if config_path:
            # Set input parameters from config file
            try:
                config = read_dict_from_toml_file(config_path)
                # compare config file parameters and tool parameters
                only_different = True
                print(f'\n------ Compare tool parameters / config -------')
                if only_different: print(f'------ show only different entries -------')
                for key, value in parameters.items():
                    try:
                        config_value = config[key]

                        # Only print if values are different (or print everything if only_different is False)
                        if only_different and value == config_value:
                            continue  # Skip if values are the same and only_different is True

                        # Convert both values to strings for length comparison
                        value_str = str(value)
                        config_value_str = str(config_value)

                        # If both string representations are shorter than 10, print side-by-side
                        if len(value_str) < 10 and len(config_value_str) < 10:
                            print(f"{key}: {value_str} || {config_value_str}")
                        else:
                            print(f"{key}:\n\t{value_str}\n\t{config_value_str}")
                    except KeyError:
                        # Skip keys not present in config
                        continue

                parameters_backup = parameters.copy()
                config_removed, config_added, config_changed = dict_diff(parameters, config)

                # apply config_file to parameters (overwrite values in parameters if they have an entry in config_file values)
                parameters.update(config)
                feedback.pushInfo(f'Read config file: ')
                feedback.pushInfo(f'Parameters overwritten through provided config file:')
                feedback.pushInfo(f'{list(config_changed.keys())}')
                feedback.pushInfo(f'Parameters not contained in config file (using values from tool-dialog/defaults):')
                feedback.pushInfo(f'{list(config_removed.keys())}')
                feedback.pushInfo(f'Unused config file parameters:')
                feedback.pushInfo(f'{list(config_added.keys())}')

                print(f'Read config file: ')
                print(f'Parameters overwritten through provided config file:')
                print(f'{list(config_changed.keys())}')
                print(f'Parameters not contained in config file (using values from tool-dialog/defaults):')
                print(f'{list(config_removed.keys())}')
                print(f'Unused config file parameters:')
                print(f'{list(config_added.keys())}')
            except FileNotFoundError:
                raise QgsProcessingException(f"The configuration file was not found at this location: {config_path}")

        # Handle the working root and temp output folder
        if parameters['create_subdir_time']:
            result_dir = self._get_result_dir(parameters['output_root'])
        else:
            result_dir = parameters['output_root']
        bk_process_dir = self._get_bk_output_dir(result_dir)
        os.makedirs(bk_process_dir, exist_ok=True)

        # set logger
        self._configure_logging(bk_process_dir, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # *************************************** #
        # --- *  Main Region-wise Processing * ---#
        # *************************************** #
        log.info('TBk Starting Region-wise Processing')

        # --- Prepare looping through regions (load regions, create folder, init arrays, setup feedback)

        # Load the perimeter vector layer from the path stored in parameters
        # to get a usable source path, the param needs to be extracted
        params = self._extract_context_params(parameters, context)
        perimeter_layer = QgsVectorLayer(params.perimeter, "perimeter", "ogr")
        if not perimeter_layer.isValid():
            raise Exception(f"Invalid perimeter layer: {perimeter_layer.source()}")
        num_regions = perimeter_layer.featureCount()
        print(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")
        log.info(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")

        # Create subfolder "regions" within result_dir
        regions_dir = os.path.join(bk_process_dir, 'regions')
        os.makedirs(regions_dir, exist_ok=True)

        # Loop over each feature in the perimeter layer
        log.info(f"Processing single regions")
        # list for storing all results
        regions_stand_map = []

        if merge_bk_process:
            regions_classified_raw = []
            regions_classified_smooth_1 = []
            regions_classified_smooth_2 = []
            regions_stands_highest_tree = []
            regions_stand_boundaries = []
            regions_stands_clipped = []
            regions_stands_merged = []
            regions_stands_simplified = []
            regions_stands_simplified2 = []

        region_ID_prefix = []

        print(f"Sorting with region attribute")
        log.info(f"Sorting with region attribute")
        # create list and sort after attribute region
        features = list(perimeter_layer.getFeatures())
        features_sorted = sorted(features, key=lambda f: f['region'])

        # initialize feedback
        # number of total_processing_steps is number of regions + merging (1)
        # + processing steps (see alg loop after merging) + local densities (2, because it's long)
        # + last step (so that the second to last step doesn't already show 100%)
        total_processing_steps = len(features_sorted) + 1 + 4 + 2 + 1
        feedback = QgsProcessingMultiStepFeedback(total_processing_steps, feedback)
        processing_step = 0

        # --- -------------------------------- ---#
        for i, feature in enumerate(features_sorted, start=1):  # perimeter_layer.getFeatures():
            # --- Create folders for current feature
            region_name = feature["region"]  # Adjust attribute name if different
            region_root_dir = os.path.join(regions_dir, str(region_name))
            region_base_data_dir = os.path.join(region_root_dir, 'base_data_preprocessed')
            region_bk_process_dir = os.path.join(region_root_dir, 'bk_process')

            os.makedirs(region_base_data_dir, exist_ok=True)

            # progress info
            processing_step = processing_step + 1
            feedback.setCurrentStep(processing_step)
            feedback.setProgressText("\n")  # insert processing log space
            feedback.setProgressText(f"Process region {region_name} :: ({i:>2} / {len(features_sorted)})")
            if feedback.isCanceled():
                return {}
            log.info(f"\n")
            log.info(f"-----------------------------------------------------")
            log.info(f"--- Processing Region {region_name} :: ({i:>2} / {len(features_sorted)}) ---")
            log.info(f"-----------------------------------------------------")
            print(f"\n-----------------------------------------------------")
            print(f"--- Processing Region {region_name} :: ({i:>2} / {len(features_sorted)}) ---")
            print(f"-----------------------------------------------------")
            print(f"to {region_base_data_dir}")

            # Construct output file path for the clipped rasters
            vhm_10m_clipped = os.path.join(region_base_data_dir, 'VHM_10m.tif')
            mg_10m_clipped = os.path.join(region_base_data_dir, 'MG_10m.tif')
            print(f"Clipping VHM10m / Coniferous raster with buffered perimeter")

            created_buffered_feature_layer = False
            if overwrite or not os.path.exists(vhm_10m_clipped) or not os.path.exists(mg_10m_clipped):
                # --- Create buffered perimeter feature layer
                buffered_feature_layer = QgsVectorLayer(f"Polygon?crs={perimeter_layer.crs().authid()}",
                                                        "buffered_mask",
                                                        "memory")
                buffered_feature = QgsFeature()
                buffered_feature.setGeometry(feature.geometry().buffer(10, 5))
                buffered_feature_layer.dataProvider().addFeature(buffered_feature)
                buffered_feature_layer.updateExtents()
                # Add the buffered layer to the map registry (otherwise it isn't found)
                QgsProject.instance().addMapLayer(buffered_feature_layer)
                created_buffered_feature_layer = True

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
                    'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
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
                    'OPTIONS': 'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                    'OUTPUT': mg_10m_clipped
                })

            if created_buffered_feature_layer:
                # --- Remove buffered layer from registry and delete it (if it was created)
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

            # region input files (clipped vhm and mg)
            parameters_region["perimeter"] = output_vector
            parameters_region["vhm_10m"] = vhm_10m_clipped
            parameters_region["coniferous_raster_for_classification"] = mg_10m_clipped

            # region outpoot roots
            parameters_region["output_root"] = region_root_dir
            parameters_region["working_root"] = region_bk_process_dir
            parameters_region["result_dir"] = region_root_dir

            parameters_region['output_stand_boundaries'] = os.path.join(region_bk_process_dir, "stand_boundaries.gpkg")
            parameters_region['h_max_input'] = os.path.join(region_bk_process_dir, "hmax.tif")

            # TODO add input parameters
            # parameters for single steps
            parameters_region["input_to_simplify"] = parameters_region["output_stand_boundaries"]
            parameters_region['stands_highest_tree'] = os.path.join(region_bk_process_dir, "stands_highest_tree.gpkg")
            parameters_region['stands_simplified'] = os.path.join(region_bk_process_dir, "stands_simplified.gpkg")

            parameters_region["input_to_clip"] = parameters_region["stands_simplified"]
            parameters_region['stands_clipped_no_gaps'] = os.path.join(region_bk_process_dir, "stands_clipped.gpkg")

            parameters_region["input_to_merge"] = parameters_region["stands_clipped_no_gaps"]
            parameters_region['stands_merged'] = os.path.join(region_bk_process_dir, "stands_merged.gpkg")

            parameters_region["input_to_clean"] = parameters_region["stands_merged"]
            parameters_region["output_stand_map_clean"] = os.path.join(region_bk_process_dir, 'TBk_Bestandeskarte.gpkg')

            parameters_region['final_stand_map_clean'] = os.path.join(region_bk_process_dir, "TBk_Bestandeskarte.gpkg")

            # --- Run Stand Delineation
            if overwrite or not os.path.exists(parameters_region["output_stand_boundaries"]):
                print(f"STAND DELINEATION: \n{parameters_region['perimeter']}")
                results_stand_delineation = processing.run(TBkStandDelineationAlgorithm(), parameters_region,
                                                           context=context, feedback=feedback)
            else:
                print(f"Skipped STAND DELINEATION, file already exists (overwrite = False)")

            # --- Simplify and eliminate
            if overwrite or not os.path.exists(parameters_region['stands_simplified']):
                print(f"SIMPLIFY & CLEAN: \n{parameters_region['output_stand_boundaries']}")
                results_simplify = processing.run(TBkSimplifyAndCleanAlgorithm(), parameters_region,
                                                  context=context, feedback=feedback)
            else:
                print(f"Skipped SIMPLIFY & CLEAN, file already exists (overwrite = False)")

            # --- Clip & Singlepart
            if overwrite or not os.path.exists(parameters_region["stands_clipped_no_gaps"]):
                print(f"CLIP: \n{parameters_region['input_to_clip']}")
                results_clipped = processing.run(TBkClipToPerimeterAndEliminateGapsAlgorithm(), parameters_region,
                                                 context=context, feedback=feedback)
            else:
                print(f"Skipped CLIP, file already exists (overwrite = False)")

            # --- Merge
            if overwrite or not os.path.exists(parameters_region["stands_merged"]):
                print(f"MERGE: \n{parameters_region['input_to_merge']}")
                algOutput = processing.run(TBkMergeSimilarNeighboursAlgorithm(), parameters_region,
                                           context=context, feedback=feedback)
            else:
                print(f"Skipped MERGE, file already exists (overwrite = False)")

            # --- Cleanup
            if overwrite or not os.path.exists(parameters_region["output_stand_map_clean"]):
                algOutput = processing.run("TBk:TBk postprocess Cleanup", parameters_region,
                                           context=context, feedback=feedback)
            else:
                print(f"Skipped cleanup, file already exists (overwrite = False)")

            # --- Collect regions and ID/name
            regions_stand_map.append(parameters_region["output_stand_map_clean"])
            # collect bk_process results as well
            if merge_bk_process:
                # add alg outputs
                regions_stand_boundaries.append(parameters_region["output_stand_boundaries"])
                regions_stands_merged.append(parameters_region["stands_merged"])
                regions_stands_clipped.append(parameters_region["stands_clipped_no_gaps"])
                regions_stands_simplified.append(parameters_region["stands_simplified"])

                regions_classified_raw.append(
                    os.path.join(region_root_dir, 'bk_process', 'classified_raw.tif'))
                regions_classified_smooth_1.append(
                    os.path.join(region_root_dir, 'bk_process', 'classified_smooth_1.tif'))
                regions_classified_smooth_2.append(
                    os.path.join(region_root_dir, 'bk_process', 'classified_smooth_2.tif'))
                regions_stands_highest_tree.append(
                    os.path.join(region_root_dir, 'bk_process', 'stands_highest_tree.gpkg'))

            region_ID_prefix.append(feature["region"])
            print(f"-----------------------------------------------------")
            print(f"--- completed {region_ID_prefix} :: ({i:>2} / {len(features_sorted)})  ---")
            print(f"-----------------------------------------------------\n")
            log.info(f"-----------------------------------------------------")
            log.info(f"--- completed {region_ID_prefix} :: ({i:>2} / {len(features_sorted)})  ---")
            log.info(f"-----------------------------------------------------")
            log.info(f"\n")

        # --- -------------------------------- ---#

        # --- Merge stand map

        # progress info
        feedback.setProgressText("\n\n") # insert processing log space
        processing_step = processing_step + 1
        feedback.setCurrentStep(processing_step)
        feedback.setProgressText("Merging of regions")
        if feedback.isCanceled():
            return {}
        print(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"Layer results per region: \n{regions_stand_map}")

        # write to working dir for compatibility with the following tools
        merged = os.path.join(bk_process_dir, 'stands_clipped.gpkg')

        # if True or not os.path.exists(merged): # force overwrite
        if overwrite or not os.path.exists(merged):
            print(f"Now merging into one single Stand Map")
            processing.run("TBk:TBk postprocess merge stand maps", {
                'tbk_map_layers': regions_stand_map,
                'id_prefix': 2,  # '2' corresponds to the "custom" option
                'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
                'OUTPUT': merged
            })

        else:
            print(f"Skipped Region merge, file already exists (overwrite = False)")

        # --- Merge bk process

        if merge_bk_process:
            # Mapping each list to a name (for vector data)
            gpkg_to_merge = {
                'stand_boundaries': regions_stand_boundaries,
                'stands_merged': regions_stands_merged,
                'stands_clipped': regions_stands_clipped,
                'stands_simplified': regions_stands_simplified,
                'stands_highest_tree': regions_stands_highest_tree,
            }

            # Mapping for raster data
            raster_to_merge = {
                'classified_raw': regions_classified_raw,
                'classified_smooth_1': regions_classified_smooth_1,
                'classified_smooth_2': regions_classified_smooth_2,
            }

            # Handle vector data
            for list_name, region_list_item in gpkg_to_merge.items():
                # Set up the output file path for vector data
                merged = os.path.join(bk_process_dir, f'{list_name}.gpkg')

                # Check if we need to overwrite or if the file doesn't exist
                if overwrite or not os.path.exists(merged):
                    print(f"Now merging {list_name} regions into one single vector file")
                    processing.run("TBk:TBk postprocess merge stand maps", {
                        'tbk_map_layers': region_list_item,  # List of vector layers to merge
                        'id_prefix': 2,  # Custom prefix
                        'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
                        'OUTPUT': merged  # Output path for the merged vector file
                    })

            # Handle raster data
            for list_name, region_list_item in raster_to_merge.items():
                # Set up the output file path for raster data
                merged_raster = os.path.join(bk_process_dir, f'{list_name}.tif')

                # Check if we need to overwrite or if the file doesn't exist
                if overwrite or not os.path.exists(merged_raster):
                    print(f"Now merging {list_name} regions into one single raster file")

                    # Run raster merging using GDAL (or appropriate processing tool for rasters)
                    processing.run("gdal:merge", {
                        'INPUT': region_list_item,  # List of raster layers to merge
                        'OUTPUT': merged_raster,  # Output path for the merged raster file
                        'NODATA_INPUT': 0,  # Define NoData value in input rasters
                        'NODATA_OUTPUT': 0,  # Define NoData value in output raster
                        'DATA_TYPE': 4,  # Use the same data type as inputs
                        'SEPARATE': False,  # False ensures layers are merged, not stacked
                        'PREFERRED': 'FIRST'  # Keeps the first valid data (prevents overwriting)
                    })

        # *************************************** #
        # ---   ***  TBk Attributierung    *** ---#
        # *************************************** #

        # prepare parameters for running multiple tbk algorithms
        parameters["result_dir"] = result_dir
        parameters["working_dir"] = bk_process_dir

        # set outputs of the individual tools (for toolchain)
        parameters['stands_clipped_no_gaps'] = os.path.join(parameters["working_dir"], "stands_clipped.gpkg")
        parameters['stands_dg'] = os.path.join(parameters["working_dir"], "stands_dg.gpkg")  # out calc_dg > in calc_nh
        parameters['dg_layer'] = os.path.join(parameters["result_dir"], "dg_layers", "dg_layer.tif")  # > in calc_nh
        parameters['stands_dg_nh'] = os.path.join(parameters["working_dir"],
                                                  "stands_dg_nh.gpkg")  # out calc_nh > in add_attributes
        parameters["input_to_attribute"] = parameters['stands_dg_nh']  # > in add_attributes
        parameters['stands_dg_nh_vegZone'] = os.path.join(parameters["working_dir"],
                                                          "stands_dg_nh_vegZone.gpkg")  # out add_attributes

        parameters['tbk_bestandesgrenzen'] = parameters['stands_dg_nh_vegZone']  # in diff_hdom_vhm
        parameters['diff_hdom_vhm'] = os.path.join(parameters["working_dir"], "diff_hdom_vhm.tif")  # out diff_hdom_vhm
        # construct points filename vhm_10m_points.gpkg from vhm_10m.tif
        parameters['vhm_10m_points'] = os.path.splitext(params.vhm_10m)[0] + "_points.gpkg"  # out diff_hdom_vhm

        parameters['final_stand_map'] = os.path.join(parameters["result_dir"],
                                                     'TBk_Bestandeskarte.gpkg')  # out finalize

        algorithms_attributation = [
            TBkCalculateCrownCoverageAlgorithm(),
            TBkAddConiferousProportionAlgorithm(),
            TBkAppendStandAttributesAlgorithm(),
            TBkPostprocessHdomDiff()
            # cleanup is not included as the region maps are already cleaned up
        ]

        # run remaining algorithms
        for alg in algorithms_attributation:
            # progress info
            processing_step = processing_step + 1
            feedback.setCurrentStep(processing_step)
            feedback.setProgressText(alg.name())
            if feedback.isCanceled():
                return {}
            print("->------------------------------------------")
            print(f"-> run {alg.name()} -")
            result = processing.run(alg, parameters, context=context, feedback=feedback)
            print(f"{result}")
            print("----------------------------------------->|-\n")

        print("\n--------------------------------------------")
        print("\n--- Final cleanup and appends ---")
        finalize_TBk(parameters['stands_dg_nh_vegZone'], parameters['final_stand_map'])
        print("--------------------------------------------")

        print("\n--------------------------------------------")
        print("\n--- Run Local Densities ---")
        # progress info
        processing_step = processing_step + 1
        feedback.setCurrentStep(processing_step)
        feedback.setProgressText("Calculate local densities (can take a while)")
        if feedback.isCanceled():
            return {}

        processing.run("TBk:TBk postprocess local density", {
            'path_tbk_input': result_dir,
            'mg_use': True,
            'mg_input': parameters["coniferous_raster"],
            'tbk_input_file': 'TBk_Bestandeskarte.gpkg', 'output_suffix': '',
            'table_density_classes': [1, 85, 100, 7, 2, 60, 85, 14, 3, 40, 60, 14, 4, 25, 40, 14, 5, 0, 25, 7, 12, 60,
                                      100, 14],
            'calc_all_dg': True, 'min_size_clump': 1200, 'min_size_stand': 1200, 'holes_thresh': 400,
            'buffer_smoothing': True,
            'buffer_smoothing_dist': 7, 'save_unclipped': False, 'grid_cell_size': 3})
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


import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeature, QgsField
from PyQt5.QtCore import QVariant


def finalize_TBk(input_layer, output_layer):
    # remove unnecessary fields and change order
    algoOutput = processing.run("native:refactorfields", {
        'INPUT': input_layer,
        'FIELDS_MAPPING': [
            {'alias': '', 'comment': '', 'expression': '"fid"', 'length': 0, 'name': 'fid', 'precision': 0,
             'sub_type': 0, 'type': 4, 'type_name': 'int8'},
            {'alias': '', 'comment': '', 'expression': '"ID"', 'length': 0, 'name': 'ID', 'precision': 0, 'sub_type': 0,
             'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"hmax"', 'length': 0, 'name': 'hmax', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"hdom"', 'length': 0, 'name': 'hdom', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"DG"', 'length': 0, 'name': 'DG', 'precision': 0, 'sub_type': 0,
             'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"NH"', 'length': 0, 'name': 'NH', 'precision': 0, 'sub_type': 0,
             'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"area_m2"', 'length': 0, 'name': 'area_m2', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"type"', 'length': 1000, 'name': 'type', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
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
            {'alias': '', 'comment': '', 'expression': '"NH_OS"', 'length': 0, 'name': 'NH_OS', 'precision': 0,
             'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"VegZone_Code"', 'length': 0, 'name': 'VegZone_Code',
             'precision': 0, 'sub_type': 0, 'type': 2, 'type_name': 'integer'},
            {'alias': '', 'comment': '', 'expression': '"ID_meta"', 'length': 0, 'name': 'ID_meta', 'precision': 0,
             'sub_type': 0, 'type': 10, 'type_name': 'text'},
            {'alias': '', 'comment': '', 'expression': '"ID_pre_merge"', 'length': 0, 'name': 'ID_pre_merge',
             'precision': 0, 'sub_type': 0, 'type': 4, 'type_name': 'int8'}], 'OUTPUT': 'TEMPORARY_OUTPUT'})

    processing.run("native:fieldcalculator", {
        'INPUT': algoOutput['OUTPUT'],
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
                f"{region_id}-{original_id}",  # Composite ID (ID field)
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
