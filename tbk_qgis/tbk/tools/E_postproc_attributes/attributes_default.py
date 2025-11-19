# *************************************************************************** #
# Postprocessing: Stand attributes default
# TODO: will be integrated into other postprocessing steps / rewritten @2025
#
# Authors: Hannes Horneber, Dominique Weber, Christoph Schaller (BFH-HAFL)
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

# Import system modules

from tbk_qgis.tbk.general.tbk_utilities import *

def calc_attributes(working_root, shape_in, shape_out, del_tmp=True):
    print("--------------------------------------------")
    print("START CALC specific attributes")

    # Copy shapefile
    in_layer = QgsVectorLayer(shape_in, "stands in", "ogr")

    ctc = QgsProject.instance().transformContext()
    QgsVectorFileWriter.writeAsVectorFormatV3(in_layer, shape_out, ctc, getVectorSaveOptions('GPKG', 'utf-8'))
    out_layer = QgsVectorLayer(shape_out, "stands in", "ogr")

    with edit(out_layer):
        # Add fields
        print("add fields...")
        provider = out_layer.dataProvider()
        provider.addAttributes([QgsField("struktur", QVariant.Int),
                                QgsField("tbk_typ", QVariant.String)])
        out_layer.updateFields()

        # Calculate fields
        print("calculate fields...")
        expression = QgsExpression('to_int(area($geometry))')
        context = QgsExpressionContext()
        context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(out_layer))

        i = 1
        for f in out_layer.getFeatures():
            i += 1

            # Struktur
            if f["hdom"] >= 28 and \
                    f["type"] == "classified" and \
                    f["area_m2"] >= 3000 and \
                    f["DG_us"] >= 15 and \
                    f["DG_ms"] >= 20 and \
                    f["DG"] <= 60:
                f["struktur"] = 1
            else:
                f["struktur"] = 0

            f["tbk_typ"] = f["type"]

            # Recalculate area
            context.setFeature(f)
            f['area_m2'] = expression.evaluate(context)

            out_layer.updateFeature(f)

            # Delete fields
    print("remove fields...")
    if del_tmp:
        delete_fields(out_layer, ["type", "NH_pixels", "NH_prob"])

    print("DONE!")
    return shape_out
