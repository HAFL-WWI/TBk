# -*- coding: utf-8 -*-

"""
/***************************************************************************
    TBk - QGIS plugin
    Toolkit for the generation of forest stand maps

    ----------------------------------------------------------------------
    begin                : 2023-01-07
    copyright            : (C) 2022 by Berner Fachhochschule HAFL
    email                : hannes.horneber@bfh.ch, christian.rosset@bfh.ch
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
import sys
import inspect

from qgis.core import QgsProcessingAlgorithm, QgsApplication
from .tbk_qgis_provider import TBkProvider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class TBkPlugin(object):

    def __init__(self):
        self.provider = None

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = TBkProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
