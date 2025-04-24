# todo: set header
import processing
import os
from collections import ChainMap
from qgis.core import (QgsProcessingMultiStepFeedback,)
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours_algorithm import TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch_algorithm import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calculate_crown_coverage_algorithm import TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion_algorithm import TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_update_stand_attributes_algorithm import TBkUpdateStandAttributesAlgorithm
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA


class TBkAlgorithmModularized(TBkProcessingAlgorithmToolA):
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

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(7, feedback)
        results = {}
        outputs = {}

        # set the stand map output directory
        result_dir = self._get_result_dir(parameters['output_root'])
        bk_dir = self._get_bk_output_dir(result_dir)

        # 1 Delineate Stand
        # todo: del_temp parameter is missing
        parameters['output_stand_boundaries'] = os.path.join(bk_dir, "stand_boundaries.gpkg")
        outputs['DelineateStand'] = self.run_delineate_stand(parameters, outputs, context, feedback)
        # todo: add classified_raw etc. to result???
        results['stand_boundaries'] = outputs['DelineateStand']['output_stand_boundaries']

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # 2 Simplify and Clean
        parameters['stands_simplified'] = os.path.join(bk_dir, "stands_simplified.gpkg")
        outputs['SimplifyAndClean'] = self.run_simplify_and_clean(parameters, outputs, context, feedback)
        results['stands_simplified'] = outputs['SimplifyAndClean']['stands_simplified']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # 3 Merge similar neighbours (FM)
        parameters['stands_merged'] = os.path.join(bk_dir, "stands_merged.gpkg")
        outputs['MergeSimilarNeighboursFm'] = self.run_merge_similar_neighbours(parameters, outputs, context, feedback)
        results['stands_merged'] = outputs['MergeSimilarNeighboursFm']['stands_merged']

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # 4 Clip to perimeter and eliminate gaps
        parameters['stands_clipped_no_gaps'] = os.path.join(bk_dir, "stands_clipped.gpkg")
        outputs['ClipToPerimeterAndEliminateGaps'] = self.run_clip_and_eliminate(parameters, outputs, context, feedback)
        results['stands_clipped_no_gaps'] = outputs['ClipToPerimeterAndEliminateGaps']['stands_clipped_no_gaps']
        results['stands_highest_tree'] = outputs['ClipToPerimeterAndEliminateGaps']['stands_highest_tree_clipped']

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # 5 Calculate crown coverage
        outputs['CalculateCrownCoverage'] = self.run_calculate_crown_coverage(parameters, outputs, context, feedback)
        # todo: add optional output destination field as for the other algs???
        results['stands_with_dg'] = outputs['CalculateCrownCoverage']['stands_with_dg']

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # 6 Add coniferous proportion
        outputs['AddConiferousProportion'] = self.run_add_coniferous_proportion(parameters, outputs, context, feedback)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Calculate attribute "struktur"
        outputs['CalculateAttributeStruktur'] = self.run_calculate_attribute_struktur(parameters, outputs, context, feedback)

        return {}

    def run_delineate_stand(self, parameters, outputs, context, feedback):
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
            'output_root': parameters['output_root'],
            'output_stand_boundaries': parameters['output_stand_boundaries'],
        }
        return processing.run('TBk:1 Delineate Stand', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)

    def run_simplify_and_clean(self, parameters, outputs, context, feedback):
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'h_max_input': outputs['DelineateStand']['output_h_max'],
            'input_to_simplify': outputs['DelineateStand']['output_stand_boundaries'],
            'logfile_name': parameters['logfile_name'],
            'min_area_m2': parameters['min_area_m2'],
            'simplification_tolerance': parameters['simplification_tolerance'],
            'working_root': outputs['DelineateStand']['result_dir'],
            'stands_simplified': parameters['stands_simplified'],
        }
        return processing.run('TBk:2 Simplify and Clean', alg_params, context=context,
                              feedback=feedback, is_child_algorithm=True)

    def run_merge_similar_neighbours(self, parameters, outputs, context, feedback):
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'input_to_merge': outputs['SimplifyAndClean']['stands_simplified'],
            'logfile_name': parameters['logfile_name'],
            'similar_neighbours_hdom_diff_rel': parameters['similar_neighbours_hdom_diff_rel'],
            'similar_neighbours_min_area': parameters['similar_neighbours_min_area'],
            'working_root': outputs['DelineateStand']['result_dir'],
            'stands_merged': parameters['stands_merged'],
        }
        return processing.run('TBk:3 Merge similar neighbours (FM)', alg_params,
                                                             context=context, feedback=feedback,
                                                             is_child_algorithm=True)

    def run_clip_and_eliminate(self, parameters, outputs, context, feedback):
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'input_to_clip': outputs['MergeSimilarNeighboursFm']['stands_merged'],
            'tmp_stands_highest_tree': outputs['SimplifyAndClean']['tmp_stands_highest_tree'],
            'logfile_name': parameters['logfile_name'],
            'perimeter': parameters['perimeter'],
            'working_root': outputs['DelineateStand']['result_dir'],
            'stands_clipped_no_gaps': parameters['stands_clipped_no_gaps']
        }
        return processing.run('TBk:4 Clip to perimeter and eliminate gaps',
                                                                    alg_params, context=context, feedback=feedback,
                                                                    is_child_algorithm=True)

    def run_calculate_crown_coverage(self, parameters, outputs, context, feedback):
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': outputs['DelineateStand']['result_dir'],
            'stands_clipped_no_gaps': outputs['ClipToPerimeterAndEliminateGaps']['stands_clipped_no_gaps'],
            'vhm_150cm': parameters['vhm_150cm']
        }
        return processing.run('TBk:5 Calculate crown coverage', alg_params,
                                                           context=context, feedback=feedback,
                                                           is_child_algorithm=True)

    def run_add_coniferous_proportion(self, parameters, outputs, context, feedback):
        alg_params = {
            'calc_mixture_for_main_layer': parameters['calc_mixture_for_main_layer'],
            'config_file': parameters['config_file'],
            'coniferous_raster': parameters['coniferous_raster'],
            'del_tmp': parameters['del_tmp'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': outputs['DelineateStand']['result_dir'],
            'stands_with_dg': outputs['CalculateCrownCoverage']['stands_with_dg']
        }
        return processing.run('TBk:6 Add coniferous proportion', alg_params,
                                                            context=context, feedback=feedback,
                                                            is_child_algorithm=True)

    def run_calculate_attribute_struktur(self, parameters, outputs, context, feedback):
        alg_params = {
            'config_file': parameters['config_file'],
            'del_tmp': parameters['del_tmp'],
            'input_for_computation': outputs['AddConiferousProportion']['stands_with_coniferous'],
            'logfile_name': parameters['logfile_name'],
            'result_dir': outputs['DelineateStand']['result_dir']
        }
        return processing.run('TBk:Calculate attribute "struktur"', alg_params,
                                                               context=context, feedback=feedback,
                                                               is_child_algorithm=True)

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkAlgorithmModularized()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate BK Modularized'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
