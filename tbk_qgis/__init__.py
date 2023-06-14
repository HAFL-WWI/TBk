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

 This script initializes the plugin, making it known to QGIS.

"""

__author__ = 'Berner Fachhochschule HAFL'
__date__ = '2020-08-03'
__copyright__ = '(C) 2023 by Berner Fachhochschule HAFL'


def classFactory(iface):
    """Load TBk class from file TBk.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .tbk_qgis_plugin import TBkPlugin
    return TBkPlugin()
