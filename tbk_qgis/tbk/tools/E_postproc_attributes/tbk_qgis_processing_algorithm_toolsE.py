# #####################################################################
# Base class for TBk sub-algorithms designed for inheritance to minimize code repetition across child algorithms.
#
# 08.11.2024
# (C) Hannes Horneber, HAFL
# #####################################################################

from tbk_qgis.tbk.general.tbk_qgis_processing_algorithm import TBkProcessingAlgorithm

class TBkProcessingAlgorithmToolE(TBkProcessingAlgorithm):
    """
    A base class for the TBk algorithms in category D. It can be inherited, so that each child algorithm can use its functions.
    """
    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return 'e   Post Processing Attributes'

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'e_pp_attr'
