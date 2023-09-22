config = {
    # TBk Jura
    # default config
    # processed by: Hannes Horneber (2023-08-15)
    # reused 2023-08 for different year (respective number replaced)
    # changed to cantonal forest mask

    # Python, TBk and R paths
    "arcgis_python": r'C:\Python27\ArcGIS10.8\python.exe',                  # ArcGIS python path
    "tbk_tool_path": r'D:\GIS-Projekte\TBk\tbk-master',                     # TBk tool path
    "r_path": r'C:\PROGRA~1\R\R-4.1.1\bin\Rscript.exe',                     # R path (use short form for spaces!)

    # multi-process mode
    "number_of_processes": 2,                                               # Nbr of processes in multi-process mode

    # Input files
    "working_root": r'D:\GIS-Projekte\TBk\TBk_JU\tbk_2022',                 # Directory containing the input files
    "vhm_10m": 'vhm_2022_10m.tif',                                          # VHM 10m as main TBk input
    "vhm_150cm": 'vhm_2022_150cm.tif',                                      # VHM 150cm to calculate DG
    "coniferous_raster": 'MG_2022_detail_100.tif',                                                 # Coniferous raster for classification
    "coniferous_raster_detail": 'MG_2022_detail_100.tif',                                      # Coniferous raster to calculate stand mean
    "perimeter": 'waldmaske_nature_forestiere_indicative_202305_jura_bufferdissolved.shp',     # Perimeter shapefile to clip final result

    # Default log file name
    "logfile_name": "tbk_processing.log",                                   # Will be stored in the result directory

    # Main TBk parameters (for details see run_stand_classification function)
    "description": 'TBk Jura 2022',                                      # Short description
    "useConiferousRasterForClassification": True,                          # If to consider it for classification
    "zoneRasterFile": 'null',                                               # Zone raster
    "min_tol": 0.1,                                                         # Relative min tolerance
    "max_tol": 0.1,                                                         # Relative max tolerance
    "min_corr": 4,                                                          # Extension of the range down [m]
    "max_corr": 4,                                                          # Extension of the range up [m]
    "min_valid_cells": 0.5,                                                 # Minimum relative amount of valid cells
    "min_cells_per_stand": 10,                                              # Minimum cells per stand
    "min_cells_per_pure_stand": 30,                                         # Minimum cells for pure mixture stands
    "vhm_min_height": 0,                                                    # VHM minimum height
    "vhm_max_height": 60,                                                   # VHM maximum height

    # Additional parameters
    "min_area_m2": 1000,                                                    # Min. area to eliminate small stands
    "similar_neighbours_min_area": 3000,                                    # Min. area to merge similar stands
    "similar_neighbours_hdom_diff_rel": 0.15,                               # hdom relative diff to merge similar stands
    "attributes_script": 'attributes_default.py',                           # Script to build custom stand attributes
    "calc_mixture_for_main_layer": True                                     # Also calc coniferous prop. for main layer
}
