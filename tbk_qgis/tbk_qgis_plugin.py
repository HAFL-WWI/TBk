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

import inspect
import os
import sys

if __name__ == "__main__":  # this will be invoked if this module is being run directly, but not via import!
    # add plugin directory to python path (so parent package tbk_qgis is found on path for relative imports)
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    __package__ = 'tbk_qgis'  # make sure relative imports work when testing (no there is a known parent package)

# add cmd folder to python path (TODO: not sure why - Hannes 2023-01-11)
cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

# Add plugin directory to python path (so shipped packages in root are found on import)
pluginPath = os.path.join(os.path.dirname(__file__))
if pluginPath not in sys.path:
    sys.path.insert(0, pluginPath)

from qgis.core import QgsApplication
from tbk_qgis_provider import TBkProvider


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
