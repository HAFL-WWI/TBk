# todo: set header
import os

import processing
import logging
from collections import ChainMap

from qgis._core import QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeature, QgsProject, QgsWkbTypes

from tbk_qgis.tbk.general.tbk_utilities import getVectorSaveOptions
from tbk_qgis.tbk.tools.C_stand_delineation.tool_stand_delineation_algorithm import TBkStandDelineationAlgorithm
from tbk_qgis.tbk.tools.C_stand_delineation.tool_simplify_and_clean_algorithm import TBkSimplifyAndCleanAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_merge_similar_neighbours_algorithm import \
    TBkMergeSimilarNeighboursAlgorithm
from tbk_qgis.tbk.tools.D_postproc_geom.tool_clip_and_patch_algorithm import TBkClipToPerimeterAndEliminateGapsAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_calculate_crown_coverage_algorithm import \
    TBkCalculateCrownCoverageAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_add_coniferous_proportion_algorithm import \
    TBkAddConiferousProportionAlgorithm
from tbk_qgis.tbk.tools.E_postproc_attributes.tool_update_stand_attributes_algorithm import \
    TBkUpdateStandAttributesAlgorithm
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA
from osgeo import ogr
ogr.UseExceptions()  # To avoid warnings, though this isn't necessary in future versions.

class TBkAlgorithmRegionwise(TBkProcessingAlgorithmToolA):
    """
    todo
    """
    # array containing the algorithms to use
    algorithms = [
        TBkStandDelineationAlgorithm(),
        TBkSimplifyAndCleanAlgorithm(),
        TBkMergeSimilarNeighboursAlgorithm(),
        TBkClipToPerimeterAndEliminateGapsAlgorithm()
    ]

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        params = []

        # Initialisation config used to adapt the output root UI description
        init_config = {'output_root': {'name': "output_root", 'description': "Output folder"}}

        # init all used algorithm and add their parameters to parameters list
        for alg in self.algorithms:
            alg.initAlgorithm(init_config)
            alg_params = alg.parameterDefinitions()
            alg_params_dict = {p.name(): p for p in alg_params}
            params.append(alg_params_dict)

        # parameters chain map used as a simple way to avoid duplicate parameter
        params_chain = ChainMap(*params)

        unique_param_definitions = list(params_chain.values())
        for param in unique_param_definitions:
            if param.name() != 'working_root':
                self.addParameter(param.clone())

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Handle the working root and temp output folder
        output_root = parameters["output_root"]

        # Load the perimeter vector layer from the path stored in parameters
        perimeter_layer = QgsVectorLayer(parameters["perimeter"], "perimeter", "ogr")
        if not perimeter_layer.isValid():
            raise Exception(f"Invalid perimeter layer: {perimeter_layer.source()}")
        num_regions = perimeter_layer.featureCount()
        print(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")

        # Create subfolder "regions" within output_root
        regions_dir = os.path.join(output_root, 'regions')
        os.makedirs(regions_dir, exist_ok=True)

        # Loop over each feature in the perimeter layer
        for feature in perimeter_layer.getFeatures():
            # --- Setup
            region_name = feature["region"]  # Adjust attribute name if different
            region_root_dir = os.path.join(regions_dir, region_name)
            region_base_data_dir = os.path.join(region_root_dir, 'base_data_preprocessed')
            os.makedirs(region_base_data_dir, exist_ok=True)
            print(f"Processing {region_name} to {region_base_data_dir}")

            # --- Create buffered perimeter feature layer
            buffered_feature_layer = QgsVectorLayer(f"Polygon?crs={perimeter_layer.crs().authid()}", "buffered_mask",
                                                    "memory")
            buffered_feature = QgsFeature()
            buffered_feature.setGeometry(feature.geometry().buffer(10, 5))
            buffered_feature_layer.dataProvider().addFeature(buffered_feature)
            buffered_feature_layer.updateExtents()
            # Add the buffered layer to the map registry (otherwise it isn't found)
            QgsProject.instance().addMapLayer(buffered_feature_layer)

            # Construct output file path for the clipped rasters
            vhm_10m_clipped = os.path.join(region_base_data_dir, 'VHM_10m.tif')
            mg_10m_clipped = os.path.join(region_base_data_dir, 'MG_10m.tif')
            print(f"Clipping VHM10m / Coniferous raster with buffered perimeter")

            # Clip VHM with buffered mask
            processing.run("gdal:cliprasterbymasklayer", {
                'INPUT': parameters["vhm_10m"],
                'MASK': QgsProcessingFeatureSourceDefinition(
                    buffered_feature_layer.source(),
                    selectedFeaturesOnly=False,
                    featureLimit=1,
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                ),
                'OUTPUT': vhm_10m_clipped
            })

            # Clip Coniferous raster with buffered perimeter
            processing.run("gdal:cliprasterbymasklayer", {
                'INPUT': parameters["coniferous_raster_for_classification"],
                'MASK': QgsProcessingFeatureSourceDefinition(
                    buffered_feature_layer.source(),
                    selectedFeaturesOnly=False,
                    featureLimit=1,
                    geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid
                ),
                'OUTPUT': mg_10m_clipped
            })

            # Construct the output path for the vector file (GeoPackage)
            output_vector = os.path.join(region_base_data_dir, f'perimeter_{region_name}.gpkg')

            # Create and populate the single-feature layer
            perimeter_single_feature = QgsVectorLayer(f"Polygon?crs={perimeter_layer.crs().authid()}",
                                                      f"perimeter_{region_name}", "memory")
            perimeter_single_feature_data = perimeter_single_feature.dataProvider()
            perimeter_single_feature_data.addAttributes(perimeter_layer.fields())
            perimeter_single_feature.updateFields()
            perimeter_single_feature_data.addFeature(feature)

            # Commit changes to the layer before saving
            perimeter_single_feature.commitChanges()

            # Save the single feature layer to the GeoPackage
            ctc = QgsProject.instance().transformContext()
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                perimeter_single_feature,  # The memory layer
                output_vector,  # output file path
                ctc,  # CRS
                getVectorSaveOptions('GPKG', 'utf-8')
            )

            # Check for errors
            if error != QgsVectorFileWriter.NoError:
                print(f"Error while saving {output_vector}: {error}")
            else:
                print(f"Successfully saved {region_name} perimeter to {output_vector}")


            # --- Run Stand Delineation

            # copy parent parameters and adjust only those for the region
            parameters_region = parameters
            parameters_region["config_file"] = ""
            parameters_region["perimeter"] = output_vector
            parameters_region["vhm_10m"] = vhm_10m_clipped
            parameters_region["coniferous_raster_for_classification"] = mg_10m_clipped
            parameters_region["output_root"] = region_root_dir
            parameters_region["result_dir"] = region_root_dir

            # execute TBkStandDelineationAlgorithm
            processing.run(TBkStandDelineationAlgorithm(), parameters_region, context=context, feedback=feedback)
            processing.run(TBkSimplifyAndCleanAlgorithm(), parameters_region, context=context, feedback=feedback)

        # set logger
        self._configure_logging(output_root, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # list for storing all results
        results = []

        # --- run main algorithm
        # log.info('Starting')
        #
        # for alg in self.algorithms:
        #     results += processing.run(alg, parameters, context=context, feedback=feedback)
        #
        # log.debug(f"Results: {results}")
        # log.info(f"Finished")

        return {}

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkAlgorithmRegionwise()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Generate BK Regionwise'

    # todo
    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('')
