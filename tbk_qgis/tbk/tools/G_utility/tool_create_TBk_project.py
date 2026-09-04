# -*- coding: utf-8 -*-
# *************************************************************************** #
# Copy TBk QGIS project template and modify it to link layers.
#
# Authors: Hannes Horneber (BFH-HAFL)
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

from pathlib import Path
import shutil

from qgis.core import (
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsProcessingParameterFile,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterDefinition
)

from qgis.PyQt.QtCore import QCoreApplication

from tbk_qgis.tbk.general.tbk_utilities import get_raster_metadata, SubprocessTimer
from tbk_qgis.tbk.tools.G_utility.tbk_qgis_processing_algorithm_toolsG import TBkProcessingAlgorithmToolG

class TBkCreateProject(TBkProcessingAlgorithmToolG):

    def addAdvancedParameter(self, parameter):
        parameter.setFlags(parameter.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        return self.addParameter(parameter)

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    # Directory containing the output files
    RESULT_DIR = "result_dir"
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # Default log file name
    LOGFILE_NAME = "logfile_name"

    # VHM 10m as main TBk input
    VHM_10M = "vhm_10m"
    # VHM 150cm as main TBk input
    VHM_150CM = "vhm_150cm"
    # Coniferous raster
    CONIFEROUS_RASTER = "coniferous_raster"
    # Coniferous raster to be used during stand delineation
    CONIFEROUS_RASTER_FOR_CLASSIFICATION = "coniferous_raster_for_classification"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        # --- Handle config argument

        # Indicates whether the tool is running in standalone or modularized mode, and adjusts the GUI/behavior if needed.
        is_standalone_context = config.get('is_standalone_context') if config else True

        # --- Parameters

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The below '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
                                                     optional=True))

        # --- Main parameters
        self.addParameter(QgsProcessingParameterFile(self.RESULT_DIR,
                                                         "Working root folder. This folder must contain the outputs "
                                                         "from previous steps.",
                                                         behavior=QgsProcessingParameterFile.Folder))

        # VHM 10m as main TBk input
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_10M,
                                                            "VHM 10m as main TBk input  (.tif)"))
        # VHM 150cm to calculate DG
        self.addParameter(QgsProcessingParameterRasterLayer(self.VHM_150CM,
                                                            "VHM 150cm to calculate DG (.tif)",
                                                            optional=True))

        # Coniferous raster
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER_FOR_CLASSIFICATION,
                                                            "MG 10m binary: Coniferous raster used during stand "
                                                            "delineation (.tif)\nA simplified binarized "
                                                            "raster may achieve better results",
                                                            optional=True))
        # Coniferous raster to calculate stand mean
        self.addParameter(QgsProcessingParameterRasterLayer(self.CONIFEROUS_RASTER,
                                                            "MG 10m: Coniferous raster to calculate stand mean (.tif)",
                                                            optional=True))


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        timer = SubprocessTimer(feedback, "CreateProject", "C")

        # --- Read parameters properly
        result_dir = Path(self.parameterAsString(parameters, self.RESULT_DIR, context))

        vhm_10m_layer = self.parameterAsRasterLayer(parameters, self.VHM_10M, context)
        vhm_150cm_layer = self.parameterAsRasterLayer(parameters, self.VHM_150CM, context)
        coniferous_layer = self.parameterAsRasterLayer(parameters, self.CONIFEROUS_RASTER, context)
        coniferous_layer_for_classification = self.parameterAsRasterLayer(parameters, self.CONIFEROUS_RASTER_FOR_CLASSIFICATION, context)

        vhm_10m = Path(vhm_10m_layer.source()) if vhm_10m_layer else None
        vhm_150cm = Path(vhm_150cm_layer.source()) if vhm_150cm_layer else None
        coniferous_raster = Path(coniferous_layer.source()) if coniferous_layer else None
        coniferous_raster_for_classification = Path(coniferous_layer_for_classification.source()) if coniferous_layer else None

        tbk_result_dir = result_dir
        tbk_result_dir.mkdir(parents=True, exist_ok=True)

        # --- Locate template (relative to plugin)
        timer.step("Resolved parameters")
        template_path = Path(__file__).resolve().parents[2] / "resources" / "TBk_Template.qgz"

        if not template_path.exists():
            raise Exception(f"Template not found: {template_path}")

        project_copy_path = tbk_result_dir / "TBk_Project.qgz"

        feedback.pushInfo(f"Copy Project Template from: {template_path}")
        feedback.pushInfo(f"to: {project_copy_path}")
        shutil.copyfile(template_path, project_copy_path)

        # --- Load project (independent!)
        timer.step("Start loading project")
        project = QgsProject()
        project.read(str(project_copy_path))

        # --- Raster metadata
        timer.step("Reading raster metadata")
        meta_data = get_raster_metadata(vhm_10m)

        epsg = meta_data["epsg"]
        xmin, ymin, xmax, ymax = meta_data["extent"]
        feedback.pushInfo(f"CRS: EPSG:{epsg}, xmin, ymin, xmax, ymax {xmin, ymin, xmax, ymax}")

        # --- Set “last zoomed extent” for the project map canvas
        timer.step("Set project map canvas extent to raster extent")
        project.writeEntry("ProjectSettings", "/MapCanvasExtentXMin", str(xmin))
        project.writeEntry("ProjectSettings", "/MapCanvasExtentXMax", str(xmax))
        project.writeEntry("ProjectSettings", "/MapCanvasExtentYMin", str(ymin))
        project.writeEntry("ProjectSettings", "/MapCanvasExtentYMax", str(ymax))

        # --- CRS
        timer.step("Apply CRS to project and all layers")
        crs = QgsCoordinateReferenceSystem(f"EPSG:{epsg}")
        project.setCrs(crs)

        for lyr in project.mapLayers().values():
            lyr.setCrs(crs)

        # --- Auto-detect related raster files
        folder = vhm_10m.parent
        files = {
            "vhm_10m_points": folder / "VHM_10m_points.gpkg",
            "vhm_150cm": folder / "VHM_150cm.tif",
            "vhm_detail": folder / "VHM_detail.tif",
            "coniferous_raster": folder / "MG_10m.tif",
            "coniferous_raster_for_classification": folder / "MG_10m_binary.tif",
            "diff_hdom_vhm": result_dir / "bk_process" / "diff_hdom_vhm.tif",
        }

        # Convert missing files to None
        for k, f in files.items():
            if not f.exists():
                feedback.pushInfo(f"File not found for {k}: {f}")
                files[k] = None
            else:
                files[k] = str(f.resolve())

        # --- Replace layer sources
        timer.step("Replace layer sources")

        def replace_layer(layer_name, new_path):
            if not new_path:
                return
            layers = project.mapLayersByName(layer_name)
            if not layers:
                feedback.pushInfo(f"> Layer not found: {layer_name}")
                return
            else:
                feedback.pushInfo(f"> Layer path replaced for: {layer_name} ({new_path})")
            layer = layers[0]
            provider = layer.providerType()
            options = layer.dataProvider().ProviderOptions()
            layer.setDataSource(new_path, layer.name(), provider, options)

        replace_layer("Vegetationshöhe (VHM) 10m", str(vhm_10m))
        replace_layer("Vegetationshöhe (VHM) 10m Labels", files["vhm_10m_points"])
        replace_layer("Vegetationshöhe (VHM) 150cm", files["vhm_150cm"])
        replace_layer("Vegetationshöhe (VHM) detail", files["vhm_detail"])
        replace_layer("Nadelholzanteil (WMG) 10m", files["coniferous_raster"])
        replace_layer("Nadelholzanteil (WMG) 10m binär", files["coniferous_raster_for_classification"])
        replace_layer("Differenz hdom <> VHM 10m", files["diff_hdom_vhm"])

        # --- Layout extent
        timer.step("Update layout extents")
        bb = QgsRectangle(xmin, ymin, xmax, ymax)

        def set_layout_extent(layout_name):
            layout = project.layoutManager().layoutByName(layout_name)
            if not layout:
                feedback.pushInfo(f"Layout not found: {layout_name}")
                return

            refmap = layout.referenceMap()
            if refmap:
                refmap.zoomToExtent(bb)

        layouts = [
            "TBk_Bestandeskarte A1 Hochformat",
            "TBk_Bestandeskarte A1 Querformat",
            "TBk_Bestandeskarte A3 Hochformat",
            "TBk_Bestandeskarte A3 Querformat",
        ]

        for l in layouts:
            set_layout_extent(l)

        # --- Save
        timer.step("Writing project")
        project.write(str(project_copy_path))

        timer.finish()

        return {"OUTPUT_PROJECT": str(project_copy_path)}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'TBk create QGIS Project (.qgz)'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def shortHelpString(self):
        return ""

    def createInstance(self):
        return TBkCreateProject()
