# *************************************************************************** #
# Estimate hdom for existing stand boundaries (GitHub issue #43).
#
# Authors: Hannes Horneber (BFH-HAFL)
# *************************************************************************** #
"""
/***************************************************************************
    TBk: Toolkit Bestandeskarte (QGIS Plugin)
    Toolkit for the generating and processing forest stand maps
    Copyright (C) 2025 BFH-HAFL (hannes.horneber@bfh.ch, christian.rosset@bfh.ch)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 ***************************************************************************/
"""

import logging

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString)
from tbk_qgis.tbk.general.tbk_utilities import ensure_dir, copy_vector_file
from tbk_qgis.tbk.tools.E_postproc_attributes.estimate_hdom_existing_stands import estimate_hdom_existing_stands
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_processing_algorithm_toolsE import TBkProcessingAlgorithmToolE


class TBkEstimateHdomExistingStandsAlgorithm(TBkProcessingAlgorithmToolE):
    """
    Estimates hdom (Oberhoehe) for existing stand boundaries that don't carry a TBk-generated
    hdom attribute yet, as a fixed percentile of the VHM pixel values within each polygon, after
    an internal MAXIMUM-resampling of the VHM to a coarser cell size (see
    estimate_hdom_existing_stands.py for the method itself, and the `resample_resolution` /
    `percentile` advanced parameters for the tunables).

    This is a standalone attribute tool, not part of the ordered Generate BK step sequence
    (1-9) - it is meant to run on stand maps produced elsewhere (e.g. BK_AG, manually digitised
    boundaries) to make them TBk-attribute-compatible.

    Also writes `homogeneity_field` (0-1 score, the inverse of an entropy/spread measure) and
    `class_field` ("clear"/"ambiguous", thresholding it): a QA signal for whether the stand's
    height distribution has one clear dominant layer, using TBk's own similar-height tolerance -
    NOT an alternative hdom value (tested and rejected, see estimate_hdom_existing_stands.py).

    This is a first approach for the issue discussed in GitHub issue #43 - the simplest, closest
    to TBk's own hdom definition, but likely the least robust for stands not delineated by TBk
    in the first place (their pixel distribution may look nothing like a TBk-classified stand's).
    """
    # ------- Define Constants -------#
    # Folder to store the log file in
    RESULT_DIR = "result_dir"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # VHM to estimate hdom from
    VHM = "vhm"
    # Default log file name
    LOGFILE_NAME = "logfile_name"

    # Input layer used for the calculation
    STANDS_INPUT = "stands_input"
    # Stands output with the estimated hdom field
    OUTPUT_STANDS_HDOM = "stands_hdom"

    # Additional parameters
    HDOM_FIELD = "hdom_field"
    STD_FIELD = "std_field"
    HOMOGENEITY_FIELD = "homogeneity_field"
    CLASS_FIELD = "class_field"
    PERCENTILE = "percentile"
    RESAMPLE_RESOLUTION = "resample_resolution"
    HOMOGENEITY_THRESHOLD = "homogeneity_threshold"
    MIN_VALID_HEIGHT = "min_valid_height"
    MAX_VALID_HEIGHT = "max_valid_height"
    DEL_TMP = "del_tmp"

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        # --- Handle config argument
        is_standalone_context = config.get('is_standalone_context') if config else True

        # --- Parameters

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
                                                     optional=True))

        # VHM to estimate hdom from
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM,
                                                            "VHM to estimate hdom from (.tif), at any resolution - it "
                                                            "is resampled internally (see `resample_resolution`)."))

        if is_standalone_context:
            # Existing stand boundaries lacking a hdom attribute
            self.addParameter(
                QgsProcessingParameterFeatureSource(self.STANDS_INPUT,
                                                    "Existing stand boundaries without a hdom attribute",
                                                    [QgsProcessing.TypeVectorPolygon]))

            self.addParameter(QgsProcessingParameterFile(self.RESULT_DIR,
                                                         "Directory to store the log file in",
                                                         behavior=QgsProcessingParameterFile.Folder))

            # --- Add output definition
            self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_STANDS_HDOM,
                                                                    "Stand output file with estimated hdom field",
                                                                    "GPKG files (*.gpkg)", ))

        # --- Advanced Parameters

        parameter = QgsProcessingParameterString(self.LOGFILE_NAME, "Log File Name (.log)",
                                                 defaultValue="tbk_processing.log")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.HDOM_FIELD, "Output field name for the estimated hdom",
                                                 defaultValue="hdom")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.STD_FIELD,
                                                 "Output field name for the pixel std. deviation within the stand "
                                                 "(indicates estimate confidence)",
                                                 defaultValue="hdom_std")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.HOMOGENEITY_FIELD,
                                                 "Output field name for the 0-1 dominant-layer homogeneity score "
                                                 "(the inverse of an entropy/spread measure: 1.0 = all pixels "
                                                 "close to one peak height, i.e. a clear dominant layer; low = "
                                                 "spread across multiple heights, no single dominant layer). Not "
                                                 "used to compute hdom itself - see `class_field`.",
                                                 defaultValue="hdom_homogeneity")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterString(self.CLASS_FIELD,
                                                 "Output field name for the \"clear\"/\"ambiguous\" flag derived "
                                                 "from `homogeneity_field` via `homogeneity_threshold`",
                                                 defaultValue="hdom_class")
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.RESAMPLE_RESOLUTION,
                                                 "Target cell size (m) for a MAXIMUM-resampling of the VHM before "
                                                 "estimating hdom (0 disables resampling). Per output cell, keeps "
                                                 "the tallest input pixel - the same operation TBk itself uses to "
                                                 "derive VHM_10m/VHM_150cm (tool_prepare_vhm_mg.py), which filters "
                                                 "out low-height gap/understory pixels that would otherwise dominate "
                                                 "a plain statistic on a fine VHM. Locally benchmarked sweet spot: "
                                                 "4-10m (RMSE 1.27-1.43m on classified stands); degrades on both "
                                                 "sides (still too noisy below, over-smoothed above). Default 10m "
                                                 "matches hdom's own definition (~100 dominant trees/ha, i.e. one "
                                                 "tree per ~10x10m).",
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=10.0, minValue=0.0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.PERCENTILE,
                                                 "Percentile (0-100) of the stand's (resampled) VHM pixels used as "
                                                 "hdom. The best value depends on `resample_resolution`: locally "
                                                 "benchmarked against classified (non-remainder) TBk stands, ~70 "
                                                 "at a 4m resample, down to ~45-50 (median) at 10m - a larger "
                                                 "resampling window already filters more noise, so a lower "
                                                 "percentile suffices and is more robust than a high one with few "
                                                 "pixels per stand.",
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=50.0, minValue=0.0, maxValue=100.0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.HOMOGENEITY_THRESHOLD,
                                                 "Minimum `homogeneity_field` value (0-1) for `class_field` to "
                                                 "read \"clear\" instead of \"ambiguous\". 0.67 gave the best "
                                                 "classified/remainder separation locally (0.50/0.60/0.67/0.75/0.80 "
                                                 "tried).",
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=0.67, minValue=0.0, maxValue=1.0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MIN_VALID_HEIGHT, "Minimum valid VHM height (m)",
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=0.0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterNumber(self.MAX_VALID_HEIGHT,
                                                 "Maximum valid VHM height (m); pixels above this are treated as "
                                                 "outliers and excluded",
                                                 type=QgsProcessingParameterNumber.Double,
                                                 defaultValue=60.0)
        self._add_advanced_parameter(parameter)

        parameter = QgsProcessingParameterBoolean(self.DEL_TMP,
                                                  "Delete the resampled VHM again once done",
                                                  defaultValue=True)
        self._add_advanced_parameter(parameter)

        self._add_gdal_create_options_parameter()

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # --- Get input parameters
        params = self._extract_context_params(parameters, context)

        # Handle the working root and temp folder (the latter only needed for the resampled VHM)
        working_root = self._get_bk_output_dir(params.result_dir)
        ensure_dir(working_root)
        tmp_output_folder = self._get_tmp_output_path(working_root)
        ensure_dir(tmp_output_folder)

        # Set the logger
        self._configure_logging(working_root, params.logfile_name, context)
        log = logging.getLogger(self.name())

        # check tif files extension
        self._check_tif_extension(params.vhm, self.VHM)

        stands_copy = copy_vector_file(params.stands_input, params.stands_hdom, context, feedback)

        # --- Estimate hdom
        # (estimate_hdom_existing_stands() logs its own "Start/Finished Estimate hdom for
        # existing stands" milestone block via SubprocessTimer, given feedback - no separate
        # _log_milestone here)
        stands_hdom = estimate_hdom_existing_stands(stands_copy,
                                                     params.vhm,
                                                     hdom_field=params.hdom_field,
                                                     std_field=params.std_field,
                                                     homogeneity_field=params.homogeneity_field,
                                                     class_field=params.class_field,
                                                     percentile=params.percentile,
                                                     resample_resolution=params.resample_resolution,
                                                     homogeneity_threshold=params.homogeneity_threshold,
                                                     min_valid_height=params.min_valid_height,
                                                     max_valid_height=params.max_valid_height,
                                                     tmp_output_folder=tmp_output_folder,
                                                     del_tmp=params.del_tmp,
                                                     gdal_create_options=params.gdal_create_options,
                                                     context=context,
                                                     feedback=feedback)

        return {self.OUTPUT_STANDS_HDOM: stands_hdom}

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkEstimateHdomExistingStandsAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Estimate hdom for existing stands'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('Estimates hdom (Oberhoehe) for existing stand boundaries that do not carry a '
               'TBk-generated hdom attribute, as a fixed percentile of the VHM pixel values within '
               'each polygon (see `percentile`), after resampling the VHM to a coarser cell size '
               'using MAXIMUM resampling (see `resample_resolution`) - the same operation TBk '
               'itself uses to derive VHM_10m/VHM_150cm, which keeps the tallest pixel per output '
               'cell and so filters out low-height gap/understory pixels that would otherwise '
               'dominate a plain statistic on a fine VHM (tried and rejected: percentiles up to '
               'p95 and histogram-mode peak detection directly on the un-resampled VHM, both far '
               'worse - see estimate_hdom_existing_stands.py for the numbers). Originating idea '
               'from a Semesterarbeit (Manuel Kraus, BFH-HAFL 2023/2024, GitHub issue #43), which '
               'used a numpy-histogram cumulative-frequency band on the un-resampled VHM instead; '
               'this simplified and resampling-extended version was locally benchmarked against '
               'the reference test dataset (data/tbk_2012), restricted to `classified` stands - '
               '`remainder` stands are excluded from validation since their existing hdom is '
               'itself not a trustworthy reference (see Kraus\' thesis, section 5). Best local '
               'result: RMSE 1.16m / 96% within +-2m (10m resample, median) - see the '
               '`resample_resolution` parameter help for the full sweep.')
