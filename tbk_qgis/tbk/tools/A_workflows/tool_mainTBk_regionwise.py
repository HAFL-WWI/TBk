# todo: set header

import processing
import logging
import traceback
from collections import ChainMap
from osgeo import ogr

from qgis.PyQt.QtWidgets import QApplication
from qgis._core import QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeature, QgsProject, QgsProcessingException, QgsProcessingParameterBoolean, \
    QgsProcessingMultiStepFeedback, QgsProcessingParameterField, QgsWkbTypes

from tbk_qgis.tbk.general.tbk_utilities import (getVectorSaveOptions, dict_diff, finalize_TBk, SubprocessTimer)
from tbk_qgis.tbk.general.persistence_utility import (read_dict_from_toml_file, write_dict_to_toml_file)
from tbk_qgis.tbk.general.qgis_processing_utility import QgsUtility
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
from tbk_qgis.tbk.tools.G_utility.tool_create_TBk_project import TBkCreateProject

import gc
import time
from datetime import timedelta
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

        self.addParameter(
            QgsProcessingParameterField('fieldname_region',
                                        'Perimeter Region-ID Field (each unique name/ID in this field will be processed separately)',
                                        type=QgsProcessingParameterField.Any,
                                        parentLayerParameterName='perimeter', allowMultiple=False,
                                        defaultValue='region'))

        parameter = QgsProcessingParameterBoolean('create_subdir_time', "Create subfolder with timestamp",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean('calc_local_density', "Calculate local densities (can take a while)",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        try:
            return self._processAlgorithm(parameters, context, feedback)
        except Exception:
            # Many child steps only report progress via print()/logging, which can be silently
            # invisible depending on QGIS version/session state (GitHub issue #5/#6). Make sure
            # a failure always surfaces its real traceback in the Processing log, not just a bare
            # "Execution failed".
            feedback.reportError(traceback.format_exc(), fatalError=True)
            raise

    def _processAlgorithm(self, parameters, context, feedback):
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

        # Write the resolved workflow parameters (including any config_file overrides applied
        # above, and with layer parameters resolved to their source paths) as a TOML file in
        # the run's bk_process_dir, so the full run - not just individual steps - has a
        # persisted record of what was actually used. Named distinctly from "input_config.txt"
        # (see tool_mainTBk.py) for consistency, even though per-region child steps here write
        # into their own region subdirectories, not this bk_process_dir.
        try:
            write_dict_to_toml_file(self._extract_context_params(parameters, context).__dict__, bk_process_dir,
                                    file_name="workflow_input_config.txt")
        except Exception:
            feedback.pushWarning('The TOML file was not written in the output folder because an error occurred')

        # set logger
        self._configure_logging(bk_process_dir, parameters['logfile_name'], context)
        log = logging.getLogger(self.name())

        # elapsed time helper — timestamps prefixed [W …] distinguish main-workflow
        # log lines from sub-algorithm output (which resets to [0:00:00] at each call)
        start_time = time.time()
        def elapsed():
            return str(timedelta(seconds=round(time.time() - start_time)))
        def wf_log(msg):
            full = f"[W {elapsed()}] {msg}"
            log.info(full)
            print(full)
            feedback.pushInfo(full)

        wf_log("====================================================================")
        wf_log(f"START WORKFLOW: {self.name()}")
        wf_log("====================================================================")

        # *************************************** #
        # --- *  Main Region-wise Processing * ---#
        # *************************************** #
        log.info('TBk Starting Region-wise Processing')

        # --- Prepare looping through regions (load regions, create folder, init arrays, setup feedback)

        # Load the perimeter vector layer from the path stored in parameters
        # to get a usable source path, the param needs to be extracted
        # TODO: this tackles the same issue as the newly implemented QgsUtility.ensure_vector_layer, however can't handle memory layers (parameterAsFeatureSource())... should be handled consistently.
        params = self._extract_context_params(parameters, context)

        # perimeter_layer = QgsVectorLayer(params.perimeter, "perimeter", "ogr")
        perimeter_layer = QgsUtility.ensure_vector_layer(params.perimeter, context)
        if not perimeter_layer.isValid():
            raise Exception(f"Invalid perimeter layer: {perimeter_layer.source()}")

        fieldname_region = parameters['fieldname_region']
        num_regions = perimeter_layer.featureCount()

        # dissolve by fieldname_region (avoid redundant IDs overwriting each others result when being subsequently processed)
        print(f"Loaded perimeter {perimeter_layer.source()}\n Dissolving {num_regions} regions by {fieldname_region}.")
        log.info(f"Loaded perimeter {perimeter_layer.source()}\n Dissolving {num_regions} regions by {fieldname_region}.")
        perimeter_layer = processing.run("native:dissolve", {
            'INPUT': perimeter_layer,
            'FIELD': [fieldname_region],
            'SEPARATE_DISJOINT': False,
            'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
        # create layer from memory layer ID
        perimeter_layer = QgsUtility.ensure_vector_layer(perimeter_layer, context)

        num_regions = perimeter_layer.featureCount()
        print(f"Regionwise processing for {num_regions} regions with unique {fieldname_region}.")
        log.info(f"Regionwise processing for {num_regions} regions with unique {fieldname_region}.")

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
        features_sorted = sorted(features, key=lambda f: f[fieldname_region])

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
            region_name = feature[fieldname_region]  # Adjust attribute name if different
            region_start = time.time()
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

            # region-scoped, indented sub-timeline: [R …] resets to 0:00:00 for each region,
            # distinguishing it from the workflow's own [W …] timeline and other regions' output
            wf_log(f"-> Region {region_name} ({i}/{len(features_sorted)})")
            region_indent = '    '
            def region_log(msg):
                line = f"{region_indent}{msg}"
                log.info(line)
                print(line)
                feedback.pushInfo(line)
            def region_step(msg):
                region_log(f"[R {str(timedelta(seconds=round(time.time() - region_start)))}] {msg}")

            # (no region_log() header here - setProgressText() above already echoed
            # "Process region ..." and wf_log() above already logged the "-> Region ..." entry)
            region_log("-------------------------------")
            region_log(f"to {region_base_data_dir}")

            # Construct the output path for the vector files (GeoPackage)
            output_vector = os.path.join(region_base_data_dir, f'perimeter_{region_name}.gpkg')
            perimeter_buffered = os.path.join(region_base_data_dir, f'perimeter_{region_name}_buffered.gpkg')
            print(f"Creating Vector Masks")

            # --- Create perimeter feature layer
            if overwrite or not _step_output_done(output_vector):
                # Delete existing file
                if os.path.exists(output_vector):
                    os.remove(output_vector)

                geom = feature.geometry()
                if not geom.isGeosValid():
                    geom = geom.makeValid()

                _write_single_feature_gpkg(perimeter_layer, geom, feature.attributes(),
                                            "perimeter", output_vector)
                _mark_step_output_done(output_vector)
                print(f"Successfully saved perimeter {region_name} to {output_vector}")

            if overwrite or not _step_output_done(perimeter_buffered):
                # --- Create buffered perimeter feature layer
                if os.path.exists(perimeter_buffered):
                    os.remove(perimeter_buffered)

                # Safe geometry handling
                geom = feature.geometry()
                if not geom.isGeosValid():
                    geom = geom.makeValid()

                _write_single_feature_gpkg(perimeter_layer, geom.buffer(11, 5), feature.attributes(),
                                            "perimeter_buffered", perimeter_buffered)
                _mark_step_output_done(perimeter_buffered)
                print(f"Successfully saved buffered perimeter to {perimeter_buffered}")

            # Construct output file path for the clipped rasters
            vhm_10m_clipped = os.path.join(region_base_data_dir, 'VHM_10m.tif')
            mg_10m_clipped = os.path.join(region_base_data_dir, 'MG_10m.tif')
            print(f"Clipping VHM10m / Coniferous raster with buffered perimeter")

            if overwrite or not _step_output_done(vhm_10m_clipped):
                # Clip VHM with buffered mask
                processing.run("gdal:cliprasterbymasklayer", {
                    'INPUT': parameters["vhm_10m"],
                    'MASK': perimeter_buffered,
                    # 'MASK': buffered_feature_layer,
                    'OPTIONS': parameters['gdal_create_options'],
                    'OUTPUT': vhm_10m_clipped
                })
                if not os.path.exists(vhm_10m_clipped):
                    raise QgsProcessingException(
                        f"Clipping VHM raster for region {region_name} produced no output file "
                        f"({vhm_10m_clipped}). The buffered perimeter mask ({perimeter_buffered}) "
                        f"may be empty or not overlap the input VHM raster.")
                _mark_step_output_done(vhm_10m_clipped)

            if overwrite or not _step_output_done(mg_10m_clipped):
                # Clip Coniferous raster with buffered perimeter
                processing.run("gdal:cliprasterbymasklayer", {
                    'INPUT': parameters["coniferous_raster_for_classification"],
                    'MASK': perimeter_buffered,
                    'OPTIONS': parameters['gdal_create_options'],
                    'OUTPUT': mg_10m_clipped
                })
                if not os.path.exists(mg_10m_clipped):
                    raise QgsProcessingException(
                        f"Clipping coniferous raster for region {region_name} produced no output file "
                        f"({mg_10m_clipped}). The buffered perimeter mask ({perimeter_buffered}) "
                        f"may be empty or not overlap the input raster.")
                _mark_step_output_done(mg_10m_clipped)

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
            if overwrite or not _step_output_done(parameters_region["output_stand_boundaries"]):
                region_step("-> stand delineation")
                step_start = time.time()
                results_stand_delineation = processing.run(TBkStandDelineationAlgorithm(), parameters_region,
                                                           context=context, feedback=feedback)
                _mark_step_output_done(parameters_region["output_stand_boundaries"])
                region_step(f"<- stand delineation done ({str(timedelta(seconds=round(time.time() - step_start)))})")
            else:
                region_log(f"Skipped stand delineation, file already exists (overwrite = False)")

            # --- Simplify and eliminate
            if overwrite or not _step_output_done(parameters_region['stands_simplified']):
                region_step("-> simplify & clean")
                step_start = time.time()
                results_simplify = processing.run(TBkSimplifyAndCleanAlgorithm(), parameters_region,
                                                  context=context, feedback=feedback)
                _mark_step_output_done(parameters_region['stands_simplified'])
                region_step(f"<- simplify & clean done ({str(timedelta(seconds=round(time.time() - step_start)))})")
            else:
                region_log(f"Skipped simplify & clean, file already exists (overwrite = False)")

            # --- Clip & Singlepart
            if overwrite or not _step_output_done(parameters_region["stands_clipped_no_gaps"]):
                region_step("-> clip to perimeter and eliminate gaps")
                step_start = time.time()
                results_clipped = processing.run(TBkClipToPerimeterAndEliminateGapsAlgorithm(), parameters_region,
                                                 context=context, feedback=feedback)
                _mark_step_output_done(parameters_region["stands_clipped_no_gaps"])
                region_step(f"<- clip to perimeter and eliminate gaps done ({str(timedelta(seconds=round(time.time() - step_start)))})")
            else:
                region_log(f"Skipped clip, file already exists (overwrite = False)")

            # --- Merge
            if overwrite or not _step_output_done(parameters_region["stands_merged"]):
                region_step("-> merge similar neighbours")
                step_start = time.time()
                algOutput = processing.run(TBkMergeSimilarNeighboursAlgorithm(), parameters_region,
                                           context=context, feedback=feedback)
                _mark_step_output_done(parameters_region["stands_merged"])
                region_step(f"<- merge similar neighbours done ({str(timedelta(seconds=round(time.time() - step_start)))})")
            else:
                region_log(f"Skipped merge, file already exists (overwrite = False)")

            # --- Cleanup
            if overwrite or not _step_output_done(parameters_region["output_stand_map_clean"]):
                region_step("-> postprocess cleanup")
                step_start = time.time()
                algOutput = processing.run("TBk:TBk postprocess Cleanup", parameters_region,
                                           context=context, feedback=feedback)
                _mark_step_output_done(parameters_region["output_stand_map_clean"])
                region_step(f"<- postprocess cleanup done ({str(timedelta(seconds=round(time.time() - step_start)))})")
            else:
                region_log(f"Skipped cleanup, file already exists (overwrite = False)")

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

            region_ID_prefix.append(feature[fieldname_region])
            region_log("-------------------------------")
            region_elapsed = str(timedelta(seconds=round(time.time() - region_start)))
            wf_log(f"<- Region {region_name} ({i}/{len(features_sorted)}) done — region: {region_elapsed}, total: {elapsed()}")

            # --- cleanup after each loop iteration

            # avoid leaking of Layer Objects (in case if parameters holds QgsMapLayer objects)
            del parameters_region
            # delete all temporary layers
            # context.temporaryLayerStore().removeAllMapLayers()
            # Let the UI thread flush before continuing:
            QApplication.processEvents()
            # forces cleanup of unused objects in memory (on Python-level objects)
            gc.collect()

        # --- -------------------------------- ---#

        # --- Merge stand map

        # progress info
        feedback.setProgressText("\n\n")  # insert processing log space
        processing_step = processing_step + 1
        feedback.setCurrentStep(processing_step)
        feedback.setProgressText("Merging of regions")
        if feedback.isCanceled():
            return {}
        print(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"All {len(region_ID_prefix)} Regions processed: \n{region_ID_prefix}")
        log.info(f"Layer results per region: \n{regions_stand_map}")

        # write to working dir for compatibility with the following tools
        merged = os.path.join(bk_process_dir, 'stands_regions_merged.gpkg')

        # if True or not os.path.exists(merged): # force overwrite
        if overwrite or not _step_output_done(merged):
            print(f"Now merging into one single Stand Map")
            processing.run("TBk:TBk postprocess merge stand maps", {
                'tbk_map_layers': regions_stand_map,
                'id_prefix': 2,  # '2' corresponds to the "custom" option
                'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
                'OUTPUT': merged
            })
            _mark_step_output_done(merged)

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
                if overwrite or not _step_output_done(merged):
                    print(f"Now merging {list_name} regions into one single vector file")
                    processing.run("TBk:TBk postprocess merge stand maps", {
                        'tbk_map_layers': region_list_item,  # List of vector layers to merge
                        'id_prefix': 2,  # Custom prefix
                        'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
                        'OUTPUT': merged  # Output path for the merged vector file
                    })
                    _mark_step_output_done(merged)

            # Handle raster data
            for list_name, region_list_item in raster_to_merge.items():
                # Set up the output file path for raster data
                merged_raster = os.path.join(bk_process_dir, f'{list_name}.tif')

                # Check if we need to overwrite or if the file doesn't exist
                if overwrite or not _step_output_done(merged_raster):
                    print(f"Now merging {list_name} regions into one single raster file")

                    # Run raster merging using GDAL (or appropriate processing tool for rasters)
                    processing.run("gdal:merge", {
                        'INPUT': region_list_item,  # List of raster layers to merge
                        'OUTPUT': merged_raster,  # Output path for the merged raster file
                        'NODATA_INPUT': 0,  # Define NoData value in input rasters
                        'NODATA_OUTPUT': 0,  # Define NoData value in output raster
                        'DATA_TYPE': 4,  # Use the same data type as inputs
                        'SEPARATE': False,  # False ensures layers are merged, not stacked
                        'PREFERRED': 'FIRST',  # Keeps the first valid data (prevents overwriting)
                        'OPTIONS': parameters['gdal_create_options']
                    })
                    _mark_step_output_done(merged_raster)

        # *************************************** #
        # ---   ***  TBk Attributierung    *** ---#
        # *************************************** #

        # prepare parameters for running multiple tbk algorithms
        parameters["result_dir"] = result_dir
        parameters["working_dir"] = bk_process_dir

        # set outputs of the individual tools (for toolchain)
        parameters['stands_clipped_no_gaps'] = os.path.join(parameters["working_dir"], "stands_regions_merged.gpkg")
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


        # --- run remaining algorithms (skip if output exists and overwrite = False)
        attribution_algs_and_outputs = [
            (TBkCalculateCrownCoverageAlgorithm(), parameters['stands_dg']),
            (TBkAddConiferousProportionAlgorithm(), parameters['stands_dg_nh']),
            (TBkAppendStandAttributesAlgorithm(), parameters['stands_dg_nh_vegZone']),
            (TBkPostprocessHdomDiff(), parameters['diff_hdom_vhm']),
            (TBkCreateProject(), os.path.join(parameters["result_dir"], 'TBk_Project.qgz')),
            # cleanup tool is not included as the region maps are already cleaned up
        ]

        for alg, skip_output in attribution_algs_and_outputs:
            # progress info (no setProgressText() here - it echoes into the Processing log as
            # a bare duplicate of the wf_log "-> alg.name()" line right below it)
            processing_step = processing_step + 1
            feedback.setCurrentStep(processing_step)
            if feedback.isCanceled():
                return {}
            if not overwrite and skip_output and _step_output_done(skip_output):
                print(f"Skipped {alg.name()}, output already exists (overwrite = False)")
                feedback.pushInfo(f"Skipped {alg.name()}, output already exists (overwrite = False)")
                continue
            wf_log(f"-> {alg.name()}")
            alg_start = time.time()
            result = processing.run(alg, parameters, context=context, feedback=feedback)
            if skip_output:
                _mark_step_output_done(skip_output)
            alg_elapsed = str(timedelta(seconds=round(time.time() - alg_start)))
            wf_log(f"<- {alg.name()} done ({alg_elapsed})")

        print("\n--------------------------------------------")
        print("\n--- Final cleanup and appends ---")
        feedback.pushInfo("\n--------------------------------------------")
        feedback.pushInfo("\n--- Final cleanup and appends ---")
        if overwrite or not _step_output_done(parameters['final_stand_map']):
            if os.path.exists(parameters['final_stand_map']):
                os.remove(parameters['final_stand_map'])
            finalize_TBk(parameters['stands_dg_nh_vegZone'], parameters['final_stand_map'])
            _mark_step_output_done(parameters['final_stand_map'])
        else:
            print(f"Skipped final cleanup, output already exists (overwrite = False)")
            feedback.pushInfo(f"Skipped final cleanup, output already exists (overwrite = False)")
        print("--------------------------------------------")
        feedback.pushInfo("--------------------------------------------")

        # progress info
        processing_step = processing_step + 1
        feedback.setCurrentStep(processing_step)
        feedback.setProgressText("Calculate local densities (can take a while)")
        if feedback.isCanceled():
            return {}

        if parameters['calc_local_density']:
            local_density_output = os.path.join(result_dir, "local_densities", "TBk_local_densities.gpkg")
            if overwrite or not _step_output_done(local_density_output):
                wf_log("-> local density")
                ld_start = time.time()
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
                _mark_step_output_done(local_density_output)
                ld_elapsed = str(timedelta(seconds=round(time.time() - ld_start)))
                wf_log(f"<- local density done ({ld_elapsed})")
            else:
                wf_log(f"Skipped local density, output already exists (overwrite = False)")
        else:
            wf_log("Skipped local density (calc_local_density = False)")

        # Run finished successfully end-to-end: the .done markers used to resume an
        # interrupted run have no further purpose and would otherwise clutter the
        # deliverable (some sit right next to TBk_Bestandeskarte.gpkg/TBk_Project.qgz
        # in result_dir). Only reached on full success — a cancelled/failed run must
        # keep them so the next resume attempt can tell what's genuinely done.
        _cleanup_step_markers(result_dir)

        wf_log("====================================================================")
        wf_log(f"FINISHED — total processing time: {elapsed()} (h:min:sec)")
        wf_log("====================================================================")
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


def _write_single_feature_gpkg(source_layer, geometry, attributes, layer_name, output_path):
    """
    Write a single feature to a new GeoPackage in one pass.

    Avoids the write-full-layer / reopen / truncate / addFeature pattern, which can
    silently leave an empty file if the reopened GPKG isn't fully committed yet
    (observed on Windows). Raises QgsProcessingException if the write fails or the
    resulting file ends up without the feature, instead of failing silently.
    """
    single_layer = QgsVectorLayer(
        f"{QgsWkbTypes.displayString(source_layer.wkbType())}?crs={source_layer.crs().authid()}",
        layer_name, "memory")
    provider = single_layer.dataProvider()
    provider.addAttributes(source_layer.fields())
    single_layer.updateFields()

    feat = QgsFeature(single_layer.fields())
    feat.setGeometry(geometry)
    feat.setAttributes(attributes)
    if not provider.addFeature(feat):
        raise QgsProcessingException(f"Failed to add feature to in-memory layer for {output_path}")

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.fileEncoding = "UTF-8"
    options.layerName = layer_name
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile

    write_result = QgsVectorFileWriter.writeAsVectorFormatV3(
        single_layer, output_path, QgsProject.instance().transformContext(), options)
    error, error_msg = write_result[0], write_result[1]
    if error != QgsVectorFileWriter.NoError:
        raise QgsProcessingException(f"Failed to write {output_path}: {error_msg}")

    written_layer = QgsVectorLayer(output_path, layer_name, "ogr")
    if not written_layer.isValid() or written_layer.featureCount() == 0:
        raise QgsProcessingException(f"Wrote {output_path} but it contains no features")


def _step_output_done(output_path):
    """
    True only if output_path exists AND a companion ".done" marker exists.

    A bare os.path.exists() on a step's output is not a reliable "step is fully done"
    signal for resuming an interrupted run: several TBk sub-algorithms write/commit their
    main output incrementally (e.g. calculate_dg.py commits stands_dg.gpkg before any of
    its six dg_layer_*.tif byproducts exist, and again after), so a process killed mid-step
    can leave an output file that exists but is incomplete. The marker is only ever written
    by _mark_step_output_done(), immediately after the step's processing.run() call returned
    without raising — it can't be left behind by a step that got killed mid-way.
    """
    return bool(output_path) and os.path.exists(output_path) and os.path.exists(output_path + ".done")


def _mark_step_output_done(output_path):
    open(output_path + ".done", 'w').close()


def _cleanup_step_markers(root_dir):
    """
    Remove all ".done" resume markers under root_dir. Call only once the whole workflow
    has finished successfully — the markers exist solely to let an interrupted run resume
    correctly, and are meaningless (and visible clutter, some sitting next to the final
    deliverables) once the run is complete.
    """
    for dirpath, _dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".done"):
                os.remove(os.path.join(dirpath, filename))


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
