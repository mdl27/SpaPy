############################################################################
# Represents a spatial dataset organized as features.  Each feature as a 
# geometry and attributes (properties in the Fiona & Shapely terms).
# Basic vector transformations are also supported.
#
# The dataset contains:
# - CRS - the coordinate system for the data. TheCRS can be an EPSG code or a Proj parameter string
# - AttributeDefs - definitions of the attributes (name, datatype, precision)
# - Type - the type of vector data.  The following are supported: "Polygon", "Point","LineString","MultiPolygon","MultiPoint","MultiLineString"
#   Note that the vector functions will only create Point, MultiLineString, and MultiPolygon files
#   This is because we do not know for many transforms if the final result will be all polygons, all multipolgons or a mix of these.
#   The current solution is to promote polygon files to MultiPolygon and LineString files to MultiLineString
#
# This class uses the open source libraries Fiona for reading and writing
# shapefiles and Shapely for a number of transformations.
#
# Resources:
# Fiona docs: https://fiona.readthedocs.io/en/stable/manual.html#introduction
# Shapely docs: https://shapely.readthedocs.io/en/stable/manual.html#objects
# - https://gis.stackexchange.com/questions/97545/using-fiona-to-write-a-new-shapefile-from-scratch
# - https://github.com/Toblerity/Fiona
# this is a test test2
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
import random
import colorsys

# Open source spatial libraries
import fiona
import shapely
import math

# SpaPy libraries
from SpaPy import SpaBase

######################################################################################################
# Global Definitions
######################################################################################################

SPAVECTOR_INTERSECTION=1
SPAVECTOR_UNION=2
SPAVECTOR_DIFFERENCE=3
SPAVECTOR_SYMETRIC_DIFFERENCE=4

SPAVECTOR_TOUCHES=5
SPAVECTOR_INTERSECTS=6
SPAVECTOR_DISJOINT=7
SPAVECTOR_OVERLAPS=8
SPAVECTOR_CROSSES=9
SPAVECTOR_CONTAINS=10

######################################################################################################
# Private utility functions
######################################################################################################
def GetSegmentLength(self,X1,Y1,X2,Y2):
	"""
	Retrieves segment length for polyline with two coordinates (begining and end)

	parameters:
		X1: x-coordinates of first point
		Y1: y-coordinates of first point
		X2: x-coordinates of second point
		Y2: y-coordinate of second point
	Returns:
		length of line segment

	"""
	DX=X2-X1
	DY=Y2-Y1
	Length=math.sqrt(DX*DX+DY*DY)
	return(Length)

def _FixUpInputs(Input1,Input2):
	# What exactly does this tool do?
	"""
	Fixes up the inputs for an overlay transform.
	"""
	NumGeometries=0
	# if the first input is a geometry and the second is not, switch them
	if (isinstance(Input1, shapely.geometry.base.BaseGeometry) and (isinstance(Input1, shapely.geometry.base.BaseGeometry)==False)):
		Temp=Input1
		Input1=Input2
		Input2=Temp

	# if both inputs are a geometry, find the intersection of the geometries and return it
	if (isinstance(Input1, shapely.geometry.base.BaseGeometry) and (isinstance(Input1, shapely.geometry.base.BaseGeometry))):
		NumGeometries=2
	elif (isinstance(Input2, shapely.geometry.base.BaseGeometry)):
		Input1=SpaBase.GetInput(Input1)
		NumGeometries=1
	else:
		Input1=SpaBase.GetInput(Input1)
		Input2=SpaBase.GetInput(Input2)

	return(Input1,Input2,NumGeometries)

############################################################################
# Dataset for vector data including points, polylines, and polygons
############################################################################

class SpaDatasetVector:
	""" 
	Class to manage vector data associated with a spatial layer.
	"""
	def __init__(self):
		# below are the properties that make up a shapefile using Fiona for reading and writing from and to shapefiles
		self.TheGeometries=[]
		self.TheAttributes=[]

		self.Driver="ESRI Shapefile"
		self.Type=None
		self.AttributeDefs={}

		# Coordinate reference systems / spatial references can be in either a WKT format or a fiona CRS string.
		# The fiona CRS strings can either contain an EPSG code or a set of PROJ parameters.
		# EPSG Code
		# wkt: Well Know Text Format 
		# Proj parameters: this is a dictionary of key/value pairs where the key is the parameter and the value is, well, the value
		# Which ever of these are set, will be written to the file on a save.  Only one should be set at any given time.
		self.CRS="epsg:4326"
		self.crs_wkt=None
		#self.ProjParameters=None

	############################################################################
	# Prviate functions
	############################################################################
	def GetDefaultValue(self,Attribute):
		"""
		Retrieves the default value for the selected attribute

		Parameters:
			Attribute: insert desired attribute here
		Returns:
			Default value
		"""
		TypeString=self.AttributeDefs[Attribute]
		Tokens=TypeString.split(":")
		Type=Tokens[0]

		Default=None
		if (Type=="int"): Default=0
		elif (Type=="float"): Default=0.0
		elif (Type=="str"): Default=""
		return(Default)

	def _AddGeometries(self,TheGeometry,TheAttributes,NewGeometries,NewAttributes):
		"""
		Adds a geometry and a list of attributes to the existing geometries and attributes

		Parameters:
			TheGeometry: Input current geometry in format [(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)]
			TheAttributes: Input current attributes
			NewGeometries: Input desired geometries in format [(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)]
			NewAttributes: Input desired attributes
		Returns:
			none

		"""

		if (TheGeometry!=None):
			# take the appropriate action based on the type of geometry
			TheType=TheGeometry.geom_type
			if ((TheType=="Polygon") or (TheType=="Point") or (TheType=="LineString")):
				NewGeometries.append(TheGeometry)
				NewAttributes.append(TheAttributes)
			elif ((TheType=="MultiPolygon") or (TheType=="MultiPoint") or (TheType=="MultiLineString")):
				for ThePolygon in TheGeometry:
					NewGeometries.append(ThePolygon)
					NewAttributes.append(TheAttributes)
			elif (TheType=="GeometryCollection"): # collections are typically empty for shapefiles
				for TheSubGeometry in TheGeometry:
					self._AddGeometries(TheSubGeometry,TheAttributes,NewGeometries,NewAttributes)
			else:
				print("Unsupported Type: "+TheType)
	############################################################################
	# Functions to interact with files (shapefiles and CSVs)
	############################################################################
	from shapely import speedups
	speedups.disable()

	def Load(self,FilePath):
		"""
		Function to load data from a path

		Parameters:
			FilePath: Path to the vector file 
		Results:
			none
		"""	
		TheShapefile=fiona.open(FilePath, 'r')

		self.CRS=TheShapefile.crs
		self.crs_wkt=TheShapefile.crs_wkt
		self.Driver=TheShapefile.driver
		self.Type=TheShapefile.schema["geometry"]
		self.AttributeDefs=TheShapefile.schema["properties"]

		GeometryIndex=0
		for TheFeature in TheShapefile:
			ShapelyGeometry=None
			if (TheFeature['geometry']!=None):
				ShapelyGeometry = shapely.geometry.shape(TheFeature['geometry']) # Converts coordinates to a shapely feature

			self.TheGeometries.append(ShapelyGeometry)
			self.TheAttributes.append(TheFeature['properties'])
			GeometryIndex+=1

		TheShapefile.close()

	def CopyMetadata(self,OtherLayer):
		"""
		Copies the metadata from another dataset into this one.  This includes coping
		the CRS, Type, and Attribute Defniitions.

		Parameters:
			OtherLayer: Another SpaDatasetVector object from which to copy metadata.
		Returns:
			none
		"""	
		self.CRS=OtherLayer.CRS
		self.crs_wkt=OtherLayer.crs_wkt
		self.Driver=OtherLayer.Driver
		self.Type=OtherLayer.Type
		self.AttributeDefs=OtherLayer.AttributeDefs

	def Save(self,FilePath):
		"""
		Saves this dataset to a file.

		Parameters:
			FilePath: Path to file where dataset is to be saved
		Returns:
		        none
		"""	
		TheSchema={"geometry":self.Type,"properties":self.AttributeDefs}

		TheCRS=self.CRS
		if (isinstance(TheCRS,int)): TheCRS={'init': 'epsg:'+format(TheCRS), 'no_defs': True} # integer must be an EPSG Code
		elif (self.crs_wkt!=None): TheCRS=self.crs_wkt
		elif (isinstance(TheCRS,str)):
			Temp=TheCRS.lower()
			Index=Temp.find("epsg")
			if (Index!=-1): # need to pull the EPSG code, otherwise, the string may already be a proj4 string
				Temp=Temp[Index+5:]
				TheCRS={'init': 'epsg:'+format(Temp), 'no_defs': True}
		else: # Should be a spatial reference object
			TheCRS=TheCRS.to_proj4()

		TheOutput=fiona.open(FilePath,'w',  encoding='utf-8',crs=TheCRS, driver=self.Driver,schema=TheSchema) # jjg - added encoding to remove warning on Natural Earth shapefiles

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures):
			TheGeometry=self.TheGeometries[FeatureIndex]

			if (TheGeometry!=None):
				FionaGeometry=shapely.geometry.mapping(TheGeometry) # converts shapely geometry back to a dictionary
				TheAttributes=self.TheAttributes[FeatureIndex]

				if (FionaGeometry["type"]=="GeometryCollection"): 
					Test=None # do nothing
				else:
					TheOutput.write({'geometry': FionaGeometry, 'properties':TheAttributes})

			FeatureIndex+=1

		TheOutput.close()
	############################################################################
	# General Information functions
	############################################################################
	def GetType(self):
		"""
		Gets the type of data stored in this dataset.  

		Parameters:
			none
		Returns:
			One of the OGC standard vector data types: "Polygon","Point","LineString",
			"MultiPolygon","MultiPoint","MultiLineString","GeometryCollection"
		"""	
		return(self.Type)

	def SetType(self,Type):
		"""
		Sets the type of data stored in this dataset.  The type can only be set when
		the object does not contain data.

		Parameters:
			Type: One of the OGC standard vector data types: "Polygon","Point","LineString",
		             "MultiPolygon","MultiPoint","MultiLineString","GeometryCollection"
		Returns:
			none
		"""	
		if (Type=="Polygon"): Type="MultiPolygon"
		if (Type=="LineString"): Type="MultiLineString"

		if (len(self.TheGeometries)>0): raise Exception("Sorry, you cannot set the type after a dataset contains data")
		self.Type=Type

	def GetCRS(self):
		"""
		Gets the CRS for this dataset. 

		Parameters:
			none
		Returns:
			The CRS is returned as a string but may contain an EPSG number or a proj4 command string (see https://proj4.org/)
		"""	
		return(self.CRS)

	def SetCRS(self,CRS):
		"""
		Sets the CRS for this dataset. 

		Parameters:
			Currently, this must be compatible with GDAL CRS specifications.
		Returns: 
			none
		"""	
		self.CRS=CRS
		self.crs_wkt=None

	############################################################################
	# Attribute management
	############################################################################
	def GetNumAttributes(self):
		"""
		Gets the number of columns of attributes for this dataset.

		Parameters:
			none
		Returns:
			The number of columns of attributes.
		"""	
		return(len(self.AttributeDefs))

	def GetAttributeName(self,Index):
		"""
		Returns the name of the attribute column specified by the index.

		Parameters:
			Index: Index of the column starting at 0.
		Returns:
			The name of an attribute column
		"""	
		Thing=list(self.AttributeDefs.keys())
		return(Thing[Index])

	def GetAttributeType(self,Index):
		"""
		Returns the type of attribute in the specified column.

		Prameters:
			Index: Index of the column starting at 0.
		Returns:
			Type of column, options include "int","float","str"
		"""	
		Thing=list(self.AttributeDefs.keys())
		Key=Thing[Index]
		Value=self.AttributeDefs[Key]
		Tokens=Value.split(":")
		return(Tokens[0])

	def GetAttributeWidth(self,Index):
		"""
		Returns the width of the attribute (i.e. precision).

		Parameters:
			Index: Index of the column starting at 0.
		Returns:
			The width of the attribute.  See AddAttribute() for more information.
		"""	
		Thing=list(self.AttributeDefs.keys())
		Key=Thing[Index]
		Value=self.AttributeDefs[Key]
		Tokens=Value.split(":")
		return(Tokens[1])

	def AddAttribute(self,Name,Type,Width=None,Default=None):
		"""
		Adds an attribute column to the dataset.

		Parameters:
			Name: 
				Name of the attribute to create
			Type: 
				Type of column, options include "int","float","str"
			Width: 
				Width,precision of the attribute.  For strings this is the number of
				characters, for integers is the number of digits, for floats this is
				a floating point value with the number of digits before the decimal
				and the factional portion containing the number of digits after the decimal
				(e.g. 10.2 would be 10 digits before the decimal and 2 digits after).
			Default:
				Default value for the columns 
		Returns: 
			none
		"""
		if (Default==None):
			if (Type=="int"): Default=0
			elif (Type=="float"): Default=0.0
			elif (Type=="str"): Default=""

		if (Width==None):
			if (Type=="int"): Width=4
			elif (Type=="float"): Width=16.6
			elif (Type=="str"): Width=254

		self.AttributeDefs[Name]=Type+":"+format(Width)
		for Row in self.TheAttributes:
			Row[Name]=Default

	def GetAttributeColumn(self,Name):
		"""
		Returns an entire column of attribute values.

		Parameters:
			Name: Name of the attribute to return

		Returns:
			List with the values from the attribute column
		"""
		Result=[]
		for Row in self.TheAttributes:
			Result.append(Row[Name])
		return(Result)

	def SelectEqual(self,Name,Match):
		"""
		Returns a selection array with the rows that have the specified
		attribute value matching the "Match" value

		Parameters:
			Name: Name of the attribute to compare to
			Match: Value to match to the attribute values.
		Returns:
			List of boolean values with True where the condition is true and False otherwise.
		"""
		Result=[]
		for Row in self.TheAttributes:
			if (Row[Name]==Match): Result.append(True)
			else: Result.append(False)
		return(Result)

	def SelectGreater(self,Name,Match):
		"""
		Returns a selection array with the rows that have the specified
		attribute value greater than the "Match" value

		Parameters:
			Name: Name of the attribute to compare to
			Match: Value to match to the attribute values.

		Returns:
			List of boolean values with True where the condition is true and False otherwise.
		"""
		Result=[]
		for Row in self.TheAttributes:
			if (Row[Name]>Match): Result.append(True)
			else: Result.append(False)
		return(Result)

	def SelectGreaterThanOrEqual(self,Name,Match):
		"""
		Returns a selection array with the rows that have the specified
		attribute value greater than or equal to the "Match" value

		Parameters:
			Name: Name of the attribute to compare to
			Match: Value to match to the attribute values.

		Returns:
			List of boolean values with True where the condition is true and False otherwise.
		"""
		Result=[]
		for Row in self.TheAttributes:
			if (Row[Name]>=Match): Result.append(True)
			else: Result.append(False)
		return(Result)

	def SelectLess(self,Name,Match):
		"""
		Returns a selection array with the rows that have the specified
		attribute value less than the "Match" value

		Parameters:
			Name: Name of the attribute to compare to
			Match: Value to match to the attribute values.

		Returns:
			List of boolean values with True where the condition is true and False otherwise.
		"""
		Result=[]
		for Row in self.TheAttributes:
			if (Row[Name]<Match): Result.append(True)
			else: Result.append(False)
		return(Result)

	def SelectLessThanOrEqual(self,Name,Match):
		"""
		Returns a selection array with the rows that have the specified
		attribute value that is less than or equal to the specied match value.

		Parameters:
			Name: Name of the attribute to compare to
			Match: Value to match to the attribute values.

		Returns:
			List of boolean values with True where the condition is true and False otherwise.
		"""
		Result=[]
		for Row in self.TheAttributes:
			if (Row[Name]<=Match): Result.append(True)
			else: Result.append(False)
		return(Result)

	def SubsetBySelection(self,Selection):
		"""
		Removes any features that do not have a True value (>0) in the Selection array.

		Parameters:
			Selection: List containing True and False values for each row/feature in the dataset.
		Returns:
			none
		"""
		NewGeometries=[]
		NewAttributes=[]
		Row=0
		while (Row<self.GetNumFeatures()):
			if (Selection[Row]):
				NewGeometries.append(self.TheGeometries[Row])
				NewAttributes.append(self.TheAttributes[Row])
			Row+=1
		self.TheGeometries=NewGeometries
		self.TheAttributes=NewAttributes

	def DeleteAttribute(self,Name):
		"""
		Deletes the specified column of attributes

		Parameters:
			Name: Name of the attribute column to delete.
		Returns:
			none
		"""
		del(self.AttributeDefs[Name])
		for Row in self.TheAttributes:
			del (Row[Name])

	def GetAttributeValue(self,AttributeName,Row):
		"""
		Returns the attribute value in the specified column and for the specified row/feature.

		Parameters:
			AttributeName: Name of the attribute column to look in for the value to return.
			Row: Index to the row/feature that contains the desired attribute value.
		Returns:
			Attribute value at the specified column and row.
		"""
		return(self.TheAttributes[Row][AttributeName])

	def SetAttributeValue(self,AttributeName,Row,NewValue):
		"""
		Sets the attribute value in the specified column and for the specified row/feature.

		Parameters:
			AttributeName: Name of the attribute column to look in for the value to return.
			Row: Index to the row/feature that contains the desired attribute value.
			NewValue: Attribute value to set at the specified column and row.
		Returns:
			none
		"""
		self.TheAttributes[Row][AttributeName]=NewValue

	############################################################################

	def SplitFeatures(self):
		"""
		Breaks up any multi geometry features (MultiPoint, MultiLine, MultiPolygon)
		into individual features.

		Parameters:
			none
		Returns: 
			none
		"""
		NewGeometries=[]
		NewAttributes=[]
		Row=0
		while (Row<self.GetNumFeatures()):
			TheGeometry=self.TheGeometries[Row]
			TheAttributes=self.TheAttributes[Row]
			self._AddGeometries(TheGeometry, TheAttributes, NewGeometries, NewAttributes)
			Row+=1

		# This is one case where we end up with a shapefile composed of individual polygons, points, or linestrings as shapes
		if (len(NewGeometries)>0): self.Type=NewGeometries[0].geom_type

		# Save the new geometries and attributes as the current ones
		self.TheGeometries=NewGeometries
		self.TheAttributes=NewAttributes

	############################################################################
	# Feature management
	############################################################################
	def GetNumFeatures(self):
		"""
		Gets the number of features/rows in the dataset.

		Parameters: 
			none
		Returns:
			number of features in dataset
		"""
		return(len(self.TheGeometries))

	def DeleteFeature(self,Row):
		"""
		Deletes the specified row/feature.  This will delete the geometries and the attributes.

		Parameters:
			Row: The row to delete. 
		Returns:
			none
		"""
		self.TheGeometries.pop(Row)
		self.TheAttributes.pop(Row)

	def AddFeature(self,TheGeometry,TheAttributes=None):
		"""
		Adds a new feature to the dataset including a new geometry and a new set of attributes.

		Parameters:
			TheGeometry: The shapely geometry to add to the dataset formatted as list of coordinates es: [(x1,y1), (x2,y2), (x3,y3), (x4,y4),(x5,y5)]
			TheAttributes: The new attributes to add.  If unspecified, default attribuets will be added.
		Returns:
			none

		"""

		if (self.Type==None): 
			self.SetType(TheGeometry.geom_type)

		# By default, we only support 
		if (TheGeometry.geom_type!=self.Type): 
			if (TheGeometry.geom_type=="Polygon"): TheGeometry=shapely.geometry.MultiPolygon([TheGeometry])
			elif (TheGeometry.geom_type=="LineString"): TheGeometry=shapely.geometry.MultiLineString([TheGeometry])
			else:
				raise Exception("The geometry does not match the specified type of "+format(self.Type))

		self.TheGeometries.append(TheGeometry)

		if (TheAttributes==None):
			TheAttributes={}

			for Attribute in self.AttributeDefs:
				Default=self.GetDefaultValue(Attribute)
				TheAttributes[Attribute]=Default

		self.TheAttributes.append(TheAttributes)

	def GetGeometry(self,Index):
		"""
		Returns the shapely geometry for the specified feature

		Parameters:
			Index: Index of feature of which geometry is to be calculated
		Returns:
			Shapely geometry for the feature.
		"""
		return(self.TheGeometries[Index])

	############################################################################
	# 
	############################################################################
	def GetFeatureArea(self,FeatureIndex):
		"""
		Returns with the area of the Feature.

		Parameters:
			FeatureIndex: Index representing figure to be calculated
		Returns:
			Area of feature
		"""		
		TheGeometry=self.TheGeometries[FeatureIndex]
		return(TheGeometry.area)

	def GetFeatureBounds(self,FeatureIndex):
		"""
		Returns the spatial bounds of the feature

		Parameters:
			FeatureIndex: Index of the desired feature
		Returns:
			spatial bounds of the feature
		"""
		TheGeometry=self.TheGeometries[FeatureIndex]
		return(TheGeometry.bounds)

	def GetFeatureLength(self,FeatureIndex):
		"""
		Returns with the length of the Feature.

		Parameters:
			FeatureIndex: Index of feature of which length is to be calculated
		Returns:
			Length of feature
		"""				
		TheGeometry=self.TheGeometries[FeatureIndex]
		return(TheGeometry.length)

	def IsFeatureEmpty(self,FeatureIndex):
		"""
		Returns True if the feature does not contain any coordinates

		Parameters:
			FeatureIndex: Index of desired feature
		Returns:
			True if feature does not contain any coordinates
		"""			
		TheGeometry=self.TheGeometries[FeatureIndex]
		return(TheGeometry.is_empty)

	def IsFeatureValid(self,FeatureIndex):
		"""
		Returns True if the feature contains a valid geometry (e.g. no overlapping segments)

		Parameters:
			FeatureIndex: 
				Index of desired feature
		Returns:
			True if feature contains valid geometry
		"""			
		TheGeometry=self.TheGeometries[FeatureIndex]
		return(TheGeometry.is_valid)

	############################################################################
	# 
	############################################################################
	def GetBounds(self):
		""" 
		Finds the bounds for all the features in the layer 

		Parameters:
			none
		Returns:
			tuple with (minx, miny, maxx, maxy)  
		"""

		NumFeatures=self.GetNumFeatures()

		MinX=None
		MinY=None
		MaxX=None
		MaxY=None

		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]
			TheBounds=TheGeometry.bounds

			if ((MinX==None) or (TheBounds[0]<MinX)): MinX=TheBounds[0]
			if ((MinY==None) or (TheBounds[1]<MinY)): MinY=TheBounds[1]
			if ((MaxX==None) or (TheBounds[2]>MaxX)): MaxX=TheBounds[2]
			if ((MaxY==None) or (TheBounds[3]>MaxY)): MaxY=TheBounds[3]

			FeatureIndex+=1
		return((MinX,MinY,MaxX,MaxY))

	############################################################################
	# Single layer transform functions
	# All these functions operate on the data in this layer but return
	# new layers
	############################################################################

	def Buffer(self,Amount):
		""" 
		Buffers this dataset by the specified amount (in dataset reference units) and returns a new layer with the buffered features 

		Parameters:
			Amount: Distance, in the datasets reference units, to buffer the data
		Returns:
			Buffered SpaDatasetVector object
		"""
		NewLayer=SpaDatasetVector()
		NewLayer.CopyMetadata(self)
		NewLayer.Type="MultiPolygon"

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]
			NewGeometry=None
			try:
				NewGeometry = TheGeometry.buffer(Amount)
			except Exception as TheException:
				# Shapely can have errors like: "TopologyException: No forward edges found in buffer subgraph" so they are filtered out here
				print("Sorry, an error has occurred: "+format(TheException))

			if (NewGeometry!=None):
				NewLayer.AddFeature(NewGeometry,self.TheAttributes[FeatureIndex])

			FeatureIndex+=1
		return(NewLayer)

	def Simplify(self,Tolerance, PreserveTopology=True):
		"""
		Simply the specified vector data (i.e. remove pixels) until the specified tolerance is reached.
		Larger values of tolerance produce simpler vectors while smaller values create more complex vectors.

		Parameters:
		        Tolerance: 
				Distance below which features will be simplified.
			PreserveTopology: 
				True to maintain the relationships between features that are touching (i.e. sharing boundaries).

		Returns:
			New dataset with the simplified data
		"""
		NewLayer=SpaDatasetVector()
		NewLayer.CopyMetadata(self)
		NewLayer.SetType(None)

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]
			TheGeometry = TheGeometry.simplify(Tolerance,PreserveTopology)
			NewLayer.AddFeature(TheGeometry,self.TheAttributes[FeatureIndex])

			FeatureIndex+=1
		return(NewLayer)

	def ConvexHull(self):
		"""
		Find the simplest polygon that surounds each feature without having any concave segments.

		Parameters:
			none
		Returns:
			New SpaLayerVector object  with the simplified data
		"""
		NewLayer=SpaDatasetVector()
		NewLayer.CopyMetadata(self)
		NewLayer.SetType(None)

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]
			TheGeometry = TheGeometry.convex_hull
			NewLayer.AddFeature(TheGeometry,self.TheAttributes[FeatureIndex])

			FeatureIndex+=1
		return(NewLayer)

	def Centroid(self):
		"""  
		Convert the features in the specified data set to points that are at the centroid (center of gravity)
		of each feature.

		Parameters:  
			none
		Returns:
			SpaDatasetVector object with centroids of each feature
		"""
		NewLayer=SpaDatasetVector()
		NewLayer.CopyMetadata(self)
		NewLayer.SetType("Point")

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]
			#print(TheGeometry.geom_type)
			TheGeometry = TheGeometry.centroid
			NewLayer.AddFeature(TheGeometry,self.TheAttributes[FeatureIndex])

			FeatureIndex+=1
		return(NewLayer)

	############################################################################
	# Overlay transform functions
	# All these functions operate on the data in this layer but return
	# new layers
	############################################################################
	def OverlayGeometryWithGeometry(self,TheGeometry,TheTarget,TheOperation):
		"""
		Perform a low-level overlay operation between two geometries

		Parameters:
			TheGeometry:
				object geometry OR an SpaDatasetVector object
			TheTarget: 
				SpaDatasetVector object
			TheOperation: 
				type of operation to be executed (SPAVECTOR_INTERSECTION, SPAVECTOR_UNION, 
				SPAVECTOR_DIFFERENCE, SPAVECTOR_SYMETRICDIFFERENCE)
		Returns:
			A SpaDatasetVector object representint the overlay between TheTarget and TheGeometry
		"""
		Result=None

		if (TheGeometry!=None):

			#print("TheGeometry valid="+format(TheGeometry.is_valid))
			#print("TheTarget valid="+format(TheTarget.is_valid))

			if (TheGeometry.is_valid):
				if (TheOperation==SPAVECTOR_INTERSECTION):
					Result = TheGeometry.intersection(TheTarget)	
				elif (TheOperation==SPAVECTOR_UNION):
					Result = TheGeometry.union(TheTarget)	
				elif (TheOperation==SPAVECTOR_DIFFERENCE):
					Result = TheGeometry.difference(TheTarget)	
				elif (TheOperation==SPAVECTOR_SYMETRICDIFFERENCE):
					Result = TheGeometry.symmetric_difference(TheTarget)	
				else:
					raise("Sorry, "+TheOperation+" is not supported for overlays")
			else:
				Result=None # don't return an invalid geometry

		return(Result)

	def OverlayWithGeometry(self,TheTarget,TheOperation,NewDataset):

		"""
		Performs an overlay operation between SpaDatasetVector object and and TheTarget geometry.  The result
		will be added to NewDataset.

		Parameters:
			TheTarget: Object geomerty formatted as a tuple ex: ([(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)])
			TheOperation: type of operation to be executed 
			NewDataset: The SpaDatasetVector object
		Returns:
			none
		"""
		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]

			NewGeometry=self.OverlayGeometryWithGeometry(TheGeometry, TheTarget,TheOperation)

			if (NewGeometry!=None) and (NewGeometry.is_empty==False) and (NewGeometry.is_valid):
				NewDataset.AddFeature(NewGeometry,self.TheAttributes[FeatureIndex])

			FeatureIndex+=1

	def OverlayWithDataset(self,TheTarget,TheOperation,NewDataset):
		"""
		Performs an overlay operation between this dataset and another dataset.
		Parameters:
			TheTarget: SpaDatasetVector object to be used in overlay
			TheOperation: type of operation to be executed 
			NewDataset: SpaDatasetVector object to be overlaid
		Returns:
			A SpaDatasetVector object 

		"""
		NumFeatures=TheTarget.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=TheTarget.TheGeometries[FeatureIndex]

			# overlay this geometry with each feature in this dataset
			TheGeometry = self.OverlayWithGeometry(TheGeometry,TheOperation,NewDataset)

			FeatureIndex+=1

	def Overlay(self,TheTarget,TheOperation):
		"""
		Overlay this dataset with a geometry or another dataset

		Parameters:
			TheTarget: SpaDatasetVector object
			TheOperation: type of operation to be executed (Union, intersection, difference, symmetric difference)
		Returns:
			A SpaDatasetVector object
		"""
		NewDataset=SpaDatasetVector()
		NewDataset.CopyMetadata(self)
		NewDataset.SetType(None) # we do not know what the resulting type will be until the first transform is complete

		if (isinstance(TheTarget, shapely.geometry.base.BaseGeometry)): # input is a shapely geometry
			self.OverlayWithGeometry(TheTarget,TheOperation,NewDataset)
		else:
			self.OverlayWithDataset(TheTarget,TheOperation,NewDataset)

		return(NewDataset)

	def OverlayWithSelf(self,TheOperation):

		"""
		Performs an overlay operation on all of the features in a vector dataset.  This is typically
		used 

		Parameters:
			TheOperation: type of operation to be executed 
		Returns:
			NewDataset: The SpaDatasetVector object
		"""
		NewDataset=SpaDatasetVector()
		NewDataset.CopyMetadata(self)
		NewDataset.SetType(None)

		NumFeatures=self.GetNumFeatures()

		if (NumFeatures>0):
			NewGeometry=self.TheGeometries[0]

			FeatureIndex=1
			while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
				TheGeometry=self.TheGeometries[FeatureIndex]

				NewGeometry=self.OverlayGeometryWithGeometry(TheGeometry, NewGeometry,TheOperation)

				FeatureIndex+=1

			# Add the new single feature with the first set of attributes
			if (NewGeometry!=None) and (NewGeometry.is_empty==False) and (NewGeometry.is_valid):
				NewDataset.AddFeature(NewGeometry,self.TheAttributes[0])

		return(NewDataset)

	############################################################################
	# Overlay transform functions
	############################################################################
	def Intersection(self,TheTarget=None):
		"""
		calculates geometric intersection of the target and the SpaDatasetVector object

		Parameters:
			TheTarget: 
				input SpaDatasetVector object 
		Returns:
			New dataset containing only intersected areas of vector datasets 
		"""
		if (TheTarget==None):
			NewLayer=self.OverlayWithSelf(SPAVECTOR_INTERSECTION)
		else:
			NewLayer=self.Overlay(TheTarget,SPAVECTOR_INTERSECTION)
		return(NewLayer)

	def Union(self,TheTarget=None):
		"""
		calculates geometric union of the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector object to find intersection with original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""	
		if (TheTarget==None):
			NewLayer=self.OverlayWithSelf(SPAVECTOR_UNION)
		else:
			NewLayer=self.Overlay(TheTarget,SPAVECTOR_UNION)
		return(NewLayer)

	def Difference(self,TheTarget=None):
		"""
		calculates difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			NewLayer=self.OverlayWithSelf(SPAVECTOR_DIFFERENCE)
		else:
			NewLayer=self.Overlay(TheTarget,SPAVECTOR_DIFFERENCE)
		return(NewLayer)

	def SymmetricDifference(self,TheTarget=None):
		"""
		calculates symetric difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			NewLayer=self.OverlayWithSelf(SPAVECTOR_SYMETRIC_DIFFERENCE)
		else:
			NewLayer=self.Overlay(TheTarget,SPAVECTOR_SYMETRIC_DIFFERENCE)
		return(NewLayer)

	############################################################################
	# Relate transform functions
	# All these functions operate on the data in this layer but return
	# new layers
	############################################################################
	def RelateGeometryWithGeometry(self,TheGeometry,TheTarget,TheOperation):
		"""
		Perform a low-level Relate operation between two geometries

		Parameters:
			TheGeometry:
				object geometry OR an SpaDatasetVector object
			TheTarget: 
				SpaDatasetVector object
			TheOperation: 
				type of operation to be executed (SPAVECTOR_INTERSECTION, SPAVECTOR_UNION, 
				SPAVECTOR_DIFFERENCE, SPAVECTOR_SYMETRICDIFFERENCE)
		Returns:
			A SpaDatasetVector object representint the Relate between TheTarget and TheGeometry
		"""
		Result=None

		if (TheGeometry!=None):

			if (TheGeometry.is_valid):
				if (TheOperation==SPAVECTOR_TOUCHES):
					Result = TheGeometry.touches(TheTarget)	
				elif (TheOperation==SPAVECTOR_INTERSECTS):
					Result = TheGeometry.intersects(TheTarget)	
				elif (TheOperation==SPAVECTOR_DISJOINT):
					Result = TheGeometry.disjoint(TheTarget)	
				elif (TheOperation==SPAVECTOR_OVERLAPS):
					Result = TheGeometry.overlaps(TheTarget)	
				elif (TheOperation==SPAVECTOR_CROSSES):
					Result = TheGeometry.crosses(TheTarget)	
				elif (TheOperation==SPAVECTOR_CONTAINS):
					Result = TheGeometry.contains(TheTarget)	
				else:
					raise("Sorry, "+TheOperation+" is not supported for Relates")
			else:
				Result=None # don't return an invalid geometry

		return(Result)

	def RelateWithGeometry(self,TheTarget,TheOperation,NewDataset):

		"""
		Performs an Relate operation between SpaDatasetVector object and and TheTarget geometry.  The result
		will be added to NewDataset.

		Parameters:
			TheTarget: Object geomerty formatted as a tuple ex: ([(Left,Top), (Right,Top), (Right,Bottom), (Left,Bottom),(Left,Top)])
			TheOperation: type of operation to be executed 
			NewDataset: The SpaDatasetVector object
		Returns:
			none
		"""
		Result=False

		NumFeatures=self.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]

			Flag=self.RelateGeometryWithGeometry(TheGeometry, TheTarget,TheOperation)

			if (Flag): Result=True

			FeatureIndex+=1

		return(Result)

	def RelateWithDataset(self,TheTarget,TheOperation,NewDataset):
		"""
		Performs a Relate operation between this dataset and another dataset.
		Parameters:
			TheTarget: SpaDatasetVector object to be used in Relate
			TheOperation: type of operation to be executed 
			NewDataset: SpaDatasetVector object to be overlaid
		Returns:
			A SpaDatasetVector object 

		"""
		Result=False

		NumFeatures=TheTarget.GetNumFeatures()
		FeatureIndex=0
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=TheTarget.TheGeometries[FeatureIndex]

			# Relate this geometry with each feature in this dataset
			Flag = self.RelateWithGeometry(TheGeometry,TheOperation,NewDataset)

			if (Flag): Result=True

			FeatureIndex+=1

		return(Result)

	def Relate(self,TheTarget,TheOperation):
		"""
		Relate this dataset with a geometry or another dataset

		Parameters:
			TheTarget: SpaDatasetVector object
			TheOperation: type of operation to be executed (Union, intersection, difference, symmetric difference)
		Returns:
			A SpaDatasetVector object
		"""
		Result=False

		NewDataset=SpaDatasetVector()
		NewDataset.CopyMetadata(self)

		if (isinstance(TheTarget, shapely.geometry.base.BaseGeometry)): # input is a shapely geometry
			Result=self.RelateWithGeometry(TheTarget,TheOperation,NewDataset)
		else:
			Result=self.RelateWithDataset(TheTarget,TheOperation,NewDataset)

		return(Result)

	def RelateWithSelf(self,TheOperation):

		"""
		Performs an Relate operation on all of the features in a vector dataset.  This is typically
		used 

		Parameters:
			TheOperation: type of operation to be executed 
		Returns:
			NewDataset: The SpaDatasetVector object
		"""
		Result=False

		NewDataset=SpaDatasetVector()
		NewDataset.CopyMetadata(self)

		NumFeatures=self.GetNumFeatures()
		NewGeometry=self.TheGeometries[0]

		FeatureIndex=1
		while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
			TheGeometry=self.TheGeometries[FeatureIndex]

			Flag=self.RelateGeometryWithGeometry(TheGeometry, NewGeometry,TheOperation)

			if (Flag): Result=True

			FeatureIndex+=1

		return(Result)

	############################################################################
	# Relate transform functions
	############################################################################
	def Touches(self,TheTarget=None):
		"""
		calculates geometric intersection of the target and the SpaDatasetVector object

		Parameters:
			TheTarget: 
				input SpaDatasetVector object 
		Returns:
			New dataset containing only intersected areas of vector datasets 
		"""
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_TOUCHES)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_TOUCHES)
		return(Flag)

	def Intersects(self,TheTarget=None):
		"""
		calculates geometric union of the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector object to find intersection with original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""	
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_INTERSECTS)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_INTERSECTS)
		return(Flag)

	def Disjoint(self,TheTarget=None):
		"""
		calculates difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_DISJOINT)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_DISJOINT)
		return(Flag)

	def Overlaps(self,TheTarget=None):
		"""
		calculates symetric difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_OVERLAPS)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_OVERLAPS)
		return(Flag)

	def Crosses(self,TheTarget=None):
		"""
		calculates symetric difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_CROSSES)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_CROSSES)
		return(Flag)

	def Contains(self,TheTarget=None):
		"""
		calculates symetric difference in values between the target and the SpaDatasetVector object

		Parameters:
			TheTarget: input vector dataset object to be subtracted from original SpaDatasetVector object
		Returns:
			A SpaDatasetVector object
		"""				
		if (TheTarget==None):
			Flag=self.RelateWithSelf(SPAVECTOR_CONTAINS)
		else:
			Flag=self.Relate(TheTarget,SPAVECTOR_CONTAINS)
		return(Flag)
############################################################################
# Layer for vector data including points, polylines, and polygons
############################################################################

class SpaLayerVector:
	def SetDataset(self,NewDataset):
		"""
		Set a new dataset for SpaLayerVector object

		parameters:
			NewDataset:
				Input name of new dataset 
		returns:
			none

		"""
		self.Dataset=NewDataset

	def GetDataset(self):
		"""
		Gets the current dataset

		returns:
			Dataset

		"""
		return(self.Dataset)

	def Render(self,TheView,RandomColors=False,MarkSize=None):
		""" 
		Render this layer into the specified view 

		Parameters:
			TheView: dimensions of the desired view formatted (x,y)

		Returns:
		        none
		"""
		# render each feature in the layer to the view
		NumFeatures=self.Dataset.GetNumFeatures()

		if (NumFeatures>0):
			TheGeometry=self.Dataset.TheGeometries[0]

			if (TheGeometry.geom_type=="Point"):
				if (MarkSize==None): MarkSize=3
				FeatureIndex=0
				while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
					TheGeometry=self.Dataset.TheGeometries[FeatureIndex]

					TheCoords=TheGeometry.coords[0]
					X=TheCoords[0]
					Y=TheCoords[1]

					TheView.RenderRefEllipse(X,Y,MarkSize)

					FeatureIndex+=1

			else:
				FeatureIndex=0
				while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
					TheGeometry=self.Dataset.TheGeometries[FeatureIndex]

					if (RandomColors):
						hue1=random.random() 
						saturation1=0.5
						luminosity1=0.7
						Test=colorsys.hsv_to_rgb(hue1, saturation1, luminosity1)
						TheView.SetFillColor((int(Test[0]*255),int(Test[1]*255),int(Test[2]*255),50))

					TheView.RenderRefGeometry(TheGeometry)

					FeatureIndex+=1

######################################################################################################
# Single line transforms for one layer
######################################################################################################
def Load(InputFile):
	TheDataset=SpaDatasetVector() #create a new layer
	TheDataset.Load(InputFile) # load the contents of the layer
	return(TheDataset)
######################################################################################################
# Single line transforms for one layer
######################################################################################################
def Buffer(InputFile,BufferDistance):
	""" 
	Buffers this dataset by the specified amount and returns a new dataset with the buffered features 

	Parameters:
		BufferDistance:
			Distance, in the datasets reference units, to buffer the data
	Returns:
		New dataset with the buffered data
	"""
	Result=None

	if (isinstance(InputFile, shapely.geometry.base.BaseGeometry)): # input is a shapely geometry
		Result = InputFile.buffer(BufferDistance)
	else: # input is another dataset
		TheInput=SpaBase.GetInput(InputFile)
		Result =TheInput.Buffer(BufferDistance)

	return(Result)

def Simplify(InputFile,Tolerance,PreserveTopology=True):
	"""
	Simply the specified vector data (i.e. remove pixels) until the specified tolerance is reached.
	Larger values of tolerance produce simpler vectors while smaller values create more complex vectors.

	Parameters:
		Tolerance: 
			Distance below which features will be simplified.
		PreserveTopology:
			True to maintain the relationships between features that are touching (i.e. sharing boundaries).

	Returns:
		New dataset with the simplified data
	"""
	Input1=SpaBase.GetInput(InputFile)
	Result=Input1.Simplify(Tolerance,PreserveTopology)

	return(Result)

def ConvexHull(InputFile):
	"""
	Find the simplest polygon that surounds each feature without having an concave segments.

	Parameters:
		InputFile: SpaDatasetVector object
	Returns:
		New dataset with the simplified data
	"""
	Input1=SpaBase.GetInput(InputFile)
	Result=Input1.ConvexHull()

	return(Result)

def Centroid(InputFile):
	"""
	Convert the features in the specified data set to points that are at the centroid (center of gravity)
	of each feature.

	Parameters:
		InputFile: SpaDatasetVector object
	Returns:
		New dataset with the centroids of each feature
	"""
	Input1=SpaBase.GetInput(InputFile)
	Result=Input1.Centroid()

	return(Result)

def Clip(InputFile,MinX=None,MinY=None,MaxX=None,MaxY=None):
	"""
	Convert the features in the specified data set to points that are at the centroid (center of gravity)
	of each feature.

	Parameters:
		InputFile: SpaDatasetVector object
	Returns:
		New dataset with the centroids of each feature
	"""
	if (isinstance(MinX, (list, tuple))):
		TheBounds=MinX
		MinX=TheBounds[0]
		MinY=TheBounds[1]
		MaxX=TheBounds[2]
		MaxY=TheBounds[3]

	BoundingPoly=shapely.geometry.Polygon([(MinX,MaxY), (MaxX,MaxY), (MaxX,MinY), (MinX,MinY),(MinX,MaxY)])

	# Crop a shapefile with a polygon 
	Result=Intersection(InputFile,BoundingPoly) # perform an intersection on a geometry to get the new layer

	return(Result)


######################################################################################################
# Single line transforms for overlay operations
######################################################################################################
def Intersection(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1,Input2,NumGeometries=_FixUpInputs(Input1,Input2)

	if (NumGeometries==2):
		Result=Input1.intersection(Input2)
	else:
		Result=Input1.Intersection(Input2)

	return(Result)

def Union(Input1,Input2=None):
	"""
	Finds the union (combines area) between two shapefiles.  Since this is a feature-by-feature
	operation, you'll typically want to shapefiles that each contain one feature.

	Parameters:
		Input1:
			SpaDatasetVector with geometries
		Input2:
			SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset with the union of each feature
	"""
	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Union(Input2)

	return(Result)

def Difference(Input1,Input2):
	"""
	Finds the difference between the features in two datasets.  Since this is a feature-by-feature
	operation, you'll typically want to shapefiles that each contain one feature.

	Parameters:
		Input1:
			SpaDatasetVector with geometries
		Input2:
			SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset with the difference of each feature
	"""
	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Difference(Input2)

	return(Result)

def SymmetricDifference(Input1,Input2):
	"""
	Finds the symetric difference between the features in two datasets.  Since this is a feature-by-feature
	operation, you'll typically want to shapefiles that each contain one feature.

	Parameters:
		Input1:
			SpaDatasetVector with geometries
		Input2:
			SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset with the symetric difference of each feature
	"""
	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.SymmetricDifference(Input2)

	return(Result)

######################################################################################################
# Single line transforms for relationship operations
######################################################################################################
def Touches(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Touches(Input2)

	return(Result)

def Intersects(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Intersects(Input2)

	return(Result)

def Disjoint(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Disjoint(Input2)

	return(Result)

def Overlaps(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Overlaps(Input2)

	return(Result)

def Crosses(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Crosses(Input2)

	return(Result)

def Contains(Input1,Input2):
	"""
	Finds the intersection (overlapping area) between two vector datasets.  Since this is a feature-by-feature
	operation, you'll typically want to use a shapefile with just one feature in it to find it's intersection
	with the features in the other shapefile.

	Note: Currently only intersections between a multi-feature dataset and a single-feature dataset are supported.

	Parameters:
		Input1: SpaDatasetVector with geometries
		Input2: SpaDatasetVector or a shapely geometry 

	Returns:
		New dataset containing only intersected areas of vector datasets
	"""
	Result=None

	Input1=SpaBase.GetInput(Input1)
	if (Input2!=None): Input2=SpaBase.GetInput(Input2)
	Result=Input1.Contains(Input2)

	return(Result)
