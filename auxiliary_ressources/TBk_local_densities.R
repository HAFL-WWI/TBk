#------------------------------------------------------------------------------#
# LOCAL STAND DENSITIES
#
# generates polygons delineating local density areas
#
# Segmentation is based on a moving window algorithm
# with a circular moving window that defaults to 7 m radius. 
# The min size for dense/sparse areas defaults to 10 a. 
# (these values can be changed in the section settings).
# An optional second pass was added to remove thin slithers (buffersmoothing - bs)  
#
# TODO: #add the following attributes to the input stand map (e.g. TBk output)
# - area per class  : Flaeche (m2) besonders dichter/lueckiger Teilflaechen
# - dg_dense / dg_sparse / dg_other  : Deckungsgrad (%) besonders dichter/lueckiger/restlicher Flaechen
# TODO: remove intersections of zones based on different moving windows
#
# ATTENTION [updated 08/2023]: 
# Thresholds were defined more or less by gut and aren't systematically validated! 
# However these values have proven to deliver mostly plausible and pragmatical results.
# They need to be adjusted to method...
# (when buffersmoothing, a "greedier" threshold might make sense, since bs shrinks the area a bit)
# ... and also the input data.
# (VHMs based on aerial imagery have a tendency to appear more dense vs. lidar-based VHMs)
#
# CHANGELOG:
# - 2023-08-14: no longer using combination of OS and UEB, but using DG directly 
#   (since it is differently calculated for lower stands)
# - 2023-08-15: redesigned approach, not using clumpy any more. switched to terra/sf.
# - 2023-08-15: now using classes. Add a row in df for each class to be computed.
# - 2023-10-23: bugfixes, also add option to calc all DGs for zones
#
# (c) by Alexandra Erbach, HAFL, BFH, 2021-10
# (c) by Hannes Horneber, HAFL, BFH, 2021-11, 2023-01, 2023-08, 2024-02
#------------------------------------------------------------------------------#

library(terra)
library(sf)
library(smoothr)
library(units)
library(exactextractr)
library(progress)

#-------------------------------#
####   SETTINGS MANDATORY    ####
#-------------------------------#

### input parameters ###
# path to TBk. This assumes the "normal" layer structure (subfolder with dg layers)
# PATH_TBk_INPUT_DIR =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.012359-52-WFOM_TBk_II/04_TBk_Vaud/Daten/tbk_2015/20190916-1853" # 2024-01-15
PATH_TBk_INPUT_DIR = "C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/tbk_hafl/tbk2012_v02/20240415-0136"

# the path to the polygons to perform the algorithm in
# these can be stands (e.g. TBk) or other perimeters
# PATH_SHP = file.path(PATH_TBk_INPUT_DIR,"TBk_Bestandeskarte.shp")
PATH_SHP = file.path(PATH_TBk_INPUT_DIR,"TBk_Bestandeskarte.gpkg")
# PATH_SHP = file.path(PATH_TBk_INPUT_DIR,"perimeter.shp")

# the path to the mg layers to compute NH per area
PATH_MG = file.path(PATH_TBk_INPUT_DIR,"../MG_10m.tif")
# PATH_MG = file.path(PATH_TBk_INPUT_DIR,"../MG.tif")
# PATH_MG = file.path(PATH_TBk_INPUT_DIR,"../MG_2022_detail.tif")

# the path to the dg layers (relative or absolute)
# default is PATH_TBk_INPUT_DIR/dg_layers/dg_layer.tif
PATH_DG = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer.tif")


PATH_DG_KS = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer_ks.tif")
PATH_DG_US = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer_us.tif")
PATH_DG_MS = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer_ms.tif")
PATH_DG_OS = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer_os.tif")
PATH_DG_UEB = file.path(PATH_TBk_INPUT_DIR,"dg_layers/dg_layer_ueb.tif")

# location of the output dataset
PATH_OUTPUT_DIR = file.path(PATH_TBk_INPUT_DIR, "local_densities")
# optional name suffix for output, e.g. "_new"
NAME_SUFFIX = "_v9"

# check paths
ls(pattern = "^PATH_") %>%
  sapply(get) %>%
  sapply(file.exists) %>%
  data.frame(exists = .)

#-------------------------------#
####    SETTINGS OPTIONAL    ####
#-------------------------------#
VERBOSE = TRUE
PLOT_RESULTS = FALSE # for visual output during processing
PLOT_INTERMEDIATE = FALSE # for detailed visual output during processing
CLIP_TO_STAND_BOUNDARIES = TRUE
# write original file with new attributes 
# this can fail if file is in use (will fall back to writing a new file in PATH_OUTPUT_DIR)
OVERWRITE_ORIGINAL_TBK = FALSE
# overwrite existing local density files from previous runs
OVERWRITE_EXISTING_LOCAL_DENSITIES = FALSE

# thresholds for removing polygon parts
# default (as of 2021-10-27): 100 / 100 m^2
# crumb_thresh <- units::set_units(900, m^2) # for large stands/polygons
holes_thresh <- units::set_units(400, m^2)
crumb_thresh <- units::set_units(200, m^2) # for TBk stands

# method to remove thin parts and details of zones
# 0 = not applied, default: 10 (0.5*thickness that is preserved)
BUFFER_SMOOTHING = 7
# default smoothing. Isn't applied if buffer_smoothing is applied or if set to 0; default: 2
KSMOOTH_FACTOR = 0

# radius of circular moving window (in m)
mw_rad = 7
mw_rad_large = 14

# minimum size for dense/sparse "clumps" (in Aren)
# min_size_clump = 15 # default (as of 2021-10-27): 10
min_size_clump = set_units(1200, "m^2")

# minimal size of stand to be processed
min_size_stand = min_size_clump
# min_size_stand = set_units(0.3, "ha")

# determine whether DG is calculated for all layers (KS, US, MS, OS, UEB)
CALC_ALL_DG = TRUE

# Table of classes that are generated
# class:        class ID
# dg_max:       dg_max of class
# dg_min:       dg_min of class
# large_window: boolean (0/1) whether to use a large moving window
# color:        color to plot the class here in R
classes_df <-
  tibble::tribble(
    ~class, ~dg_max, ~dg_min, ~large_window, ~color,
    1,       1,       0.85,   0,             'red',
    2,       0.85,    0.6,    1,             'orange',
    3,       0.6 ,    0.4,    1,             'green',
    4,       0.4 ,    0.25,   1,             'lightblue',
    5,       0.25,    0,      0,             'blue',
    12,      1,       0.60,   1,             'orangered'
  ) %>%
  data.frame()

as_units(min_size_stand)
####_________________________####
####       INITIALIZE        ####
#-------------------------------#

#### ensure dir / log ####
if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("----- PREPARE LOG/DIRECTORY ------")
if(VERBOSE) print("----------------------------------")
START_TIME = Sys.time()
if(VERBOSE) print(paste0("START TIME: ", format(START_TIME, "%Y-%m-%d_%H-%M")))
if(VERBOSE) print(paste0("create output directory and processing log: "))
if(VERBOSE) print(PATH_OUTPUT_DIR)
# attempt to create dir non-recursively, if that fails (likely parent dir not there) try recursive
tryCatch(expr = {
  dir.create(file.path(PATH_OUTPUT_DIR), recursive = FALSE, showWarnings = TRUE)
}, error=function(cond) {
  # recursive dir creation can fail if one of the parent dirs is write-protected (the function seemingly has no if-exist-check)
  dir.create(file.path(PATH_OUTPUT_DIR), recursive = TRUE, showWarnings = TRUE)
  return(cond)
}, silent = TRUE)

log_filepath = file.path(PATH_OUTPUT_DIR, paste0("TBk_local_densities", NAME_SUFFIX, paste0("_log_",format(START_TIME, "%Y-%m-%d_%H-%M-%S"),".txt")))
# start logging R output/message stream (while maintaining console output with split)
sink(file = log_filepath, append = TRUE, type = c("output", "message"), split = TRUE) # needs to be stopped and unlinked in the end

if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("----- START LOCAL DENSITIES ------")
if(VERBOSE) print("----------------------------------")

if(VERBOSE) print("Ensured Folder and Log file")
if(VERBOSE) print(log_filepath)

if(VERBOSE) print("Initialize: Load data from:")
if(VERBOSE) print(PATH_SHP)

#### load data #### 
# load dg raster "DG" (Hauptschicht = hs) and vector data
hs = rast(PATH_DG)
# load other dg rasters (needed only to determine dgs per zone)
if(CALC_ALL_DG){
  dg_ks = rast(PATH_DG_KS)
  dg_us = rast(PATH_DG_US)
  dg_ms = rast(PATH_DG_MS)
  dg_os = rast(PATH_DG_OS)
  dg_ueb = rast(PATH_DG_UEB)
}
mg = rast(PATH_MG)
stands_all = st_read(PATH_SHP)
stands_all$ID_TMP = 1:nrow(stands_all) # unique ID for each geometry
st_agr(stands_all) = "constant" # avoid later warnings

# store resolution
res_hs <- set_units(res(hs)[1], "m")

#### init function ####
# function ras2poly: creates a polygon from a raster and adds attributes from parent
ras2poly <- function(ras_foc, i=0, class=0, poly_parent=NULL){
  # raster to polygon
  poly <- st_as_sf(as.polygons(ras_foc == 1, dissolve=TRUE))
  if(PLOT_INTERMEDIATE) plot(ras_foc, col='red', main=paste0(i, ": (standID:", poly_parent$ID, "  | ID_TMP:", poly_parent$ID_TMP, " class ", class, ")"))
  if(PLOT_INTERMEDIATE) lines(poly_parent)
  if(PLOT_INTERMEDIATE) lines(poly)
  
  # remove holes
  poly_filled <- smoothr::fill_holes(poly, holes_thresh)
  if(PLOT_INTERMEDIATE) lines(poly_filled, col='blue')
  
  # smooth (via buffer or with smoothing algorithm)
  if(BUFFER_SMOOTHING != 0) {
    # remove previous results
    if(exists("poly_smooth")) remove("poly_smooth")
    # catch the case that the negative buffer deletes the whole polygon
    tryCatch(expr={
      poly_smooth = sf::st_buffer(poly_filled, dist= -BUFFER_SMOOTHING)
    }, error=function(cond) {
      # optional: print alert if negative buffer melts polygon
      # message(paste("Polygon melted to buffer:", BUFFER_SMOOTHING))
    }, silent = TRUE)
    
    if(!exists("poly_smooth")) return(NULL) # failed to create
    poly_smooth = sf::st_buffer(poly_smooth, dist=  BUFFER_SMOOTHING+1.5)
  } else {
    # default smoothing
    if(KSMOOTH_FACTOR != 0) {
      poly_smooth <- smoothr::smooth(poly_filled, method = "ksmooth", smoothness = KSMOOTH_FACTOR)
    } else {
      # no smoothing
      poly_smooth <- poly_filled
    }
  }
  if(PLOT_INTERMEDIATE) lines(poly_smooth, col='brown')
  
  # remove small areas (drop crumbs) and crop to stand area
  poly_final <- smoothr::drop_crumbs(poly_smooth, threshold = crumb_thresh)
  if(is.null(poly_final) || !(nrow(poly_final) > 0)) return(NULL)
  
  if(CLIP_TO_STAND_BOUNDARIES) {
    # clip to stand boundaries
    # poly_final <- raster::intersect(poly_final, poly_parent)
    st_agr(poly_final) <- "constant" # avoid warnings
    poly_final <- st_intersection(poly_final, poly_parent)
    
    if(is.null(poly_final) || !(nrow(poly_final) > 0)) return(NULL)
    # ... copies all attributes, so we oughta remove (most of) them
    poly_final <- poly_final[,-(1:ncol(poly_final))]
  }
  # if(PLOT_INTERMEDIATE) plot(poly_final, col='green', add=T)
  if(PLOT_INTERMEDIATE) lines(poly_final, col='green')
  
  # add attributes
  poly_final$nr <- i
  poly_final$class <- class
  # poly_final$area <- st_area(poly_final)
  if(!is.null(poly_parent)){
    poly_final$ID_TMP  <- poly_parent$ID_TMP
    poly_final$standID <- poly_parent$ID
    poly_final$standArea <- st_area(poly_parent) %>% as.numeric() %>% round()
  }
  return(poly_final)
}

####_________________________####
####          MAIN           ####
#-------------------------------#


if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("Done loading data")

# init statstable for attributes
statstable <- data.frame()
# init iteration variables
j <- n_errors <- 0
ID_errors = cbind("i", "stand_ID", "error_message")

# optional plot output
# uncommend dev.off() after for loop when activating these lines
#pdf(paste("C:/Temp/myplots_",name,"_",mw_rad,"_",min_dens,"_",max_dens,".pdf",sep=""), onefile=TRUE, paper="a4", width = 8.27, height = 11.69)
#par(mfrow=c(3,2), oma = c(0, 0, 2, 0))

# Filter stands that are too small
if(VERBOSE) print(paste0("Loaded ", nrow(stands_all), " stands."))
stands = stands_all[st_area(stands_all) >= min_size_stand, ]
if(VERBOSE) print(paste0("Processing ", nrow(stands), " stands that are larger than ", min_size_stand, " ", units(min_size_stand), "."))

### ******************** ####
### iterate over stands/polygons ####
if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("Iterate over stands.")

# init progress bar
pb <- progress_bar$new(format = "(:spin) [:bar] :percent [Elapsed time: :elapsedfull || Estimated time remaining: :eta]",
                       total = nrow(stands),
                       complete = "=",   # Completion bar character
                       incomplete = "-", # Incomplete bar character
                       current = ">",    # Current bar character
                       clear = FALSE,    # If TRUE, clears the bar when finish
                       width = 100)      # Width of the progress bar

for (i in 1:nrow(stands)){
  # debug lines to check single stands
# for (i in 42:47){
  # PLOT_INTERMEDIATE = T # for detailed visual output during processing

  # iteration initialization
  pb$tick()
  flag_polys_created_stand <- F
  # initialize stand stats row with named columns
  stats <- t(setNames(c(stands[i,]$ID, stands[i,]$ID_TMP, i), c("stand_ID", "ID_TMP", "proc_ID")))
  
  error_message = NULL # reset
  error_message = tryCatch(expr={
    # buffer stand to have look at surrounding pixels for focal window
    # stand_buffered = raster::buffer(stands[i,], width= mw_rad_large) # deprecated raster package
    stand_buffered = sf::st_buffer(stands[i,], dist = mw_rad_large)

    # crop and mask hs layer to stand shape
    hs_extent <- crop(hs,stand_buffered)
    hs_mask <- mask(hs_extent,stand_buffered)
    
    # trim if NA values are present
    #TODO check if this works as it is supposed to...
    if (length(hs_mask[!is.na(hs_mask)])>0) {
      # Trim (shrink) a Raster* object by removing outer rows and columns that all have the same value (e.g. NA). 
      # hs_crop <- raster::trim(hs_mask,values=NA)
      hs_crop <- terra::trim(hs_mask, value=NA)
    } else {
      hs_crop <- hs_mask
    }
    
    # create raster masked to stand for calculating dg
    hs_crop_unbuffered <- mask(hs_crop,stands[i,])
    if(PLOT_INTERMEDIATE) plot(hs_crop)
    # if(PLOT_INTERMEDIATE) plot(hs_crop_unbuffered, add=T, col='red')
    if(PLOT_INTERMEDIATE) lines(stands[i,])
    
    # create focal windows
    fw <- terra::focalMat(hs_crop, mw_rad, type='circle')
    fw_2 <- terra::focalMat(hs_crop, mw_rad_large, type='circle')
    # fw <- raster::focalWeight(hs_crop, mw_rad, type='circle')
    # fw_2 <- raster::focalWeight(hs_crop, mw_rad_large, type='circle')
    
    # init focal map
    # basic check whether stand area is bigger than focal window (otherwise skip stand)
    if (nrow(hs_crop) >= 2*nrow(fw) & ncol(hs_crop) >= 2*ncol(fw)){
      # focal: each map contains the degree of cover of neighboring cells (in mw_rad radius)
      focal_map = focal(hs_crop, w=fw, na.rm=TRUE, na.policy="omit")
      focal_map_2 = focal(hs_crop, w=fw_2, na.rm=TRUE, na.policy="omit")
      
      # writeRaster(focal_map, file.path(PATH_OUTPUT_DIR, paste0("focal_map", NAME_SUFFIX, ".tif")))
      #TODO check effect of na.rm = FALSE
      # focal_map = focal(hs_crop, w=fw, na.rm=FALSE, na.policy="omit")
      if(PLOT_INTERMEDIATE) plot(focal_map)
      if(PLOT_INTERMEDIATE) lines(stands[i,])
      if(PLOT_INTERMEDIATE) plot(focal_map_2)
      if(PLOT_INTERMEDIATE) lines(stands[i,])
      
      ### ** ** ** ** ** ** ** ####
      ### > iterate over classes   ####
      
      # run for each class
      for(k in 1:nrow(classes_df)) {
        # flag to check whether a polygon for this class was created (if not, stats table will be populated with NA)
        flag_polys_created_class <- F
        class = classes_df[k,]$class
        
        # use different focal windows for different zone types
        # adding small constants since focal results are not always exactly aligned to 0.0 - 1.0
        if (classes_df[k,]$large_window) {
          ras_foc = (focal_map_2 <= classes_df[k,]$dg_max+0.0001) * (focal_map_2 >= classes_df[k,]$dg_min-0.0001)
        } else {
          ras_foc = (focal_map <=   classes_df[k,]$dg_max+0.0001) * (focal_map >= classes_df[k,]$dg_min-0.0001)
        }
        
        # if(PLOT_INTERMEDIATE) plot(ras_foc)
        # if(PLOT_INTERMEDIATE) lines(stands[i,])
        
        # remove areas overlapping stand
        #TODO check effect when doing this
        # ras_foc[is.na(hs_crop_unbuffered)] <- NA
        
        # eliminate small clusters in raster
        #TODO may improve performance, but may also worsen results (omit important parts)
        # threshold_nr_pixels = min_size_clump / res_hs^2
        # ras_foc_filtered = terra::sieve(ras_foc, threshold=threshold_nr_pixels)
        # plot(ras_foc_filtered)
        # ras_foc <- ras_foc_filtered
        # remove 0 values
        ras_foc[ras_foc == 0] <- NA
        # if(PLOT_INTERMEDIATE)  plot(ras_foc)
        
        #### >> create polygon ####
        # create polygons for density zones
        # check if dense cluster cells are present
        if(length(ras_foc[ras_foc==1])>0){
          # raster to polygon
          multipolygon = ras2poly(ras_foc=ras_foc, i=i, class=class, poly_parent=stands[i,])
          # multipolygon = poly_final

          # check if a non-null polygon is produced
          if(!is.null(multipolygon)){
            # split multipolygon into single polygons and compute area
            
            # it can happen that the resulting geometry contains not only polygons but linestrings/points (probably result of intersect)
            new_polys <- suppressWarnings(st_collection_extract(multipolygon, type = "POLYGON")) # avoid warning if all geometries are polygons
            new_polys <- st_cast(new_polys, "POLYGON", warn = FALSE) # avaoid warning
            new_polys$area <- st_area(new_polys)
            
            # filter by size
            new_polys = new_polys[new_polys$area > min_size_clump,]
            
            # check if any remain
            if((nrow(new_polys) > 0)){
              #### >> add attributes to zones ####
              # add DG attribute
              new_polys$area_pct = round(new_polys$area / new_polys$standArea, 2)
              new_polys$DG = round(exactextractr::exact_extract(hs_crop_unbuffered,new_polys, fun ="mean", progress = F),2)*100
              new_polys$DG_stand = stands[i,]$DG
              
              if(CALC_ALL_DG){
                new_polys$DG_ks = round(exactextractr::exact_extract(dg_ks,new_polys, fun ="mean", progress = F),2)*100
                new_polys$DG_us = round(exactextractr::exact_extract(dg_us,new_polys, fun ="mean", progress = F),2)*100
                new_polys$DG_ms = round(exactextractr::exact_extract(dg_ms,new_polys, fun ="mean", progress = F),2)*100
                new_polys$DG_os = round(exactextractr::exact_extract(dg_os,new_polys, fun ="mean", progress = F),2)*100
                new_polys$DG_ueb = round(exactextractr::exact_extract(dg_ueb,new_polys, fun ="mean", progress = F),2)*100

                new_polys$DG_ks_stand = stands[i,]$DG_ks
                new_polys$DG_us_stand = stands[i,]$DG_us
                new_polys$DG_ms_stand = stands[i,]$DG_ms
                new_polys$DG_os_stand = stands[i,]$DG_os
                new_polys$DG_ueb_stand = stands[i,]$DG_ueb
              }
              new_polys$NH = round(exactextractr::exact_extract(mg,new_polys, fun ="mean", progress = F),0)
              new_polys$NH_stand = stands[i,]$NH
              new_polys$hdom = stands[i,]$hdom
              
              #### >> populate attributes for stands ####
              area_class = round(sum(new_polys$area))
              area_class_pct = round(sum(new_polys$area) / as.numeric(st_area(stands[i,])), 2)
              # dg_class = mean(new_polys$DG_zone)
              dg_class = round(sum(new_polys$DG * new_polys$area) / sum(new_polys$area))
              # nh_class = mean(new_polys$NH_zone)
              nh_class = round(sum(new_polys$NH * new_polys$area) / sum(new_polys$area))
              
              # init or bind to sf polys collection
              if(j>1){
                polys <- rbind(polys, new_polys)
              } else {
                polys <- new_polys
              }
              j <- j+nrow(new_polys)
              # flag for plotting
              flag_polys_created_stand <- T
              flag_polys_created_class <- T
            }
          } 
        } # end if polygon creation
        
        if(!flag_polys_created_class) {
          # populate stand attributes with NA if no polys have been created for class
          area_class <- area_class_pct <- dg_class <- nh_class <- NA
        }
        # append to stands stats vector
        stats <- cbind(stats, area_class, area_class_pct, dg_class, nh_class)
      } # end for-loop through class
      ### ** ** ** ** ** ** ** ####
      
      #### >> TODO: solve intersections orange <> red  ####
      # remove intersections
      # calc attributes afterwards
      
      #### > plot results (optional) ####
      # plot results for visual plausibility check
      if(PLOT_RESULTS){
        # try - failed plotting shouldn't fail the processing
        try(expr={
          plot(hs_crop, main=paste0(i, " ", flag_polys_created_stand, ": (standID:", stands[i,]$ID, "  | ID_TMP:", stands[i,]$ID_TMP, "  | size = ",round(set_units(st_area(stands[i,]), "ha"),1), " ha)"))
          lines(stands[i,])
          # lines(stands[i,], col='green')
          if(flag_polys_created_stand){
            # select only polys for current stand
            polys_temp = polys[polys$standID == stands[i,]$ID,]
            for(k in 1:nrow(classes_df)) {
              lines(polys_temp[polys_temp$class == classes_df[k,]$class,],col=classes_df[k,]$color)
            }
          }
          mtext(text=paste0("mw_rad = ", mw_rad),
                side=3, outer=T,line=0, cex=0.8)
        })
      }
    } else {
      # no dense/sparse areas because too small
      # create stats row anyways to indicate that stand_ID was processed without finding density zones
      # set proc_ID to negative to indicate no find
      stats <- t(setNames(c(stands[i,]$ID, stands[i,]$ID_TMP, -i), c("stand_ID", "ID_TMP" ,"proc_ID")))
      for(k in 1:nrow(classes_df)) {
        area_class <- area_class_pct <- dg_class <- nh_class <- NA
        stats <- cbind(stats, area_class, area_class_pct, dg_class, nh_class)
      }
    }
    
    # set proc_ID to negative to indicate no find
    if(!flag_polys_created_stand) stats[,"proc_ID"] = -i
    
    # append to stands stats vector
    statstable <- rbind(statstable,stats)
  }, error=function(cond) {
    message(paste("Problem with stand: ", i))
    # optional: print error message
    # message(cond)
    return(cond)
  })
  
  # keep list of errors
  if(any(class(error_message) == "error")){
    n_errors = n_errors + 1
    error_and_message = cbind(i, stands$ID_TMP[i], error_message$message)
    ID_errors = rbind(ID_errors, error_and_message)
  }
}
### ******************** ####
if(VERBOSE) print("") # empty line
if(VERBOSE) print("Finished iteration over stands.")
if(VERBOSE) print(paste0("Errors: ", n_errors, " (out of ", nrow(stands), " processed)"))
# dev.off()

#### write error proc IDs ####
if(!is.null(ID_errors) && n_errors > 0){
  #TODO change this to output not proc IDs (list IDs) but the actual stand ID 
  capture.output(ID_errors, file = file.path(PATH_OUTPUT_DIR, paste0("TBk_local_densities", NAME_SUFFIX, "_errors_proc_ID.txt")))
} 


#### write gpkg local density zones ####
if(VERBOSE) print("----------------------------------")
if(VERBOSE) print(paste0("write local density zones to folder: "))
if(VERBOSE) print(PATH_OUTPUT_DIR)

# write files for polygons
polys$ID_TMP <- NULL # tmp. ID is not part of output!
polys$area <- round(as.numeric(polys$area))  # drop unit & round to m^2
polys$area_pct <- as.numeric(polys$area_pct) # drop unit 

PATH_OUTPUT_FILE = file.path(PATH_OUTPUT_DIR, paste0("TBk_local_densities", NAME_SUFFIX, ".gpkg"))
if (file.exists(PATH_OUTPUT_FILE)) {
  if (OVERWRITE_EXISTING_LOCAL_DENSITIES) {
    # delete file first
    # st_write / write_sf allow overwriting the contents of gpkg that are currently used
    # (also for some reason the st_write overwrite routine keeps the original file size 
    # if bigger than the contents it is overwritten with)
    # the use of file.remove avoids both these behaviors (errors when file is used)
    print(paste0("Delete existing results: " , PATH_OUTPUT_FILE))
    if (!file.remove(PATH_OUTPUT_FILE)) {
      PATH_OUTPUT_FILE = file.path(PATH_OUTPUT_DIR, paste0("TBk_local_densities", NAME_SUFFIX, "_", format(START_TIME, "%Y-%m-%d_%H-%M-%S"), ".gpkg"))
    }
  } else {
    # if not supposed to overwrite, create file with timestamp
    PATH_OUTPUT_FILE = file.path(PATH_OUTPUT_DIR, paste0("TBk_local_densities", NAME_SUFFIX, "_", format(START_TIME, "%Y-%m-%d_%H-%M-%S"), ".gpkg"))
  }
}
st_write(st_as_sf(polys), append = FALSE, PATH_OUTPUT_FILE)


#### append attributes to input ####
# and export to file

# add names to table
col_names <- c("stand_ID", "ID_TMP", "local_densities_proc_ID")
for(k in 1:nrow(classes_df)) {
  names_4_class_k <- paste0("z", classes_df[k,]$class, "_", c("area", "area_pct", "dg", "nh"))
  col_names <- c(col_names, names_4_class_k)
}
# data.frame(old = names(statstable), new = col_names) # check the renaming
names(statstable) <- col_names

#TODO: Sometimes result attributes have a varying amount of rows and can't be merged to original table
tryCatch(expr={
  if(VERBOSE) print("----------------------------------")
  if(VERBOSE) print(paste0("left join attribute rows to input geometries (stands)"))
  if(VERBOSE) print(paste0(nrow(statstable), " of ", nrow(stands_all), " were processed (check proc_ID, others are NA)."))
  
  # connect statstable with existing attributetable/geometry (left outer join)
  stands_out = merge(x = stands_all, y = statstable, by = "ID_TMP", all.x = TRUE)
  stands_out$ID_TMP <- NULL # tmp. ID is not part of output!
  stands_out$stand_ID <- NULL # same goes to stand_ID (identical with ID)!
  
  if(OVERWRITE_ORIGINAL_TBK){
    if(VERBOSE) print("Attempt to overwrite input geometries with appendend attributes: ")
    if(VERBOSE) print(PATH_SHP)
    if(VERBOSE) print("Create backup first:")
    PATH_SHP_BACKUP = file.path(PATH_OUTPUT_DIR,paste0(tools::file_path_sans_ext(basename(PATH_SHP)),"_original_backup", "_", format(START_TIME, "%Y-%m-%d_%H-%M-%S"),".gpkg"))
    if(VERBOSE) print(PATH_SHP_BACKUP)
    
    # attempt overwrite. If it fails, toggle overwrite flag.
    # st_write / write_sf allow overwriting the contents of gpkg that are currently used
    # using file.remove and st_write allows to avoid this
    if(file.copy(PATH_SHP, PATH_SHP_BACKUP)){
      print(paste0("Backup successful. Attempting to delete original input geometries."))
      if (!file.remove(PATH_SHP)) {
        print(paste0("Couldn't delete original dataset, won't overwrite."))
        OVERWRITE_ORIGINAL_TBK = FALSE
      } else {
        print(paste0("Delete successful. Will now write input geometires with appended attributes to original path."))
        PATH_OUTPUT_TBK_FILE = PATH_SHP
      }
    } else {
      print(paste0("Couldn't backup, won't overwrite."))
      OVERWRITE_ORIGINAL_TBK = FALSE
    }
  }
  
  if(!OVERWRITE_ORIGINAL_TBK){
    if(VERBOSE) print(paste0("write input geometries with appended attributes to folder: "))
    if(VERBOSE) print(PATH_OUTPUT_DIR)
    
    # write file with new attributes to PATH_OUTPUT_DIR
    PATH_OUTPUT_TBK_FILE = file.path(PATH_OUTPUT_DIR, paste0(tools::file_path_sans_ext(basename(PATH_SHP)),"_local-densities", NAME_SUFFIX, ".gpkg"))
    if (file.exists(PATH_OUTPUT_TBK_FILE)) {
      if (OVERWRITE_EXISTING_LOCAL_DENSITIES) {
        # attempt deleting file first, checks whether file can be deleted
        print(paste0("Delete existing results: " , PATH_OUTPUT_TBK_FILE))
        if (!file.remove(PATH_OUTPUT_TBK_FILE)) {
          PATH_OUTPUT_TBK_FILE = file.path(PATH_OUTPUT_DIR, paste0(tools::file_path_sans_ext(basename(PATH_SHP)),"_local-densities", NAME_SUFFIX, "_", format(START_TIME, "%Y-%m-%d_%H-%M-%S"), ".gpkg"))  
        }
      } else {
        # if not supposed to overwrite, create file with timestamp
        PATH_OUTPUT_TBK_FILE = file.path(PATH_OUTPUT_DIR, paste0(tools::file_path_sans_ext(basename(PATH_SHP)),"_local-densities", NAME_SUFFIX, "_", format(START_TIME, "%Y-%m-%d_%H-%M-%S"), ".gpkg"))  
      }
    }
  } 
  st_write(stands_out, PATH_OUTPUT_TBK_FILE)
  
}, error=function(cond) {# optional: print alert # message(paste("")))
}, silent = FALSE)


if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("------------   DONE   ------------")
if(VERBOSE) print("----------------------------------")
#### output statistics ####
END_TIME = Sys.time()
if(VERBOSE) print(paste0("END TIME: ", format(END_TIME, "%Y-%m-%d_%H-%M")))
DURATION = END_TIME - START_TIME
if(VERBOSE) print(paste0("DURATION: ", DURATION, " secs"))
if(VERBOSE) print(paste0("NR STANDS/PERIMETERS: ", nrow(stands)))
if(VERBOSE) print(paste0("AVG TIME PER STAND: ", DURATION/nrow(stands), " secs"))
if(VERBOSE) print(paste0("NR CREATED POLYGONS: ", nrow(polys)))
if(VERBOSE) print(paste0("AVG TIME PER POLYGON: ", DURATION/nrow(polys), " secs"))

if(VERBOSE) print("----------------------------------")
# stop logging
sink()

