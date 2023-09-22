######################################################################
# Create a basic Project for TBk output. Should run in a standalone process.
#
# (C) Dominique Weber,  Christoph Schaller, HAFL, BFH
######################################################################

import sys
import os
from pathlib import Path

if __name__ == "__main__":  # this will be invoked if this module is being run directly, but not via import!
    sys.path.insert(0, str(Path(__file__).parents[2]))  # add tbk directory to python path (so tbk.utility is found on path)

from qgis.utils import iface
from qgis.core import *
from qgis.gui import *

from tbk_qgis.tbk.utility.tbk_utilities import *

from shutil import copyfile


def create_project(result_dir, tool_path, root_dir, vhm_10m, vhm_150cm):
    print("--------------------------------------------")
    print("START Create Project...")

    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)

    # Supply path to qgis install location
    #QgsApplication.setPrefixPath("/path/to/qgis/installation", True)

    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    qgs = QgsApplication([], False)

    # Load providers
    qgs.initQgis()

    # copy default Project file
    print("Copy Project...")
    project_copy_path = copy_resource_file(tool_path, os.path.join("resources", "TBk_Template.qgz"),
        result_dir, "TBk_Project.qgz")
 #   project_copy_path = copy_resource_file(tool_path, os.path.join("resources", "TBk_Bestandeskarte.qgz"),
 #       result_dir, "TBk_Bestandeskarte.qgz")
    copy_resource_file(tool_path, os.path.join("resources", "BFH_Logo_A_de_100_RGB.png"),
                       result_dir, "BFH_Logo_A_de_100_RGB.png")
    copy_resource_file(tool_path, os.path.join("resources", "NorthArrow_04.svg"),
                       result_dir,"NorthArrow_04.svg")

    # set correct extent and spatial reference
    print("QGIS Project: Set extent and spatial reference...")
    #vhm_10m_path = os.path.join(root_dir,vhm_10m)
    vhm_10m_path = vhm_10m
    meta_data = get_raster_metadata(vhm_10m_path)

    project = QgsProject.instance()
    project.read(project_copy_path)

    crs = QgsCoordinateReferenceSystem()
    crs.createFromString("EPSG:{0}".format(meta_data["epsg"]))

    project.setCrs(crs)

    for lyr in QgsProject.instance().mapLayers().values():
        lyr.setCrs(crs)

    layer = QgsProject.instance().mapLayersByName("Oberschicht")[0]

    canvas = QgsMapCanvas()
    canvas.setExtent(layer.extent())

    print("QGIS Project: Replace VHM paths...")
    #Replace VHM paths
    layer = QgsProject.instance().mapLayersByName("VHM detail")[0]
    base_name = layer.name()
    provider = layer.providerType()
    options = layer.dataProvider().ProviderOptions()
    layer.setDataSource(
        vhm_150cm,
        base_name,
        provider,
        options
    )

    layer = QgsProject.instance().mapLayersByName("VHM 10m")[0]
    base_name = layer.name()
    provider = layer.providerType()
    options = layer.dataProvider().ProviderOptions()
    layer.setDataSource(
        vhm_10m,
        base_name,
        provider,
        options
    )

    print("QGIS Project: Update Layout extents...")
    def setLayoutExtent(name, bb):
        # get the project's layout
        plm = project.layoutManager()
        layout = plm.layoutByName(name) # your layout name

        #get reference map
        refmap = layout.referenceMap()
        
        # set extent    
        refmap.zoomToExtent(bb)

    xmin = meta_data["extent"][0]
    ymin = meta_data["extent"][1]
    xmax = meta_data["extent"][2]
    ymax = meta_data["extent"][3]

    bb = QgsRectangle(xmin, ymin, xmax, ymax )

    setLayoutExtent("TBk_Bestandeskarte A1 Hochformat",bb)
    setLayoutExtent("TBk_Bestandeskarte A1 Querformat",bb)
    setLayoutExtent("TBk_Bestandeskarte A3 Hochformat",bb)
    setLayoutExtent("TBk_Bestandeskarte A3 Querformat",bb)

    print("QGIS Project: Write project.")
    project.write()

    # Finally, exitQgis() is called to remove the
    # provider and layer registries from memory
    qgs.exitQgis()


def copy_resource_file(tool_path, source, target_path, target):
    source_path = os.path.join(tool_path, source)
    target_copy_path = os.path.join(target_path, target)
    copyfile(source_path, target_copy_path)
    print(f" |  copied: {source_path}")
    print(f" |- to: {target_copy_path}")

    return target_copy_path


if __name__ == "__main__":
    # read params
    print(sys.argv)
    tbk_path = str(sys.argv[1])
    tbk_tool_path = str(sys.argv[2])
    working_root = str(sys.argv[3])
    vhm_10m = str(sys.argv[4])
    vhm_150cm = str(sys.argv[5])

    # run create project function
    create_project(tbk_path, tbk_tool_path, working_root, vhm_10m, vhm_150cm)
