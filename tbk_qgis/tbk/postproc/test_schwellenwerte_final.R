library(raster)
library(rgdal)
library(rgeos)
library(landscapemetrics)
library(smoothr)
library(units)

### input parameters ###
# path
#path = "P:/HAFL/7 WWI/74a FF WG/742a Aktuell/L.008456-52-FWWG-01_TBk_Projekt_HAFL/Wiliwald/20180418-1520/"
#path = "P:/HAFL/7 WWI/74b FF GNG/742b Aktuell/2018-2020_FINTCH_R.009030-52-FWGN-01/AP6_Abgrenzung_der_WST/Entwicklung/TBk_Luzern/Testperimeter/20190703-2033/"
#path = "P:/HAFL/7 WWI/74a FF WG/742a Aktuell/L.007736-52-FWWG_BGB_SmartForest/TBk_fuer_WIS2/TBk/20170411-1227/"
path = "P:/HAFL/7 WWI/74b FF GNG/742b Aktuell/2018-2020_FINTCH_R.009030-52-FWGN-01/AP6_Abgrenzung_der_WST/Entwicklung/TBk_Bern/BGB_20191114/20191114-1517/"

# radius of circular moving window (in m)
mw_rad = 7

# minimum size for dense/sparse "clumps" (in Aren)
min_size_clump = 10

# minimal density value for identification of "dense pixels" (moving window)
min_dens = 0.8

# maximal density value for identification of "sparse pixels" (moving window)
max_dens = 0.25

# name of forest
name = "bgb"

##############################################################################

os = raster(paste(path,"dg_layers/dg_layer_os.tif",sep=""),values=T)
ueb = raster(paste(path,"dg_layers/dg_layer_ueb.tif",sep=""),values=T)
stands = readOGR(paste(path,"TBk_Bestandeskarte.shp",sep=""))
hs <- merge(os,ueb)

#hs = raster(paste(path,"dg_lim_stat.tif",sep=""),values=T)
#stands = readOGR(paste(path,"TBk_BGB_final.shp",sep=""))

res_hs <- res(hs)[1]

# function which eliminates all "clumps" smaller than min. size
minsizefunc <- function(x, minsize){
  x_clump <- clump(x, directions=8, gaps=F)
  clumpFreq <- as.data.frame(freq(x_clump))
  # vector of clump ID's whose size is smaller than the minimum size
  excludeID <- clumpFreq$value[which(clumpFreq$count < minsize)]
  # assign NA to all clumps whose IDs are found in excludeID
  x[x_clump %in% excludeID] <- NA
  return(x)
}

# main script: create attributes
statstable <- data.frame()
k <- j <- 0
pdf(paste("C:/Temp/myplots_",name,"_",mw_rad,"_",min_dens,"_",max_dens,".pdf",sep=""), onefile=TRUE, paper="a4", width = 8.27, height = 11.69)
par(mfrow=c(3,2), oma = c(0, 0, 2, 0))

for (i in 1:length(stands)){

  hs_extent <- crop(hs,stands[i,])
  hs_mask <- mask(hs_extent,stands[i,])
  
  if (length(hs_mask[!is.na(hs_mask)])>0){
  hs_crop <- trim(hs_mask,values=NA)
  } else {
  hs_crop <- hs_mask  
  }
  
  # 1) area and dg of very dense / sparse areas per stock
  fw <- focalWeight(hs_crop, mw_rad, type='circle')
  fw[fw>0] <- 1
  
  if (nrow(hs_crop) >= nrow(fw) & ncol(hs_crop) >= ncol(fw)){
    
  check <- T  
  
  min_sum <- (length(which(fw==1))-1)*min_dens
  max_sum <- (length(which(fw==1))-1)*max_dens
  
  ras_foc_1 <- focal(hs_crop, w=fw) >= min_sum
  ras_foc_2 <- focal(hs_crop, w=fw) <= max_sum
  
  ras_foc_1[ras_foc_1 == 0] <- NA
  ras_foc_2[ras_foc_2 == 0] <- NA
 
  # elimination of areas smaller than min. size
  ras_foc_1 <- minsizefunc(ras_foc_1, min_size_clump*100/res_hs^2)
  ras_foc_2 <- minsizefunc(ras_foc_2, min_size_clump*100/res_hs^2)
  
  # calculation of dg's
  dg_dense <- round(length(ras_foc_1[ras_foc_1==1 & hs_crop==1])/length(ras_foc_1[ras_foc_1==1]),2)
  dg_sparse <- round(length(ras_foc_2[ras_foc_2==1 & hs_crop==1])/length(ras_foc_2[ras_foc_2==1]),2)
  dg_other <- round(length(hs_crop[is.na(ras_foc_1) & is.na(ras_foc_2) & hs_crop==1])/length(hs_crop[is.na(ras_foc_1) & is.na(ras_foc_2) & !is.na(hs_crop)]),2)
  
  # dense / sparse total area (in Aren) 
  area_dense <- round(length(ras_foc_1[ras_foc_1==1])*res_hs^2/100,2)
  area_sparse <- round(length(ras_foc_2[ras_foc_2==1])*res_hs^2/100,2)

  } else {
  check <- F
  dg_dense <- area_dense <- dg_sparse <- area_sparse <- dg_other <- clumpy <- NA
  }
  
  
  # 2) clumpiness index
  if (length(hs_crop[!is.na(hs_crop)])>0){
    clumpy <- lsm_c_clumpy(hs_crop)$value[2]
  }
  
  stats <- c(area_dense, dg_dense, area_sparse, dg_sparse, dg_other, clumpy)
  statstable <- rbind(statstable,stats)
  
  # raster to polygon
  area_thresh <- units::set_units(100, m^2)
  
  if (length(ras_foc_1[ras_foc_1==1])>0 & check==T){
    j <- j+1
    ras_foc_1_poly <- rasterToPolygons(ras_foc_1, dissolve=T)
    ras_foc_1_filled <- fill_holes(ras_foc_1_poly, set_units(100, m^2))
    ras_foc_1_smooth <- smooth(ras_foc_1_filled, method = "ksmooth", smoothness = 2)
    ras_foc_1_smooth <- drop_crumbs(ras_foc_1_smooth, threshold = area_thresh)
    ras_foc_1_smooth@data$nr <- i
    ras_foc_1_smooth@data$dg <- dg_dense
    ras_foc_1_smooth@data$area <- gArea(ras_foc_1_smooth, byid=T)
    check_red <- T
    if(j>1){
      poly_dense <- rbind(poly_dense, ras_foc_1_smooth)
     }
    else {
      poly_dense <- ras_foc_1_smooth
      }
  } else {check_red <- F}

  if (length(ras_foc_2[ras_foc_2==1])>0 & check==T){
    k <- k+1
    ras_foc_2_poly <- rasterToPolygons(ras_foc_2, dissolve=T)
    ras_foc_2_filled <- fill_holes(ras_foc_2_poly, set_units(100, m^2))
    ras_foc_2_smooth <- smooth(ras_foc_2_filled, method = "ksmooth", smoothness = 2)
    ras_foc_2_smooth <- drop_crumbs(ras_foc_2_smooth, threshold = area_thresh)
    ras_foc_2_smooth@data$nr <- i
    ras_foc_2_smooth@data$dg <- dg_dense
    ras_foc_2_smooth@data$area <- gArea(ras_foc_2_smooth, byid=T)
    check_blue <- T
    if(k>1){
      poly_sparse <- rbind(poly_sparse, ras_foc_2_smooth)
    }
    else {
      poly_sparse <- ras_foc_2_smooth
    }
  } else {check_blue <- F}
  
 
  # plot
  plot(hs_crop, main=paste(i, " (size = ",round(as.numeric(as.character(stands$area_m2)[i])/100,1) , " ; clumpy = ",round(clumpy,2),")", sep=""))
  lines(stands[i,])
  if(check_red){lines(ras_foc_1_smooth,col='red')}
  if(check_blue){lines(ras_foc_2_smooth, col='blue')}
  mtext(text=paste("mw_rad = ",mw_rad, " ; min_dens = ",min_dens, " ; max_dens = ", max_dens, sep=""),side=3, outer=T,line=0, cex=0.8)
  }
dev.off()

names(statstable) <- c("area.d", "dg.dense", "area.sp", "dg.sparse", "dg.other", "clumpy")



# export as shapefile
stands@data <- cbind(stands@data, statstable)
writeOGR(stands, "C:/Temp/BGB_TBk/clumpy_results",layer=paste("stands_",name,"_new",sep=""),driver="ESRI Shapefile", overwrite_layer=T)
writeOGR(poly_dense, "C:/Temp/BGB_TBk/clumpy_results",layer=paste("dense_",name,sep=""),driver="ESRI Shapefile", overwrite_layer=T)
writeOGR(poly_sparse, "C:/Temp/BGB_TBk/clumpy_results",layer=paste("sparse_",name,sep=""),driver="ESRI Shapefile", overwrite_layer=T)