# -*- coding: utf-8 -*-
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

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import QgsProcessingProvider
from PyQt5.QtGui import *


from tbk_qgis.tbk.tools.A_workflows.tool_mainTBk import TBkAlgorithmMainWorkflow
from tbk_qgis.tbk.tools.A_workflows.tool_mainTBk_regionwise import TBkAlgorithmRegionwise
from tbk_qgis.tbk.tools.B_preproc.tool_prepare_vhm_mg import TBkPrepareVhmMgAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours import TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion import TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calc_crown_coverage import TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_append_attributes import TBkAppendStandAttributesAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_tree_species_from_raster import TBkTreeSpeciesFromRaster
from tbk_qgis.tbk.tools.F_additional_modules.tool_local_density import TBkPostprocessLocalDensity
from tbk_qgis.tbk.tools.F_additional_modules.tool_estimate_ddom_SD import TBkDdomSDEstimate
from tbk_qgis.tbk.tools.F_additional_modules.tool_estimate_volume import TBkVEstimate
from tbk_qgis.tbk.tools.F_additional_modules.tool_OS_change import TBkPostprocessOSChange
from tbk_qgis.tbk.tools.F_additional_modules.tool_wis2_export import TBkPostprocessWIS2Export
from tbk_qgis.tbk.tools.F_additional_modules.tool_prep_wis2web_export import TBkPrepareWIS2Export
from tbk_qgis.tbk.tools.F_additional_modules.tool_import_wis2web_csv import TBkImportWIS2WebCSV
from tbk_qgis.tbk.tools.G_utility.tool_postprocess_cleanup import TBkPostprocessCleanup
from tbk_qgis.tbk.tools.G_utility.tool_hdom_vhm_diff import TBkPostprocessHdomDiff
from tbk_qgis.tbk.tools.G_utility.tool_merge_stand_maps import TBkPostprocessMergeStandMaps
from tbk_qgis.tbk.tools.G_utility.tool_extract_perimeter import TBkPostprocessExtractPerimeter
from tbk_qgis.tbk.tools.G_utility.tool_optimized_spatial_join import OptimizedSpatialJoin
from tbk_qgis.tbk.tools.Y_legacy.tool_prepare_vhm_algorithm import TBkPrepareVhmAlgorithm
from tbk_qgis.tbk.tools.Y_legacy.tool_prepare_mg_algorithm import TBkPrepareMgAlgorithm
from tbk_qgis.tbk.tools.Y_legacy.tool_prepare_all_algorithm import TBkPrepareAlgorithm
from tbk_qgis.tbk.tools.Y_legacy.tool_calc_structure import TBkUpdateStandAttributesAlgorithm


class TBkProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        # [grpID: a]    grpName: Main Workflows
        self.addAlgorithm(TBkAlgorithmMainWorkflow())
        self.addAlgorithm(TBkAlgorithmRegionwise())
        # [grpID: b]    grpName: Preprocessing
        self.addAlgorithm(TBkPrepareVhmMgAlgorithm())
        # [grpID: c]    grpName: Stand Delineation (Core)
        self.addAlgorithm(TBkStandDelineationAlgorithm())
        self.addAlgorithm(TBkSimplifyAndCleanAlgorithm())
        # [grpID: d]    grpName: Postprocessing Geometry
        self.addAlgorithm(TBkMergeSimilarNeighboursAlgorithm())
        self.addAlgorithm(TBkClipToPerimeterAndEliminateGapsAlgorithm())
        # [grpID: e]    grpName: Postprocessing Attributes
        self.addAlgorithm(TBkCalculateCrownCoverageAlgorithm())
        self.addAlgorithm(TBkAddConiferousProportionAlgorithm())
        self.addAlgorithm(TBkAppendStandAttributesAlgorithm())
        # [grpID: f]    grpName: Additional Modules
        self.addAlgorithm(TBkDdomSDEstimate())
        self.addAlgorithm(TBkPostprocessLocalDensity())
        self.addAlgorithm(TBkPostprocessOSChange())
        self.addAlgorithm(TBkVEstimate())
        self.addAlgorithm(TBkPostprocessWIS2Export())
        self.addAlgorithm(TBkImportWIS2WebCSV())
        self.addAlgorithm(TBkPrepareWIS2Export())
        # [grpID: g]    grpName: Utility
        self.addAlgorithm(TBkPostprocessCleanup())
        self.addAlgorithm(TBkPostprocessHdomDiff())
        self.addAlgorithm(TBkPostprocessMergeStandMaps())
        self.addAlgorithm(TBkTreeSpeciesFromRaster())
        self.addAlgorithm(TBkPostprocessExtractPerimeter())
        self.addAlgorithm(OptimizedSpatialJoin())
        # [grpID: y]    grpName: Legacy
        # self.addAlgorithm(BkAGAlgorithm())
        # self.addAlgorithm(TBkMainWorkflowOld())
        self.addAlgorithm(TBkUpdateStandAttributesAlgorithm())
        self.addAlgorithm(TBkPrepareVhmAlgorithm())
        self.addAlgorithm(TBkPrepareMgAlgorithm())
        self.addAlgorithm(TBkPrepareAlgorithm())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'TBk'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        # return self.tr('TBk')
        return self.tr('TBk for QGIS 3.40')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """
        path = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'icon_tbk.png')
        return QIcon(path)
        # return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name() [return self.name()].
        """
        return 'TBk: Toolkit Bestandeskarte v0.4.1'
