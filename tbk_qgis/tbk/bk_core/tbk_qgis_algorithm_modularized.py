# todo: set header
import processing
import logging
from collections import ChainMap
from tbk_qgis.tbk.bk_core.tbk_qgis_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.bk_core.tbk_qgis_processing_algorithm import TBkProcessingAlgorithm
from tbk_qgis.tbk.bk_core.tbk_qgis_stand_delineation_algorithm import TBkStandDelineationAlgorithm


class TBkAlgorithmModularized(TBkProcessingAlgorithm):
    """
    todo
    """
    # array containing the algorithms to use
    algorithms = [
        TBkStandDelineationAlgorithm(),
        TBkSimplifyAndCleanAlgorithm(),
    ]

    # todo: avoid repetition + ensure that a parameter is not added twice
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # init all used algorithm and add there parameters to parameters list
        for alg in self.algorithms:
            alg.initAlgorithm(config)
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

        # Handle the working root and temp output folders
        output_root = parameters["output_root"]
        result_dir = self._get_result_dir(output_root)
        parameters.update({'result_dir': result_dir})

        # set logger
        self._configure_logging(result_dir, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # --- run main algorithm
        log.info('Starting')

        for alg in self.algorithms:
            results = processing.run(f"TBk:{alg.name()}", parameters)

        return {}  # todo

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
        return ' Generate BK Modularized'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
