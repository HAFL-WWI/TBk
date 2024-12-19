# *************************************************************************** #
# Copy QGIS project template for TBk output and adjust.
# Should run in a standalone process: Since QGIS opens the project to be created,
# if run in processing, it will close the currently loaded project to do so.
#
# Authors: Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
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

import shutil
import sys
import os
from pathlib import Path

if __name__ == "__main__":  # this will be invoked if this module is being run directly, but not via import!
    sys.path.insert(0, str(
        Path(__file__).parents[2]))  # add tbk directory to python path (so tbk.utility is found on path)
    # this import will work if above line is executed
    from tbk.utility.tbk_utilities import *
else:
    # this replaces above import, if this is executed in the regular QGIS environment where processing plugins are "known"
    from tbk_qgis.tbk.utility.tbk_utilities import *

from qgis.utils import iface
from qgis.core import *
from qgis.gui import *

from shutil import copyfile


def create_project(working_root, tmp_output_folder, tbk_result_dir, tbk_tool_path, vhm_10m, vhm_150cm, coniferous_raster,
                   del_tmp):
    print("--------------------------------------------")
    print("START Create Project...")

    if not os.path.isdir(tbk_result_dir):
        os.makedirs(tbk_result_dir)

    # Supply path to qgis install location
    # QgsApplication.setPrefixPath("/path/to/qgis/installation", True)

    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    qgs = QgsApplication([], False)

    # Load providers
    qgs.initQgis()

    # copy default Project file
    print("Copy Project...")
    project_copy_path = copy_resource_file(tbk_tool_path, os.path.join("resources", "TBk_Template.qgz"),
                                           tbk_result_dir, "TBk_Project.qgz")
    #    copy_resource_file(tbk_tool_path, os.path.join("resources", "BFH_Logo_A_de_100_RGB.png"),
    #                       tbk_result_dir, "BFH_Logo_A_de_100_RGB.png")
    #    copy_resource_file(tbk_tool_path, os.path.join("resources", "NorthArrow_04.svg"),
    #                       tbk_result_dir,"NorthArrow_04.svg")

    # set correct extent and spatial reference
    print("QGIS Project: Get Raster metadata for EPSG...")
    # vhm_10m_path = os.path.join(root_dir,vhm_10m)
    vhm_10m_path = vhm_10m
    meta_data = get_raster_metadata(vhm_10m_path)

    print("QGIS Project: Read project...")
    project = QgsProject.instance()
    project.read(project_copy_path)

    print("QGIS Project: Set spatial reference...")
    crs = QgsCoordinateReferenceSystem()
    crs.createFromString("EPSG:{0}".format(meta_data["epsg"]))

    project.setCrs(crs)

    for lyr in QgsProject.instance().mapLayers().values():
        lyr.setCrs(crs)

    print("QGIS Project: Set extent...")
    layer = QgsProject.instance().mapLayersByName("Bestandesgrenzen")[0]

    canvas = QgsMapCanvas()
    canvas.setExtent(layer.extent())

    print("QGIS Project: Replace VHM paths...")
    # Replace VHM paths
    # layer = QgsProject.instance().mapLayersByName("Vegetationshöhe (VHM) 150cm")[0]
    # base_name = layer.name()
    # provider = layer.providerType()
    # options = layer.dataProvider().ProviderOptions()
    # layer.setDataSource(
    #     vhm_150cm,
    #     base_name,
    #     provider,
    #     options
    # )
    #
    # layer = QgsProject.instance().mapLayersByName("Vegetationshöhe (VHM) 10m")[0]
    # base_name = layer.name()
    # provider = layer.providerType()
    # options = layer.dataProvider().ProviderOptions()
    # layer.setDataSource(
    #     vhm_10m,
    #     base_name,
    #     provider,
    #     options
    # )
    #
    # layer = QgsProject.instance().mapLayersByName("Nadelholzanteil (WMG) 10m")[0]
    # base_name = layer.name()
    # provider = layer.providerType()
    # options = layer.dataProvider().ProviderOptions()
    # layer.setDataSource(
    #     coniferous_raster,
    #     base_name,
    #     provider,
    #     options
    # )

    print("QGIS Project: Update Layout extents...")

    def setLayoutExtent(name, bb):
        # get the project's layout
        plm = project.layoutManager()
        layout = plm.layoutByName(name)  # your layout name

        # get reference map
        refmap = layout.referenceMap()

        # set extent    
        refmap.zoomToExtent(bb)

    xmin = meta_data["extent"][0]
    ymin = meta_data["extent"][1]
    xmax = meta_data["extent"][2]
    ymax = meta_data["extent"][3]

    bb = QgsRectangle(xmin, ymin, xmax, ymax)

    setLayoutExtent("TBk_Bestandeskarte A1 Hochformat", bb)
    setLayoutExtent("TBk_Bestandeskarte A1 Querformat", bb)
    setLayoutExtent("TBk_Bestandeskarte A3 Hochformat", bb)
    setLayoutExtent("TBk_Bestandeskarte A3 Querformat", bb)

    print("QGIS Project: Write project.")
    project.write()

    # Finally, exitQgis() is called to remove the
    # provider and layer registries from memory
    qgs.exitQgis()


def copy_resource_file(tbk_tool_path, source, target_path, target):
    source_path = os.path.join(tbk_tool_path, source)
    target_copy_path = os.path.join(target_path, target)
    copyfile(source_path, target_copy_path)
    print(f" |  copied: {source_path}")
    print(f" |- to: {target_copy_path}")

    return target_copy_path


if __name__ == "__main__":
    # parse params from command line and run
    print(sys.argv)
    working_root = str(sys.argv[1])
    tmp_output_folder= str(sys.argv[2])
    tbk_result_dir = str(sys.argv[3])
    tbk_tool_path = str(sys.argv[4])
    vhm_10m = str(sys.argv[5])
    vhm_150cm = str(sys.argv[6])
    coniferous_raster = str(sys.argv[7])
    del_tmp = (str(sys.argv[8]).lower() in ['true', '1', 't'])

    # run create project function
    create_project(working_root, tmp_output_folder, tbk_result_dir, tbk_tool_path, vhm_10m, vhm_150cm, coniferous_raster,
                   del_tmp)
