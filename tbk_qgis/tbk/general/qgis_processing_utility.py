#######################################################################
# Helper Classes and Functions for QGIS Processing.
#
# (C) Hannes Horneber, Christoph Schaller, HAFL
#######################################################################

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