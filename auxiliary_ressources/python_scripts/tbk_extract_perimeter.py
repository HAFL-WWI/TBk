from qgis.core import *
from qgis.gui import *
import os

#------- INPUT PARAMETERS -------#
#--- Set paths

# extraction perimeter
extraction_perimeter = "C:/Users/hbh1/Projects/H07_TBk/TBk__Kleinprojekte/HAFL/data/bgb/extraction_perimeter.gpkg|layername=extraction_perimeter"

# TBk path
tbk_path        = "C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/data_hafl/tbk2012/20230310-1426"
tbk_output_path = "C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/data_hafl/tbk2012/extracted/20230310-1426"

print("--------------------------------------")
print("----------- TBk EXTRACTION -----------")
print(f"Extracting from {tbk_path}")
print(f"to {tbk_output_path}")
print(f"with perimeter {extraction_perimeter}")
print("--------------------------------------")

#--- Set (default) paths
tbk_main_dataset = "TBk_Bestandeskarte.shp"
# TBk_Bestandeskarte = "TBk_Bestandeskarte.gpkg"

# vector datasets
tbk_vector_datasets = ["local_densities/TBk_local_densities.gpkg",
          "stands_highest_tree.shp",
          "polygons_to_dissolve.shp",
          "stands_simplified.shp"]

# raster datasets
tbk_raster_datasets = ["dg_layers/dg_layer.tif",
                       "dg_layers/dg_layer_ks.tif",
                       "dg_layers/dg_layer_us.tif",
                       "dg_layers/dg_layer_ms.tif",
                       "dg_layers/dg_layer_os.tif",
                       "dg_layers/dg_layer_ueb.tif",
                       "../VHM_10m.tif",
                       "../VHM_150cm.tif",
                       "../VHM_detail.tif",
                       "../MG.tif",
                       "classified_raw.tif",
                       "classified_smooth_2.tif"]

print("Using default paths and extracting ")
print(tbk_main_dataset)
print(tbk_vector_datasets)
print(tbk_raster_datasets)

#------- INITIALIZE -------#
TBk_Bestandeskarte_in = os.path.join(tbk_path, tbk_main_dataset)
TBk_Bestandeskarte_out = os.path.join(tbk_output_path, tbk_main_dataset)

temp_extraction_perimeter_vector = os.path.join(tbk_output_path, 'temp', 'extraction_perimeter_vector.gpkg')
temp_extraction_perimeter_raster = os.path.join(tbk_output_path, 'temp', 'extraction_perimeter_raster.gpkg')

#------- PROCESSING -------#

# init processing results/outputs
outputs = {}

#--- Extract stands and prepare stand-based extraction perimeter
print("----------- SETUP EXTRACTION -----------")
print("build spatial index")
alg_params = { 'INPUT': TBk_Bestandeskarte_in }
outputs['TBk_Bestandeskarte_Indexed'] = processing.run('native:createspatialindex', alg_params)

# Extract by location
if not os.path.exists(TBk_Bestandeskarte_out):
    print("extract stands to " + TBk_Bestandeskarte_out)
    # create output folder if it doesn't exist
    if not os.path.exists(os.path.dirname(TBk_Bestandeskarte_out)):
        os.makedirs(os.path.dirname(TBk_Bestandeskarte_out))
    alg_params = {
        'INPUT': TBk_Bestandeskarte_in,
        'INTERSECT': extraction_perimeter,
        'PREDICATE': [0],  # intersect
        'OUTPUT': TBk_Bestandeskarte_out
    }
    outputs['TBk_Bestandeskarte_extracted'] = processing.run('native:extractbylocation', alg_params)
else:
    outputs['TBk_Bestandeskarte_extracted'] = {'OUTPUT': TBk_Bestandeskarte_out}
# # print("load")
# my_layer = load_layer(outputs['TBk_Bestandeskarte_extracted']['OUTPUT'], "TBk_Bestandeskarte_extracted")

# Buffer+Dissolve stands for vector and raster
if not os.path.exists(temp_extraction_perimeter_vector):
    # create output folder if it doesn't exist
    if not os.path.exists(os.path.dirname(temp_extraction_perimeter_vector)):
        os.makedirs(os.path.dirname(temp_extraction_perimeter_vector))
    alg_params = {
        'DISSOLVE': True,
        'DISTANCE': 0.0001,
        'END_CAP_STYLE': 0,  # Round
        'INPUT': outputs['TBk_Bestandeskarte_extracted']['OUTPUT'],
        'JOIN_STYLE': 0,  # Round
        'MITER_LIMIT': 2,
        'SEGMENTS': 5,
        'OUTPUT': temp_extraction_perimeter_vector
    }
    outputs['extraction_perimeter_vector'] = processing.run('native:buffer', alg_params)

    alg_params = {
        'DISSOLVE': True,
        'DISTANCE': 10.0,
        'END_CAP_STYLE': 0,  # Round
        'INPUT': outputs['TBk_Bestandeskarte_extracted']['OUTPUT'],
        'JOIN_STYLE': 0,  # Round
        'MITER_LIMIT': 2,
        'SEGMENTS': 5,
        'OUTPUT': temp_extraction_perimeter_raster
    }
    outputs['extraction_perimeter_raster'] = processing.run('native:buffer', alg_params)

#--- Extract from Vector Layers
print("----------- START EXTRACTING VECTOR DATASETS -----------")

# iterate over all vector datasets
for i, ds in enumerate(tbk_vector_datasets):
    # build input and output path
    dataset_in = os.path.join(tbk_path, ds)
    dataset_out = os.path.join(tbk_output_path, ds)

    print(dataset_out)
    if not os.path.exists(dataset_out):
        # create output folder if it doesn't exist
        if not os.path.exists(os.path.dirname(dataset_out)):
            os.makedirs(os.path.dirname(dataset_out))
        alg_params = {
            'INPUT': dataset_in,
            'INTERSECT': temp_extraction_perimeter_vector,
            'PREDICATE': [6],  # are within
            'OUTPUT': dataset_out
        }
        outputs[f'vector_{i}'] = processing.run('native:extractbylocation', alg_params)

#--- Extract from Raster Layers
print("----------- START EXTRACTING RASTER DATASETS -----------")
# iterate over all raster datasets
for i, ds in enumerate(tbk_raster_datasets):
    # build input and output path
    dataset_in = os.path.join(tbk_path, ds)
    dataset_out = os.path.join(tbk_output_path, ds)

    print(dataset_out)
    if not os.path.exists(dataset_out):
        # create output folder if it doesn't exist
        if not os.path.exists(os.path.dirname(dataset_out)):
            os.makedirs(os.path.dirname(dataset_out))
        # Clip raster by mask layer
        alg_params = {
            'ALPHA_BAND': False,
            'CROP_TO_CUTLINE': True,
            'DATA_TYPE': 0,  # Use Input Layer Data Type
            'EXTRA': '',
            'INPUT': dataset_in,
            'KEEP_RESOLUTION': False,
            'MASK': temp_extraction_perimeter_raster,
            'MULTITHREADING': True,
            'NODATA': None,
            'OPTIONS':'COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
            'SET_RESOLUTION': False,
            'SOURCE_CRS': None,
            'TARGET_CRS': None,
            'TARGET_EXTENT': None,
            'X_RESOLUTION': None,
            'Y_RESOLUTION': None,
            'OUTPUT': dataset_out
        }
        outputs[f'raster_{i}'] = processing.run('gdal:cliprasterbymasklayer', alg_params)

print("----------- EXTRACTION FINISHED, CLEANING UP -----------")
#--- Cleanup

try:
    os.remove(temp_extraction_perimeter_vector)
    os.remove(temp_extraction_perimeter_raster)
    print('Temp Files deleted')
except:
    print("Temp Files were not deleted")

try:
    print(f'attempt delete {os.path.dirname(temp_extraction_perimeter_raster)}')
    os.rmdir(os.path.dirname(temp_extraction_perimeter_raster))
    print('Temp Folder deleted')
except:
    print("Temp folder was not deleted")

print("-----------       DONE     -----------")
print("--------------------------------------")
print(outputs)