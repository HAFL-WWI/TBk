# TBk QGIS Plugin
Toolkit for developing forest stand maps (in German TBk: **T**oolkit **B**estands**k**arte) from remote sensing data: a simple python algorithm that builds a tree stand map, based on a vegetation height model ([TBk on planfor.ch](https://www.planfor.ch/tool/9)).


## 1 Introduction
TBk was developed at BFH-HAFL for creating stand maps from remote sensing data. It can be used to automatically delineate stands based on the spatial distribution of the dominant trees, characterized by the maximum height per unit area of a vegetation height model (VHM). For each stand, the dominant height (hdom), the maximum height (hmax) and the degree of cover (DG, in German: Deckungsgrad) of the main layer are determined. In addition, the basic structure (uniform or non-uniform) of the stands can be roughly determined and the proportion of coniferous wood can be estimated. A description of all attributes can be found at the end of this document. In a post-processing step, particularly dense and “sparse” sub-areas within the stands can also be separated.

| |                                                                                                                                                                                                                                                                                                                |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**Result** | TBk stand map with information regarding top height, crown cover, mixing ratio (deciduous or coniferous wood proportion) and basic structure, provided as vector geometries with attributes.                                                                                                                   |
|**Data sources** | - Forest mask: project perimeter (vector geometry)<br/>- Vegetation height model: raster data, e.g. from LiDAR data with a resolution of ≤ 1 m (or LFI vegetation height model, Link)<br/>- Degree of forest mixture: information on deciduous/coniferous wood (raster data, resolution typically 10 m)        |
| **Accuracy** | - General: Accuracy and timeliness depend on the VHM. The primary sources of error are steep northern slopes and rocks.<br/>- Stand boundaries: The demarcation is accurate to about 10-20 m and the minimum stand size is 10 a (by default)|
| **Contact:** | Berner Fachhochschule BFH<br/> Hochschule für Agrar-, Forst- und Lebensmittelwissenschaften HAFL<br/> Hannes Horneber (hannes.horneber@bfh.ch) <br/> Christian Rosset (christian.rosset@bfh.ch) 


## 2 Installing the QGIS plugin
The plugin requires QGIS version 3.10 or higher. In addition, the QGIS version must have GRASS and GRASS Provider installed and enabled (see Plugin Management). 

The plugin can be installed as a ZIP file and then imported into QGIS.

The plugin adds tools to the Processing tool window. These are functions for preprocessing (prepare base data, e.g. VHM and mixture degree), for generating the stand map, and for postprocessing stand maps (e.g. postprocess local density to determine sparse and dense areas). 

To avoid problems, it is recommended to run the plugin locally, i.e. do not save input and output data on a shared drive / cloud-service (like OneDrive). Sometimes (temporary) output files can't be written or read and cause errors. 


## 3 Preparation of input data
The input data must meet certain conditions and may need to be processed beforehand. The necessary steps are explained in this section. They should definitely be carried out in the order listed here.
The following input data is required:
• Project perimeter as vector geometry (“forest mask”)
• Vegetation height model (VHM) as a grid with a resolution of ≤ 1.5 m
• forest mixture degree (MG) (optional)
The input data does not necessarily have to be stored in the same coordinate system, but it is recommended to project all input data into the same coordinate system before starting. In any case, all input data must be correctly projected, i.e. there must be no errors in the projection. NoData must also be defined correctly.

### 3.1. Error checking: project perimeter
The project perimeter should be available as a single layer that covers the entire forest area to be processed.
It is imperative that there are no geometry or topology errors (e.g. duplicate nodes, overlaps, gaps, etc.), otherwise the TBk algorithm will stop and no result can be generated. Therefore, the perimeter layer should always be checked for such errors first and, if necessary, corrected. There is a particular risk of topological errors with multi-polygons consisting of many small parts (e.g. if forest paths are excluded from the project perimeter).
In QGIS, the standard tools for this are Check validity and Repair geometries. Many simple errors can be corrected using these two standard tools.

### 3.2. Preparation of the vegetation height model
The VHM should be available in a resolution of ≤ 1.5 m (since this resolution is used for calculating the crown cover) and cover the entire project perimeter. However, the TBk stand delineation algorithm requires a version of the VHM that is masked to the project perimeter, aggregated to 10 x 10m, and additionally a 150 x 150cm version of the VHM as input.
The QGIS plugin contains the preprocessing tool to generate the required files.
If the script is executed multiple times, the already existing output data is actually automatically deleted because it cannot be overwritten. However, this does not work properly if the data is still open somewhere. Therefore, to be on the safe side, it is recommended to either manually delete the already generated output data or specify a different storage location/file name before running the script again.

### 3.3. Preparation of forest mixture grid
The use of a forest mixture grid is optional but recommended. If it is used, the TBk algorithm requires raster data with values from 0 and 100 as input, which describe the proportion of coniferous wood as a percentage per pixel. The grid should cover the entire project perimeter and has to be aligned to the 10 x 10 m VHM.
Again, the QGIS plugin contains the preprocessing tool to generate the required files.
If the input raster already indicates the NH portion in values of 0 and 100, the prepare script should still be executed to ensure the correct alignment with the VHM. However, the check mark “Reclassify MG Values” must then be deactivated. 
If the script is executed multiple times, the already existing output data is actually automatically deleted because it cannot be overwritten. However, this does not work properly if the data is still open somewhere. To be on the safe side, it is therefore recommended to either manually delete the already generated output data or to specify a different storage location/file name before running the script again.


## 4 TBk execution
The main algorithm is implemented in the plugin in the TBk generation function.
 
The files generated by the preprocessing functions are used as input: `vhm_10m.tif`, `vhm_150cm.tif`, `MG_10m.tif` and `MG_10m_binary.tif` (both optional). Apart from these, the project perimeter is needed as vector geometry.
In addition, the storage location for the output has to be specified (otherwise the result will be written to a temporary folder and is hard to find). Under 'Advanced parameters', there are various customization options, but normally these do not need to and should not be changed. 

The “Delete temporary files and fields” box is ticked by default.

Main output is the stand map 'TBk_Bestandeskarte.gpkg' described at the beginning. In addition, a QGIS project file 'TBk_Project.qgz' is generated, which visualizes the results in a variety of ways. Four predefined, complete print layouts (A1 and A3, each in portrait and landscape format) are also available for generating printed maps.
