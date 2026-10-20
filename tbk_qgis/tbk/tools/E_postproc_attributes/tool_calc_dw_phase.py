# *************************************************************************** #
# Calculate the Dauerwald-Ueberfuehrungsphase (nach Schuetz) per stand: DW_Phase + a/b/c Zusatz.
#
# Authors: Hannes Horneber (BFH-HAFL)
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

import shutil
from pathlib import Path

from qgis.PyQt.QtCore import QMetaType, QVariant
from qgis.core import (QgsFeature,
                       QgsFeatureRequest,
                       QgsFeatureSink,
                       QgsField,
                       QgsFields,
                       QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingOutputFile,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterVectorLayer,
                       QgsProviderRegistry,
                       QgsVectorDataProvider,
                       QgsVectorLayer)
from tbk_qgis.tbk.tools.E_postproc_attributes.calculate_dw_phase import REQUIRED_FIELDS, calc_dw_phase
from tbk_qgis.tbk.tools.E_postproc_attributes.tbk_qgis_processing_algorithm_toolsE import TBkProcessingAlgorithmToolE
from tbk_qgis.tbk.tools.F_additional_modules.tool_OS_change import _TBkStylePostProcessor

# Bundled style: DW_Phase categories + a/b/c hatching + Dauerwald labels (from TBk_Template.qgz)
STYLE_PATH = Path(__file__).resolve().parents[2] / "resources" / "styles" / "tbk_dw_phase.qml"


def _value(feature, idx):
    """Attribute value with QGIS NULL converted to None"""
    v = feature.attribute(idx)
    if v is None or (isinstance(v, QVariant) and v.isNull()):
        return None
    return v


class TBkCalculateDWPhaseAlgorithm(TBkProcessingAlgorithmToolE):
    """
    Adds the Dauerwald-Ueberfuehrungsphase (DW_Phase, -3 to 5) and its a/b/c Zusatz (DW_Phase_abc) to a
    TBk stand map, using the same logic as the "TBk Dauerwaldcode" layers of the TBk QGIS project template
    (see calculate_dw_phase.py). Optionally works in place (fields are added to / overwritten in the input
    file, no new output file) and writes a matching .qml style.
    """
    # ------- Define Constants -------#
    # File storing configuration parameters
    CONFIG_FILE = "config_file"
    # Input stand map
    STANDS_INPUT = "stands_input"
    # Add the fields to the input layer instead of creating a new output
    IN_PLACE = "in_place"
    # Write the bundled .qml style next to the output
    WRITE_QML = "write_qml"
    # Stands output with DW_Phase fields
    OUTPUT_STANDS_DW = "stands_dw_phase"
    # Path of the written .qml
    OUTPUT_QML = "qml"

    # Output field names (the bundled .qml relies on these)
    DW_PHASE_FIELD = "DW_Phase"
    DW_PHASE_ABC_FIELD = "DW_Phase_abc"

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along with some other properties.
        """
        # --- Parameters

        # Config file containing all parameter key-value pairs
        self.addParameter(QgsProcessingParameterFile(self.CONFIG_FILE,
                                                     'Configuration file to set the algorithm parameters. The bellow '
                                                     'non-optional parameters must still be set but will not be used.',
                                                     extension='toml',
                                                     optional=True))

        self.addParameter(QgsProcessingParameterVectorLayer(self.STANDS_INPUT,
                                                            "TBk stand map (needs fields " +
                                                            ", ".join(REQUIRED_FIELDS) + ")",
                                                            [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(QgsProcessingParameterBoolean(self.IN_PLACE,
                                                        "In place: add/overwrite the fields directly in the input "
                                                        "file (no new output file is created, output below is "
                                                        "ignored)",
                                                        defaultValue=False))

        self.addParameter(QgsProcessingParameterBoolean(self.WRITE_QML,
                                                        "Write .qml style (DW_Phase colours, a/b/c hatching, "
                                                        "Dauerwald labels) next to the output",
                                                        defaultValue=True))

        # --- Add output definition
        self.addParameter(QgsProcessingParameterFeatureSink(self.OUTPUT_STANDS_DW,
                                                            "Stand output with DW_Phase fields",
                                                            type=QgsProcessing.TypeVectorPolygon,
                                                            optional=True,
                                                            createByDefault=True))
        self.addOutput(QgsProcessingOutputFile(self.OUTPUT_QML, ".qml style"))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        in_place = self.parameterAsBoolean(parameters, self.IN_PLACE, context)
        write_qml = self.parameterAsBoolean(parameters, self.WRITE_QML, context)
        layer = self.parameterAsVectorLayer(parameters, self.STANDS_INPUT, context)
        if layer is None:
            raise QgsProcessingException("Invalid input stand layer.")

        missing = [f for f in REQUIRED_FIELDS if layer.fields().indexOf(f) < 0]
        if missing:
            raise QgsProcessingException(f"Input stand layer is missing required fields: {missing}")

        new_fields = [QgsField(self.DW_PHASE_FIELD, QMetaType.Int),
                      QgsField(self.DW_PHASE_ABC_FIELD, QMetaType.QString, len=1)]

        if in_place:
            output = self._process_in_place(layer, new_fields, feedback)
            qml_path = self._layer_file_path(output)
            qml_path = qml_path.with_name(qml_path.stem + "_DW_Phase.qml") if qml_path else None
        else:
            output = self._process_to_sink(parameters, context, layer, new_fields, feedback)
            qml_path = self._layer_file_path(output)
            qml_path = qml_path.with_suffix('.qml') if qml_path else None
            if write_qml and context.willLoadLayerOnCompletion(output):
                # apply the style right away if the output gets added to the canvas (see _TBkStylePostProcessor)
                self._style_postprocessor = _TBkStylePostProcessor(STYLE_PATH)
                context.layerToLoadOnCompletionDetails(output).setPostProcessor(self._style_postprocessor)

        results = {self.OUTPUT_STANDS_DW: output}
        if write_qml and qml_path:
            shutil.copyfile(STYLE_PATH, qml_path)
            feedback.pushInfo(f"Wrote style: {qml_path}")
            results[self.OUTPUT_QML] = str(qml_path)
        return results

    def _process_to_sink(self, parameters, context, layer, new_fields, feedback):
        """Copy all features to a new output with the DW fields added (overwritten if already present)"""
        source = self.parameterAsSource(parameters, self.STANDS_INPUT, context)
        out_fields = QgsFields(source.fields())
        for field in new_fields:
            if out_fields.indexOf(field.name()) < 0:
                out_fields.append(field)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_STANDS_DW, context,
                                               out_fields, source.wkbType(), source.sourceCrs())
        if sink is None:
            raise QgsProcessingException("Could not create output layer (no output set while not in place?).")

        idx_in = [source.fields().indexOf(f) for f in REQUIRED_FIELDS]
        idx_phase = out_fields.indexOf(self.DW_PHASE_FIELD)
        idx_abc = out_fields.indexOf(self.DW_PHASE_ABC_FIELD)
        n_extra = len(out_fields) - len(source.fields())

        total = source.featureCount() or 1
        for i, feat in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
            phase, abc = calc_dw_phase(*[_value(feat, idx) for idx in idx_in])
            attrs = feat.attributes() + [None] * n_extra
            attrs[idx_phase] = phase
            attrs[idx_abc] = abc
            out_feat = QgsFeature(out_fields)
            out_feat.setGeometry(feat.geometry())
            out_feat.setAttributes(attrs)
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
            feedback.setProgress(i / total * 100)

        return dest_id

    def _process_in_place(self, layer, new_fields, feedback):
        """Add (if missing) and fill the DW fields directly in the input layer's data source"""
        if layer.isEditable():
            raise QgsProcessingException("Input layer is in edit mode - save or discard its edits first.")

        # use an own layer instance for file layers (not the project layer, which lives in the main thread)
        edit_layer = QgsVectorLayer(layer.source(), "dw_phase_in_place", "ogr") \
            if layer.providerType() == "ogr" else layer
        provider = edit_layer.dataProvider()
        caps = provider.capabilities()
        if not (caps & QgsVectorDataProvider.AddAttributes and caps & QgsVectorDataProvider.ChangeAttributeValues):
            raise QgsProcessingException(f"Input layer can't be edited in place ({layer.source()}).")

        to_add = [f for f in new_fields if provider.fields().indexOf(f.name()) < 0]
        if to_add:
            if not provider.addAttributes(to_add):
                raise QgsProcessingException(f"Could not add fields {[f.name() for f in to_add]} to input layer.")
            edit_layer.updateFields()

        fields = provider.fields()
        idx_in = [fields.indexOf(f) for f in REQUIRED_FIELDS]
        idx_phase = fields.indexOf(self.DW_PHASE_FIELD)
        idx_abc = fields.indexOf(self.DW_PHASE_ABC_FIELD)

        request = QgsFeatureRequest().setFlags(QgsFeatureRequest.NoGeometry).setSubsetOfAttributes(idx_in)
        changes = {}
        total = edit_layer.featureCount() or 1
        for i, feat in enumerate(edit_layer.getFeatures(request)):
            if feedback.isCanceled():
                break
            phase, abc = calc_dw_phase(*[_value(feat, idx) for idx in idx_in])
            changes[feat.id()] = {idx_phase: phase, idx_abc: abc}
            feedback.setProgress(i / total * 100)

        if not provider.changeAttributeValues(changes):
            raise QgsProcessingException("Could not write DW_Phase values to input layer.")
        feedback.pushInfo(f"Wrote {self.DW_PHASE_FIELD}/{self.DW_PHASE_ABC_FIELD} in place for {len(changes)} "
                          f"features: {layer.source()}")

        # the project layer has to pick up the new fields, done in postProcessAlgorithm() (main thread)
        self._in_place_layer = layer
        return layer.source()

    @staticmethod
    def _layer_file_path(layer_source):
        """File path of an ogr layer source (None for memory/temporary layers)"""
        path = QgsProviderRegistry.instance().decodeUri("ogr", layer_source).get("path")
        return Path(path) if path and Path(path).is_file() else None

    def postProcessAlgorithm(self, context, feedback):
        layer = getattr(self, "_in_place_layer", None)
        if layer is not None:
            layer.dataProvider().reloadData()
            layer.updateFields()
            layer.triggerRepaint()
        return {}

    def createInstance(self):
        """
        Returns a new algorithm instance
        """
        return TBkCalculateDWPhaseAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Calculate Dauerwald phase (DW_Phase)'

    def shortHelpString(self):
        """
        Returns a localised short help string for the algorithm.
        """
        return ('Adds the Dauerwald-Überführungsphase (nach Schütz) to a TBk stand map, with the same logic as '
                'the "TBk Dauerwaldcode" layers of the TBk QGIS project:\n'
                '- DW_Phase: -3/-2/-1 Vorbereitung (Jungwald, hdom below threshold), 0 Stabilisierung, '
                '1 Nachwuchsförderung, 2 Strukturierung, 3 Gleichgewicht, 4 Struktur geht verloren (zuviel MS), '
                '5 Struktur geht verloren (zuwenig OS)\n'
                '- DW_Phase_abc: a/b/c hdom stage (phases 0-5 only)\n'
                'hdom thresholds depend on NH/LH (NH > 50%) and vegetation height zone (VegZone_Code).\n\n'
                'In place: the fields are added to (or overwritten in) the input file itself, no new output '
                'file. The input layer must not be in edit mode.\n'
                'Write .qml: copies the bundled style next to the output (<output>.qml, or '
                '<input>_DW_Phase.qml in place) and applies it when the output is loaded.\n\n'
                'Note: the QGIS "Edit Features In-Place" toolbox mode is not supported, as it can\'t add new '
                'fields - use the In place option instead.')
