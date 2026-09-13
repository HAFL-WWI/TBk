# *************************************************************************** #
# Estimate hdom (Oberhoehe) for existing stand boundaries that don't carry a
# TBk-generated hdom attribute, from the VHM pixel distribution within each
# polygon.
#
# The simplest of the approaches discussed in GitHub
# issue #43 - a single fixed percentile, closely mirroring how TBk itself
# derives hdom (mean height of the stand's VHM cells). Precisely *because*
# it leans on that TBk-native definition, it is likely less robust for
# stands that were NOT delineated by TBk in the first place (e.g. BK_AG,
# hand-digitised boundaries) - their pixel distribution may not resemble a
# TBk-classified stand's at all. See tool_estimate_hdom_existing_stands.py's
# class docstring for how this relates to the other approaches being
# explored for #43.
#
# Method: hdom = a single fixed percentile of the valid VHM pixel values per
# stand, after an optional MAXIMUM-resampling of the VHM to a coarser cell
# size (`resample_resolution`, default 10m). Originally ported as a
# numpy-histogram cumulative-frequency band (see Semesterarbeit, Manuel
# Kraus, BFH-HAFL, 2023/2024, GitHub issue #43), then simplified and
# extended after local benchmarking against the reference test dataset
# (data/tbk_2012), restricted to `classified` stands only - `remainder`
# stands are excluded from validation since their existing hdom is itself
# not a trustworthy reference (see Kraus' thesis, section 5).
#
# Why resample first: a fine VHM (e.g. 150cm) has plenty of low-height
# gap/understory pixels interspersed with canopy pixels, which drag down any
# plain statistic computed directly on it (tried: percentile up to p95,
# histogram mode, histogram mode restricted to the upper part of the
# distribution - all clearly worse than resampling first, down to RMSE
# 17-22m for a naive histogram mode). A per-window MAXIMUM (not mean/median)
# picks the tallest pixel in each resampled cell, i.e. the local canopy top -
# which is exactly how TBk itself derives VHM_10m/VHM_150cm from its finest
# VHM input (see tool_prepare_vhm_mg.py, `gdal:warpreproject` with
# RESAMPLING=maximum) and is not a TBk-specific artifact: it approximates
# hdom's own definition (mean height of the ~100 dominant trees/ha, i.e. one
# tree per ~10x10m). A local sweep (1-20m target resolution, on VHM_150cm)
# found a clear optimum at 4-10m (RMSE 1.27-1.43m, ~95-97% within +-2m,
# best percentile shifting from ~70 at 4m down to ~45 at 10m as the window
# grows), degrading on both sides (RMSE 2.5-3.8m at 1-3m: window still too
# small to filter gap noise; RMSE 2.6-5.6m at 15-20m: over-smoothed, too few
# independent cells per stand). Default 10m was chosen for that domain
# grounding (hdom's own ~100 trees/ha definition) and consistency with TBk's
# own VHM_10m convention, not because it was the single best value tested.
#
# This mirrors, more robustly, the same underlying idea as the existing
# `hp80` fallback already used for remainder stands in
# bk_hafl_ClassificationHelper.add_vhm_stats() / bk_hafl_post_process.py -
# just with a lower percentile (median-ish vs. 80th), since a classified
# stand's resampled pixels already form one coherent, comparatively
# homogeneous cluster, unlike a remainder's.
#
# Confidence flag (`class_field`, see _hdom_class()): also classifies each
# stand as "clear" (one dominant height layer) or "ambiguous" (none), via a
# histogram-peak + TBk-similar-height-tolerance homogeneity ratio. This
# ratio does discriminate `classified` from `remainder` TBk stands
# reasonably well (median ratio 0.82 vs. 0.54) - but using the peak height
# itself as the hdom value, instead of just as a QA flag, was tried and
# rejected: it did not beat the plain percentile even on "clear" stands.
#
# Only pixels whose *center* falls inside a stand are used (GDAL
# RasterizeLayer's default, without ALL_TOUCHED) - see GitHub issue #43
# discussion (A. Benini) on edge effects from including pixels that merely
# touch a polygon's border.
#
# Authors: Hannes Horneber (BFH-HAFL); leaning on Manuel Kraus' Semesterarbeit (BFH-HAFL, 2023/2024)
# and the existing hp80 logic (Dominique Weber/Christian Rosset, 2017-2021)
# *************************************************************************** #
"""
/***************************************************************************
    TBk: Toolkit Bestandeskarte (QGIS Plugin)
    Toolkit for the generating and processing forest stand maps
    Copyright (C) 2025 BFH-HAFL (hannes.horneber@bfh.ch, christian.rosset@bfh.ch)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 ***************************************************************************/
"""

import logging
import numpy
from PyQt5.QtCore import QMetaType

from tbk_qgis.tbk.general.tbk_utilities import *
from tbk_qgis.tbk.tools.C_stand_delineation.bk_hafl_ClassificationHelper import ClassificationHelper

# Substep narration only (file/console at DEBUG); joins the "Estimate hdom for existing
# stands" logger stream set up by tool_estimate_hdom_existing_stands.py, the only caller.
log = logging.getLogger('Estimate hdom for existing stands')

# TBk's own "similar height" tolerance (see C_stand_delineation/tool_stand_delineation_algorithm.py
# MIN_TOL/MAX_TOL/MIN_CORR/MAX_CORR defaults) - reused as-is in _hdom_class() below, so
# "homogeneous" means the same thing here as it does during TBk's own pixel classification.
_SIMILAR_HEIGHT_MIN_TOL = 0.1
_SIMILAR_HEIGHT_MAX_TOL = 0.1
_SIMILAR_HEIGHT_MIN_CORR = 4.0
_SIMILAR_HEIGHT_MAX_CORR = 4.0
_PEAK_BIN_WIDTH = 1.0


def _extract_valid_pixels(vhm_ds, band, gt, inv_gt, nodata, geom, min_valid_height, max_valid_height,
                          mem_rast_drv, mem_vec_drv, srs):
    """
    Reads the VHM pixels whose center falls inside `geom` (a windowed read + an in-memory
    rasterized mask, avoiding loading the whole VHM into memory), filtered to nodata- and
    height-range-valid values. Returns a flat 1-D array (possibly empty).
    """
    env = geom.GetEnvelope()  # (minX, maxX, minY, maxY)
    px0, py0 = gdal.ApplyGeoTransform(inv_gt, env[0], env[3])
    px1, py1 = gdal.ApplyGeoTransform(inv_gt, env[1], env[2])
    px_min = max(0, int(min(px0, px1)))
    py_min = max(0, int(min(py0, py1)))
    px_max = min(vhm_ds.RasterXSize, int(max(px0, px1)) + 1)
    py_max = min(vhm_ds.RasterYSize, int(max(py0, py1)) + 1)
    w, h = px_max - px_min, py_max - py_min
    if w <= 0 or h <= 0:
        return numpy.empty(0, dtype=float)

    # in-memory mask raster aligned to the windowed VHM grid, geometry rasterized without
    # ALL_TOUCHED (RasterizeLayer's default) so only center-covered pixels are burned in
    mask_x0 = gt[0] + px_min * gt[1] + py_min * gt[2]
    mask_y0 = gt[3] + px_min * gt[4] + py_min * gt[5]
    mask_ds = mem_rast_drv.Create('', w, h, 1, gdal.GDT_Byte)
    mask_ds.SetGeoTransform((mask_x0, gt[1], gt[2], mask_y0, gt[4], gt[5]))
    mask_ds.SetProjection(vhm_ds.GetProjection())
    mask_ds.GetRasterBand(1).Fill(0)

    mem_vec = mem_vec_drv.CreateDataSource('')
    mem_lyr = mem_vec.CreateLayer('', srs=srs, geom_type=ogr.wkbUnknown)
    mem_feat = ogr.Feature(mem_lyr.GetLayerDefn())
    mem_feat.SetGeometry(geom)
    mem_lyr.CreateFeature(mem_feat)
    gdal.RasterizeLayer(mask_ds, [1], mem_lyr, burn_values=[1])
    mask = mask_ds.GetRasterBand(1).ReadAsArray()

    window = band.ReadAsArray(px_min, py_min, w, h).astype(float)
    pixels = window[mask == 1]

    if nodata is not None:
        pixels = pixels[pixels != nodata]
    pixels = pixels[(pixels >= min_valid_height) & (pixels <= max_valid_height)]
    return pixels


def _max_resample_vhm(vhm, resample_resolution, tmp_output_folder,
                      gdal_create_options, context=None, feedback=None):
    """
    Resamples `vhm` to `resample_resolution` (m) using MAXIMUM resampling (per output cell,
    the tallest input pixel) - the same operation TBk's own preprocessing uses to derive
    VHM_10m/VHM_150cm from its finest VHM input (tool_prepare_vhm_mg.py). Returns the path to
    the resampled raster (written under `tmp_output_folder`).
    """
    resampled_path = os.path.join(tmp_output_folder, f"vhm_maxresample_{resample_resolution}m.tif")
    processing.run("gdal:warpreproject", {
        'INPUT': vhm, 'SOURCE_CRS': None, 'TARGET_CRS': None,
        'RESAMPLING': 7,  # maximum
        'NODATA': None, 'TARGET_RESOLUTION': resample_resolution,
        'OPTIONS': gdal_create_options, 'DATA_TYPE': 0,
        'TARGET_EXTENT': None, 'TARGET_EXTENT_CRS': None,
        'MULTITHREADING': False, 'EXTRA': '', 'OUTPUT': resampled_path
    }, context=context, feedback=feedback, is_child_algorithm=True)
    return resampled_path


def _percentile_hdom(pixels, percentile):
    """
    hdom = the given percentile (0-100) of the stand's valid VHM pixels; std is the plain
    std. deviation of those pixels (a rough per-stand dispersion/confidence indicator, not
    tied to the percentile itself - a high value flags a heterogeneous stand worth a visual
    check, regardless of which percentile is configured).
    """
    return float(numpy.percentile(pixels, percentile)), float(numpy.std(pixels))


def _hdom_homogeneity(pixels):
    """
    Scores (0-1) whether the stand's (resampled) pixels have one clear dominant height layer -
    a QA signal for `hdom_field`, NOT an alternative way to compute hdom itself (tried: using
    the peak's own mean as hdom instead of the percentile - it did not outperform the plain
    percentile even on the most homogeneous stands, see module docstring).

    Method: find the histogram mode (peak, 1m bins), then return the fraction of pixels that
    fall within TBk's own "similar height" tolerance band around it (`_SIMILAR_HEIGHT_*` - the
    same tolerance TBk itself uses to grow clusters during stand delineation, see
    bk_hafl_ClassificationHelper.get_similar_neighbours()) - the inverse of an entropy/spread
    measure: 1.0 means every pixel is close to the peak (one clear layer), low values mean the
    height distribution is spread across multiple layers/heights with no single peak. Locally,
    this discriminates `classified` from `remainder` TBk stands reasonably well (median 0.82 vs.
    0.54) - see `_hdom_class()` for the derived "clear"/"ambiguous" cutoff.
    """
    lo, hi = pixels.min(), pixels.max()
    if hi <= lo:
        return 1.0
    edges = numpy.arange(lo, hi + _PEAK_BIN_WIDTH, _PEAK_BIN_WIDTH)
    hist, edges = numpy.histogram(pixels, bins=edges)
    peak_idx = numpy.argmax(hist)
    peak_height = (edges[peak_idx] + edges[peak_idx + 1]) / 2.0
    mask = ClassificationHelper.get_similar_neighbours(pixels, peak_height,
                                                       _SIMILAR_HEIGHT_MIN_TOL, _SIMILAR_HEIGHT_MAX_TOL,
                                                       _SIMILAR_HEIGHT_MIN_CORR, _SIMILAR_HEIGHT_MAX_CORR)
    return float(mask.sum()) / pixels.size


def _hdom_class(homogeneity, homogeneity_threshold):
    """"clear"/"ambiguous", thresholding `_hdom_homogeneity()`'s score - see that function."""
    return "clear" if homogeneity >= homogeneity_threshold else "ambiguous"


def estimate_hdom_existing_stands(stands_output, vhm,
                                  hdom_field="hdom", std_field="hdom_std",
                                  homogeneity_field="hdom_homogeneity", class_field="hdom_class",
                                  percentile=50, resample_resolution=10.0, homogeneity_threshold=0.67,
                                  min_valid_height=0.0, max_valid_height=60.0,
                                  tmp_output_folder=None, del_tmp=True,
                                  gdal_create_options='COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9',
                                  context=None, feedback=None):
    """
    Adds/overwrites `hdom_field`, `std_field`, `homogeneity_field` and `class_field` on
    `stands_output` (a GPKG path, already a copy of the input stands - see
    tool_estimate_hdom_existing_stands.py) by estimating hdom per polygon from `vhm`, as the
    given percentile of the stand's valid VHM pixels (after an optional MAXIMUM-resampling of
    `vhm` - see module docstring for why), and scoring whether that stand has one clear
    dominant height layer (`homogeneity_field`/`class_field`, see `_hdom_homogeneity()`) - a QA
    signal, not an alternative hdom value.

    :param stands_output: path to the (already copied) stands GPKG to write results into
    :param vhm: path to the VHM raster to estimate hdom from, at any resolution
    :param hdom_field: output field name for the estimated hdom
    :param std_field: output field name for the pixel std. deviation within the stand
        (indicates estimate confidence - high values flag stands worth a visual check)
    :param homogeneity_field: output field name for the 0-1 dominant-layer homogeneity score
        (1.0 = all pixels close to one peak height; low = spread across multiple heights)
    :param class_field: output field name for the "clear"/"ambiguous" flag derived from
        `homogeneity_field` via `homogeneity_threshold`
    :param percentile: percentile (0-100) of the stand's valid VHM pixels used as hdom
    :param resample_resolution: target cell size (m) for the MAXIMUM-resampling step before
        pixel extraction; falsy (0/None) skips resampling and uses `vhm` as given
    :param homogeneity_threshold: minimum `homogeneity_field` value for `class_field` to read "clear"
    :param min_valid_height: pixels below this height (m) are treated as outliers and excluded
    :param max_valid_height: pixels above this height (m) are treated as outliers and excluded
    :param tmp_output_folder: folder for the resampled VHM; required if `resample_resolution` is set
    :param del_tmp: delete the resampled VHM again once done
    :param gdal_create_options: GDAL raster creation options for the resampled VHM
    """
    timer = SubprocessTimer(feedback, "Estimate hdom for existing stands", "H", log=log)

    working_vhm = vhm
    resampled_vhm = None
    if resample_resolution:
        if not tmp_output_folder:
            raise ValueError("tmp_output_folder is required when resample_resolution is set")
        ensure_dir(tmp_output_folder)
        timer.step(f"max-resampling VHM to {resample_resolution}m (denoises gaps/understory, "
                  f"mirrors how TBk itself derives VHM_10m/VHM_150cm - see module docstring)...")
        resampled_vhm = _max_resample_vhm(vhm, resample_resolution, tmp_output_folder,
                                          gdal_create_options, context=context, feedback=feedback)
        working_vhm = resampled_vhm

    timer.step("loading VHM...")
    vhm_ds = gdal.Open(working_vhm, gdal.GA_ReadOnly)
    band = vhm_ds.GetRasterBand(1)
    gt = vhm_ds.GetGeoTransform()
    inv_gt = gdal.InvGeoTransform(gt)
    nodata = band.GetNoDataValue()
    srs = osr.SpatialReference(wkt=vhm_ds.GetProjection())

    # OGR's in-memory vector driver was named 'Memory' before GDAL 3.11 and merged into the
    # unified 'MEM' name from GDAL 3.11 onwards ('Memory' still works there as a deprecated
    # alias). Try both so this works across GDAL versions.
    mem_vec_drv = ogr.GetDriverByName('MEM') or ogr.GetDriverByName('Memory')
    mem_rast_drv = gdal.GetDriverByName('MEM')

    stands_layer = QgsVectorLayer(stands_output, "stands", "ogr")
    feature_count = stands_layer.featureCount()

    skipped = 0
    with edit(stands_layer):
        provider = stands_layer.dataProvider()
        existing_fields = [f.name() for f in provider.fields()]
        new_fields = [QgsField(name, QMetaType.Double, len=10, prec=2)
                     for name in (hdom_field, std_field, homogeneity_field) if name not in existing_fields]
        if class_field not in existing_fields:
            new_fields.append(QgsField(class_field, QMetaType.QString, len=20))
        if new_fields:
            provider.addAttributes(new_fields)
            stands_layer.updateFields()

        timer.step(f"estimating hdom for {feature_count} stands...")
        for i, f in enumerate(stands_layer.getFeatures()):
            if i % 2000 == 0 and feedback is not None and feedback.isCanceled():
                break

            geometry = f.geometry()
            if geometry is None or geometry.isEmpty():
                f[hdom_field] = core.NULL
                f[std_field] = core.NULL
                f[homogeneity_field] = core.NULL
                f[class_field] = core.NULL
                skipped += 1
                stands_layer.updateFeature(f)
                continue

            geom = ogr.CreateGeometryFromWkb(bytes(geometry.asWkb()))
            pixels = _extract_valid_pixels(vhm_ds, band, gt, inv_gt, nodata, geom,
                                           min_valid_height, max_valid_height,
                                           mem_rast_drv, mem_vec_drv, srs)
            if pixels.size == 0:
                f[hdom_field] = core.NULL
                f[std_field] = core.NULL
                f[homogeneity_field] = core.NULL
                f[class_field] = core.NULL
                skipped += 1
            else:
                hdom, std = _percentile_hdom(pixels, percentile)
                homogeneity = _hdom_homogeneity(pixels)
                f[hdom_field] = hdom
                f[std_field] = std
                f[homogeneity_field] = homogeneity
                f[class_field] = _hdom_class(homogeneity, homogeneity_threshold)
            stands_layer.updateFeature(f)

    vhm_ds = None

    if resampled_vhm is not None and del_tmp:
        delete_raster(resampled_vhm)

    if skipped:
        log.warning(f"{skipped}/{feature_count} stand(s) had no valid VHM pixels (empty geometry, "
                   f"outside raster extent, nodata, or entirely outside "
                   f"[{min_valid_height}, {max_valid_height}]m height range) and were left NULL.")

    timer.finish()
    return stands_output
