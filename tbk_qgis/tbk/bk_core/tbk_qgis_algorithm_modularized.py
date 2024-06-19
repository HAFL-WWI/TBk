# todo: set header
from tbk_qgis.tbk.bk_core.tbk_qgis_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.bk_core.tbk_qgis_processing_algorithm import TBkProcessingAlgorithm
from tbk_qgis.tbk.bk_core.tbk_qgis_stand_delineation_algorithm import TBkStandDelineationAlgorithm


class TBkAlgorithmModularized(TBkProcessingAlgorithm):
    """
    todo
    """

    # todo: store the algorithm instances in a list and run them in a for loop? Put the instanciations in the initAlgorithm method
    def __init__(self):
        TBkProcessingAlgorithm.__init__(self)
        self.stand_delineation_algorithm = TBkStandDelineationAlgorithm()
        self.simplify_and_clean_algorithm = TBkSimplifyAndCleanAlgorithm()

    # todo: avoid repetition + ensure that a parameter is not added twice
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """

        self.stand_delineation_algorithm.initAlgorithm(config)
        # Add the child algorithm's parameters to this algorithm
        for param in self.stand_delineation_algorithm.parameterDefinitions():
            self.addParameter(param.clone())

        self.simplify_and_clean_algorithm.initAlgorithm(config)

        for param in self.simplify_and_clean_algorithm.parameterDefinitions():
            if param.name() != 'working_root':
                self.addParameter(param.clone())

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Use the parameters from the config file if provided; otherwise, use the input parameters.
        params = self._get_input_or_config_params(parameters, context)

        outputs = self.stand_delineation_algorithm.processAlgorithm(params.__dict__, context, feedback)
        # Set the working root, so that it can be read in the simplify algorithm
        params.working_root = outputs['WORKING_ROOT']
        self.simplify_and_clean_algorithm.processAlgorithm(params.__dict__, context, feedback)

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
