# todo: set header
import processing
import logging
from collections import ChainMap
from tbk_qgis.tbk.general.tbk_utilities import dict_diff
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
    # Dictionary storing algorithms and parameters, typically using result parameters from previous tools.
    # invoker_params must be given for each algorithm even if empty.
    algorithms = {
        '1 Delineate Stand': { "algorithm": TBkStandDelineationAlgorithm(), "invoker_params": {"result_dir": "result_dir"}},
        '2 Simplify and Clean': {"algorithm": TBkSimplifyAndCleanAlgorithm(), "invoker_params": {"input_to_simplify_name": "stand_boundaries", "output_name": "output_simplified"}},
        '3 Merge similar neighbours (FM)': {"algorithm": TBkMergeSimilarNeighboursAlgorithm(), "invoker_params": {"input_to_merge_name": "output_simplified", "output_name": "output_merged"}},
        '4 Clip to perimeter and eliminate gaps': {"algorithm": TBkClipToPerimeterAndEliminateGapsAlgorithm(), "invoker_params": {"input_to_clip_name": "output_merged", "output_name": "output_clipped"}},
        '5 Calculate crown coverage': {"algorithm": TBkCalculateCrownCoverageAlgorithm(), "invoker_params": {}},
        '6 Add coniferous proportion': {"algorithm": TBkAddConiferousProportionAlgorithm(), "invoker_params": {}},
        'Calculate attribute "struktur"': {"algorithm": TBkUpdateStandAttributesAlgorithm(), "invoker_params": {}},
    }

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # Initialisation config used to adapt the tool if run in a modularized context.
        init_config = {
            # Indicates the tool is running in a standalone or modularized context in the initAlgorithm() method
            'is_standalone_context': False,
            # Path used for the output_root of all invoked tools
            'output_root': {'name': "output_root", 'description': "Output folder"} # todo: still used???
        }

        # init all used algorithm and add there parameters to parameters list
        for key, value  in self.algorithms.items():
            alg = value['algorithm']
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
        # --- get and check input parameters

        # Add result_dir and working_root to the parameters for shared access across all tools.
        output_root = parameters["output_root"]
        result_dir = self._get_result_dir(output_root)
        working_root = self._get_bk_output_dir(result_dir)
        parameters.update({'result_dir': result_dir, 'working_root': working_root})

        # set logger
        self._configure_logging(result_dir, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # Dictionary to store the results
        results = {}

        # --- run main algorithm
        log.info('Starting')

        for key, value in self.algorithms.items():
            log.info(f'Starting processing tool: {key}')

            alg = value['algorithm']

            # Update the parameters. It would be simpler update directly the dictionary parameter's. But we pass it
            # via invoker_params parameter to clearly indicate in the sub-tools that these parameters originate from this tool.
            invoker_params = {"invoker_params": value['invoker_params']}
            parameters.update(invoker_params)
            log.debug(f"Added the following invoker_params to the parameters: {invoker_params}")

            results = processing.run(alg, parameters, context=context, feedback=feedback, is_child_algorithm=True)
            log.debug(f"Results of the tool: {results}")

            config_removed, config_added, config_changed = dict_diff(parameters, results)

            if config_changed:
                log.debug(f"The parameters {list(config_changed.keys())} values was overridden by the previous tool results, "
                        f"which could lead to undesired behavior")

            # Adapt the output key (standard key is "output") otherwise the value can be overridden in the next sub-algorithm.
            # Handling of a result with multiple results is not implemented.
            if 'output_name' in value['invoker_params'] and len(results)==1:
                new_key = value['invoker_params']['output_name']
                results = { new_key: list(results.values())[0]}

            # Add the algorithm outputs to the parameters, so that they can be reused as input in the following tool
            parameters.update(results)

        log.debug(f"Results: {results}")
        log.info(f"Finished")

        return {}

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
