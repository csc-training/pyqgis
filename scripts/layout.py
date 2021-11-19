# LAYER VISUALIZATION IN MAP

# Set layer name and desired paremeters
layer_name = 'Paavo'
thematic_field = 'pt_vakiy'

# Define the layout's output filepath
fn = 'C:/temp/layout_export.pdf'

classification_method = QgsClassificationQuantile()
#You can use any of these classification method classes:
#QgsClassificationQuantile()
#QgsClassificationEqualInterval()
#QgsClassificationJenks()
#QgsClassificationPrettyBreaks()
#QgsClassificationLogarithmic()
#QgsClassificationStandardDeviation()

layer = QgsProject().instance().mapLayersByName(layer_name)[0]

# Get color ramp by name (set above)
# See default_style.colorRampNames() for all options
default_style = QgsStyle().defaultStyle()
color_ramp = default_style.colorRamp('PuBu')

# Use Graduated symbology
renderer = QgsGraduatedSymbolRenderer()
renderer.setClassAttribute(thematic_field)
renderer.setClassificationMethod(classification_method)
num_classes = 5
renderer.updateClasses(layer, num_classes)
renderer.updateColorRamp(color_ramp)

# Remove outlines of polygons to keep the fill colors visible
# with small polygons
for sym in renderer.symbols(QgsRenderContext()):
    sym.symbolLayer(0).setStrokeStyle(Qt.PenStyle(Qt.NoPen))

layer.setRenderer(renderer)
layer.triggerRepaint()

# LAYOUT CREATION
# Create new layout
project = QgsProject.instance()
manager = project.layoutManager()
layoutName = 'pyqgis_test_layout'
layouts_list = manager.printLayouts()
# remove any duplicate layouts 
# (only important when running the same script several times).
for layout in layouts_list:
    if layout.name() == layoutName:
        manager.removeLayout(layout)
layout = QgsPrintLayout(project)
layout.initializeDefaults()
layout.setName(layoutName)
manager.addLayout(layout)

# Map in layout
# create map item in the layout
map = QgsLayoutItemMap(layout)
map.setRect(20, 20, 20, 20)

# Map settings for layout
map.setExtent(layer.extent())
map.setScale(65000000)
map.setBackgroundColor(QColor(200, 200, 200))
layout.addLayoutItem(map)

# Change map location and size
map.attemptMove(QgsLayoutPoint(5, 20, QgsUnitTypes.LayoutMillimeters))
map.attemptResize(QgsLayoutSize(180, 180, QgsUnitTypes.LayoutMillimeters))

# Legend in layout
legend = QgsLayoutItemLegend(layout)
legend.setTitle("Legend")
layerTree = QgsLayerTree()
layerTree.addLayer(layer)
legend.model().setRootGroup(layerTree)
layout.addLayoutItem(legend)
legend.attemptMove(QgsLayoutPoint(230, 15, QgsUnitTypes.LayoutMillimeters))

# Scalebar in layout
scalebar = QgsLayoutItemScaleBar(layout)
scalebar.setStyle('Line Ticks Up')
scalebar.setUnits(QgsUnitTypes.DistanceKilometers)
scalebar.setNumberOfSegments(2)
scalebar.setNumberOfSegmentsLeft(0)
scalebar.setUnitsPerSegment(50)
scalebar.setLinkedMap(map)
scalebar.setUnitLabel('km')
scalebar.setFont(QFont('Arial', 14))
scalebar.update()
layout.addLayoutItem(scalebar)
scalebar.attemptMove(QgsLayoutPoint(220, 190, QgsUnitTypes.LayoutMillimeters))

# Map title in layout
title = QgsLayoutItemLabel(layout)
title.setText("My Title")
title.setFont(QFont('Arial', 24))
title.adjustSizeToText()
layout.addLayoutItem(title)
title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))

## LAYOUT EXPORT
exporter = QgsLayoutExporter(layout)


#exporter.exportToImage(fn, QgsLayoutExporter.ImageExportSettings())
exporter.exportToPdf(fn, QgsLayoutExporter.PdfExportSettings())