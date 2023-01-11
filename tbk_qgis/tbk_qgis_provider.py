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
        copyright            : (C) 2020 by Berner Fachhochschule HAFL
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
__copyright__ = '(C) 2020 by Berner Fachhochschule HAFL'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import QgsProcessingProvider
from PyQt5.QtGui import *

from tbk.bk_core.tbk_qgis_algorithm import TBkAlgorithm
from tbk.preproc.tbk_qgis_prepare_vhm_algorithm import TBkPrepareVhmAlgorithm
from tbk.preproc.tbk_qgis_prepare_mg_algorithm import TBkPrepareMgAlgorithm
from tbk.postproc.tbk_qgis_postprocess_local_density import TBkPostprocessLocalDensity
from .resources import *


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
        self.addAlgorithm(TBkAlgorithm())
        self.addAlgorithm(TBkPrepareVhmAlgorithm())
        self.addAlgorithm(TBkPrepareMgAlgorithm())
        self.addAlgorithm(TBkPostprocessLocalDensity())

    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'TBk_generation'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('TBk_generation')

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
        #return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return self.name()