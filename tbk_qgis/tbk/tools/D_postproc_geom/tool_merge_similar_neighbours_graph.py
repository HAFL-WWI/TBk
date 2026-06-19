# TODO: This tool and tool_merge_similar_neighbours.py could be unified into a single
# QGIS Processing tool with a 'Method' enum parameter (QgsProcessingParameterEnum):
#   0 - Iterative  : picks the longest-border partner per small stand, repeats until
#                    convergence; conservative, predictable.
#   1 - Graph-based: finds connected components of similar neighbours and dissolves
#                    each component in one pass; handles chains and multi-partner cases
#                    in a single run, but may merge more aggressively.
# The shared parameter definitions could move to TBkProcessingAlgorithmToolD and the
# two core functions called by a branch on the selected method value.

import logging
import os

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString)
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir
from tbk_qgis.tbk.tools.D_postproc_geom.merge_similar_neighbours_graph import merge_similar_neighbours_graph
from tbk_qgis.tbk.tools.D_postproc_geom.tbk_qgis_processing_algorithm_toolsD import TBkProcessingAlgorithmToolD


class TBkMergeSimilarNeighboursGraphAlgorithm(TBkProcessingAlgorithmToolD):
    """
    Graph-based alternative to TBkMergeSimilarNeighboursAlgorithm.

    Builds a similarity graph (edges: small stand <-> similar classified neighbour),
    finds connected components, and dissolves each component in a single pass.
    Handles chains and multi-partner cases that the iterative tool resolves over
    several passes.
    """

    WORKING_ROOT = "working_root"
    CONFIG_FILE = "config_file"
    LOGFILE_NAME = "logfile_name"

    INPUT_TO_MERGE = "input_to_merge"
    OUTPUT_MERGED = "stands_merged"
    SIMILAR_NEIGHBOURS_MIN_AREA_M2 = "similar_neighbours_min_area"
    SIMILAR_NEIGHBOURS_HDOM_DIFF_REL = "similar_neighbours_hdom_diff_rel"
    DEL_TMP = "del_tmp"

    def initAlgorithm(self, config=None):
        is_standalone_context = config.get('is_standalone_context') if config else True

        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
                                                     optional=True))

        if is_standalone_context:
            self.addParameter(QgsProcessingParameterFile(self.WORKING_ROOT,
                                                         "Working root folder. This folder must contain the outputs "
                                                         "from previous steps.",
                                                         behavior=QgsProcessingParameterFile.Folder))

            self.addParameter(
                QgsProcessingParameterFeatureSource(self.INPUT_TO_MERGE, "Input layer to be merged",
                                                    [QgsProcessing.TypeVectorPolygon],
                                                    optional=True))

            self.addParameter(
                QgsProcessingParameterFileDestination(self.OUTPUT_MERGED,
                                                      "Merge Similar Neighbours Output (GeoPackage)",
                                                      "GPKG files (*.gpkg)",
                                                      optional=True))

        parameter = QgsProcessingParameterNumber(self.SIMILAR_NEIGHBOURS_MIN_AREA_M2,
                                                 "Min. area to merge similar stands",
                                                 type=QgsProcessingParameterNumber.Integer, defaultValue=2000)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.SIMILAR_NEIGHBOURS_HDOM_DIFF_REL,
                                                 "hdom relative diff to merge similar stands",
                                                 type=QgsProcessingParameterNumber.Double, defaultValue=0.15)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, "Log File Name (.log)",
                                                 defaultValue="tbk_processing.log")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP, "Delete temporary files and fields",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

    def processAlgorithm(self, parameters, context, feedback):
        self.prepare(parameters, context, feedback)

        params = self._extract_context_params(parameters, context)

        working_root = self._get_bk_output_dir(params.working_root)
        ensure_dir(working_root)
        tmp_output_folder = self._get_tmp_output_path(working_root)
        ensure_dir(tmp_output_folder)

        self._configure_logging(working_root, params.logfile_name)
        log = logging.getLogger('Merge similar neighbours (graph-based)')

        log.info('Starting')
        log.debug(f"Used parameters: {params.input_to_merge}, {params.stands_merged}, "
                  f"{params.similar_neighbours_min_area}, {params.similar_neighbours_hdom_diff_rel}, {params.del_tmp}")

        results = merge_similar_neighbours_graph(params.input_to_merge,
                                                 params.stands_merged,
                                                 params.similar_neighbours_min_area,
                                                 params.similar_neighbours_hdom_diff_rel)

        return {self.OUTPUT_MERGED: results["stands_merged"]}

    def createInstance(self):
        return TBkMergeSimilarNeighboursGraphAlgorithm()

    def name(self):
        return '3b Merge similar neighbours graph-based (FM)'

    def shortHelpString(self):
        return (
            'Graph-based alternative to "Merge similar neighbours".\n\n'
            'Builds a similarity graph where edges connect small stands (area < min area) '
            'to any classified neighbour with a similar hdom (relative difference < threshold) '
            'and a shared border. Connected components of this graph are dissolved in a single pass.\n\n'
            'Key difference from the iterative approach: a small stand between two similar large '
            'stands causes all three to merge together, and chains of small stands are resolved '
            'in one run rather than over several passes.\n\n'
            'Within each component the largest stand (by area) provides the output attributes '
            '(hdom, type, etc.). area_m2 is recalculated from the merged geometry.'
        )
