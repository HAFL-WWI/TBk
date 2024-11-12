######################################################################
# Stand attributes default
#
# (C) Dominique Weber, Christoph Schaller,  HAFL, BFH
######################################################################

# Import system modules

from tbk_qgis.tbk.general.tbk_utilities import *


#
########################################################################################

def calc_attributes(working_root, tmp_output_folder, del_tmp=True):
    print("--------------------------------------------")
    print("START CALC specific attributes")

    # TBk folder path
    working_root

    # Filenames
    shape_in = os.path.join(working_root, "stands_clipped.gpkg")
    shape_out = os.path.join(tmp_output_folder, "stands_attributed_tmp.gpkg")

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
    return (shape_out)