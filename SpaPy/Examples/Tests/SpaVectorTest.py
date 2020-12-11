############################################################################
# Test File for the Spatial (SP) libraries
#
# Copyright (C) 2020, Humboldt State University, Jim Graham
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software  Foundation, either version 3 of the License, or (at your
# option) any later  version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# A copy of the GNU General Public License is available at
# <http://www.gnu.org/licenses/>.
############################################################################

import sys  

# Open source spatial libraries
import shapely
import numpy

# SpaPy libraries
sys.path.append(".") 
import SpaPlot
import SpaVectors
import SpaView
import SpaReferencing
import SpaDensify

# Paths to files
CountriesFilePath="./Examples/Data/NaturalEarth/ne_110m_admin_0_countries.shp"

OutputFolderPath="./Examples/Temp/"

############################################################################
# STLayerVector functions
############################################################################

#########################################################################
# Informational and then save a clone

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer

TheDataset.Load(CountriesFilePath) # load the contents of the layer

print("Type: "+format(TheDataset.GetType())) # get the type of data in the dataset

print("CRS: "+format(TheDataset.GetCRS())) # return the corodinate reference system

print("NumFeatures: "+format(TheDataset.GetNumFeatures())) # get the number of features in the dataset

print("Bounds: "+format(TheDataset.GetBounds())) # get the spatial bounds of the features

NumAttributes=TheDataset.GetNumAttributes()

print("NumAttributes: "+format(NumAttributes)) # return the definitions for the attributes (this function will change in the future)

Index=0
while (Index<NumAttributes):
	print("Attribute: "+format(TheDataset.GetAttributeName(Index))+", Type: "+format(TheDataset.GetAttributeType(Index))+", Width: "+format(TheDataset.GetAttributeWidth(Index))) 
	Index+=1

# Save the result
TheDataset.Save(OutputFolderPath+"CountryClone.shp") 

#########################################################################
# Clean up the attributes

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer

TheDataset.Load(CountriesFilePath) # load the contents of the layer

# Remove some attributes
TheDataset.DeleteAttribute("ADM0_DIF")
TheDataset.DeleteAttribute("GEOU_DIF")
TheDataset.DeleteAttribute("SU_DIF")
TheDataset.DeleteAttribute("BRK_A3")

# Save the result
TheDataset.Save(OutputFolderPath+"Country_AttributesRemoved.shp") 

#########################################################################
# Delete features

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

# delete the first 10 features
Index=1
while (Index<10):
	TheDataset.DeleteFeature(0)
	Index+=1

# Save the result
TheDataset.Save(OutputFolderPath+"Country_First10gone.shp") 

#########################################################################
# Add a new feature

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

# add a square geometry in at 0,0
TheGeometry=shapely.geometry.Polygon([(-10,10), (10,10), (10,-10), (-10,-10),(-10,10)])

TheDataset.AddFeature(TheGeometry)

# Save the result
TheDataset.Save(OutputFolderPath+"Country_AddedPoly.shp") 

#########################################################################
# Remove label ranks <= 2

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

# remove all label ranks of 2 or below
LabelRanks=TheDataset.GetAttributeColumn("LABELRANK")
Selection=numpy.greater(LabelRanks,2)
TheDataset.SubsetBySelection(Selection)

# Save the result
TheDataset.Save(OutputFolderPath+"Country_LabelRanksGreaterThan2.shp") 

#########################################################################
# Attribute value functions

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer

TheDataset.Load(CountriesFilePath) # load the contents of the layer
	
# Add a new attribute
TheDataset.AddAttribute("testy","str",254,"hi")

print("Attribute: "+format(TheDataset.GetAttributeValue("ADMIN",0))) # return a single attribute in row 0

TheDataset.SetAttributeValue("testy",0,"test2") # set an attribute in row 0

# sum all of the label rank attribute values in the dataset
NumFeatures=TheDataset.GetNumFeatures()
Index=0
Sum=0
while (Index<NumFeatures):
	Sum+=TheDataset.GetAttributeValue("LABELRANK",Index)
	Index+=1
	
print("Sum of label ranks:"+format(Sum))
print("Mean of label ranks:"+format(Sum/NumFeatures))

# Save the result
TheDataset.Save(OutputFolderPath+"Country_AttributeValues.shp") 

#########################################################################
# Remove all the features except the US and then breaking it into mulitple features

print("Selecting the United States of America and breaking it into individual features for each polygon")

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

# remove all label ranks of 2 or below
Selection=TheDataset.SelectEqual("ADMIN","United States of America")
TheDataset.SubsetBySelection(Selection)

TheDataset.SplitFeatures()

# Save the result
TheDataset.Save(OutputFolderPath+"Country_US.shp") 

#########################################################################
# One layer operations
# Buffer

TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

NewLayer=TheDataset.Buffer(11) # 
NewLayer.Save(OutputFolderPath+"Buffer.shp") # save the output

# Simplify
NewLayer=TheDataset.Simplify(1) # 
NewLayer.Save(OutputFolderPath+"Simplify.shp") # save the output

# Centroid
NewLayer=TheDataset.Centroid() # 
NewLayer.Save(OutputFolderPath+"Centroid.shp") # save the output

#########################################################################
# Overlay operations

#Create the bounding polygon
Top=90
Bottom=0
Left=-180
Right=0

print("Finding the intersection, union, and difference between a polygon and the geometries")

BoundingPoly=shapely.geometry.Polygon([(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)])

NewLayer=TheDataset.Intersection(BoundingPoly) # perform an intersection on a geometry to get the new layer
NewLayer.Save(OutputFolderPath+"Intersection.shp") # save the output

NewLayer=TheDataset.Union(BoundingPoly) # perform an intersection on a geometry to get the new layer
NewLayer.Save(OutputFolderPath+"Union.shp") # save the output

NewLayer=TheDataset.Difference(BoundingPoly) # 
NewLayer.Save(OutputFolderPath+"Union.shp") # save the output

#########################################################################
# Plotting operations

if (False):
	ThePlotter=SpaPlot()
	
	ThePlotter.Plot(TheDataset)
	ThePlotter.Show()

#########################################################################
# Vector rendering operations

TheBounds=TheDataset.GetBounds()
MinX=TheBounds[0]
MinY=TheBounds[1]
MaxX=TheBounds[2]
MaxY=TheBounds[3]

TheView=SpaView.SpaView(500,500)
TheView.SetBounds(MinX,MaxX,MinY,MaxY)

TheLayer=SpaVectors.SpaLayerVector()
TheLayer.SetDataset(TheDataset)
TheLayer.Render(TheView)
TheView.Save(OutputFolderPath+"RenderedVectors.png")

############################################################################
# projection tests
############################################################################

Parameters={
	"datum":"WGS84",
	"proj":"aea",
   "lon_0":0,
    "lat_1":60,
    "lat_2":40
}
TheDataset=SpaVectors.SpaDatasetVector() #create a new layer
TheDataset.Load(CountriesFilePath) # load the contents of the layer

NewDataset=SpaDensify.Densify(TheDataset,1) # 

NewLayer=SpaReferencing.Project(CountriesFilePath,Parameters)
NewLayer.Save(OutputFolderPath+"Projected.shp")

############################################################################
# One-line operations
############################################################################
############################################################################
# Basic vector operations
############################################################################

BufferedLayer=SpaVectors.Buffer(CountriesFilePath,10)
BufferedLayer.Save(OutputFolderPath+"Buffered.shp")

NewLayer=SpaVectors.Centroid(CountriesFilePath)
NewLayer.Save(OutputFolderPath+"Centroid.shp")

NewLayer=SpaVectors.ConvexHull(CountriesFilePath)
NewLayer.Save(OutputFolderPath+"ConvexHull.shp")

NewLayer=SpaVectors.Simplify(CountriesFilePath,10)
NewLayer.Save(OutputFolderPath+"Simplify.shp")

############################################################################
# Overlay operations with a geometry
#############################################################################

# Create the bounding polygon
Top=45  
Bottom=20
Left=-125
Right=-40

BoundingPoly=shapely.geometry.Polygon([(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)])

# Crop a shapefile with a polygon 
NewLayer=SpaVectors.Intersection(CountriesFilePath,BoundingPoly) # perform an intersection on a geometry to get the new layer
NewLayer.Save(OutputFolderPath+"Intersection.shp")

# Union the shapefile with the polygon
NewLayer=SpaVectors.Union(CountriesFilePath,BoundingPoly) # perform a union on a geometry to get the new layer
NewLayer.Save(OutputFolderPath+"Union.shp") # save the output

# Find the difference between the shapefile and the polygon
NewLayer=SpaVectors.Difference(CountriesFilePath,BoundingPoly) # 
NewLayer.Save(OutputFolderPath+"Difference.shp") # save the output

print("done")

