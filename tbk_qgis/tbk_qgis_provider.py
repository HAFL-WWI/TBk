# -*- coding: utf-8 -*-

######################################################################
# (C) Christoph Schaller,  HAFL, BFH
######################################################################

"""
/***************************************************************************
 TBk
                                 A QGIS plugin
 Toolkit for the generation of forest stand maps
 Generated by Plugin Builder: https://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-08-03
        copyright            : (C) 2023 by Berner Fachhochschule HAFL
        email                : christian.rosset@bfh.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
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

from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_algorithm import TBkAlgorithm
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_algorithm_modularized import TBkAlgorithmModularized
from tbk_qgis.tbk.tools.B_preproc.tbk_qgis_prepare_vhm_mg_algorithm import TBkPrepareVhmMgAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tbk_qgis_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tbk_qgis_clip_and_patch_algorithm import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tbk_qgis_merge_similar_neighbours_algorithm import TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tbk_qgis_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_add_coniferous_proportion_algorithm import TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_calculate_crown_coverage_algorithm import TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_update_stand_attributes_algorithm import TBkUpdateStandAttributesAlgorithm
from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_postprocess_local_density import TBkPostprocessLocalDensity
from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_postprocess_OSChange import TBkPostprocessOSChange
from tbk_qgis.tbk.tools.F_additional_modules.tbk_qgis_postprocess_wis2_export import TBkPostprocessWIS2Export
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_postprocess_cleanup import TBkPostprocessCleanup
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_postprocess_hdomDiff import TBkPostprocessHdomDiff
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_postprocess_merge_stand_maps import TBkPostprocessMergeStandMaps
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_postprocess_extract_perimeter import TBkPostprocessExtractPerimeter
from tbk_qgis.tbk.tools.G_utility.optimized_spatial_join import OptimizedSpatialJoin
from tbk_qgis.tbk.tools.Y_legacy.tbk_qgis_prepare_vhm_algorithm import TBkPrepareVhmAlgorithm
from tbk_qgis.tbk.tools.Y_legacy.tbk_qgis_prepare_mg_algorithm import TBkPrepareMgAlgorithm
from tbk_qgis.tbk.tools.Y_legacy.tbk_qgis_prepare_all_algorithm import TBkPrepareAlgorithm


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
        # [grpID: Y_legacy]      grpName: 0 Preprocessing
        self.addAlgorithm(TBkPrepareVhmMgAlgorithm())
        # [grpID: core]         grpName: 1 Bk Generation
        self.addAlgorithm(TBkStandDelineationAlgorithm())
        self.addAlgorithm(TBkSimplifyAndCleanAlgorithm())
        self.addAlgorithm(TBkMergeSimilarNeighboursAlgorithm())
        self.addAlgorithm(TBkClipToPerimeterAndEliminateGapsAlgorithm())
        self.addAlgorithm(TBkCalculateCrownCoverageAlgorithm())
        self.addAlgorithm(TBkAddConiferousProportionAlgorithm())
        self.addAlgorithm(TBkUpdateStandAttributesAlgorithm())
        self.addAlgorithm(TBkAlgorithm())
        self.addAlgorithm(TBkAlgorithmModularized())
        # [grpID: postproc]     grpName: 2 Postprocessing
        self.addAlgorithm(TBkPostprocessCleanup())
        self.addAlgorithm(TBkPostprocessHdomDiff())
        self.addAlgorithm(TBkPostprocessMergeStandMaps())
        self.addAlgorithm(TBkPostprocessOSChange())
        self.addAlgorithm(TBkPostprocessLocalDensity())
        self.addAlgorithm(TBkPostprocessWIS2Export())
        self.addAlgorithm(TBkPostprocessExtractPerimeter())
        # [grpID: utlity]     grpName: X Utility
        self.addAlgorithm(OptimizedSpatialJoin())
        # [grpID: legacy]     grpName: Y LEGACY
        # self.addAlgorithm(BkAGAlgorithm())
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
        return self.tr('TBk for QGIS 3.34')

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
        return 'TBk: Toolkit Bestandeskarte v0.3.1'
