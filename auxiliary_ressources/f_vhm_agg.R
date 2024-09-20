# _________________________ ####
# WHAT IT'S ALL ABOUT ####
#------------------------------------------------------------------------------#
# The main function() f_vhm_agg() can be used as specification of 
# terra::aggregate()'s argument fun. Thus it is an alternative to generating
# VHM 10m with gdal:warpreproject as max of original VHM within 10m x 10m.
# f_vhm_agg() is a rather complex function(). In its current version it's actually
# too complex! f_vhm_agg()'s functionality hardly differs from one of vhm3()
# [s. https://github.com/HAFL-WWI/TBk/files/15335154/vhm_resample.R.txt]. 
# f_vhm_agg()'s code is tidied up, avoids redundancies and includes all parameters
# of cases 1 to 5 as function arguments. This facilitate experimenting and
# further development.
# 
# (c) by Attilio Benini, HAFL, BFH, 2024-09-09
#------------------------------------------------------------------------------#
# _________________________ ####
# NOTES ####
#------------------------------------------------------------------------------#
# 1) objects or function-arguments having a name starting with the prefix f_ are
#    function()s or arguments whichs' specification has to be a function().
#
# 2) arguments having suffix _1 to _5 refer to cases 1 to 5.
# _________________________ ####
# FUNCTION CODE ####
#------------------------------------------------------------------------------#
# > HELPER FUNCTIIONS FOR f_vhm_agg() ####
#------------------------------------------------------------------------------#
# helper functions for internal use in f_vhm_agg()

f_get_dom_layer <- function(tab) {as.integer(names(tab)[tab == max(tab)])}

f_mean_weighted_max <- function(x) {ceiling((max(x) * 2 + mean(x)) / 3)}
#------------------------------------------------------------------------------#
# > FUNCTIONS f_vhm_agg() ####
#------------------------------------------------------------------------------#
# argument description function f_vhm_agg() for VHM aggregation

#' @param vec numeric vector with values from original VHM within 10m x 10m pixel
# case 1
#' @param f_h_top_min_1 function with a single argument h_max to get minimum
#' height of top layer (h_top_min_1)
#' @param min_percentage_1 (default = 33) min. percentage of valid pixels >= h_top_min_1
# case 2
#' @param f_h_top_min_2 function with a single argument h_max to get minimum height
#' of overstory layer (h_top_min_2)
#' @param min_percentage_2 (default = 50) min. percentage of valid pixels >= h_top_min_2
# case 3
#' @param f_h_low_max_3 function with a single argument h_max to get maximum height
#' of understory layer (h_low_max_3)
#' @param min_percentage_3 (default = 67) min. percentage of valid pixels < h_low_max_3
# case 4
#' @param h_layer_breaks_4 height-layer-breaks to detect a dominate canopy height layer
#' in case 4, which must include > 50% of valid original pixels
# case 5
#' @param h_layer_breaks_5 height-layer-breaks to detect a dominate canopy height layer
#' in case 5, which is the one having the highest number of valid original pixels.
#' If several layers have the highest number, then of these layers the one having
#' the upper range is detected as the dominate. h_layer_breaks_5 should have the same
#' min and max as h_layer_breaks_4 and length(h_layer_breaks_5) =< length(h_layer_breaks_4) - 1
#' must be TRUE.
# further arguments
#' @param output_type string: "vhm" or "case". If "vhm" a raster-layer with aggregated
#' VHM is returned. If "case" a raster-layer with case values (1 to 5) is returned.
#' @param verbose if TRUE print some information about aggregation. Default FALSE.
#' @param plot if TRUE plots matrix of original VHM value per 10m x 10m pixel + some
#' key figures about aggregation. Works only if verbose = TRUE. Default FALSE.
#' @param NA_value numeric pixel value in original VHM standing for not available
#' / NA (default 128).
#' @param no_veg_value numeric pixel value in original VHM standing for no
#' vegetation (default -99). --> internally this value is treated as NA. At the time
#' not really needed.
#' @param NA_max_percentage max percentage (default 99) of NAs among values from
#' original VHM within 10m x 10m pixel, up to which aggregation is done, else
#' return NA
#' @param agg_fact integer / aggregation factor (default NULL / not specified)
#' = cell resolution of input VHM / resolution of aggregated VHM. Must be specified
#' if verbose TRUE and plot = TRUE.

# function code
f_vhm_agg <- function(
    vec,
    # case 1
    f_h_top_min_1 = function(h_max){max(0.9 * h_max - 3, 1)}, # max(,1) ensures it is > 0
    # f_h_top_min_1 = function(h_max){max(0.9 * h_max - 5, 1)}, # max(,1) ensures it is > 0
    min_percentage_1 = 33, # [%]
    # case 2
    f_h_top_min_2 = function(h_max){max(0.85 * h_max - 5, 1)}, # max(,1) ensures it is > 0
    # f_h_top_min_2 = function(h_max){max(0.8 * h_max - 5, 1)}, # max(,1) ensures it is > 0
    min_percentage_2 = 50, # [%]
    # case 3
    f_h_low_max_3 = function(h_max){max(h_max / (2 - 0.5 * h_max / 40), 1)}, # max(,1) ensures it is > 0
    # f_h_low_max_3 = function(h_max){max(2 / 3 * h_max, 1)}, # simplify code / result should be similar
    min_percentage_3 = 67, # [%]
    # case 4 
    h_layer_breaks_4 = c(0,9,17,24,31,60),
    # case 5 
    h_layer_breaks_5 = c(0,17,24,60),
    # further arguments
    output_type       = c("vhm", "case"),
    na.rm             = TRUE,
    verbose           = FALSE,
    plot              = FALSE,
    NA_value          = 128,
    no_veg_value      = -99,
    NA_max_percentage = 99,
    agg_fact          = NULL
){
  NA_max_percentage <- NA_max_percentage / 100
  output_type <- match.arg(output_type)
  
  if(verbose) print("-------")
  # replace NA value by actual NAs
  vec[vec == NA_value] = NA
  
  # copy vector for image
  vec_orig = vec
  case     = 0
  
  # 0A filter: all same
  # if all values are the same, return those
  if (length(unique(vec)) == 1) {return(vec[1])}

  # 0B filter: most NA
  # remove NA values for computation (e.g. of percentages)
  vec <- vec[!is.na(vec)]
  if (length(vec) == 0 || length(vec) / length(vec_orig) <= 1 - NA_max_percentage) {return(NA_integer_)}
  # 0C filter: most 0 Vegetation
  # remove 0 values for computation (e.g. of percentages)
  vec[vec == no_veg_value] <- NA
  vec <- vec[!is.na(vec)]
  if (length(vec) == 0 || length(vec) / length(vec_orig) <= 1 - NA_max_percentage) {return(0)}

  if (verbose) print(paste0("NA%:", length(vec[!is.na(vec)]), "/", length(vec)))
  
  # case 1
  h_max <- max(vec)
  # minimum height of top layer
  h_top_min_1 <- f_h_top_min_1(h_max)
  # pixel value >= minimum height of top layer
  vec_filtered <- vec[vec >= h_top_min_1]
  if (length(vec_filtered) / length(vec) > min_percentage_1 / 100) {
    result <- h_max
    case   <- 1
  }
  
  # case 2
  if (case == 0) { # only if no previous case applied
    # minimum height of overstory layer
    h_top_min_2 <- f_h_top_min_2(h_max)
    # pixel values >=  minimum height of overstory layer
    vec_filtered <- vec[vec >= h_top_min_2]
    if (length(vec_filtered) / length(vec) > min_percentage_2 / 100) {
      result <- h_max
      case   <- 2
    }
  }
  
  # case 3
  if (case == 0) { # only if no previous case applied
    # maximum height of understory layer
    h_low_max_3 <- f_h_low_max_3(h_max)
    # pixels values < maximum height of understory layer
    vec_filtered <- vec[vec < h_low_max_3]
    if (length(vec_filtered) / length(vec) > min_percentage_3 / 100) {
      # determine aggregated height with mean_weighted_max() from pixels values < maximum height of understory layer
      result <- f_mean_weighted_max(vec_filtered)
      case   <- 3
    }
  }
  
  # case 4
  if (case == 0) { # only if no previous case applied
    # assign class values
    vec_layered <- findInterval(vec, h_layer_breaks_4)
    # get percentages per class
    vec_stats <- table(vec_layered) / length(vec_layered)

    if (max(vec_stats) > 0.5) {
      # detect dominating height layer (covering > 50% of the valid pixels)
      dom_layer_4 <- f_get_dom_layer(vec_stats)
      # determine aggregated height with mean_weighted_max() from pixels belonging to dom. height layer
      result <- f_mean_weighted_max(vec[vec_layered == dom_layer_4]) # mean_weighted_max
      case   <- 4
    }
  }
  
  # case 5
  if (case == 0) { # only if no previous case applied
    # assign class values
    vec_layered <- findInterval(vec, h_layer_breaks_5)
    # get percentages per class
    vec_stats <- table(vec_layered) / length(vec_layered)

    # detect dominating height layer
    dom_layer_5 <- f_get_dom_layer(vec_stats)
    dom_layer_5 <- max(dom_layer_5) # if dom_layer_5 includes more than 1 class take the highest one
    # determine aggregated height with mean_weighted_max() from pixels belonging to dom. height layer
    result <- f_mean_weighted_max(vec[vec_layered == dom_layer_5])
    case   <- 5
  }
  
  # DEBUG/VIS: Plot # 
  if(verbose && plot && output_type == "vhm"){
    if (missing(agg_fact)) {
      stop(
        "argument agg_fact (aggregation factor) not specified. agg_fact must be an integer. agg_fact = cell resolution of input VHM / resolution of aggregated VHM.",
        call. = FALSE
      )
    }
    # redundant but needed for case 1/2 (these are not computed then)
    h_top_min_2 <- f_h_top_min_2(h_max)
    h_low_max_3 <- f_h_low_max_3(h_max)

    # build the matrix data
    x <- matrix(vec_orig, nrow = agg_fact, ncol = agg_fact)
    # format the data for the plot
    xval <- formatC(x, format = "f", digits = 2)
    pal  <- grDevices::colorRampPalette(c(rgb(0.96, 1, 0.96), rgb(0.1, 0.9, 0.1)), space = "rgb")
    if (h_max == result) {
      h_hmax_reslult <- paste0(" h_max = ", round(h_max, 1), " = h_agg")
    } else {
      h_hmax_reslult <- paste0(" h_max = ", round(h_max, 1), " > h_agg = ", round(result, 1))
    }
    main_ <- paste(
      sep = "\n",
      "", # leaf 1st ...
      "", # ... 2nd line empty --> make sure actutal title is readable
      paste0("case ", case),
      paste0(
        h_hmax_reslult,
        paste0(
          " | data ",
          length(vec[!is.na(vec_orig)]) / length(vec_orig) * 100,
          "% (",
          length(vec[!is.na(vec_orig)]), "/", length(vec_orig),
          ")"
          )
      ),
      paste0(
        "h_top_min_1: ", formatC(h_top_min_1, format = "d"), " | ",
        formatC(length(vec[vec >= h_top_min_1]) / length(vec), format = "f", digits = 2)
      ),
      paste0(
        "h_top_min_2: ", formatC(h_top_min_2, format = "d"), " | ",
        formatC(length(vec[vec >= h_top_min_2]) / length(vec), format = "f", digits = 2)
      ),
      paste0(
        "h_low_max_3: ", formatC(h_low_max_3, format = "d"), " | ",
        formatC(length(vec[vec <= h_low_max_3]) / length(vec), format = "f", digits = 2)
      )
    )
    #Plot the matrix
    x_hm <- gplots::heatmap.2(
      x,
      Rowv       = FALSE,
      Colv       = FALSE,
      dendrogram = "none",
      main       = main_,
      cex.main   = 0.7, # title smaller
      xlab       = "Columns",
      ylab       = "Rows",
      col        = pal, 
      tracecol   = "#303030",
      trace      = "none", 
      cellnote   = xval,
      notecol    = "black",
      notecex    = 0.8,
      keysize    = 1.5,
      margins    = c(5, 5)
      )
  }
  
  if (output_type == "vhm") { return(result) } else { return(case) }
}
####_________________________####
#### END OF SCRIPT ####
#------------------------------------------------------------------------------#
