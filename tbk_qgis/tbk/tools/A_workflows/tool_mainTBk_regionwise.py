# todo: set header
import os

import processing
import logging
from collections import ChainMap

from qgis._core import QgsProcessingFeatureSourceDefinition, QgsFeatureRequest, QgsVectorLayer, QgsVectorFileWriter, \
    QgsFeature, QgsProject, QgsWkbTypes, QgsProcessing

from tbk_qgis.tbk.general.tbk_utilities import getVectorSaveOptions
from tbk_qgis.tbk.tools.A_workflows.tbk_qgis_processing_algorithm_toolsA import TBkProcessingAlgorithmToolA
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
from tbk_qgis.tbk.tools.G_utility.tool_postprocess_merge_stand_maps import TBkPostprocessMergeStandMaps

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
        overwrite = False

        # set logger
        self._configure_logging(output_root, parameters['logfile_name'])
        log = logging.getLogger(self.name())

        # --- run main algorithm
        log.info('TBk Starting Regionwise Processing')

        # Load the perimeter vector layer from the path stored in parameters
        perimeter_layer = QgsVectorLayer(parameters["perimeter"], "perimeter", "ogr")
        if not perimeter_layer.isValid():
            raise Exception(f"Invalid perimeter layer: {perimeter_layer.source()}")
        num_regions = perimeter_layer.featureCount()
        log.info(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")
        print(f"Loaded perimeter {perimeter_layer.source()}.\nRegionwise processing for {num_regions} regions")

        # Create subfolder "regions" within output_root
        regions_dir = os.path.join(output_root, 'regions')
        os.makedirs(regions_dir, exist_ok=True)

        # Loop over each feature in the perimeter layer
        log.info(f"Processing single regions")
        # list for storing all results
        region_stand_maps = []
        region_ID_prefix = []
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

            if overwrite or not os.path.exists(vhm_10m_clipped):
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

            if overwrite or not os.path.exists(mg_10m_clipped):
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

            # --- Remove buffered layer from registry and delete it
            QgsProject.instance().removeMapLayer(buffered_feature_layer.id())
            buffered_feature_layer = None  # Ensures layer is dereferenced

            # Construct the output path for the vector file (GeoPackage)
            output_vector = os.path.join(region_base_data_dir, f'perimeter_{region_name}.gpkg')

            if overwrite or not os.path.exists(output_vector):
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

            # --- Configure parameters for region

            # copy parent parameters and adjust only those relevant for the region
            parameters_region = parameters.copy()
            parameters_region["config_file"] = ""
            parameters_region["perimeter"] = output_vector
            parameters_region["vhm_10m"] = vhm_10m_clipped
            parameters_region["coniferous_raster_for_classification"] = mg_10m_clipped
            parameters_region["output_root"] = region_root_dir
            parameters_region["working_root"] = os.path.join(region_root_dir, 'bk_process')
            parameters_region["result_dir"] = region_root_dir
            # todo: some of these paths are still hardcoded, need to be dynamic
            parameters_region["output_stand_delineation"] = os.path.join(region_root_dir, 'bk_process',
                                                                         'stand_boundaries.gpkg')
            # --- Run Stand Delineation
            if overwrite or not os.path.exists(parameters_region["output_stand_delineation"]):
                print(f"STAND DELINEATION: \n{parameters_region['perimeter']}")
                results_stand_delineation = processing.run(TBkStandDelineationAlgorithm(), parameters_region,
                                                           context=context, feedback=feedback)
            else:
                print(f"Skipped STAND DELINEATION, file already exists (overwrite = False)")

            parameters_region["input_to_simplify"] = parameters_region["output_stand_delineation"]
            parameters_region["output_simplified"] = os.path.join(region_root_dir, 'bk_process',
                                                                  'stands_simplified.gpkg')
            # --- Simplify and eliminate
            if overwrite or not os.path.exists(parameters_region["output_simplified"]):
                print(f"SIMPLIFY & CLEAN: \n{parameters_region['input_to_simplify']}")
                results_simplify = processing.run(TBkSimplifyAndCleanAlgorithm(), parameters_region,
                                                  context=context, feedback=feedback)
            else:
                print(f"Skipped SIMPLIFY & CLEAN, file already exists (overwrite = False)")

            parameters_region["input_to_clip"] = parameters_region["output_simplified"]
            parameters_region["output_clipped"] = os.path.join(region_root_dir, 'bk_process', 'stands_clipped.gpkg')

            # --- Clip
            if overwrite or not os.path.exists(parameters_region["output_clipped"]):
                print(f"CLIP: \n{parameters_region['input_to_clip']}")
                results_clipped = processing.run(TBkClipToPerimeterAndEliminateGapsAlgorithm(), parameters_region,
                                                 context=context, feedback=feedback)
            else:
                print(f"Skipped CLIP, file already exists (overwrite = False)")

            # --- Merge
            parameters_region["input_to_merge"] = parameters_region["output_clipped"]
            parameters_region["output_merged"] = os.path.join(region_root_dir, 'bk_process', 'stands_merged.gpkg')

            if overwrite or not os.path.exists(parameters_region["output_merged"]):
                print(f"MERGE: \n{parameters_region['input_to_merge']}")
                algOutput = processing.run(TBkMergeSimilarNeighboursAlgorithm(), parameters_region,
                               context=context, feedback=feedback)
            else:
                print(f"Skipped MERGE, file already exists (overwrite = False)")

            # --- Eliminate second pass
            parameters_region["input_to_simplify_2"] = parameters_region["output_merged"]
            parameters_region["output_simplified_2"] = os.path.join(region_root_dir, 'bk_process', 'stands_simplified_2.gpkg')
            # remove small and elongated polygons
            # expression = f"with_variable('shape_index', $area / ($perimeter^2) * 100, " \
            #              f"($area < {parameters_region['min_area_m2']})" \
            #              f"OR (shape_index < 1.5 AND $area < ({parameters_region['min_area_m2']} + 500) AND \"hdom\" < 10)" \
            #              f"OR (shape_index < 2.05 AND $area < ({parameters_region['min_area_m2']} + 500) AND \"type\" = 'remainder')" \
            #              f"OR (shape_index < 2.2 AND \"type\" = 'remainder')"
            expression = f"with_variable('shape_index', $area / ($perimeter^2) * 100, " \
                         f"($area < {parameters_region['min_area_m2']}) " \
                         f"OR (@shape_index < 1.5 AND $area < ({parameters_region['min_area_m2']} + 500) AND hdom < 10) " \
                         f"OR (@shape_index < 2.05 AND $area < ({parameters_region['min_area_m2']} + 500) AND type = 'remainder') " \
                         f"OR (@shape_index < 2.2 AND type = 'remainder'))"

            if overwrite or not os.path.exists(parameters_region["output_simplified_2"]):
                print(f"Second ELIMINATE pass: \n{parameters_region['output_simplified_2']}")
                # Select by area_attribute
                alg_params = {
                    'EXPRESSION': expression,
                    'INPUT': algOutput['OUTPUT'],
                    'METHOD': 0,  # creating new selection
                }
                algOutput = processing.run('qgis:selectbyexpression', alg_params, context=context,
                                           feedback=feedback, is_child_algorithm=True)

                # processing.run("native:saveselectedfeatures", {
                #     'INPUT': algOutput['OUTPUT'],
                #     'OUTPUT': 'C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_test/regions/test_select.gpkg'})

                # Eliminate selected polygons
                alg_params = {
                    'INPUT': algOutput['OUTPUT'],
                    'MODE': 2,  # Largest Common Boundary
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }
                algOutput = processing.run('qgis:eliminateselectedpolygons', alg_params,
                                           context=context, feedback=feedback,
                                           is_child_algorithm=True)
                # Field calculator
                alg_params = {
                    'FIELD_LENGTH': 0,
                    'FIELD_NAME': "area_m2",
                    'FIELD_PRECISION': 0,
                    'FIELD_TYPE': 0,  # Decimal (double)
                    'FORMULA': '$area',
                    'INPUT': algOutput['OUTPUT'],
                    'OUTPUT': parameters_region["output_simplified_2"]
                }
                algOutput = processing.run('native:fieldcalculator', alg_params, context=context,
                                           feedback=feedback, is_child_algorithm=True)
            else:
                print(f"Skipped second eliminate, file already exists (overwrite = False)")

            # --- Cleanup
            parameters_region["input_to_clean"] = parameters_region["output_simplified_2"]
            parameters_region["output_clean"] = os.path.join(region_root_dir, 'bk_process', 'stands_clean.gpkg')

            if overwrite or not os.path.exists(parameters_region["output_simplified_2"]):
                algOutput = processing.run("TBk:TBk postprocess Cleanup",
                               {'input_stand_map': algOutput['OUTPUT'],
                                'output_stand_map_clean': parameters_region["output_clean"]})
                # algOutput = processing.run("TBk:TBk postprocess Cleanup",
                #                {'input_stand_map': 'abc',
                #                 'output_stand_map_clean': parameters_region["output_clean"]})
            else:
                print(f"Skipped cleanup, file already exists (overwrite = False)")

            # --- Collect regions and ID/name
            region_stand_maps.append(parameters_region["output_clean"])
            region_ID_prefix.append(feature["region"])

        print(f"All Regions processed: \n{region_ID_prefix}")
        log.info(f"All Regions processed: \n{region_ID_prefix}")
        log.info(f"All Regions processed: \n{region_stand_maps}")

        parameters_region["output_clean"] = os.path.join(region_root_dir, 'tbk_regions_merged.gpkg')

        print(f"Now merging into one single Stand Map")
        processing.run("TBk:TBk postprocess merge stand maps", {
            'tbk_map_layers': region_stand_maps,
            'id_prefix': 2,  # '2' corresponds to the "custom" option
            'custom_prefix_list': str(region_ID_prefix),  # Pass the list as a string
            'OUTPUT': parameters_region["output_clean"]
        })

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


from qgis.core import QgsVectorLayer, QgsFeature, QgsField, QgsVectorFileWriter, QgsWkbTypes
from qgis.PyQt.QtCore import QVariant

import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeature, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant

import os
from qgis.core import QgsVectorLayer, QgsVectorFileWriter, QgsProject, QgsFeature, QgsField, QgsWkbTypes
from PyQt5.QtCore import QVariant


def merge_layers_with_composite_id(vector_paths, region_ids, output_path):
    """
    Merges multiple vector layers into a single layer, adding a composite ID.

    Parameters:
        vector_paths (list): List of paths to the vector layers to be merged.
        region_ids (list): List of region IDs corresponding to each vector layer.
        output_path (str): Path to save the merged output layer.
    """

    # Verify inputs
    if len(vector_paths) != len(region_ids):
        raise ValueError("The number of region IDs must match the number of vector paths.")

    # Remove existing output file if it exists
    if os.path.exists(output_path):
        os.remove(output_path)

    # Create an empty memory layer for merging
    crs = QgsProject.instance().crs()  # Assume all layers share project CRS
    merged_layer = QgsVectorLayer(f"Polygon?crs={crs.authid()}", "merged_layer", "memory")
    merged_data_provider = merged_layer.dataProvider()

    # Fields to include in the merged layer
    merged_data_provider.addAttributes([
        QgsField("ID", QVariant.String),
        QgsField("ID_inRegion", QVariant.String)
    ])
    merged_layer.updateFields()

    # Iterate through each vector layer and region ID
    for path, region_id in zip(vector_paths, region_ids):
        # Attempt to load the layer
        layer = QgsVectorLayer(path, "temp_layer", "ogr")

        if not layer.isValid():
            print(f"Error: Could not load the layer from path: {path}")
            continue  # Skip this layer if it couldn't be loaded

        # Ensure the original layer has an "ID" field
        if "ID" not in [field.name() for field in layer.fields()]:
            print(f"Warning: Layer at {path} does not contain an 'ID' field. Skipping this layer.")
            continue

        # Process features and add them to the merged layer
        for feature in layer.getFeatures():
            new_feature = QgsFeature()
            new_feature.setGeometry(feature.geometry())

            # Set the composite ID and original ID fields
            original_id = feature["ID"]
            new_feature.setAttributes([
                f"{region_id}_{original_id}",  # Composite ID (ID field)
                original_id  # Original ID (ID_inRegion field)
            ])

            merged_data_provider.addFeature(new_feature)

    # Define output options and write the merged layer to a file
    output_options = QgsVectorFileWriter.SaveVectorOptions()
    output_options.driverName = "GPKG"
    output_options.fileEncoding = "UTF-8"
    output_options.layerName = "stands_regions_merged"  # Explicit layer name

    error = QgsVectorFileWriter.writeAsVectorFormatV3(
        merged_layer,
        output_path,
        QgsProject.instance().transformContext(),
        output_options
    )

    # Check for errors during the write operation
    if error == QgsVectorFileWriter.NoError:
        print(f"Successfully saved merged layer to {output_path}")
    else:
        print(f"Error: Could not save merged layer to {output_path}. Error code: {error}")
