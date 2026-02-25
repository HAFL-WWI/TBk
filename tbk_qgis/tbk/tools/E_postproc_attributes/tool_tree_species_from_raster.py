# -*- coding: utf-8 -*-
# *************************************************************************** #
# Calculate tree species proportions in polygons based on a species raster.
#
# Integrated into TBk QGIS Plugin: Bestandeskarte Toolkit
#
# Author: Hannes Horneber (BFH-HAFL), adjusted for plugin integration
# *************************************************************************** #

from PyQt5.QtCore import QCoreApplication, QVariant, QMetaType
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterVectorLayer,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterString,
    QgsProcessingParameterFeatureSink,
    QgsProcessingMultiStepFeedback,
    QgsProcessingException,
    QgsVectorLayer,
    QgsProcessingUtils,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsWkbTypes,
    QgsFeatureSink
)
from collections import defaultdict
import processing
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_processing_algorithm_toolsE import TBkProcessingAlgorithmToolE

# -----------------------------
# HELPER FUNCTIONS
# =============================
def _ensure_vector_layer(obj, context, fallback_name="zonal_hist"):
    """
    Accepts either a QgsVectorLayer or a string (path/URI),
    and returns a valid QgsVectorLayer or raises QgsProcessingException.
    """
    if hasattr(obj, "fields") and hasattr(obj, "getFeatures"):
        # already a layer-like object
        return obj

    if isinstance(obj, str):
        # 1) Try resolving through Processing utils (handles 'memory:' URIs)
        if QgsProcessingUtils is not None:
            try:
                lyr = QgsProcessingUtils.mapLayerFromString(obj, context)
                if lyr and lyr.isValid():
                    return lyr
            except Exception:
                pass

        # 2) Fallback: try opening with OGR provider
        lyr = QgsVectorLayer(obj, fallback_name, "ogr")
        if lyr and lyr.isValid():
            return lyr

    # If we reach here, it's not a usable vector layer
    raise QgsProcessingException(f"Could not resolve obj to a vector layer (got: {type(obj)}).")


class TBkTreeSpeciesFromRaster(TBkProcessingAlgorithmToolE):

    INPUT_VECTOR = "INPUT_VECTOR"
    INPUT_RASTER = "INPUT_RASTER"
    CLASS_MAPPING = "CLASS_MAPPING"
    OUTPUT = "OUTPUT"

    # this maps the raster values of Thuenen Institut to the WIS.2 Desktop tree species (p100 - p800)
    # DEFAULT_MAPPING = (
    #     "p100: 8; " # PicAbie (Fichte, spruce)
    #     "p120: 14; " # AbiAlba (Weisstanne, silver fir)
    #     "p140: 9; " # PinSylv (Föhre, pine)
    #     "p160: 10; " # LarDeci (Lärche, larch)
    #     "p390: 4; " # other coniferous
    #     "p410: 3; " # FagSylv (Buche, beech)
    #     "p420: 5; " # Que (Eiche, oak)
    #     "p430: 99; " # FraExe (Esche, ash)
    #     "p440: 99; " # AcerPseu (Ahorn, maple)
    #     "p800: 2,6,16,17" # other decidious
    # )
    # DEFAULT_MAPPING = (
    #     "PicAbie: 8; " # Picea Abies (Fichte, spruce)
    #     "AbiAlba: 14; " # Abies Alba (Weisstanne, silver fir)
    #     "PinSylv: 9; " # Pinus Sylvestris (Föhre, pine)
    #     "LarDeci: 10; " # Larix Decidua (Lärche, larch)
    #     "ConEtc: 4; " # other coniferous
    #     "FagSylv: 3; " # Fagus Sylvatica (Buche, beech)
    #     "Que: 5; " # Quercus (Eiche, oak)
    #     "FolEtc: 2,6,16,17" # other decidious
    # )

    # this maps the raster values of the BGB tree species to the WIS.2 Web tree species convention
    DEFAULT_MAPPING = ("FagSylv: 1; Que: 2; LarDeci: 3; FolEtc: 4; PicAbie: 5" )

    def tr(self, string):
        return QCoreApplication.translate("Processing", string)

    # -----------------------------
    # PARAMETERS
    # =============================
    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_VECTOR,
                self.tr("Input polygons (e.g. stand map)"),
                [QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_RASTER,
                self.tr("Input tree species raster")
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.CLASS_MAPPING,
                self.tr("Class mapping with commata-separated pairs of name:raster value (e.g. FagSylv: 1; ConEtc: 2,3,4)"),
                defaultValue=self.DEFAULT_MAPPING
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Polygons with appended tree species"),
                type=QgsProcessing.TypeVectorPolygon
            )
        )

    # -----------------------------
    # PROCESSING
    # =============================
    def processAlgorithm(self, parameters, context, model_feedback):

        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}

        # --- Step 1: Validate inputs
        feedback.pushInfo("Validating inputs...")

        vector_layer = self.parameterAsVectorLayer(parameters, self.INPUT_VECTOR, context)
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)

        if vector_layer is None:
            raise QgsProcessingException("Input polygon layer is invalid.")

        if vector_layer.wkbType() not in (QgsWkbTypes.Polygon, QgsWkbTypes.MultiPolygon):
            raise QgsProcessingException("Input layer must contain polygons.")

        if raster_layer is None:
            raise QgsProcessingException("Input raster layer is invalid.")

        # Parse mapping
        mapping_str = self.parameterAsString(parameters, self.CLASS_MAPPING, context)
        class_mapping = {}

        for entry in mapping_str.split(";"):
            if ":" not in entry:
                raise QgsProcessingException(f"Invalid mapping entry: '{entry}'")
            key, values = entry.split(":")
            class_mapping[key.strip()] = [int(v.strip()) for v in values.split(",")]

        feedback.pushInfo(f"Parsed class mapping: {class_mapping}")

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # --- Step 2: Zonal histogram

        feedback.pushInfo("Computing zonal histogram...")

        alg_params = {
            "INPUT_RASTER": raster_layer.source(),
            "RASTER_BAND": 1,
            "INPUT_VECTOR": parameters[self.INPUT_VECTOR],
            "COLUMN_PREFIX": "histo_",
            "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT
        }

        outputs["ZonalHistogram"] = processing.run(
            "native:zonalhistogram",
            alg_params,
            context=context,
            feedback=feedback,
            is_child_algorithm=True
        )

        hist_layer_obj = outputs["ZonalHistogram"]["OUTPUT"]
        hist_layer = _ensure_vector_layer(hist_layer_obj, context, fallback_name="zonal_hist")
        # --- Step 3: Build output layer & compute species proportions
        feedback.pushInfo("Building output layer...")

        # Build fields = hist_layer fields except histogram + mapping fields
        new_fields = QgsFields()
        for field in hist_layer.fields():
            if not field.name().startswith("histo_"):
                new_fields.append(field)

        for key in class_mapping.keys():
            new_fields.append(QgsField(key, QMetaType.Int, '', 10, 0))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            new_fields,
            vector_layer.wkbType(),
            vector_layer.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException("Could not create output layer.")

        # --- Process each polygon
        # *******************************************
        total = hist_layer.featureCount()
        for i, feat in enumerate(hist_layer.getFeatures()):
            if feedback.isCanceled():
                break

            total_px = 0
            counts = defaultdict(int)

            # Init keys
            for key in class_mapping:
                counts[key] = 0

            # Count occurrences
            for field in feat.fields():
                name = field.name()
                if not name.startswith("histo_"):
                    continue

                value_str = name.replace("histo_", "").strip()
                try:
                    raster_value = int(float(value_str))
                except Exception:
                    # skip bizarre names
                    continue

                count = feat[name] if feat[name] is not None else 0
                total_px += count

                for key, raster_ids in class_mapping.items():
                    if raster_value in raster_ids:
                        counts[key] += count

            # Compute percentages
            if total_px > 0:
                raw = {k: (counts[k] / total_px) * 100 for k in class_mapping}
                rounded = {k: round(v) for k, v in raw.items()}
                adjust = 100 - sum(rounded.values())
                # Assign adjustment to the largest
                if adjust != 0:
                    max_key = max(rounded, key=rounded.get)
                    rounded[max_key] += adjust
            else:
                # fallback: 100% to first class
                first = next(iter(class_mapping.keys()))
                rounded = {k: (100 if k == first else 0) for k in class_mapping}

            new_feat = QgsFeature()
            new_feat.setGeometry(feat.geometry())

            base_attrs = [
                feat[field.name()] for field in hist_layer.fields()
                if not field.name().startswith("histo_")
            ]

            attrs = base_attrs + [rounded[k] for k in class_mapping]
            new_feat.setAttributes(attrs)

            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)

            feedback.setProgress(i / total * 100)

        # --- Return result
        results[self.OUTPUT] = dest_id
        return results

    # -----------------------------
    # METADATA
    # =============================
    def name(self):
        return "tbk_tree_species_from_raster"

    def displayName(self):
        return self.tr("Tree species from raster")

    def createInstance(self):
        return TBkTreeSpeciesFromRaster()