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
# (c) by Hannes Horneber, HAFL, BFH, 2021-11, 2023-01, 2023-08
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
# PATH_TBk_INPUT =  "C:/Users/hbh1/Projects/H07_TBk/TBk_GL/Entwicklung/TBk_GL/20211011-0951_vhm2_min12a" # 2021-11-10
# PATH_TBk_INPUT =  "C:/Users/hbh1/Projects/H07_TBk/TBk_FL/TBk_FL/20210426-1427" # 2022-01-05
# PATH_TBk_INPUT =  "C:/Users/hbh1/Projects/H07_TBk/TBk_diverse/2023-01_Volketswil/tbk2018/20230125-0942" # 2022-01-05
# PATH_TBk_INPUT =  "C:/Users/hbh1/Projects/H07_TBk/TBk_JU/Dev/DG_split/data_aoi" # 2023-08-14
# PATH_TBk_INPUT =  "D:/GIS-Projekte/TBk/TBk_JU/tbk_2022/20230530-1332_arcpy" # 2023-08-14
# PATH_TBk_INPUT =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.008456-52-FWWG-01_TBk_Projekt_HAFL/_Kleinprojekte/2023-10_Limmattal/tbk_2022/20231019-1105" # 2023-09-20
# PATH_TBk_INPUT =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.008456-52-FWWG-01_TBk_Projekt_HAFL/_Kleinprojekte/2023-09_Toppwald/tbk_2012/20230912-1001" # 2023-10-25
# PATH_TBk_INPUT =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.012359-52-WFOM_TBk_II/02_TBk_Jura/Daten/_HARA_/tbk_2022/20230530-1332_arcpy" # 2023-11-03
# PATH_TBk_INPUT =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.012359-52-WFOM_TBk_II/05_TBk_Valais/Daten/TBk_2022/20231031-1501" # 2023-11-05
PATH_TBk_INPUT =  "//bfh.ch/data/HAFL/7 WWI/74a FF WG/742a Aktuell/L.012359-52-WFOM_TBk_II/05_TBk_Valais/Daten/_Sierre_visite2/tbk_2021_50a/20231122-1446" # 2023-11-05

# the path to the polygons to perform the algorithm in
# these can be stands (e.g. TBk) or other perimeters
# PATH_SHP = file.path(PATH_TBk_INPUT,"TBk_Bestandeskarte.gpkg")
PATH_SHP = file.path(PATH_TBk_INPUT,"TBk_Bestandeskarte.shp")
# PATH_SHP = file.path(PATH_TBk_INPUT,"perimeter.shp")

# the path to the mg layers to compute NH per area
PATH_MG = file.path(PATH_TBk_INPUT,"../MG.tif")
# PATH_MG = file.path(PATH_TBk_INPUT,"../MG_2022_detail.tif")

# the path to the dg layers (relative or absolute) 
# default is PATH_TBk_INPUT/dg_layers/dg_layer_XX.tif
PATH_DG = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer.tif")


PATH_DG_KS = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_ks.tif")
PATH_DG_US = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_us.tif")
PATH_DG_MS = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_ms.tif")
PATH_DG_OS = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_os.tif")
PATH_DG_UEB = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_ueb.tif")

# location of the output dataset
PATH_OUTPUT = file.path(PATH_TBk_INPUT, "local_densities")
# optional name suffix for output, e.g. "_new"
NAME_SUFFIX = "_v8"

#-------------------------------#
####    SETTINGS OPTIONAL    ####
#-------------------------------#
VERBOSE = TRUE
PLOT_RESULTS = FALSE # for visual output during processing
PLOT_INTERMEDIATE = FALSE # for detailed visual output during processing
CLIP_TO_STAND_BOUNDARIES = TRUE
# write original file with new attributes 
# this can fail if file is in use (will fall back to writing a new file in PATH_OUTPUT)
OVERWRITE_ORIGINAL_TBK = FALSE

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

# Create empty data frame
classes_df <- data.frame(class = numeric(),
                         dg_max = numeric(),    
                         dg_min = numeric(),
                         large_window = numeric(),
                         color = character(),
                         stringsAsFactors = FALSE)

# List of classes that are generated
# each row represents one class
# config contains class ID, dg_max, dg_min of class, 
# boolean (0/1) whether to use a large moving window
# and a color to plot the class here in R
classes_df[nrow(classes_df)+1, ] <- list(1,   1, 0.85, 0, 'red')
classes_df[nrow(classes_df)+1, ] <- list(2,0.85, 0.6 , 1, 'orange')
classes_df[nrow(classes_df)+1, ] <- list(3,0.6 , 0.4 , 1, 'green')
classes_df[nrow(classes_df)+1, ] <- list(4,0.4 , 0.25, 1, 'lightblue')
classes_df[nrow(classes_df)+1, ] <- list(5,0.25, 0   , 0, 'blue')

classes_df[nrow(classes_df)+1, ] <- list(12,   1, 0.60, 1, 'orangered')

as_units(min_size_stand)
####_________________________####
####       INITIALIZE        ####
#-------------------------------#

if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("----- START LOCAL DENSITIES ------")
if(VERBOSE) print("----------------------------------")

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

# store resolution
res_hs <- set_units(res(hs)[1], "m")

#### init function ####
# function ras2poly: creates a polygon from a raster and adds attributes from parent
ras2poly <- function(ras_foc, i=0, class=0, poly_parent=NULL){
  # raster to polygon
  poly <- st_as_sf(as.polygons(ras_foc == 1, dissolve=TRUE))
  if(PLOT_INTERMEDIATE) plot(ras_foc, col='red', main=paste0(i, ": (standID:", poly_parent$ID, " class ", class, ")"))
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
    poly_final$standID <- poly_parent$ID
    poly_final$standArea <- poly_parent$area_m2
  }
  return(poly_final)
}

####_________________________####
####          MAIN           ####
#-------------------------------#
print("----------------------------------")
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
stands = stands_all[set_units(stands_all$area_m2, "m^2") > min_size_stand, ]
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
  # PLOT_INTERMEDIATE = T # for detailed visual output during processing
  # for (i in 42:47){
  
  # iteration initialization
  pb$tick()
  flag_polys_created_stand <- F
  # initialize stand stats row with named columns
  stats <- t(setNames(c(stands[i,]$ID, i), c("stand_ID", "proc_ID")))
  
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
      
      # writeRaster(focal_map, file.path(PATH_OUTPUT, paste0("focal_map", NAME_SUFFIX, ".tif")))
      #TODO check effect of na.rm = FALSE
      # focal_map = focal(hs_crop, w=fw, na.rm=FALSE, na.policy="omit")
      if(PLOT_INTERMEDIATE) plot(focal_map)
      if(PLOT_INTERMEDIATE) lines(stands[i,])
      if(PLOT_INTERMEDIATE) plot(focal_map_2)
      if(PLOT_INTERMEDIATE) lines(stands[i,])
      
      ### ** ** ** ** ** ** ** ####
      ### > iterate over classes   ####
      flag_polys_created_class <- F
      
      # run for each class
      for(k in 1:nrow(classes_df)) {
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
            new_polys <- st_collection_extract(multipolygon, type = "POLYGON")
            new_polys <- st_cast(new_polys, "POLYGON")
            new_polys$area <- st_area(new_polys)
            
            # filter by size
            new_polys = new_polys[new_polys$area > min_size_clump,]
            
            # check if any remain
            if((nrow(new_polys) > 0)){
              #### >> add attributes to zones ####
              # add DG attribute
              new_polys$area_pct = round(new_polys$area / new_polys$standArea, 2)
              new_polys$DG = round(exactextractr::exact_extract(hs_crop_unbuffered,new_polys, fun ="mean"),2)*100
              new_polys$DG_stand = stands[i,]$DG
              
              if(CALC_ALL_DG){
                new_polys$DG_ks = round(exactextractr::exact_extract(dg_ks,new_polys, fun ="mean"),2)*100
                new_polys$DG_us = round(exactextractr::exact_extract(dg_us,new_polys, fun ="mean"),2)*100
                new_polys$DG_ms = round(exactextractr::exact_extract(dg_ms,new_polys, fun ="mean"),2)*100
                new_polys$DG_os = round(exactextractr::exact_extract(dg_os,new_polys, fun ="mean"),2)*100
                new_polys$DG_ueb = round(exactextractr::exact_extract(dg_ueb,new_polys, fun ="mean"),2)*100

                new_polys$DG_ks_stand = stands[i,]$DG_ks
                new_polys$DG_us_stand = stands[i,]$DG_us
                new_polys$DG_ms_stand = stands[i,]$DG_ms
                new_polys$DG_os_stand = stands[i,]$DG_os
                new_polys$DG_ueb_stand = stands[i,]$DG_ueb
              }
              new_polys$NH = round(exactextractr::exact_extract(mg,new_polys, fun ="mean"),0)
              new_polys$NH_stand = stands[i,]$NH
              new_polys$hdom = stands[i,]$hdom
              
              #### >> populate attributes for stands ####
              area_class = sum(new_polys$area)
              area_class_pct = area_class / stands[i,]$area_m2
              dg_class = mean(new_polys$DG_zone)
              nh_class = mean(new_polys$NH_zone)
              
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
          plot(hs_crop, main=paste0(i, " ", flag_polys_created_stand, ": (standID:", stands[i,]$ID, " | size = ",round(set_units(st_area(stands[i,]), "ha"),1), " ha)"))
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
      stats <- t(setNames(c(stands[i,]$ID, -i), c("stand_ID", "proc_ID")))
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
    error_and_message = cbind(i, stands$ID[i], error_message$message)
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
  capture.output(ID_errors, file = file.path(PATH_OUTPUT, paste0("TBk_local_densities", NAME_SUFFIX, "_errors_proc_ID.txt")))
} 


#### write gpkg local density zones ####
if(VERBOSE) print("----------------------------------")
if(VERBOSE) print(paste0("write local density zones to: "))
if(VERBOSE) print(PATH_OUTPUT)
dir.create(file.path(PATH_OUTPUT), recursive = TRUE, showWarnings = TRUE)

# write files for polygons
st_write(st_as_sf(polys), append = FALSE, 
         file.path(PATH_OUTPUT, paste0("TBk_local_densities", NAME_SUFFIX, ".gpkg")))


#### append attributes to input ####
# and export to file

# add names to table
col_names <- t(c("stand_ID", "local_densities_proc_ID"))
for(k in 1:nrow(classes_df)) {
  name_area_class <- paste0("z",classes_df[k,]$class, "_", "area")
  name_area_class_pct <- paste0("z",classes_df[k,]$class, "_", "area_pct") 
  name_dg_class <- paste0("z",classes_df[k,]$class, "_", "dg") 
  name_nh_class <- paste0("z",classes_df[k,]$class, "_", "nh") 
  col_names <- cbind(col_names, name_area_class, name_area_class_pct, name_dg_class, name_nh_class)
}
names(statstable) <- col_names

#TODO: Sometimes result attributes have a varying amount of rows and can't be merged to original table
tryCatch(expr={
  if(VERBOSE) print("----------------------------------")
  if(VERBOSE) print(paste0("left join attribute rows to input geometries (stands)"))
  if(VERBOSE) print(paste0(nrow(statstable), " of ", nrow(stands_all), " were processed (check proc_ID, others are NA)."))
  
  # connect statstable with existing attributetable/geometry (left outer join)
  stands_out = merge(x = stands_all, y = statstable, by.x = "ID", by.y = "stand_ID", all.x = TRUE)
  
  if(!OVERWRITE_ORIGINAL_TBK){
    if(VERBOSE) print(paste0("write input geometries with appendes attributes to folder: ", PATH_OUTPUT))
    # write file with new attributes to PATH_OUTPUT
    write_sf(stands_out, file.path(PATH_OUTPUT, paste0(tools::file_path_sans_ext(basename(PATH_SHP)),"_local-densities", NAME_SUFFIX, ".gpkg") ))
  }
  if(OVERWRITE_ORIGINAL_TBK){
    if(VERBOSE) print(paste0("attempt to overwrite input geometries with appendend attributes: ", PATH_SHP))
    # write file with new attributes to 
    write_sf(stands_out, file.path(PATH_SHP))
  }
}, error=function(cond) {# optional: print alert # message(paste("")))
}, silent = TRUE)


if(VERBOSE) print("----------------------------------")
if(VERBOSE) print("------------   DONE   ------------")
if(VERBOSE) print("----------------------------------")
