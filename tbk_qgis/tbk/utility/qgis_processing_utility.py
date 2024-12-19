# -*- coding: utf-8 -*-
# *************************************************************************** #
# Helper Classes and Functions for QGIS Processing.
#
# (C) Hannes Horneber, Christoph Schaller (BFH-HAFL)
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
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import logging

# Helper class that implements an interface for using the QGIS feedback in the logging context
class QgisHandler(logging.Handler):
    feedback = None

    def __init__(self, feedback, *args, **kwargs):
        super(QgisHandler, self).__init__(*args, **kwargs)
        self.feedback = feedback

    def emit(self, record):
        try:
            message = self.format(record)
            # Don't do anything if the StreamHandler does not exist
            if message == None:
                return
            self.feedback.pushInfo(message)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

        # QgsMessageLog.logMessage("File "+ii.source()+": all pixels set to no data", tag="Raster Processing", level=QgsMessageLog.INFO )

    # def format(self, record):
    #    try:
    #        message = logging.StreamHandler.format(self, record)
    #    # Catch the case when there is a zombie logger, when re-launching
    #    #  the simulation with 'p'.
    #    # This seems to be caused by an incorrect cleaning on the Builder
    #    except AttributeError as detail:
    #        return None
#
#    return message