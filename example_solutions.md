# Example solutions for the tasks and challenges 

These are only one of many possible solutions

## Day 1

### Task 1

Take a look at QgsVectorLayer documentation and find out how to get the extent of the layer. What type is the returned object?

<details>
  <summary>Solution</summary>
  
```python
# print extent
print(layer.extent())
# get type of extent
print(type(layer.extent()))
```

</details>

### Task 2

Get the bounding box of each geometry. Which NUTS2 polygon's bounding box is the largest?

<details>
  <summary>Solution</summary>

```python
previous_area =  0

for feat in layer.getFeatures():
    geometry = feat.geometry()
    bbox = geometry.boundingBox()
    area = bbox.area()

    print(feat['name'], "\nBoundingBox: {0} km\nArea: {1} sqr km\n".format(bbox, 
          round(area / 1000000, 0)))
          
    if area > previous_area:
        largest_feature = feat

    previous_area = area
    
    print(largest_feature['name'], "has the largest bounding box")
```
  
</details>

### Task 3

Build another WFS request URL, create a vector layer with the URL and add the layer to the project. Choose one of Statistics Finland's services, for example [this](https://geo.stat.fi/geoserver/vaestoalue/wfs?service=WFS&version=2.0.0&request=GetCapabilities), or another service of your choice.


<details>
  <summary>Solution</summary>
  
from link, eg find a different featurename and replace it within the URL after typename:

```python
region_url = ("https://geo.stat.fi/geoserver/vaestoalue/wfs?service=WFS&version=auto&"+
            "request=GetFeature&typename=vaestoalue:suuralue_vaki2014&srsname=EPSG:3067")
region_layer = QgsVectorLayer(region_url, "suuralue_vaki2014", "WFS")

if region_layer.isValid():
    QgsProject.instance().addMapLayer(region_layer)
else:
    print("Oops, something went wrong! Is the layer path correct?")
```

</details>

### Task 4


* Play around with different tolerance levels to see how the layers change. Notice that heavy simplification leads to incorrect geometries (overlaps and gaps). This is because we simplify each geometry individually without snapping them to nearby nodes.
* Run another transformation on the geometries. Use smooth or whichever piques your interest. Notice that other algorithms use different parameters than tolerance level which we defined for simplifying.


<details>
  <summary>Solution</summary>
  

```python
#simple example for smoothening plus other things done in simplification script:

original_layer = QgsProject.instance().mapLayersByName("NUTS2_FIN_pop")[0]

# list where the features of the new layer will be gathered
smoothened_feat_list = []


# looping through features of the the layer
for input_order, feat in enumerate(original_layer.getFeatures()):
    # original geometry
    geometry = feat.geometry()
    
    # returns a new smoothened geometry
    # smoothing happens with default parameters (int = 1, offset: float = 0.25, minimumDistance: float = - 1, maxAngle: float = 180) which could be  given as variables before for loop 
    smoothened = geometry.smooth()
    
    # a list with this feature's name and population
    trimmed_attributes = [feat['name'], feat['pop']]
    
    # creating a new feature by passing a id
    feat = QgsFeature(input_order)
    # adding the new geometry and trimmed attributes to the layer
    feat.setGeometry(smoothened)
    feat.setAttributes(trimmed_attributes)

    # adding all the features to a list
    smoothened_feat_list.append(feat)

geometry_type = QgsWkbTypes.displayString(original_layer.wkbType()) # Example: Multipolygon

# taking the original layer's CRS
layer_crs = original_layer.sourceCrs().authid() # Example: EPSG:3067

path_str = '{0}?crs={1}'.format(geometry_type, layer_crs) # example: Multipolygon?crs=EPSG:3067

name_str = "Smoothened_{0}_default".format(original_layer.sourceName()) # example: Simplified_Paavo_5000

# creating the new vector layer as a temporary (memory) layer
smoothened_layer = QgsVectorLayer(path_str, name_str, "memory")
provider = smoothened_layer.dataProvider()

# add fields
provider.addAttributes([QgsField("name", QVariant.String),
                    QgsField("pop",  QVariant.Int)])
smoothened_layer.updateFields()
# adding all the features the fields
provider.addFeatures(smoothened_feat_list)

#check the layer is valid
if smoothened_layer.isValid():
    # inserting the new layer to the project
    QgsProject.instance().addMapLayer(smoothened_layer)
else:
    print("Faulty layer")
```

</details>

### Task 5

What is the median share of students (perc_students_valid) in postal code regions that have at least 30 students (pt_opisk)?


<details>
  <summary>Solution</summary>
  
```python
# this is just one approach of many
# add a filter for student population
filter_exp = '"pt_opisk" > 30' 
paavo.setSubsetString(filter_exp)

agg_exp_median = QgsAggregateCalculator.Median
paavo.aggregate(aggregate=agg_exp_median, fieldOrExpression="perc_students_valid")

# undoing filter
paavo.setSubsetString("")
```

</details>

### Challenge X: Layer styling and exporting map layouts

* Make a map with some other variable. Absolute values should normally not be used directly in a choropleth map. So, first calculate some other relative variable.
<details>
  <summary>Solution</summary>
  
```python
# Calculate the share of highly educated of population, the same way as earlier for student procentage.
# Do this rather in Python console, or only once from Python editor, not to add new column each time you try some new visualization.
degree_exp = '("ko_yl_kork" / "pt_vakiy") *100'
layer.addExpressionField(degree_exp, QgsField("degree_perc",  QVariant.Double, prec=1))
# Use "degree_perc" as thematic_field.
```

</details>

* Zoom in the map in the layout to your home area.
  
<details>
  <summary>Solution</summary>  
  
```python
# For zooming in, change map scale, for example:
map.setScale(2000000)

# Option 1 for setting the area. Use map extent from QGIS main map.
# Zoom in the map to your area and then run the script with setExtent set in this way:
map.setExtent(iface.mapCanvas().extent())
# Option 2 for setting the area. Set coordinate values manually. You can still check corner coordinates from QGIS main map.
map.setExtent(QgsRectangle(340000, 6650000, 370000, 6680000))
```

</details>
  

### Challenge Y: Playing around with a drawing tool


* The PolygonMapTool draws a polygon in the map in an eye-catching red. Find where the color is defined, figure out how it works and change the color.

* The polygon is drawn on a empty surface. Add a background layer by inserting some code to function showWindow under the class drawWindow. For example, get the first vector layer in the current QGIS project and define it as self.layer.

* Currently the program prints out the nodes of the drawn polygon. It does this by iterating a list called points, consisting of QgsPointXY's.
    * Modify the code in closeEvent to create a polygon QgsGeometry (hint: see this).
    * Create an empty QgsFeature and set the polygon as its geometry
    * Create a vector layer in memory and add the feature to it
    * Add the vector layer to the project


<details>
  <summary>Solution</summary>
  
[Script solution](https://github.com/csc-training/pyqgis/blob/main/scripts/SOLUTION_day1_challengeY.py)

</details>

## Day 2

### Task 1

Using the GUI, run Simplify algorithm, under Vector geometry. The easiest way to find it is to use the search bar.

* Change Tolerance to 5000, otherwise keep the default settings.
* Run the algorithm. It should add a new memory layer with simplified geometry to the project.

<details>
  <summary>Solution</summary>
  
![](https://i.imgur.com/PpZw72L.png)
-> Adds layer named 'Simplified'

</details>

### Task 2

Modify the script above by adding one more algorithm to the pipeline, namely Add geometry attributes

* Find out the algorithm id of Add geometry attributes.
* Create the parameter dictionary as needed for the algorithm (HINT: if you're lost, run the algorithm through the GUI first)
* Add the algorithm call to the end of the script and modify the previous algorithm call accordingly.

<details>
  <summary>Solution</summary>

```python

# find algorithm ID of Add geometry attributes
for alg in QgsApplication.processingRegistry().algorithms():
    search_str = "add geometry attributes"
    if search_str in alg.displayName().lower():
        print(alg.displayName(), "->", alg.id())

# returns qgis:exportaddgeometrycolumns , which is the algorithm id

# create parameter dictionary

parameter_dictionary = {'INPUT': remaining_fields ,'CALC_METHOD':1,'OUTPUT':'TEMPORARY_OUTPUT'}


## add to rest of process:
                        
# YOUR path to the NUTS2 layer
input_layer_path = 'C:/Users/tatu/pyqgis_practical/data/practical_data.gpkg|layername=NUTS2_FIN_pop'

input_layer = QgsVectorLayer(input_layer_path, "input_layer", "ogr")

tolerance = 5000
# list of field names to keep
fields_to_keep = ['name', 'pop']

# get all fields
all_fields = input_layer.fields().names()

# BASICALLY: create a list containing all fields except those that are in the "keep" list
drop_fields = [field for field in all_fields if field not in fields_to_keep]

simplified_layer = processing.run("native:simplifygeometries", 
              {'INPUT':input_layer,
               'METHOD':0,
               'TOLERANCE':tolerance,
               'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'] # NOTICE THAT THE LAYER IS IMMEDIATELY FETCHED FROM THE DICT

remaining_fields = processing.run("qgis:deletecolumn", 
               {'INPUT':simplified_layer,
                'COLUMN':drop_fields,
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT'] 
                        
                        
processing.runAndLoadResults("qgis:exportaddgeometrycolumns", parameter_dictionary)
# -> creates 'Added geom info' layer
                 
```
  
</details>

### Task 3: Finalizing the model

* Re-create the simplify-and-trim algorithm with the graphical modeler using Simplify and Keep fields. It should look something like the pic below.
* NOTE! Use Algorithm output as the input layer for the second algorithm.
* Simplification tolerance is simply a Number input.
* To use the model click Run model button (green arrow) in upper toolbar and fill in inputs as you wish.
* If the input fields are not in logical order (fields before layer), adjust this under menu Model -> Reorder Model Inputs.


<details>
  <summary>Solution</summary>
  
![](https://i.imgur.com/1T2vEc2.png)

</details>

### Challenge X: Processing algorithm with the @alg decorator


* There's an unused output called SUM_OF_FIELD. Use aggregation (check the first day for a refresher) to get the sum of values in the given value field: append the value to the results dictionary.

* Add another algorithm of your choice after the points generation and use the points as inputs. The algorithm could for example be Buffer or Rasterize. Return both the outputs both processes. See here for an example.

<details>
  <summary>Solution</summary>
  
[Script solution](https://github.com/csc-training/pyqgis/blob/main/scripts/SOLUTION_day2_challengeX.py)

</details>
