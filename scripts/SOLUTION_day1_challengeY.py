class drawWindow(QMainWindow):
    def __init__(self):
        """Initializing the necessary resources."""
        QMainWindow.__init__(self)

        # creating map canvas, which draws the maplayers
        # setting up features like canvas color
        self.canvas = QgsMapCanvas()
        self.canvas.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.enableAntiAliasing(True)

        # Qmainwindow requires a central widget. Canvas is placed
        self.setCentralWidget(self.canvas)

        # creating each desired action
        self.actionPan = QAction("Pan tool", self)
        self.actionDraw = QAction("Polygon tool", self)
        self.actionConnect = QAction("Connect polygon", self)
        self.actionClear = QAction("Clear", self)
        self.actionClose = QAction("Close", self)

        # these two function as on/off. the rest are clickable
        self.actionPan.setCheckable(True)
        self.actionDraw.setCheckable(True)

        # when actions are clicked, do corresponding function
        self.actionPan.triggered.connect(self.pan)
        self.actionDraw.triggered.connect(self.draw)
        self.actionClear.triggered.connect(self.clear)
        self.actionConnect.triggered.connect(self.connect)
        self.actionClose.triggered.connect(self.close)

        # toolbar at the top of the screen: houses actions as buttons

        self.toolbar = self.addToolBar("Canvas actions")
        # ensure user can't close the toolbar
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.toolbar.setMovable(False)
        # change order here to change their placement on toolbar
        self.toolbar.addAction(self.actionPan)
        self.toolbar.addAction(self.actionDraw)
        self.toolbar.addAction(self.actionConnect)
        self.toolbar.addAction(self.actionClear)
        self.toolbar.addAction(self.actionClose)

        # link action to premade map tool
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        # And the draw tool created below
        self.toolDraw = PolygonMapTool(self.canvas)
        self.toolDraw.setAction(self.actionDraw)

        # set draw tool by default
        self.draw()

    def pan(self):
        """Simply activates pan tool"""
        self.canvas.setMapTool(self.toolPan)
        # make sure the other button isn't checked to avoid confusion
        self.actionDraw.setChecked(False)

    def draw(self):
        """Activates draw tool"""
        self.canvas.setMapTool(self.toolDraw)
        self.actionPan.setChecked(False)

    def clear(self):
        self.toolDraw.reset()

    def connect(self):
        """Calls the polygon tool to connect an unconnected polygon"""
        self.toolDraw.finishPolygon()

    def showWindow(self):
        """Shows the map canvas: currently the canvas is empty,
       but a reference layer can be added to it """
        
        

        proj_layers = QgsProject.instance().mapLayers()
        self.layer = list(proj_layers.values())[0]
        #Add code here if you want to add a layer to the window
        self.canvas.setExtent(self.layer.extent())
        self.canvas.setLayers([self.layer])
        self.show()

    def closeEvent(self, event):
        """Activated anytime Mapwindow is closed either programmatically or
            if the user finds some other way to close the window. Automatically
            finishes the polygon if it's unconnected.
        """
        self.toolDraw.finishPolygon()
        points = self.getPolygon()
        if points:
            polygon = QgsGeometry.fromPolygonXY([points])
            feature = QgsFeature()
            feature.setGeometry(polygon)
            data_str = "Polygon?crs=epsg:3067"
            new_layer = QgsVectorLayer(data_str, "drawn_polygon", "memory")
            new_layer.dataProvider().addFeatures([feature])
            if new_layer.isValid():
                QgsProject.instance().addMapLayer(new_layer)
            else:
                print("Unable to create a new layer from the drawing")
            print(polygon)
            for point in points:
                print(point)
        QMainWindow.closeEvent(self, event)

    def getPolygon(self):
        return self.toolDraw.getPoints()

    def getPolygonBbox(self):
        return self.toolDraw.getPolyBbox()

class PolygonMapTool(QgsMapToolEmitPoint):
    """This class holds a map tool to create a polygon from points got by clicking
        on the map window. Points are stored in a list of point geometries, which is when finishing the polygon"""
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        # rubberband class gives the user visual feedback of the drawing
        self.rubberBand = QgsRubberBand(self.canvas, True)

        # setting up outline and fill color in RGB tuples
        self.rubberBand.setColor(QColor(4, 222, 37))
        # RGB color values, last value indicates transparency (0-255)
        self.rubberBand.setFillColor(QColor(4, 222, 77,140))
        self.rubberBand.setWidth(3)

        self.points = []
        # a flag indicating when a single polygon is finished
        self.finished = False
        self.poly_bbox = False
        self.double_click_flag = False
        self.reset()

    def reset(self):
        """Empties the canvas and the points gathered thus far"""
        self.rubberBand.reset(True)
        self.poly_bbox = False
        self.points.clear()

    def keyPressEvent(self, e):
        """Pressing ESC resets the canvas. Pressing enter connects the polygon"""
        if (e.key() == 16777216):
            self.reset()
        if (e.key() == 16777220):
            self.finishPolygon()

    def canvasDoubleClickEvent(self, e):
        """Finishes the polygon on double click"""
        self.double_click_flag = True
        self.finishPolygon()

    def canvasReleaseEvent(self, e):
        """Activated when user clicks on the canvas. Gets coordinates, draws
        them on the map and adds to the list of points."""
        if self.double_click_flag:
            self.double_click_flag = False
            return

        # if the finished flag is activated, the canvas will be reset
        # for a new polygon
        if self.finished:
            self.reset()
            self.finished = False

        self.click_point = self.toMapCoordinates(e.pos())

        self.rubberBand.addPoint(self.click_point, True)
        self.points.append(self.click_point)
        self.rubberBand.show()


    def finishPolygon(self):
        """Activated by user or when the map window is closed without connecting
            the polygon. Makes the polygon valid by making first and last point
            the same. This is reflected visually. Up until now the user has been
            drawing a line: a polygon is created and shown on the map."""
        # nothing will happen if the code below has already been ran
        if self.finished:
            return
        # connecting the polygon is valid if there's already at least 3 points
        elif len(self.points)>2:
            first_point = self.points[0]
            self.points.append(first_point)
            self.rubberBand.closePoints()
            self.rubberBand.addPoint(first_point, True)
            self.finished = True
            # a polygon is created and added to the map for visual purposes
            map_polygon = QgsGeometry.fromPolygonXY([self.points])
            self.rubberBand.setToGeometry(map_polygon)
            # get the bounding box of this new polygon
            self.poly_bbox = self.rubberBand.asGeometry().boundingBox()
        else:
            self.finished = True

    def getPoints(self):
        """Returns list of PointXY geometries, i.e. the polygon in list form"""
        self.rubberBand.reset(True)
        return self.points

myDrawWindow = drawWindow()
myDrawWindow.showWindow()