from qgis.core import *
from qgis.gui import *
import os

#@qgsfunction(args='auto', group='Custom')
def load_layer(path, layer_name="", verbose=False):
    """
    Attempts to load a vector layer in QGIS
    """
    file_extension = os.path.splitext(path)[1]
    if file_extension.lower() == '.tif':
        layer = QgsRasterLayer(path, layer_name)
    else:
        layer = QgsVectorLayer(path, layer_name, "ogr")

    # check if layer is valid
    if not layer.isValid():
        # iface.messageBar().pushMessage("Layer " + layer_name + " konnte nicht geladen werden!")
        if verbose:
            print("Layer " + layer_name + " konnte nicht geladen werden!")
    else:
        # iface.messageBar().pushMessage("Layer " + layer_name + "geladen!")
        if verbose:
            print("Layer " + layer_name + " geladen!")
        QgsProject.instance().addMapLayer(layer)
    return layer

# print all loaded layers
layerList = QgsProject.instance().layerTreeRoot().findLayers()
for layer in layerList:
    print(layer.name())