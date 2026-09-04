# todo: set header
import processing
import os
import time
import logging
import traceback
from collections import ChainMap
from datetime import timedelta

from qgis._core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingMultiStepFeedback
from tbk_qgis.tbk.general.tbk_utilities import finalize_TBk
from tbk_qgis.tbk.general.persistence_utility import write_dict_to_toml_file
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours import \
    TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calc_crown_coverage import \
    TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_append_attributes import \
    TBkAppendStandAttributesAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion import \
    TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.G_utility.tool_postprocess_cleanup import TBkPostprocessCleanup
from tbk_qgis.tbk.tools.G_utility.tool_hdom_vhm_diff import TBkPostprocessHdomDiff
from tbk_qgis.tbk.tools.G_utility.tool_create_TBk_project import TBkCreateProject
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA


class TBkAlgorithmMainWorkflow(TBkProcessingAlgorithmToolA):
    """
    todo
    """
    # required by the inherited prepare(), which reads this parameter to merge config_file
    # overrides into `parameters` before processAlgorithm() runs
    CONFIG_FILE = "config_file"

    # array containing the algorithms to use
    algorithms = [
        TBkStandDelineationAlgorithm(),
        TBkSimplifyAndCleanAlgorithm(),
        TBkMergeSimilarNeighboursAlgorithm(),
        TBkClipToPerimeterAndEliminateGapsAlgorithm(),
        TBkCalculateCrownCoverageAlgorithm(),
        TBkAddConiferousProportionAlgorithm(),
        TBkAppendStandAttributesAlgorithm(),
        TBkPostprocessCleanup(),
    ]

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # Initialisation config used to adapt the tool if run in a modularized context.
        init_config = {
            # Indicates the tool is running in a standalone or modularized context in the initAlgorithm() method
            'is_standalone_context': False,
        }

        # init all used algorithm and add there parameters to parameters list
        for alg in self.algorithms:
            alg.initAlgorithm(init_config)

            # Append the child parameters definitions to this algorithm
            alg_params = alg.parameterDefinitions()
            alg_params_dict = {p.name(): p for p in alg_params}
            params.append(alg_params_dict)

        # parameters chain map used as a simple way to avoid duplicate parameter
        params_chain = ChainMap(*params)

        unique_param_definitions = list(params_chain.values())
        for param in unique_param_definitions:
            if param.name() != 'working_root':
                self.addParameter(param.clone())

        parameter = QgsProcessingParameterBoolean('create_subdir_time', "Create subfolder with timestamp", defaultValue=True)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean('calc_local_density', "Calculate local densities (can take a while)",
                                                  defaultValue=False)
        self.addParameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(12, feedback)
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
        # merges config_file overrides into `parameters` (in place) before anything below reads
        # from it, matching every individual TBk tool's own behavior
        self.prepare(parameters, context, feedback)

        intermediate_results = {}
        main_results = {}
        outputs = {}

        # set the stand map output directory and file
        if parameters['create_subdir_time']:
            result_dir = self._get_result_dir(parameters['output_root'])
        else: result_dir = parameters['output_root']
        bk_process_dir = self._get_bk_output_dir(result_dir)
        parameters['stands_clean'] = os.path.join(bk_process_dir, "stands_clean.gpkg")
        parameters['final_stand_map'] = os.path.join(result_dir, "TBk_Bestandeskarte.gpkg")

        # Write the resolved workflow parameters (including any config_file overrides, and with
        # layer parameters resolved to their source paths) as a TOML file in the run's
        # bk_process_dir, so the full run - not just individual steps - has a persisted record
        # of what was actually used. Named distinctly from "input_config.txt" - several child
        # steps (stand delineation, simplify & clean) share this same bk_process_dir as their
        # own working_root and write *their* own input_config.txt into it later in the run,
        # which would otherwise silently overwrite this one with just that step's subset.
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
            feedback.pushInfo(full)

        wf_log("====================================================================")
        wf_log(f"START WORKFLOW: {self.name()}")
        wf_log("====================================================================")

        # --- 1 Delineate Stand

        wf_log("-> 1 Delineate Stand")
        step_start = time.time()

        # create output filename parameters
        parameters['output_stand_boundaries'] = os.path.join(bk_process_dir, "stand_boundaries.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'coniferous_raster_for_classification': parameters['coniferous_raster_for_classification'],
            'del_tmp': parameters['del_tmp'],
            'description': parameters['description'],
            'logfile_name': parameters['logfile_name'],
            'max_corr': parameters['max_corr'],
            'max_tol': parameters['max_tol'],
            'min_cells_per_pure_stand': parameters['min_cells_per_pure_stand'],
            'min_cells_per_stand': parameters['min_cells_per_stand'],
            'min_corr': parameters['min_corr'],
            'min_tol': parameters['min_tol'],
            'min_valid_cells': parameters['min_valid_cells'],
            'vhm_10m': parameters['vhm_10m'],
            'vhm_max_height': parameters['vhm_max_height'],
            'vhm_min_height': parameters['vhm_min_height'],
            'output_root': result_dir,
            'output_stand_boundaries': parameters['output_stand_boundaries'],
        }
        outputs['DelineateStand'] = processing.run('TBk:1 Delineate Stand', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)

        # store outputs in dict
        intermediate_results['h_max_input'] = outputs['DelineateStand']['output_h_max']
        intermediate_results['classified_raw'] = outputs['DelineateStand']['classified_raw']
        intermediate_results['classified_smooth_1'] = outputs['DelineateStand']['classified_smooth_1']
        intermediate_results['classified_smooth_2'] = outputs['DelineateStand']['classified_smooth_2']
        intermediate_results['stand_boundaries'] = outputs['DelineateStand']['output_stand_boundaries']
        wf_log(f"<- 1 Delineate Stand done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # --- 2 Simplify and Clean

        wf_log("-> 2 Simplify and Clean")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_simplified'] = os.path.join(bk_process_dir, "stands_simplified.gpkg")
        parameters['stands_highest_tree'] = os.path.join(bk_process_dir, "stands_highest_tree.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'h_max_input': outputs['DelineateStand']['output_h_max'],
            'input_to_simplify': outputs['DelineateStand']['output_stand_boundaries'],
            'logfile_name': parameters['logfile_name'],
            'min_area_m2': parameters['min_area_m2'],
            'simplification_tolerance': parameters['simplification_tolerance'],
            'smoothing': parameters['smoothing'],
            'working_root': result_dir,
            'stands_simplified': parameters['stands_simplified'],
            'stands_highest_tree': parameters['stands_highest_tree'],
        }
        outputs['SimplifyAndClean'] = processing.run('TBk:2 Simplify and Clean', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)

        # store outputs in dict
        intermediate_results['stands_simplified'] = outputs['SimplifyAndClean']['stands_simplified']
        intermediate_results['stands_highest_tree'] = outputs['SimplifyAndClean']['stands_highest_tree']
        wf_log(f"<- 2 Simplify and Clean done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # --- 3 Merge similar neighbours (FM)

        wf_log("-> 3 Merge similar neighbours (FM)")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_merged'] = os.path.join(bk_process_dir, "stands_merged.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'input_to_merge': outputs['SimplifyAndClean']['stands_simplified'],
            'logfile_name': parameters['logfile_name'],
            'similar_neighbours_hdom_diff_rel': parameters['similar_neighbours_hdom_diff_rel'],
            'similar_neighbours_min_area': parameters['similar_neighbours_min_area'],
            'working_root': result_dir,
            'stands_merged': parameters['stands_merged'],
        }
        outputs['MergeSimilarNeighboursFm'] =  processing.run('TBk:3 Merge similar neighbours (FM)', alg_params,
                              context=context, feedback=feedback,
                              is_child_algorithm=True)

        # store outputs in dict
        intermediate_results['stands_merged'] = outputs['MergeSimilarNeighboursFm']['stands_merged']
        wf_log(f"<- 3 Merge similar neighbours (FM) done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # --- 4 Clip to perimeter and eliminate gaps

        wf_log("-> 4 Clip to perimeter and eliminate gaps")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_clipped_no_gaps'] = os.path.join(bk_process_dir, "stands_clipped.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'input_to_clip': outputs['MergeSimilarNeighboursFm']['stands_merged'],
            'stands_highest_tree': outputs['SimplifyAndClean']['stands_highest_tree'],
            'logfile_name': parameters['logfile_name'],
            'perimeter': parameters['perimeter'],
            'working_root': result_dir,
            'stands_clipped_no_gaps': parameters['stands_clipped_no_gaps']
        }
        outputs['ClipToPerimeterAndEliminateGaps'] =  processing.run('TBk:4 Clip to perimeter and eliminate gaps',
                              alg_params, context=context, feedback=feedback,
                              is_child_algorithm=True)

        # store outputs in dict
        intermediate_results['stands_clipped_no_gaps'] = outputs['ClipToPerimeterAndEliminateGaps']['stands_clipped_no_gaps']
        wf_log(f"<- 4 Clip to perimeter and eliminate gaps done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # --- 5 Calculate crown coverage

        wf_log("-> 5 Calculate crown coverage")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_dg'] = os.path.join(bk_process_dir, "stands_dg.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'gdal_create_options': parameters['gdal_create_options'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': result_dir,
            'stands_clipped_no_gaps': outputs['ClipToPerimeterAndEliminateGaps']['stands_clipped_no_gaps'],
            'stands_dg': parameters['stands_dg'],
            'vhm_150cm': parameters['vhm_150cm']
        }
        outputs['CalculateCrownCoverage'] =  processing.run('TBk:5 Calculate crown coverage', alg_params,
                              context=context, feedback=feedback,
                              is_child_algorithm=True)

        # store outputs in dict
        intermediate_results['stands_dg'] = outputs['CalculateCrownCoverage']['stands_dg']

        main_results['dg_layer_main'] = outputs['CalculateCrownCoverage']['dg_layer_main']
        main_results['dg_layer_ks'] = outputs['CalculateCrownCoverage']['dg_layer_ks']
        main_results['dg_layer_us'] = outputs['CalculateCrownCoverage']['dg_layer_us']
        main_results['dg_layer_ms'] = outputs['CalculateCrownCoverage']['dg_layer_ms']
        main_results['dg_layer_os'] = outputs['CalculateCrownCoverage']['dg_layer_os']
        main_results['dg_layer_ueb'] = outputs['CalculateCrownCoverage']['dg_layer_ueb']
        wf_log(f"<- 5 Calculate crown coverage done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # --- 6 Add coniferous proportion

        wf_log("-> 6 Add coniferous proportion")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_dg_nh'] = os.path.join(bk_process_dir, "stands_dg_nh.gpkg")

        # compile params and run tool
        alg_params = {
            'calc_mixture_for_main_layer': parameters['calc_mixture_for_main_layer'],
            'config_file': parameters['config_file'],
            'coniferous_raster': parameters['coniferous_raster'],
            'del_tmp': parameters['del_tmp'],
            'dg_layer': outputs['CalculateCrownCoverage']['dg_layer_main'],
            'gdal_create_options': parameters['gdal_create_options'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': result_dir,
            'stands_dg': outputs['CalculateCrownCoverage']['stands_dg'],
            'stands_dg_nh': parameters['stands_dg_nh'],
        }
        outputs['AddConiferousProportion'] =  processing.run('TBk:6 Add coniferous proportion', alg_params,
                              context=context, feedback=feedback,
                              is_child_algorithm=True)
        wf_log(f"<- 6 Add coniferous proportion done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # --- Append stand attributes

        wf_log("-> Append stand attributes")
        step_start = time.time()

        # create output filename parameters
        parameters['stands_dg_nh_vegZone'] = os.path.join(bk_process_dir, "stands_dg_nh_vegZone.gpkg")

        # compile params and run tool
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'forestSiteDefault': parameters['forestSiteDefault'],
            'forestSiteLayer': parameters['forestSiteLayer'],
            'forestSiteLayerField': parameters['forestSiteLayerField'],
            'input_to_attribute': outputs['AddConiferousProportion']['stands_dg_nh'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': result_dir,
            'vegZoneDefault': parameters['vegZoneDefault'],
            'vegZoneLayer': parameters['vegZoneLayer'],
            'vegZoneLayerField': parameters['vegZoneLayerField'],
            'stands_dg_nh_vegZone': parameters['stands_dg_nh_vegZone']
        }
        outputs['AppendStandAttributes'] =  processing.run('TBk:Append stand attributes', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)
        wf_log(f"<- Append stand attributes done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # --- TBk postprocess Cleanup

        wf_log("-> TBk postprocess Cleanup")
        step_start = time.time()

        # compile params and run tool
        alg_params = {
            'input_to_clean': outputs['AppendStandAttributes']['stands_dg_nh_vegZone'],
            'output_stand_map_clean': parameters['stands_clean'],
            'result_dir': result_dir,
            'logfile_name': parameters['logfile_name'],
        }
        outputs['TbkPostprocessCleanup'] = processing.run('TBk:TBk postprocess Cleanup', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)
        wf_log(f"<- TBk postprocess Cleanup done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # --- TBk postprocess Hdom diff

        wf_log("-> TBk postprocess Hdom diff")
        step_start = time.time()

        alg_params = {
            'tbk_bestandesgrenzen': outputs['TbkPostprocessCleanup']['OUTPUT'],
            'vhm_10m': parameters['vhm_10m'],
            'diff_hdom_vhm': os.path.join(bk_process_dir, "diff_hdom_vhm.tif"),
            'vhm_10m_points': os.path.splitext(parameters['vhm_10m'])[0] + "_points.gpkg",
        }
        outputs['PostprocessHdomDiff'] = processing.run(TBkPostprocessHdomDiff(), alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)
        wf_log(f"<- TBk postprocess Hdom diff done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # --- TBk create QGIS Project (.qgz)

        wf_log("-> TBk create QGIS Project (.qgz)")
        step_start = time.time()

        alg_params = {
            'config_file': parameters['config_file'],
            'result_dir': result_dir,
            'vhm_10m': parameters['vhm_10m'],
            'vhm_150cm': parameters['vhm_150cm'],
            'coniferous_raster_for_classification': parameters['coniferous_raster_for_classification'],
            'coniferous_raster': parameters['coniferous_raster'],
        }
        outputs['CreateProject'] = processing.run(TBkCreateProject(), alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)
        wf_log(f"<- TBk create QGIS Project (.qgz) done ({str(timedelta(seconds=round(time.time() - step_start)))})")

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # --- Finalize: normalize field schema, calculate PH_STRUCTURE, recalculate area_m2

        finalize_TBk(outputs['TbkPostprocessCleanup']['OUTPUT'], parameters['final_stand_map'])
        main_results['TBk_Bestandeskarte'] = parameters['final_stand_map']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # --- Calculate local densities (optional)

        if parameters['calc_local_density']:
            wf_log("-> local density")
            step_start = time.time()
            processing.run("TBk:TBk postprocess local density", {
                'path_tbk_input': result_dir,
                'mg_use': True,
                'mg_input': parameters["coniferous_raster"],
                'tbk_input_file': 'TBk_Bestandeskarte.gpkg', 'output_suffix': '',
                'table_density_classes': [1, 85, 100, 7, 2, 60, 85, 14, 3, 40, 60, 14, 4, 25, 40, 14, 5, 0, 25, 7, 12, 60,
                                          100, 14],
                'calc_all_dg': True, 'min_size_clump': 1200, 'min_size_stand': 1200, 'holes_thresh': 400,
                'buffer_smoothing': True,
                'buffer_smoothing_dist': 7, 'save_unclipped': False, 'grid_cell_size': 3
            }, context=context, feedback=feedback, is_child_algorithm=True)
            wf_log(f"<- local density done ({str(timedelta(seconds=round(time.time() - step_start)))})")
        else:
            wf_log("Skipped local density (calc_local_density = False)")

        feedback.setCurrentStep(12)

        wf_log("====================================================================")
        wf_log(f"FINISHED — total processing time: {elapsed()} (h:min:sec)")
        wf_log("====================================================================")

        # return { 'intermediate_results': intermediate_results, 'main_results': main_results }
        return main_results

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkAlgorithmMainWorkflow()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate BK'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
