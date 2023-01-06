# TBk QGIS Plugin
**T**oolkit zur Erarbeitung von **B**estandes**k**arten aus Fernerkundungsdaten: a simple python algorithm that builds a tree stand map, based on a vegetation height model ([TBk on planfor.ch](https://www.planfor.ch/tool/9)).


## 1 Einführung
Mit dem an der HAFL entwickelten Toolkit zur Erarbeitung von Bestandeskarten aus Fernerkundungsdaten (TBk) lassen sich Bestände automatisch aufgrund der räumlichen Verteilung der dominierenden Bäume, gekennzeichnet durch die maximale Höhe pro Are eines Vegetationshöhenmodells (VHM), abgrenzen. Pro Bestand wird die Oberhöhe (hdom), die maximale Höhe (hmax) und der Deckungsgrad (DG) der Hauptschicht ermittelt. Zusätzlich kann die Grundstruktur (gleichförmig oder ungleichförmig) der Bestände grob bestimmt sowie der Nadelholzanteil geschätzt werden. Eine Beschreibung aller Attribute findet sich am Ende dieses Dokuments. In einem Nachbearbeitungsschritt können zudem besonders dichte sowie «lückige» Teilflächen innerhalb der Bestände ausgeschieden werden.
Der gesamte Programmcode wurde als QGIS-Plugin implementiert, dessen korrekte Anwendung in diesem Dokument erläutert wird, ergänzt durch Video-Tutorials.

| | |
|-------------|----------------------------------------------------------------|
|**Resultat** | TBk Bestandeskarte mit Angaben bezüglich Oberhöhe, Deckungsgrad, Mischungsverhältnis (Laub- bzw. Nadelholzanteil) und Grundstruktur, bereitgestellt als ESRI Polygon Shapefile |
|**Datengrundlagen** | - Waldmaske: Projektperimeter als ESRI Shapefile<br/>- Vegetationshöhenmodell: Aus LiDAR-Daten mit einer Auflösung von ≤ 1 m (oder Vegetationshöhenmodell LFI, Link)<br/>- Waldmischungsgrad: Angabe zu Laub-/Nadelholz |
| **Genauigkeit** |	- Allgemein: Genauigkeit und Aktualität sind abhängig vom VHM. Primäre Fehlerquellen sind steile Nordhänge und Felsen.<br/>- Bestandesgrenzen: Die Abgrenzung ist auf ca. 10-20 m genau und die minimale Bestandesgrösse beträgt standardmässig 10 Aren.<br/>- Nadelholzanteil: Die Gesamtgenauigkeit beträgt ca. 95%. |
| **Kontakt** | Hannes Horneber (HAFL), hannes.horneber@bfh.ch |


## 2 Installation QGIS Plugin
Das Plugin erfordert die QGIS Version 3.10 oder höher. Ausserdem muss zwangsläufig die QGIS Version «Desktop with GRASS» verwendet werden (beim Download von QGIS werden automatisch immer 2 Versionen erstellt, «QGIS Desktop» und «QGIS Desktop with Grass»). 

Das Plugin muss zunächst als ZIP-Datei lokal abgespeichert und diese dann in QGIS importiert werden. Das zugehörige Video «TBk_plugin_install» erläutert das Vorgehen.

Das Plugin enthält 4 Funktionen: TBk prepare MG und TBk prepare VHM zur Vorbereitung der Inputdaten, TBk generation für die Generierung der Bestandeskarte, und TBk postprocess local density für die Ausscheidung von besonders dichten oder «lückigen» Teilflächen pro Bestand im Nachgang.

Um Probleme zu vermeiden wird empfohlen, das Plugin lokal laufen zu lassen, d.h. Input- und Output-Daten nicht auf einem Share Laufwerk zu speichern.


## 3 Vorbereitung Inputdaten
Die Inputdaten müssen zwingend gewisse Bedingungen erfüllen und ggf. vorher bearbeitet werden. Die notwendigen Schritte werden in diesem Abschnitt erläutert. Sie sollten unbedingt in der hier aufgeführten Reihenfolge durchgeführt werden.
Als Inputdaten werden benötigt:
•	Projektperimeter als ESRI Shapefile (« Waldmaske »)
•	Vegetationshöhenmodell (VHM) als Raster mit Auflösung ≤ 1m
•	Waldmischungsgrad (WMG) (optional)
Die Input-Daten müssen nicht zwangsläufig im selben Koordinatensystem gespeichert sein, es wird aber dazu geraten, vor Beginn alle Input-Daten in das gleiche Koordinatensystem zu projizieren. In jedem Fall müssen alle Input-Daten unbedingt korrekt projiziert sein, d.h. es dürfen auf keinen Fall Fehler in der Projizierung vorliegen. Auch Leerwerte müssen korrekt definiert sein.

### 3.1. Fehlerüberprüfung Projektperimeter
Der Projektperimeter sollte als ein einziges Shapefile vorliegen, welches das gesamte Waldgebiet abdeckt (ausschliesslich Wald).
Es ist zwingend notwendig, dass keine Geometrie- oder Topologiefehler vorliegen (z.B. doppelte Knoten, Überlappungen, Lücken, …), ansonsten stoppt der TBk Algorithmus und es kann kein Resultat erzeugt werden. Deshalb sollte die Shape-Datei unbedingt zunächst auf derartige Fehler überprüft und diese ggf. behoben werden. Die Gefahr für Topologiefehler besteht insbesondere bei kleinteiligen Multi-Polygonen (z.B. wenn Forstwege aus dem Projektperimeter ausgenommen sind).
In QGIS gibt es dafür die Standard-Werkzeuge Gültigkeit prüfen und Geometrien reparieren, sowie für eine detaillierte und differenziertere Überprüfung das Kern-Plugin Geometrien prüfen. Viele einfachere Fehler lassen sich schon mithilfe der beiden genannten Standard-Werkzeuge beheben. Die Verwendung wird im Video «TBk_preprocessing» kurz dargestellt.

### 3.2. Vorbereitung Vegetationshöhenmodell
Das VHM sollte in einer Auflösung von ≤ 1m vorliegen und den gesamten Projektperimeter abdecken. Der TBk-Algorithmus benötigt jedoch als Input eine auf den Projektperimeter zugeschnittene, auf 10x10m aggregierte Version, sowie eine 150x150cm Version des VHM.
Das QGIS Plugin enthält eine Funktion TBk prepare VHM, welche diese Schritte automatisiert ausführt und die benötigten Dateien generiert. Die Verwendung wird im Video «TBk_preprocessing» erläutert.
Falls das Skript mehrmalig ausgeführt wird, werden die bereits vorhandenen Output-Daten eigentlich automatisch gelöscht, da sie nicht überschrieben werden können. Das funktioniert aber nicht einwandfrei, falls die Daten noch irgendwo geöffnet sind. Zur Sicherzeit wird deshalb empfohlen, vor einem erneuten Durchlauf entweder die bereits generierten Output-Daten manuell zu löschen oder einen anderen Speicherort/Dateinamen anzugeben.

### 3.3. Vorbereitung Waldmischungsgrad-Raster
Die Verwendung eines Waldmischungsgrad-Rasters ist optional, wird aber empfohlen. Falls es verwendet wird, benötigt der TBk-Algorithmus als Input ein Raster mit Werten von 0 und 100, welche den Nadelholzanteil in Prozent pro Pixel beschreiben. Das Raster sollte den gesamten Projektperimeter abdecken.
Die Funktion TBk prepare MG des QGIS Plugins übernimmt die erforderliche Klassifizierung, falls die Originaldatei andere Werte aufweist, und führt weitere notwendige Schritte, wie z.B. das Zuschneiden auf den Projektperimeter, automatisiert aus. 
Falls das Input-Raster schon den NH-Anteil in Werten von 0 und 100 angibt, sollte das Prepare Script dennoch ausgeführt werden, um z.B. die korrekte Ausrichtung am VHM (alignment) sicherzustellen. Das Häkchen «Reclassify MG Values» muss dann jedoch deaktiviert werden. 
Falls das Skript mehrmalig ausgeführt wird, werden die bereits vorhandenen Output-Daten eigentlich automatisch gelöscht, da sie nicht überschrieben werden können. Das funktioniert aber nicht einwandfrei, falls die Daten noch irgendwo geöffnet sind. Zur Sicherzeit wird deshalb empfohlen, vor einem erneuten Durchlauf entweder die bereits generierten Output-Daten manuell zu löschen oder einen anderen Speicherort/Dateinamen anzugeben.
Die korrekte Verwendung wird im Video «TBk_preprocessing» dargestellt.



## 4 Ausführung TBk
Der Hauptalgorithmus ist im Plugin in der Funktion TBk generation implementiert.
 
Als Input werden die von den Preprocessing-Funktionen generierten Dateien genutzt: «vhm_10m.tif», «vhm_150cm.tif», «MG» (optional) und zudem das Shapefile des Projektperimeters.
Ausserdem sollte der Speicherort für den Output festgelegt werden. Unter «Fortgeschrittene Parameter» befinden sich noch diverse Anpassungsmöglichkeiten, die aber im Normalfall nicht verändert werden müssen und sollten. 

Das Häkchen «Delete temporary files and fields» ist standardmässig gesetzt.

Achtung, falls kein MG-Raster verwendet wird, sollte das folgende Häkchen "Consider coniferous raster for classification" entfernt werden. Ebenso das Häkchen «Also calc coniferous prop. for main layer» (ganz unten in der Liste der fortgeschrittenen Parameter).

Die korrekte Ausführung wird im Video «TBk_main» dargestellt. Der Haupt-Output ist das eingangs beschriebene Bestandes-Shapefile «TBk_Bestandeskarte.shp». Zudem wird direkt eine QGIS-Projektdatei «TBk_Bestandeskarte.qgz» generiert, welche die Ergebnisse vielfältig visualisiert. Im Rahmen dieser stehen ausserdem 4 vorgefertigte, vollständige Drucklayouts (A1 und A3, jeweils Hoch- und Querformat) für die Generierung von Karten zur Verfügung.


## 5 Zusatzfunktion – Lokale Dichten
Des Weiteren verfügt das Plugin über die Zusatzfunktion TBk postprocess local density, mit dem nach der erfolgten Bestandesabgrenzung besonders dichte sowie «lückige» Teilflächen innerhalb der Bestände ausgeschieden werden können.
Wird diese Funktion ausgeführt, findet sich im generierten Output-Ordner «clumpy_results» das Bestandes-Shapefile mit den zusätzlichen Attributen «area_dense, dg_dense, area_sparse, dg_sparse, dg_other». Diese bezeichnen Fläche (area) und Deckungsgrad (dg) besonders dichter bzw. lückiger Teilfächen, sowie den Deckungsgrad der übrigen Bestandesfläche (dg_other). Zusätzlich werden die ausgegebenen Flächen jeweils als Shapefile gespeichert und können danach dem QGIS-Projekt der Bestandeskarte manuell hinzugefügt werden.
Die Ausscheidung basiert auf einem sogenannten moving window Algorithmus mit einem zirkulären mowing window mit 7m Radius. Die Mindestgrösse für ausgeschiedene dichte/lückige Flächen beträgt standardmässig 10 Aren und kann unter ‘Fortgeschrittene Parameter’ verändert werden.
 

Die korrekte Verwendung wird im Video «TBk_local_density» demonstriert.

