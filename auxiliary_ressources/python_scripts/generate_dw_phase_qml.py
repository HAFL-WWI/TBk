# *************************************************************************** #
# Generate tbk_qgis/tbk/resources/styles/tbk_dw_phase.qml (style of the "Calculate Dauerwald phase" tool)
# from the "TBk Dauerwaldcode" + "TBk Dauerwaldcode Zusatz abc" layers of TBk_Template.qgz.
#
# Combines both into one rule-based renderer on the DW_Phase / DW_Phase_abc attributes (instead of the
# template's on-the-fly expressions) and keeps the Dauerwald labels. Re-run after changing these layers
# in the template:
#   C:\OSGeo4W\bin\python-qgis-ltr.bat auxiliary_ressources\python_scripts\generate_dw_phase_qml.py
#
# Authors: Hannes Horneber (BFH-HAFL)
# *************************************************************************** #
import os
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

from qgis.core import QgsApplication, QgsRuleBasedRenderer, QgsVectorLayer

REPO = Path(__file__).resolve().parents[2]
TEMPLATE = REPO / "tbk_qgis" / "tbk" / "resources" / "TBk_Template.qgz"
OUT_QML = REPO / "tbk_qgis" / "tbk" / "resources" / "styles" / "tbk_dw_phase.qml"
LAYER_DW = "TBk Dauerwaldcode"
LAYER_ABC = "TBk Dauerwaldcode Zusatz abc"
# a/b/c is only hatched where it deviates from the "regular" combination (same rule as the template)
ABC_SKIP_PHASE = {'a': 1, 'b': 2, 'c': 3}

FIELDS = ("field=VegZone_Code:integer&field=NH:double&field=hdom:double&field=DG_os:double&field=DG_ueb:double"
          "&field=DG_ms:double&field=DG_us:double&field=DG_ks:double&field=DW_Phase:integer"
          "&field=DW_Phase_abc:string(1)")


def template_layer(qgs_root, name, tmp_dir):
    """Load the style of a template layer onto an in-memory layer (via a temporary .qml)"""
    ml = [m for m in qgs_root.iter("maplayer") if m.findtext("layername") == name][0]
    qml = ET.Element("qgis", {"version": qgs_root.get("version"), "styleCategories": "AllStyleCategories"})
    for k in ("labelsEnabled", "hasScaleBasedVisibilityFlag", "minScale", "maxScale", "simplifyDrawingHints",
              "simplifyLocal", "simplifyDrawingTol", "simplifyMaxScale", "simplifyAlgorithm"):
        if ml.get(k) is not None:
            qml.set(k, ml.get(k))
    for child in ml:
        qml.append(child)
    qml_path = os.path.join(tmp_dir, name.replace(" ", "_") + ".qml")
    ET.ElementTree(qml).write(qml_path, encoding="utf-8", xml_declaration=False)

    layer = QgsVectorLayer("Polygon?crs=EPSG:2056&" + FIELDS, name, "memory")
    msg, ok = layer.loadNamedStyle(qml_path)
    if not ok:
        raise RuntimeError(f"Could not load style of '{name}': {msg}")
    return layer


def main():
    with zipfile.ZipFile(TEMPLATE) as z:
        qgs_root = ET.fromstring(z.read([n for n in z.namelist() if n.endswith(".qgs")][0]))

    with tempfile.TemporaryDirectory() as tmp_dir:
        layer_dw = template_layer(qgs_root, LAYER_DW, tmp_dir)
        layer_abc = template_layer(qgs_root, LAYER_ABC, tmp_dir)

        root = QgsRuleBasedRenderer.Rule(None)

        # DW_Phase classes (incl. the template's legend-only text entries, which never match)
        group_dw = QgsRuleBasedRenderer.Rule(None, 0, 0, "", "Dauerwaldphase / phase de conversion")
        for cat in layer_dw.renderer().categories():
            value = str(cat.value())
            expr = "ELSE" if value in ("", "NULL") else f'"DW_Phase" = {value}'
            rule = QgsRuleBasedRenderer.Rule(cat.symbol().clone(), 0, 0, expr, cat.label())
            rule.setActive(cat.renderState())
            group_dw.appendChild(rule)
        root.appendChild(group_dw)

        # a/b/c hatching on top
        group_abc = QgsRuleBasedRenderer.Rule(None, 0, 0, "", "Zusatz a/b/c")
        for cat in layer_abc.renderer().categories():
            value = str(cat.value())
            if value not in ABC_SKIP_PHASE:
                continue
            expr = f'"DW_Phase_abc" = \'{value}\' AND "DW_Phase" <> {ABC_SKIP_PHASE[value]}'
            rule = QgsRuleBasedRenderer.Rule(cat.symbol().clone(), 0, 0, expr, cat.label())
            rule.setActive(cat.renderState())
            group_abc.appendChild(rule)
        root.appendChild(group_abc)

        layer_dw.setRenderer(QgsRuleBasedRenderer(root))
        msg, ok = layer_dw.saveNamedStyle(str(OUT_QML))
        if not ok:
            raise RuntimeError(f"Could not save {OUT_QML}: {msg}")
        print(f"Wrote {OUT_QML}")


if __name__ == "__main__":
    QgsApplication.setPrefixPath("C:/OSGeo4W/apps/qgis-ltr", True)
    qgs = QgsApplication([], False)
    qgs.initQgis()
    try:
        main()
    finally:
        qgs.exitQgis()
    sys.exit(0)
