"""
    Geometric Classification v.0.3
    =======================================
    Python script for geometric classification in QGIS
    
    Author: Denis Francisci <denis.francisci@gmail.com>, 2014-2021
    
    License
        
    Geometric Classification is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This script is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    
    References and acknowledgement:
    -------   
    Kelly Thomas: http://gis.stackexchange.com/questions/48613/how-to-apply-a-graduated-renderer-in-pyqgis/48719#48719
    Carson Farmer: http://carsonfarmer.com/2010/09/playing-around-with-classification-algorithms-python-and-qgis/
    Dent B. D. 1999, Cartography. Thematic Map Design. Fifth Edition, London.
    Conolly J., Lake M. 2006, Geographical Information Systems in Archaeology, Cambridge.
""" 

###########################SCRIPT CODE########################## 

from PyQt5.QtGui import *

def validatedDefaultSymbol( geometryType ):
    symbol = QgsSymbol.defaultSymbol( geometryType )
    if symbol is None:
        if geometryType == QGis.Point:
            symbol = QgsMarkerSymbolV2()
        elif geometryType == QGis.Line:
            symbol =  QgsLineSymbolV2 ()
        elif geometryType == QGis.Polygon:
            symbol = QgsFillSymbolV2 ()
    return symbol

def makeSymbologyForRange( layer, min , max, title, color):
    symbol = validatedDefaultSymbol( layer.geometryType() )
    symbol.setColor( color )
    range = QgsRendererRange( min, max, symbol, title )
    return range

def getValuesFromAttributeTable( layer, fieldName ):
    provider = layer.dataProvider()
    fieldIndex = provider.fieldNameIndex(fieldName)
    values = []
    for feat in layer.getFeatures():
        values.append( feat.attributes()[fieldIndex] )
    values.sort()
    return values

def arbitaryColor( amount, max ):
    color = QColor()
    color.setHsv( 240 * amount / float( max - 1 ), 255, 255 )
    return color

def makeLegend( layer, fieldName, breaks ):
    classes = len( breaks ) - 1
    rangeList = []
    for i in range( classes ):
        label = str( round(breaks[i],2) ) + " - " + str( round(breaks[i+1],2) )
        rangeList.append( makeSymbologyForRange( layer, breaks[i] , breaks[i+1], label, arbitaryColor( i, classes ) ) )
    renderer = QgsGraduatedSymbolRenderer( fieldName, rangeList )
    renderer.setMode( QgsGraduatedSymbolRenderer.Custom )
    return renderer 

def geometric(values, classes):
    _min = min(values)
    _max = max(values) + 0.00001 #temporary bug correction: without +0.00001 the max value is not rendered in map
    X = (_max / _min) ** (1 / float(classes))
    res = [_min * X**k for k in range(classes+1)]
    return res
    
def applySymbology( layer, classes, fieldName):
    values = getValuesFromAttributeTable( layer, fieldName )
    breaks = geometric(values, classes)
    renderer = makeLegend( layer, fieldName, breaks )
    layer.setRenderer( renderer )

    
#######################SET YOUR VARIABLES####################### 

targetField = 'FIELD' #type the attribute table's field to classify

classes = 6 # type the number of classes

#FOR LOADING AND CLASSIFYING A SHAPEFILE NOT YET LOADED UNCOMMENT THE FOLLOWING LINE
#layer = QgsVectorLayer( '/PATH/TO/YOUR_SHAPEFILE.shp', 'YOUR_LAYER_NAME', 'ogr')

#FOR CLASSIFYING A LOADED AND SELECTED LAYER UNCOMMENT THE FOLLOWING LINE
layer = qgis.utils.iface.activeLayer() #script runs on active layer [REMEBER to update layer with update button]

################################################################

if layer.isValid():
    applySymbology(layer, classes, targetField)
    QgsProject.instance().addMapLayers( [layer] ) 
