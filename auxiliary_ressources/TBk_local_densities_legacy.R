#------------------------------------------------------------------------------#
# LOCAL STAND DENSITIES
#
# adds the following attributes to an input stand map (e.g. TBk output)
# - area_dense / area_sparse  : Flaeche (m2) besonders dichter/lueckiger Teilflaechen
# - dg_dense / dg_sparse / dg_other  : Deckungsgrad (%) besonders dichter/lueckiger/restlicher Flaechen
# - clumpy : (Clumpiness Index)[https://rdrr.io/github/r-spatialecology/landscapemetrics/man/lsm_c_clumpy.html]
# and generates polygons delineating these areas
#
# Segmentation is based on a moving window algorithm
# with a circular moving window that defaults to 7 m radius. 
# The min size for dense/sparse areas defaults to 10 a. 
# (these values can be changed in the section settings).
# An optional second pass was added to remove thin slithers (buffersmoothing - bs)  
#
# ATTENTION [added 05/2023]: 
# Thresholds for dense degree of cover (currently > 0.8) 
# respectively sparse degree of cover (currently < 0.25) were defined 
# more or less by gut and aren't systematically validated! 
# However these values have proven to deliver mostly plausible and pragmatical results.
# They need to be adjusted to method...
# (when buffersmoothing, a "greedier" threshold might make sense, since bs shrinks the area a bit)
# ... and also the input data.
# (VHMs based on aerial imagery have a tendency to appear more dense vs. lidar-based VHMs)
#
# (c) by Alexandra Erbach, HAFL, BFH, 2021-10
# (c) by Hannes Horneber, HAFL, BFH, 2021-11, 2023-01
#
# DEVELOPMENT DISCONTINUED AFTER 2023-01, major changes led to a new version
#------------------------------------------------------------------------------#

library(raster)
library(terra)
library(rgdal)
library(rgeos)
library(landscapemetrics)
library(smoothr)
library(units)
library(igraph)
library(lidR)

#-------------------------------#
####   SETTINGS MANDATORY    ####
#-------------------------------#

### input parameters ###
# path to TBk. This assumes the "normal" layer structure (subfolder with dg layers)
PATH_TBk_INPUT =  "C:/Users/hbh1/Projects/H07_TBk/Dev/TBk_QGIS_Plugin/data/TBk_main/20230810-0054" # 2022-01-05

# location of the output dataset
PATH_OUTPUT = file.path(PATH_TBk_INPUT, "local_densities")
# optional name suffix for output - if left empty (""), input .shp will be overwritten
NAME_SUFFIX = "_no_smoothing"

#-------------------------------#
####    SETTINGS OPTIONAL    ####
#-------------------------------#
VERBOSE = TRUE
PLOT_RESULTS = FALSE # for visual output during processing
CLIP_TO_STAND_BOUNDARIES = TRUE
# write original file with new attributes 
# this can fail if file is in use (will fall back to writing a new file in PATH_OUTPUT)
OVERWRITE_ORIGINAL_TBK = FALSE

# the path to the dg layers (relative or absolute) 
# default is PATH_TBk_INPUT/dg_layers/dg_layer_XX.tif
PATH_DG_os = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_os.tif")
PATH_DG_ueb = file.path(PATH_TBk_INPUT,"dg_layers/dg_layer_ueb.tif")

# the path to the polygons to perform the algorithm in
# these can be stands (e.g. TBk) or other perimeters
PATH_SHP = file.path(PATH_TBk_INPUT,"TBk_Bestandeskarte.shp")
# PATH_SHP = file.path(PATH_TBk_INPUT,"perimeter.shp")

# thresholds for removing polygon parts
# default (as of 2021-10-27): 100 / 100 m^2
# crumb_thresh <- units::set_units(900, m^2) # for large stands/polygons
holes_thresh <- units::set_units(125, m^2)
crumb_thresh <- units::set_units(100, m^2) # for TBk stands

# method to remove thin parts and details of zones
# 0 = not applied, default: 10 (0.5*thickness that is preserved)
BUFFER_SMOOTHING = 0
# default smoothing. Isn't applied if buffer_smoothing is applied or if set to 0; default: 2
KSMOOTH_FACTOR = 0

# radius of circular moving window (in m)
mw_rad = 7

# minimum size for dense/sparse "clumps" (in Aren)
min_size_clump = 10 # default (as of 2021-10-27): 10

# minimal density value for identification of "dense pixels" (moving window)
min_dens = 0.80 # default (as of 2021-10-27): 0.8

# maximal density value for identification of "sparse pixels" (moving window)
max_dens = 0.25 # default (as of 2021-10-27): 0.25

####_________________________####
####       INITIALIZE        ####
#-------------------------------#
if(VERBOSE) print("Initialize: Load data from:")
if(VERBOSE) print(PATH_SHP)

# load dg rasters and shapefile
os = raster(PATH_DG_os,values=T)
ueb = raster(PATH_DG_ueb)
stands = readOGR(PATH_SHP)

# create "HauptSchicht" (include Ueberhaelter)
hs = calc(stack(os,ueb),max)
res_hs <- res(hs)[1]


#### init functions ####
# function minsizefunc: eliminates all "clumps" smaller than min. size
minsizefunc <- function(x, minsize){
  x_clump <- clump(x, directions=8, gaps=F)
  clumpFreq <- as.data.frame(freq(x_clump))
  # vector of clump ID's whose size is smaller than the minimum size
  excludeID <- clumpFreq$value[which(clumpFreq$count < minsize)]
  # assign 0 to all clumps whose IDs are found in excludeID
  x[x_clump %in% excludeID] <- NA
  return(x)
}

# function ras2poly: creates a polygon from a raster and adds attributes from parent
ras2poly <- function(ras_foc, i=0, dg=0, poly_parent=NULL){
  # raster to polygon
  poly <- rasterToPolygons(ras_foc, dissolve=T)
  # plot(poly)
  # remove holes
  poly_filled <- fill_holes(poly, holes_thresh)
  # plot(poly_filled, add =T, col='blue')
  # smooth (via buffer or with smoothing algorithm)
  if(BUFFER_SMOOTHING != 0) {
    if(exists("poly_smooth")) remove("poly_smooth")
    # catch the case that the negative buffer deletes the whole polygon
    tryCatch(expr={poly_smooth = buffer(poly_filled, width= -BUFFER_SMOOTHING)}, 
             error=function(cond) {
               # optional: print alert if negative buffer melts polygon
               # message(paste("Polygon melted to buffer:", BUFFER_SMOOTHING))
             }, silent = TRUE)
    # poly_smooth = buffer(poly_filled, width= -BUFFER_SMOOTHING)
    if(!exists("poly_smooth")) return(NULL)
    poly_smooth = buffer(poly_smooth, width=  BUFFER_SMOOTHING+1.5)
    
    # buffer results in a SpatialPolygons (instead of SpatialPolygonsDataFrame SPDF)
    # -> convert to SPDF, Create dataframe with IDs by extracting polygon ID's
    ( pid <- sapply(slot(poly_smooth, "polygons"), function(x) slot(x, "ID")) )
    ( poly_smooth.df <- data.frame( ID=1:length(poly_smooth), row.names = pid) )
    poly_smooth <- SpatialPolygonsDataFrame(poly_smooth, poly_smooth.df)
  } else {
    # default smoothing
    if(KSMOOTH_FACTORTH != 0) {
      poly_smooth <- smooth(poly_filled, method = "ksmooth", smoothness = 2)
    } else {
      # no smoothing
      poly_smooth <- poly_filled
    }
  }
  # plot(poly_smooth, add =T, col='red')
  # remove small areas (drop crumbs)
  poly_final <- drop_crumbs(poly_smooth, threshold = crumb_thresh)
  if(is.null(poly_final)) return(NULL)
  
  if(CLIP_TO_STAND_BOUNDARIES) {
    # clip to stand boundaries
    poly_final <- raster::intersect(poly_final, poly_parent)
    if(is.null(poly_final)) return(NULL)
    # ... copies all attributes, so we oughta remove (most of) them
    poly_final <- poly_final[,-(1:ncol(poly_final))]
  }
  # plot(poly_final, add =T, col='green')

  # add attributes
  poly_final@data$nr <- i
  poly_final@data$dg <- dg_dense
  poly_final@data$area <- gArea(poly_final, byid=T)
  if(!is.null(poly_parent)){
    poly_final@data$standID <- poly_parent$ID
    poly_final@data$standArea <- poly_parent$area_m2
  }
  return(poly_final)
}

####_________________________####
####          MAIN           ####
#-------------------------------#
if(VERBOSE) print("Initialize: Loaded data")

# init statstable for attributes
statstable <- data.frame()
# init iteration variables
k <- j <- 0

# optional plot output
#pdf(paste("C:/Temp/myplots_",name,"_",mw_rad,"_",min_dens,"_",max_dens,".pdf",sep=""), onefile=TRUE, paper="a4", width = 8.27, height = 11.69)
#par(mfrow=c(3,2), oma = c(0, 0, 2, 0))

if(VERBOSE) print("Iterate over stands.")
if(VERBOSE) progressBar = txtProgressBar(min=0, max=length(stands), initial=0, width=100, style=3) 
### *iterate over stands/polygons* ####
for (i in 1:length(stands)){
  if(VERBOSE) setTxtProgressBar(progressBar, i)
  
  # get hs layer for stand 
  stand_buffered = buffer(stands[i,], width= mw_rad)
  #TODO maybe buffer this, to remove polygon margins to stand
  hs_extent <- crop(hs,stand_buffered)
  hs_mask <- mask(hs_extent,stand_buffered)
  
  # trim if NA values are present
  #TODO check if this works as it is supposed to...
  if (length(hs_mask[!is.na(hs_mask)])>0){
    # Trim (shrink) a Raster* object by removing outer rows and columns that all have the same value (e.g. NA). 
    hs_crop <- trim(hs_mask,values=NA)
  } else {
    hs_crop <- hs_mask  
  }
  
  # create raster masked to stand for calculating dg
  hs_crop_unbuffered <- mask(hs_crop,stands[i,])
  # plot(hs_crop)
  # plot(hs_crop_unbuffered, add=T, col='red')
  
  #### > 1) attr: area and dg of very dense / sparse areas per stock  #### 
  fw <- focalWeight(hs_crop, mw_rad, type='circle')
  fw[fw>0] <- 1
  
  # basic check whether stand area is bigger than focal window (otherwise skip stand)
  if (nrow(hs_crop) >= nrow(fw) & ncol(hs_crop) >= ncol(fw)){
    check <- T  
    
    min_sum <- (length(which(fw==1))-1)*min_dens
    max_sum <- (length(which(fw==1))-1)*max_dens
    
    # dense area
    ras_foc_1 <- focal(hs_crop, w=fw) >= min_sum
    # sparse area
    ras_foc_2 <- focal(hs_crop, w=fw) <= max_sum
    
    ras_foc_1[ras_foc_1 == 0] <- NA
    ras_foc_2[ras_foc_2 == 0] <- NA
    
    # elimination of areas smaller than min. size
    ras_foc_1 <- minsizefunc(ras_foc_1, min_size_clump*100/res_hs^2)
    ras_foc_2 <- minsizefunc(ras_foc_2, min_size_clump*100/res_hs^2)
    
    # calculation of dg's
    dg_dense <- round(length(ras_foc_1[ras_foc_1==1 & hs_crop_unbuffered==1])/length(ras_foc_1[ras_foc_1==1]),2)
    dg_sparse <- round(length(ras_foc_2[ras_foc_2==1 & hs_crop_unbuffered==1])/length(ras_foc_2[ras_foc_2==1]),2)
    dg_other <- round(length(hs_crop_unbuffered[is.na(ras_foc_1) & is.na(ras_foc_2) & hs_crop_unbuffered==1])/length(hs_crop_unbuffered[is.na(ras_foc_1) & is.na(ras_foc_2) & !is.na(hs_crop_unbuffered)]),2)
    
    # dense / sparse total area (in Aren) 
    area_dense <- round(length(ras_foc_1[ras_foc_1==1])*res_hs^2/100,2)
    area_sparse <- round(length(ras_foc_2[ras_foc_2==1])*res_hs^2/100,2)

    #### > 2) attr: clumpiness index  #### 
    if (length(hs_crop[!is.na(hs_crop)])>0){
      clumpy <- lsm_c_clumpy(hs_crop)$value[2]
    }
    
    # fill statstable with attributes
    stats <- c(area_dense, dg_dense, area_sparse, dg_sparse, dg_other, clumpy)
    statstable <- rbind(statstable,stats)
    
    #### > 3) poly: dense #### 
    
    # dense zones 
    # check if dense cells are present
    if (length(ras_foc_1[ras_foc_1==1])>0){
      # raster to polygon
      new_poly_dense = ras2poly(ras_foc=ras_foc_1, i=i, dg=dg_dense, poly_parent=stands[i,])
      # check if non-null polygon is produced
      if(!is.null(new_poly_dense)){
        j <- j+1
        if(j>1){
          poly_dense <- rbind(poly_dense, new_poly_dense)
        }
        else {
          poly_dense <- new_poly_dense
        }
        # flag for plotting
        check_blue <- T
      } else {check_blue <- F}
    } else {check_red <- F}
    
    #### > 4) poly: sparse #### 
    # sparse zones 
    # check if sparse cells are present
    if (length(ras_foc_2[ras_foc_2==1])>0){
      # raster to polygon
      new_poly_sparse = ras2poly(ras_foc=ras_foc_2, i=i, dg=dg_sparse, poly_parent=stands[i,])
      # check if non-null polygon is produced
      if(!is.null(new_poly_sparse)){
        k <- k+1
        if(k>1){
          poly_sparse <- rbind(poly_sparse, new_poly_sparse)
        }
        else {
          poly_sparse <- new_poly_sparse
        }
        # flag for plotting
        check_blue <- T
      } else {check_blue <- F}
    } else {check_blue <- F}
    
    # plot results for visual plausibility check
    if(PLOT_RESULTS){
      try(expr={
        plot(hs_crop, main=paste0(i, " (size = ",round(gArea(stands[i,], byid=T)/100,1) , "a ; clumpy = ",round(clumpy,2),")",
                                  "\nad ", area_dense, " |dd", dg_dense, " |as ", area_sparse, " |ds ", dg_sparse, " |do ", dg_other))
        lines(stands[i,])
        lines(stands[i,], col='green')
        if(check_red){lines(new_poly_dense,col='red')}
        if(check_blue){lines(new_poly_sparse, col='blue')}
        mtext(text=paste("mw_rad = ",mw_rad, " ; min_dens = ",min_dens, " ; max_dens = ", max_dens, sep=""),
              side=3, outer=T,line=0, cex=0.8)
      })
    }
  } else {
    # no dense/sparse areas
    check <- F
    dg_dense <- area_dense <- dg_sparse <- area_sparse <- dg_other <- clumpy <- NA
  }
  
  
}
# dev.off()
if(VERBOSE) close(progressBar)

#### export as shapefiles ####
# add names to table
names(statstable) <- c("area.d", "dg.dense", "area.sp", "dg.sparse", "dg.other", "clumpy")
# connect statstable with existing attributetable/geometry
stands@data <- cbind(stands@data, statstable)

if(OVERWRITE_ORIGINAL_TBK){
  # write file with new attributes to PATH_OUTPUT
  writeOGR(stands, PATH_TBk_INPUT, layer=paste0(tools::file_path_sans_ext(basename(PATH_SHP)), NAME_SUFFIX),
           driver="ESRI Shapefile", overwrite_layer=T)
}
if(!OVERWRITE_ORIGINAL_TBK){
  # write file with new attributes to PATH_OUTPUT
  writeOGR(stands, PATH_OUTPUT, layer=paste0(tools::file_path_sans_ext(basename(PATH_SHP)), NAME_SUFFIX),
           driver="ESRI Shapefile", overwrite_layer=T)
}

# write files for polygons
writeOGR(poly_dense, PATH_OUTPUT, layer=paste0("TBk_dense_areas", NAME_SUFFIX),
         driver="ESRI Shapefile", overwrite_layer=T)
writeOGR(poly_sparse, PATH_OUTPUT, layer=paste0("TBk_sparse_areas", NAME_SUFFIX),
         driver="ESRI Shapefile", overwrite_layer=T)