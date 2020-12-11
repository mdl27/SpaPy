############################################################################
# Classes and functions for working with spatially referenced raster data.
# The GDAL libraries are heavily relied upon for this and the data can be
# maintained in file (as a GDAL dataset) or in numpy arrays.
#
# Note, the GDAL documentation at: https://www.gdal.org/gdal_tutorial.html
# is not update to date with the Python gdal reelases.  The standard
# Python documentation is closer:
# https://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html
#
# Supports the following gdal types:
# gdal.GDT_Byte
# gdal.GDT_UInt16
# gdal.GDT_Int16
# gdal.GDT_UInt32
# gdal.GDT_Int32
# gdal.GDT_Float32
# gdal.GDT_Float64
#
# The GDAL bindings return numpy arrays of the data so this was helpful:
# https://gis.stackexchange.com/questions/150300/how-to-place-an-numpy-array-into-geotiff-image-using-python-gdal
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

import os
import numbers
import math

# Open source spatial libraries
import gdal
import numpy
import scipy
import ogr
import scipy.ndimage
from osgeo import osr

# Spa Libraries
import SpaPy

from SpaRasterMath import * # required for defines

############################################################################
# Globals
############################################################################

class SpaDatasetRaster:
	"""
	Class to manage the data associated with a spatial layer

	Attributes:
		GDALDataset:

		GDALDataType

		WidthInPixels: an integer representing the number of pixels along the x-axis

		HeightInPixels: an integer representing the number of pixels along the x-axis

		NumBands: an integer representing the number of bands

		NoDataValue:

		TheMask:

		TheBands:

		XMin:

		YMin:

		PixelWidth
		PixelHeight

		TheWKT
		GCS
		UTMZone
		UTMSouth

	"""
	def __init__(self):
		""""
		Initializes an empty instance of SpaDatasetRasters
		"""

		# below are the properties that make up a shapefile using Fiona for reading and writing from and to shapefiles

		self.GDALDataset=None
		self.GDALDataType=None

		self.WidthInPixels=100
		self.HeightInPixels=100
		self.NumBands=1

		# mask, if NoDataValue!=None, then TheMask contains 1 where there is data, 0 otherwise
		self.NoDataValue=None
		self.TheMask=None

		# the actual data for each band as numpy arrays
		self.TheBands=None # list with one entry for each band

		# reference coordinates for the raster
		self.XMin=0
		self.YMax=0
		self.PixelWidth=1
		self.PixelHeight=1

		# projection information
		self.TheWKT=None
		self.GCS="WGS84"
		self.UTMZone=None
		self.UTMSouth=False

	def CopyPropertiesButNotData(self,RasterDataset):
		"""
		Copy all attributes pertaining to metadata from another instance of SpaDatasetRasters into this instance

		Parameters:
			RasterDataset: A SpaDasetRaster object (cannot take a path name, at this point)

		Returns:
			None
		"""
		self.GDALDataset=None
		self.GDALDataType=RasterDataset.GDALDataType

		self.WidthInPixels=RasterDataset.WidthInPixels
		self.HeightInPixels=RasterDataset.HeightInPixels
		self.NumBands=RasterDataset.NumBands

		self.NoDataValue=RasterDataset.NoDataValue
		self.TheMask=None

		self.TheBands=None

		self.XMin=RasterDataset.XMin
		self.YMax=RasterDataset.YMax
		self.PixelWidth=RasterDataset.PixelWidth
		self.PixelHeight=RasterDataset.PixelHeight

		self.TheWKT=RasterDataset.TheWKT
		self.GCS=RasterDataset.GCS
		self.UTMZone=RasterDataset.UTMZone
		self.UTMSouth=RasterDataset.UTMSouth

	def Clone(self):
		"""
		Duplicates this instance of SpaDatasetRaster

		Parameters:
			None
		Returns:
			SpaDatasetRaster object that is an exact copy of the inputted SpaDatasetRaster object
		"""
		NewDataset=SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(self)

		# copy the bands of data
		NewDataset.TheBands=[]
		for SourceArray in self.TheBands:
			DestinArray = numpy.array(SourceArray)
			#DestinArray = [row[:] for row in SourceArray]
			NewDataset.TheBands.append(DestinArray)

		# make a copy of the mask, if there is one
		if (self.NoDataValue!=None) and (self.TheMask is not None):
			NewDataset.TheMask=numpy.array(self.TheMask)
		else:
			NewDataset.TheMask=None
			
		return(NewDataset)

	############################################################################
	# General Information functions
	############################################################################
	def GetDriverNames(self):
		"""
		Retrieves driver names for provided SpaDatasetRaster

		Parameters:
			None
		Returns:
			driver information for provided SpaDatasetRaster
		"""		
		return(self.GDALDataset.GetDriver().ShortName, self.GDALDataset.GetDriver().LongName)

	def GetWidthInPixels(self):
		"""
		Retrieves width in pixels for provided SpaDatasetRaster

		Parameters:
			None
		Returns:
			Width (in pixels) of provided SpaDatasetRaster
		"""		
		return(self.WidthInPixels)

	def SetWidthInPixels(self,New):
		"""
		Redefines width (in pixels) of provided SpaDatasetRaster

		Parameters:
			New: Value of desired raster width
		Returns:
			none
		"""		
		self.WidthInPixels=New

	def GetHeightInPixels(self):
		"""
		Retrieves height for provided SpaDatasetRaster

		Parameters:
			None
		Returns:
			Height (in pixels) of provided raster
		"""	
		return(self.HeightInPixels)

	def SetHeightInPixels(self,New):
		"""
		Redefines height of provided SpaDatasetRaster

		Parameters:
			New: Value of desired raster height (in pixels)
		Returns:
			none
		"""				
		self.HeightInPixels=New

	def GetNumBands(self):
		"""
		Retrieves number of bands in provided SpaDatasetRaster

		Parameters:
			None
		Returns:
			number of bands found in provided raster
		"""			
		return(self.NumBands)

	def SetNumBands(self,NumBands): 
		"""
		Sets new value for number of bands in provided SpaDatasetRaster

		Parameters:
			NumBands: Insert value of desired band amount found in raster
		Returns:
			none
		"""		
		self.NumBands=NumBands

	def GetProjection(self):
		"""
		Retrieves projection of provided SpaDatasetRaster

		Parameters:
			None
		Returns:
			Projection information for provided raster formatted into a list that includes projection, geographic coordinate system, spheroid, etc.
		"""					
		return(self.GDALDataset.GetProjection()) # jjg


	def GetResolution(self):
		""" 
		Returns the resolution of the raster as a tuple with (X,Y) 
		
		Parameters: 
			none
		Returns:
			the resolution of the raster as a tuple with (X,Y)
	              
		"""
		return((self.PixelWidth,self.PixelHeight))

	def SetResolution(self,PixelWidth,PixelHeight=None):
		"""
		Redefines resolution of provided SpaDatasetRaster

		Parameters:
			PixelWidth: Value of desired pixel width in pixel units
		Returns:
			none
		"""				
		if (PixelHeight==None): PixelHeight=PixelWidth
		self.PixelWidth=PixelWidth
		self.PixelHeight=PixelHeight
		

	def GetBounds(self):
		"""
		Retreives bounds of provided SpaDatasetRaster formatted as (XMin,YMin,YMax,XMax)

		Parameters:
			None
		Returns:
			Bound information for provided raster
		"""
		Result=None

		Resolution=self.GetResolution()

		XMax=self.XMin+(self.WidthInPixels*Resolution[0])
		YMin=self.YMax+(self.HeightInPixels*Resolution[1]) # The resolution will be negative so we add the height 

		Result=(self.XMin,YMin,XMax,self.YMax)

		return(Result)

	def GetRefXFromPixelX(self,PixelX):
		#Need additional information to complete notes (function of tool-inputs, outputs, etc.)
		"""
		Converts from Pixel (view/raster) coordinates to Reference (map) coordinates in the horizontal direction

		Parameters:
			PixelX= pixel coordinates in the horizontal direction (x-coordinate)
		Returns:
			Reference coordinates in the horizontal direction
		"""		
		Resolution=self.GetResolution()
		RefX=self.XMin+(PixelX*Resolution[0])
		return(RefX)

	def GetRefYFromPixelY(self,PixelY):
		#Need additional information to complete notes (function of tool-inputs, outputs, etc.)
		"""
		Converts from Pixel (view/raster) coordinates to Reference (map) coordinates in the vertical direction

		Parameters:
			PixelY= pixel coordinates in the vertical direction (y-coordinate)
		Returns:
			Reference point information for listed pixel from SPDatatsetRaster 
		"""				
		Resolution=self.GetResolution()
		RefY=self.YMax-(PixelY*Resolution[1])
		return(RefY)

	def GetPixelXFromRefX(self,RefX):
		"""
		Converts from Reference (map) coordinates to Pixel (view/raster) coordinates in the horizontal direction

		Parameters:
			RefX= Reference coordinates in the horizontal direction (x-coordinate)
		Returns:
			Pixel coordinates in the horizontal direction
		"""								
		Resolution=self.GetResolution()
		PixelX=0+((RefX-self.XMin)// Resolution[0])
		return(int(PixelX))

	def GetPixelYFromRefY(self,RefY):
		"""
		This function converts from Reference (map) coordinates to Pixel (view/raster) coordinates in the vertical direction

		Parameters:
			RefY= Reference coordinates in the vertical direction (y-coordinate)
		Returns:
			Pixel coordinates in the horizontal direction
		"""						
		Resolution=self.GetResolution()
		PixelY=0-((self.YMax-RefY) //Resolution[1])
		return(int(PixelY))

	def SetNorthWestCorner(self,X,Y):
		""""
		Sets northwest corner of raster to desired coordinates (x,y)
	
		Parameters:
			X= insert desired x-coordinate here
			Y= insert desired y-coordinate here
		Returns:
			a SpaDatasetRaster object
	
		"""		
		self.XMin=X 
		self.YMax=Y

	def GetBand(self,Index):
		"""
		Retreive band information for selected band
		
		Parameters:
			Index: format as a tuple.
		Returns:
			Band information for selected band
			
		"""
		if (self.TheBands==None): throw("ERror")

		return(self.TheBands[Index])

	def SetBands(self,TheBands):
		# Need more information about format of TheBands
		"""
		Sets the band values in SpaRaster object equal to those specified
		
		Parameters:
			TheBands=desired band values
		Returns:
			none
			
		"""	
		self.TheBands=TheBands

	def GetBands(self):
		"""
		Retreive band information for SpaRaster object
		
		Parameters:
			none
		Returns:
			Band information for SpaRaster object
			
		"""		
		return(self.TheBands)

	def GetMinMax(self,Index):
		"""
		Returns the min and max values for the specified band
		
		Parameters:
			Index: insert specified band here 
		Return:
			Returns a tuple (static list) with the minimum and maximum raster values for the specific band index
		"""
		srcband = self.GDALDataset.GetRasterBand(Index)
		return(srcband.GetMinimum(),srcband.GetMaximum())

	# Results additional information for each band.
	# Not sure what to do with this function in the future
	def GetBandInfo(self,Index):
		"""
		Retreive band info from SpaDatasetRaster object for selected band
		
		Parameters:
			Index: Input desired band here
		Returns:
			Selcted band information for SpaDatasetRaster object
			
		"""				
		srcband = self.GDALDataset.GetRasterBand(Index)
		Result=None
		if (srcband!=None):
			Result={
			    "Scale":srcband.GetScale(),
			    "UnitType":srcband.GetUnitType(),
			    "ColorTable":srcband.GetColorTable()
			}
		return(Result)

	def GetType(self):
		"""
		returns the GDAL types, these are shown in the GetNumPyType() function
		
		Parameters:
			none
		Returns:
		        SpaDatasetRaster object type information
			
		"""		
		return(self.GDALDataType)

	def SetType(self,GDALDataType):
		"""
		Set GDAL type for SpaDatasetRaster object
	
		Parameters:
			Desired data type
		Returns:
			none
	
		"""		
		self.GDALDataType=GDALDataType
		
		if (self.GDALDataset!=None):
			self.GDALDataset = gdal.Translate('', GDALDataset, format="MEM",outputType=GDALDataType)

	def GetNoDataValue(self):
		return(self.NoDataValue)
	############################################################################
	# Functions to manage spatial references
	############################################################################
	def SetUTM(self,Zone,South=False):
		"""
		Set SpaDatadetRaster object to UTM zone specified
	
		Parameters:
			Zone: insert zone number here
		Returns:
			none
	
		"""		
		self.UTMZone=Zone
		self.UTMSouth=South

	############################################################################
	# Functions to setup the arrays of data
	############################################################################
	def AllocateArray(self):
		""" 
		Allocates the numpy array for the raster.
		NumPyType - uint8, int16, int32, float32 are supported.   
		 (see https://docs.scipy.org/doc/numpy-1.13.0/user/basics.types.html)
		Parameters:
			none
		Returns:
			An array of values
		"""
		#self.NumPyType=NumPyType
		NumPyType=self.GetNumPyType()

		self.TheBands=[]

		Count=0
		while (Count<self.NumBands):
			self.TheBands.append(numpy.zeros((self.HeightInPixels,self.WidthInPixels), dtype=NumPyType))
			Count+=1

		return(self.TheBands)

	############################################################################
	# Functions to interact with files (shapefiles and CSVs)
	############################################################################
	def GetNumPyType(self):
		"""
		Returns with NumPy Type of SpaDatasetRaster object
	
		Parameters:
			none
		Returns:
			Numpy Type of SpaDatasetRaster object
	
		"""				
		NumPyType=None
		if (self.GDALDataType==gdal.GDT_Byte): NumPyType="uint8"
		elif (self.GDALDataType==gdal.GDT_Byte): NumPyType="int8"
		elif (self.GDALDataType==gdal.GDT_UInt16): NumPyType="uint16"
		elif (self.GDALDataType==gdal.GDT_Int16): NumPyType="int16"
		elif (self.GDALDataType==gdal.GDT_UInt32): NumPyType="uint32"
		elif (self.GDALDataType==gdal.GDT_Int32): NumPyType="int32"
		elif (self.GDALDataType==gdal.GDT_Float32): NumPyType="float32"
		elif (self.GDALDataType==gdal.GDT_Float64): NumPyType="float64"
		elif (self.GDALDataType==gdal.GDT_CFloat64): NumPyType="complex64"
		return(NumPyType)

	def Load(self,FilePathOrDataset):
		"""
		Loads raster file (this enables us to later perform operations on the raster)
		Parameters:
			FilePathOrDataset: A SpaDatasetRaster object OR a string representing the path to the raster file
		Returns:
			none
	
		"""				
		if isinstance(FilePathOrDataset,gdal.Dataset):
			self.GDALDataset=FilePathOrDataset
		else:
			self.GDALDataset=gdal.Open(FilePathOrDataset)
		if (self.GDALDataset==None):
			raise Exception("Sorry, the file "+FilePathOrDataset+" could not be opened.  Please, make sure the file path is correct and is of a supported file type.")
		else:
			# get the desired band
			outband = self.GDALDataset.GetRasterBand(1)

			# Get the GDAL data type and convert it to a numpy datatype

			self.GDALDataType=outband.DataType

			# get the dimensions in pixels and the number of bands
			self.WidthInPixels=self.GDALDataset.RasterXSize
			self.HeightInPixels=self.GDALDataset.RasterYSize

			self.NumBands=self.GDALDataset.RasterCount

			####################################
			# Get the spatial location of the raster data
			# adfGeoTransform[0] /* top left x */
			# adfGeoTransform[1] /* w-e pixel resolution */
			# adfGeoTransform[2] /* 0 */
			# adfGeoTransform[3] /* top left y */
			# adfGeoTransform[4] /* 0 */
			# adfGeoTransform[5] /* n-s pixel resolution (negative value) */

			TheGeoTransform=self.GDALDataset.GetGeoTransform()

			self.XMin=TheGeoTransform[0]
			self.YMax=TheGeoTransform[3]

			self.PixelWidth=TheGeoTransform[1]
			self.PixelHeight=TheGeoTransform[5]

			#Thing=self.GDALDataset.GetProjection()
			self.TheWKT=self.GDALDataset.GetProjectionRef()


			self.TheBands =[]
			Count=0
			while (Count<self.NumBands):
				TheBand=self.GDALDataset.GetRasterBand(Count+1)
				self.TheBands.append(TheBand.ReadAsArray())
				Count+=1

			self.NoDataValue=outband.GetNoDataValue()

			if (self.NoDataValue!=None): # have to create the mask
				self.TheMask=numpy.equal(self.TheBands[0],self.NoDataValue)

	def Save(self,TheFilePath):
		""" 
		Creates a new raster in the layer.
		TheFilePath - Fill file path with the file extension (tif, jpg, png, or asc)
		Common file formats include: GTiff, PNG, JPEG, HFA (ERDAS Imagine or img), AAIGrid (Esri ASCII Ggrid)
		All FileFormats are listed at: https://www.gdal.org/formats_list.html 
		
		Parameters:
			TheFilePath: A string representing the path to the folder where file is to be stored
		Returns:
			none
		"""

		FileName,Extension=os.path.splitext(TheFilePath)

		Extension=Extension.lower()

		DriverName="GTiff"
		if (Extension==".png"):
			DriverName="PNG"
		elif (Extension==".jpg"):
			DriverName="JPG"
		elif (Extension==".asc"):
			DriverName="AAIGrid"
		elif (Extension==".img"):
			DriverName="HFA"

		# Create the file
		driver = gdal.GetDriverByName(DriverName)

		outRaster = driver.Create(TheFilePath, self.WidthInPixels, self.HeightInPixels, self.NumBands,self.GDALDataType)

		outRaster.SetGeoTransform((self.XMin, self.PixelWidth, 0, self.YMax, 0, self.PixelHeight))

		###########################################
		#Setup the spatial reference
		if (self.TheWKT!=None):
			outRasterSRS = osr.SpatialReference()
			#outRasterSRS.ImportFromWkt(self.TheWKT)
			outRasterSRS.SetProjection(self.TheWKT)

			outRaster.SetProjection(self.TheWKT)

		if (self.UTMZone!=None):
			# setup the spatial reference
			srs = osr.SpatialReference()

			North=1
			if (self.UTMSouth): North=0
			srs.SetUTM(self.UTMZone,North)

			srs.SetWellKnownGeogCS(self.GCS)

			outRaster.SetProjection(srs.ExportToWkt())

		#write out the data

		Count=0
		while (Count<self.NumBands):
			outband = outRaster.GetRasterBand(Count+1)

			TheBand=self.TheBands[Count]

			if (self.NoDataValue!=None):
				outband.SetNoDataValue(self.NoDataValue)
				TheBand=numpy.where(self.TheMask,self.NoDataValue,TheBand)

			outband.WriteArray(TheBand)
			outband.FlushCache()

			Count+=1
	#######################################################################
	# Transforms
	def Polygonize(self):
		import SpaVectors
		import shapely.wkt
		""" 
		Converts a raster to a polygon feature set.  Each contiguous area of the raster
		(i.e. ajoining pixels that have the same value) are grouped as one polygon.  The
		only attribute is "band1" as this only works for one band.
		
		Parameters:
			none
		Returns:
			A Polygon featurset
		"""
		drv = ogr.GetDriverByName("Memory")

		#get spatial reference info
		srs = osr.SpatialReference()
		srs.ImportFromWkt(self.TheWKT)

		# Create a temporary data set in memory
		DestinDataSource = drv.CreateDataSource('out')	
		DestinLayer = DestinDataSource.CreateLayer('', srs = srs ) #

		# add the attribute for the pixel values
		AttributeType=ogr.OFTInteger
		if ((self.GDALDataType==gdal.GDT_Float32) or (self.GDALDataType==gdal.GDT_Float64)): AttributeType=ogr.OFSTFloat32;
		
		FieldDefinition = ogr.FieldDefn("band1", AttributeType)
		DestinLayer.CreateField(FieldDefinition)
		AttributeIndex = 0

		# create polygons from the first raster band
		srcband=self.GDALDataset.GetRasterBand(1)

		gdal.Polygonize(srcband, None, DestinLayer, AttributeIndex, [], callback=None)	

		# create a new dataset in SpaVectors
		OutDataset = SpaVectors.SpaDatasetVector()

		OutDataset.AttributeDefs["band1"]='int:1'
		
		for feature in DestinLayer:
			# get the spatial reference and convert to WKT and then convert to a ShapelyGeometry
			Geometry=feature.GetGeometryRef().ExportToWkt()
			ShapelyGeometry=shapely.wkt.loads(Geometry)
			
			# setup the attribute array and add the feature to the output dataset
			Value=feature.GetField(0)
			if (isinstance(Value,list)): Value=Value[0]
			Attributes={"band1":Value}
			
			OutDataset.AddFeature(ShapelyGeometry,Attributes)

		return(OutDataset)

	#def Warp(self,DestinFilePath):
		#"""
		#Works but only writes to disk
		#"""
		#drv = ogr.GetDriverByName("ESRI Shapefile")
		#dst_ds = drv.CreateDataSource( DestinFilePath + ".shp" )
		#dst_layer = dst_ds.CreateLayer(DestinFilePath, srs = None )

		#srcband=self.GDALDataset.GetRasterBand(1)

	def Math(self,Operation,Input2):

		"""
		Handles all raster math operations using numPy arrays - called by one-line functions

		Parameters:
			Operation: An integer specifying which numpy function to call
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster file OR a constant value as a float
		Returns:
			SpaRasterDataset object
		"""

		BandIndex=0
		NewDataset=self.Clone()
		NewBands=[]

		if (isinstance(Input2, numbers.Number)==False): # input is another dataset
			# jjg - add checks for same number of bands, convertion to save width, height, and data type
			Input2=SpaPy.GetInput(Input2) # get the input as a dataset

			for TheBand in self.TheBands: # add each of the bands from each of the datasets
				Band2=Input2.GetBand(BandIndex)

				if (Operation==SPAMATH_ADD): NewBands.append(numpy.add(TheBand,Band2))
				elif (Operation==SPAMATH_SUBTRACT): NewBands.append(numpy.subtract(TheBand,Band2))
				elif (Operation==SPAMATH_MULTIPLY): NewBands.append(numpy.multiply(TheBand,Band2))
				elif (Operation==SPAMATH_DIVIDE): NewBands.append(numpy.divide(TheBand,Band2))
				elif (Operation==SPAMATH_EQUAL): NewBands.append(numpy.equal(TheBand,Band2))
				elif (Operation==SPAMATH_NOT_EQUAL): NewBands.append(numpy.not_equal(TheBand,Band2))
				elif (Operation==SPAMATH_GREATER): NewBands.append(numpy.greater(TheBand,Band2))
				elif (Operation==SPAMATH_LESS): NewBands.append(numpy.less(TheBand,Band2))
				elif (Operation==SPAMATH_GREATER_OR_EQUAL): NewBands.append(numpy.greater_equal(TheBand,Band2))
				elif (Operation==SPAMATH_LESS_OR_EQUAL): NewBands.append(numpy.less_equal(TheBand,Band2))
				elif (Operation==SPAMATH_AND): NewBands.append(numpy.logical_and(TheBand,Band2))
				elif (Operation==SPAMATH_OR): NewBands.append(numpy.logical_or(TheBand,Band2))
				elif (Operation==SPAMATH_MAX): NewBands.append(numpy.maximum(TheBand, Band2))
				elif (Operation==SPAMATH_MIN): NewBands.append(numpy.minimum(TheBand, Band2))

				if (Operation==SPAMATH_EQUAL) or (Operation==SPAMATH_NOT_EQUAL) or (Operation==SPAMATH_GREATER) or (Operation==SPAMATH_LESS) or \
				   (Operation==SPAMATH_GREATER_OR_EQUAL) or (Operation==SPAMATH_LESS_OR_EQUAL) or (Operation==SPAMATH_AND) or (Operation==SPAMATH_OR) or \
				   (Operation==SPAMATH_MAX) or (Operation==SPAMATH_MIN): 
					NewBands[BandIndex]=NewBands[BandIndex].astype(int)
					NewDataset.GDALDataType=gdal.GDT_Byte
					
				BandIndex+=1
					
		else: # input is a scalar value ... all unary operators are in here
			for TheBand in self.TheBands:
				if (Operation==SPAMATH_ADD): NewBands.append(numpy.add(TheBand,Input2))
				elif (Operation==SPAMATH_SUBTRACT): NewBands.append(numpy.subtract(TheBand,Input2))
				elif (Operation==SPAMATH_MULTIPLY): NewBands.append(numpy.multiply(TheBand,Input2))
				elif (Operation==SPAMATH_DIVIDE): NewBands.append(numpy.divide(TheBand,Input2))
				elif (Operation==SPAMATH_EQUAL): NewBands.append(numpy.equal(TheBand,Input2))
				elif (Operation==SPAMATH_NOT_EQUAL): NewBands.append(numpy.not_equal(TheBand,Input2))
				elif (Operation==SPAMATH_GREATER): NewBands.append(numpy.greater(TheBand,Input2))
				elif (Operation==SPAMATH_LESS): NewBands.append(numpy.less(TheBand,Input2))
				elif (Operation==SPAMATH_GREATER_OR_EQUAL): NewBands.append(numpy.greater_equal(TheBand,Input2))
				elif (Operation==SPAMATH_LESS_OR_EQUAL): NewBands.append(numpy.less_equal(TheBand,Input2))
				elif (Operation==SPAMATH_AND): NewBands.append(numpy.logical_and(TheBand,Input2))
				elif (Operation==SPAMATH_OR): NewBands.append(numpy.logical_or(TheBand,Input2))
				elif (Operation==SPAMATH_NOT): NewBands.append(numpy.logical_not(TheBand))
				elif (Operation==SPAMATH_ROUND): NewBands.append(numpy.around(TheBand,Input2))
				elif (Operation==SPAMATH_ROUND_INTEGER): NewBands.append(numpy.rint(TheBand))
				elif (Operation==SPAMATH_ROUND_FIX): NewBands.append(numpy.fix(TheBand))
				elif (Operation==SPAMATH_ROUND_FLOOR): NewBands.append(numpy.floor(TheBand))
				elif (Operation==SPAMATH_ROUND_CEIL): NewBands.append(numpy.ceil(TheBand))
				elif (Operation==SPAMATH_ROUND_TRUNC): NewBands.append(numpy.trunc(TheBand))
				elif (Operation==SPAMATH_NATURAL_LOG): NewBands.append(numpy.log(TheBand))
				elif (Operation==SPAMATH_LOG): NewBands.append(numpy.log10(TheBand))
				elif (Operation==SPAMATH_EXPONENT): NewBands.append(numpy.exp(TheBand))
				elif (Operation==SPAMATH_POWER): NewBands.append(numpy.power(TheBand, Input2))
				elif (Operation==SPAMATH_SQUARE): NewBands.append(numpy.square(TheBand))
				elif (Operation==SPAMATH_SQUARE_ROOT): NewBands.append(numpy.sqrt(TheBand))
				elif (Operation==SPAMATH_ABSOLUTE): NewBands.append(numpy.absolute(TheBand))
				#elif (Operation==SPAMATH_CLIP_TOP): NewBands.append(numpy.clip(TheBand,0,Input2))
				#elif (Operation==SPAMATH_CLIP_BOTTOM): NewBands.append(numpy.clip(TheBand,Input2,10000))

				if (Operation==SPAMATH_EQUAL) or (Operation==SPAMATH_NOT_EQUAL) or (Operation==SPAMATH_GREATER) or (Operation==SPAMATH_LESS) or \
				   (Operation==SPAMATH_GREATER_OR_EQUAL) or (Operation==SPAMATH_LESS_OR_EQUAL) or (Operation==SPAMATH_AND) or (Operation==SPAMATH_OR) or \
				   (Operation==SPAMATH_MAX) or (Operation==SPAMATH_MIN): 
					NewBands[BandIndex]=NewBands[BandIndex].astype(int)
					NewDataset.GDALDataType=gdal.GDT_Byte
						
				BandIndex+=1


		NewDataset.SetBands(NewBands)
		return(NewDataset)

	#######################################################################
	# Common math operators that are overloaded
	#######################################################################
	def __add__(self, Input2): 
		"""
		Performs pixel-wise addition of two rasters OR of one raster and a constant
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster file OR 
			a constant value as a float
		Returns:
			A SpaDatasetRaster object where the value of each cell is equal to the sum of the values 
			of the corresponding cells in each of the two inputs
		"""
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPMATH_ADD,Input2))

	def __sub__(self, Input2): 
		"""
		Performs pixel-wise subtraction of two rasters OR of one raster and a constant
		
		Parameters:
			Input2:A SpaDatasetRaster object OR a string representing the path to the raster file 
				OR a constant value as a float
		Returns:
			A SpaDatasetRaster object where the value of each cell is equal to the difference between 
			the provided SPRasterDatasetObject and Input2
		"""		
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPMATH_SUBTRACT,Input2))

	def __mul__(self, Input2): 
		"""
		Performs pixel-wise multiplication of two rasters OR of one raster and a constant
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster file 
			OR a constant value as a float
		Returns:
			A SpaDatasetRaster object where the value of each cell is equal to the product of the values of 
			the corresponding cells in each of the two raster dataset objects
		"""		
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPMATH_MULTIPLY,Input2))

	def __truediv__(self, Input2): 
		"""
		Performs function for pixel-wise division two rasters OR of one raster and a constant
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster file 
			OR a constant value as a float
		Returns:
			A SpaDatasetRaster object where the value of each cell is equal to the quotient 
			of the values on the corresponding cells
		"""				
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPMATH_DIVIDE,Input2))

	# Common comparison operators
	def __lt__(self, Input2): # less than
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is less than Input2 and 0 for cells where it is not
		"""				
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_LESS,Input2))

	def __le__(self, Input2): # less than or equal
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is less than or equal to Input2 and 0 for cells where it is not
		"""		
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_LESS_OR_EQUAL,Input2))

	def __eq__(self, Input2): # equal
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is equal to Input2 and 0 for cells where it is not
		"""					
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_EQUAL,Input2))

	def __ne__(self, Input2): # not equal
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is not equal to Input2
			and 0 for cells where it is not
		"""							
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_NOT_EQUAL,Input2))

	def __ge__(self, Input2): # greater than or equal
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is greater than or equal to 
			Input2 and 0 for cells where it is not
		"""			
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_GREATER_OR_EQUAL,Input2))

	def __gt__(self, Input2): # greater than
		"""
		Performs  pixel-wise comparison between two rasters OR between one raster and a constant.
		
		Parameters:
			Input2: 
			A SpaDatasetRaster object OR a string representing the path to the raster 
			file OR a constant value as a float
		Returns:
			A SpaDatasetRaster object with values of 1 for cells where self is greater than 
			Input2 and 0 for cells where it is not
		"""			
		Input1=SpaPy.GetInput(self)
		return(Input1.Math(SPAMATH_GREATER,Input2))

	# Common boolean operators (jjg boolean operators cannot be overriden in Python, we have to use And())
	#def __and__(self, Input2):# greater than 
		#"""
		#One-line function for logical operation between two boolean rasters OR between one boolean raster and a constant boolean value. The order of the parameters does not matter.

		#Parameters:
			#Input2: SpaDatasetRaster object OR a string representing the path to the raster file OR a boolean consta
                #Returns:
			#A SpaDatasetRaster object where each cell true if the corresponding cells in both inputs are true. 
		#"""			
		#Input1=SpaPy.GetInput(self)
		#return(Input1.Math(SPAMATH_AND,Input2))
	#def __or__(self, Input2): # greater than
		## need more info on function
		#"""
		#One-line function for logical operation between two boolean rasters OR between one boolean raster and a constant boolean value. The order of the parameters does not matter.

		#Parameters:
			#Input2: SpaDatasetRaster object OR a string representing the path to the raster file OR a boolean constant

		#Returns:
			#A SpaDatasetRaster object where each cell true if the corresponding cells in either inputs are true. 
                #"""				
		#Input1=SpaPy.GetInput(self)
		#return(Input1.Math(SPAMATH_OR,Input2))
	
	#def __inv__(self, Input2): # greater than
		## need more info
		#"""
		#Returns with a SpaDatasetRaster object containing only values...
		#Parameters:
			#Input2: A SpaDatasetRaster object OR a string representing the path to the raster file OR a constant value as a float
		#Returns:
			#A SpaDatasetRaster object
		#"""			
		#Input1=SpaPy.GetInput(self)
		#return(Input1.Math(SPAMATH_NOT,Input2))

	#######################################################################
	# 
	#######################################################################
	def Reclassify(self,InputClasses,OutputClasses,mode):
		"""
		Reclassify a raster dataset using numpy
		
		Parameters:
			InputClasses: A SpaDatasetRaster object OR a string representing the path to the raster file
			OutputClasses: A string representing the path to the file where output will be stored
			mode: The format of the values which will be used for reclassification (either range or discrete)

		Returns:
			A SpaRasterDataset object reclassified to the parameters outlined in mode
		"""

		if mode=="discrete":
			NewDataset = SpaDatasetRaster()
			NewDataset = self.Clone()
			NewBands=[]
			condlist=[]
			choicelist=[]
			for TheBand in self.TheBands:
				for cond in InputClasses:
					condlist.append(TheBand==cond)
				for choice in OutputClasses:
					choicelist.append(numpy.ones_like(TheBand)*choice)
				NewBand=numpy.select(condlist,choicelist)
				NewBands.append(NewBand)
			NewDataset.SetBands(NewBands)
			return(NewDataset)

		elif mode=="range":
			NewDataset = SpaDatasetRaster()
			NewDataset = self.Clone()
			NewBands=[]
			condlist=[]
			choicelist=[]
			for TheBand in self.TheBands:
				for cond in InputClasses:
					if InputClasses.index(cond)==0:
						condlist.append(numpy.logical_and(TheBand>cond[0],TheBand<=cond[1]))

					else:
						condlist.append(numpy.logical_and(TheBand>cond[0],TheBand<=cond[1]))
				for choice in OutputClasses:
					choicelist.append(numpy.ones_like(TheBand)*choice)
				NewBand=numpy.select(condlist,choicelist)
				NewBands.append(NewBand)
			NewDataset.SetBands(NewBands)
			return(NewDataset)

#######################################################################
# additional core transforms
#######################################################################

class SpaResample(SpaPy.SpaTransform):
	"""
	Abstract class to define projectors
	"""
	def __init__(self):
		super().__init__()

		self.SetSettings(Resample,{
		    "RowRate":10,
		    "ColumnRate":10,
		})

	def Crop(Self,InputRasterDataset,Bounds):
		"""
		Crops a raster to a specified extent
		Parameters:
			InputRasterDataset: A SpaDatasetRaster object OR a string representing the path to the raster file
			Bounds: new extent formatted as [x1,y1,x2,y2] 
		Return:
			A cropped SpaRasterDataset object 
		
		"""
		NewDataset=SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(InputRasterDataset)

		GDALDataset = InputRasterDataset.GDALDataset
		GDALDataset = gdal.Translate('', GDALDataset, format="MEM", projWin = Bounds)
		NewDataset.Load(GDALDataset)
		GDALDataset = None
		return(NewDataset)

	def NumpyCrop(self,InputRasterDataset,Bounds):
		"""
		Crops a raster using extract by pixel
		Parameters:
			InputRasterDataset: A SpaDatasetRaster object
			Bounds: A list representing UpperLeftX, UpperLeftY, LowerRightX, and LowerRightY coordinates, in map units.
		Returns:
			A SpaDatsetRasterObject
		"""
		NewDataset=SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(InputRasterDataset)

		UpperLeftRefX=Bounds[0]
		UpperLeftRefY=Bounds[1]
		LowerRightRefX=Bounds[2]
		LowerRightRefY=Bounds[3]

		UpperLeftPixelX=InputRasterDataset.GetPixelXFromRefX(UpperLeftRefX)
		UpperLeftPixelY=InputRasterDataset.GetPixelYFromRefY(UpperLeftRefY)
		LowerRightPixelX=InputRasterDataset.GetPixelXFromRefX(LowerRightRefX)
		LowerRightPixelY=InputRasterDataset.GetPixelYFromRefY(LowerRightRefY)

		NewDataset = self.ExtractByPixels(InputRasterDataset, UpperLeftPixelX, UpperLeftPixelY, LowerRightPixelX, LowerRightPixelY)

		return(NewDataset)

	def Scale(self,InputRasterDataset,ZoomFactor,order=3):
		"""
		Resamples the raster based on the specified ZoomFactor.
		This appears to work well.
		Parameters:
			InputRasterDataset: A SpaDatasetRaster object OR a string representing the path to the raster file
			ZoomFactor: 
		Return:
			A SpaRasterDataset object scaled to the specified extent
		"""
		#check to see if input is a str or a SpaDatasetRaster object

		InputRasterDataset = SpaPy.GetInput(InputRasterDataset)

		OutputDataset=SpaDatasetRaster()
		OutputDataset.CopyPropertiesButNotData(InputRasterDataset)

		OutputBands=[]
		InputBands=InputRasterDataset.GetBands()

		NumBands=OutputDataset.GetNumBands()

		OutputDataset.PixelHeight=InputRasterDataset.PixelHeight/ZoomFactor
		OutputDataset.PixelWidth=InputRasterDataset.PixelWidth/ZoomFactor

		# go through each of the rows in the output raster sampling data from the input rows
		BandIndex=0
		while (BandIndex<NumBands):

			InputBand=InputBands[BandIndex]

			#OutputBand=scipy.ndimage.zoom(InputBand, ZoomFactor, order=order, mode='constant', cval=0.0, prefilter=True)
			# jjg - we need another way to deal with no data values - convert them to zeros on load and then convert back on save?
			super_threshold_indices = InputBand<0.00000001
			InputBand[super_threshold_indices] = 0
			OutputBand=scipy.ndimage.zoom(InputBand, ZoomFactor)

			OutputBands.append(OutputBand)

			OutputDataset.HeightInPixels=numpy.size(OutputBand,0)
			OutputDataset.WidthInPixels=numpy.size(OutputBand,1)

			BandIndex+=1

		# add the new band to the output dataset
		OutputDataset.TheBands=OutputBands

		TheMask = InputRasterDataset.TheMask
		if (TheMask is not None):
			OutputMask = scipy.ndimage.zoom(TheMask,ZoomFactor,output=None,order=order,mode='constant',cval=0.0,prefilter=True)
			OutputDataset.TheMask=OutputMask
		else: 
			OutputDataset.TheMask=None
		
		return(OutputDataset)

	def ExtractByPixels(self,InputRasterDataset,StartColumn,StartRow,EndColumn,EndRow):
		"""
		Extracts a portion of the raster image using pixel locations.
		
		Parameters:
			InputRasterDataset: 
				A SpaDatasetRaster object OR a string representing the path to the raster file
			StartColumn: 
				input first column of input raster to be extracted into new layer
			StartRow: 
				input first row of input raster to be extracted into new layer
			EndColumn: 
				input last column of input raster to be extracted inot new layer
			EndRow: 
				input last column of input raster to be extracted into new layer
		Returns:
		        A SpaRastserDataset object extracted to the outlined extent
		"""
		OutputDataset=SpaDatasetRaster()
		OutputDataset.CopyPropertiesButNotData(InputRasterDataset)

		OutputBands=[]
		InputBands=InputRasterDataset.GetBands()

		OutputDataset.HeightInPixels=EndRow-StartRow+1
		OutputDataset.WidthInPixels=EndColumn-StartColumn+1

		OutputDataset.XMin=OutputDataset.XMin+(StartColumn*OutputDataset.PixelWidth)
		OutputDataset.YMax=OutputDataset.YMax+(StartRow*OutputDataset.PixelHeight)

		NumBands=OutputDataset.GetNumBands()

		# go through each of the rows in the output raster sampling data from the input rows
		BandIndex=0
		while (BandIndex<NumBands):

			InputBand=InputBands[BandIndex]

			OutputBand=InputBand[StartRow:EndRow+1,StartColumn:EndColumn+1]

			OutputBands.append(OutputBand)

			BandIndex+=1

		# add the new band to the output dataset
		OutputDataset.TheBands=OutputBands

		return(OutputDataset)

	def NearestNeighbor(self,InputRasterDataset):
		"""
		Creates a sampled version of the specified raster
		This uses NumPy arrays with Python to sample pixel by
		pixel and is really slow.
		
		Parameters:
			InputRasterDataset: 
				A SpaDatasetRaster object OR a string representing the path to the raster file
		Returns:
			A SpaDatasetRaster resampled using Nearest Neighbor resampling method
		"""
		#check to see if input is a str or a SpaDatasetRaster object

		InputRasterDataset = SpaPy.GetInput(InputRasterDataset)

		OutputDataset=SpaDatasetRaster()
		OutputDataset.CopyPropertiesButNotData(InputRasterDataset)

		NumPyType=OutputDataset.GetNumPyType()

		# get information from the rasters
		InputWidthInPixels=InputRasterDataset.GetWidthInPixels()
		InputHeightInPixels=InputRasterDataset.GetHeightInPixels()

		# get settings
		TheSettings=self.GetSettings(Resample)
		RowRate=TheSettings["RowRate"]
		ColumnRate=TheSettings["ColumnRate"]

		# these will move to settings

		OutputRowStart=0
		OutputColumnStart=0

		InputColumnStart=0
		InputRowStart=0

		# can specify either a sample rate or a width and height in pixels for the output
		# below is specifying the sample rate

		OutputRowEnd=math.floor(InputHeightInPixels/RowRate)
		OutputColumnEnd=math.floor(InputWidthInPixels/ColumnRate)

		OutputDataset.HeightInPixels=OutputRowEnd
		OutputDataset.WidthInPixels=OutputColumnEnd

		# Need to call this function to resample the mask
		OutputMask=None
		InputMask=None

		# output the output bands
		OutputBands=[]
		InputBands=InputRasterDataset.GetBands()

		NumBands=OutputDataset.GetNumBands()

		# go through each of the rows in the output raster sampling data from the input rows
		BandIndex=0
		while (BandIndex<NumBands):

			OutputBands.append(numpy.zeros((OutputDataset.HeightInPixels,OutputDataset.WidthInPixels), dtype=NumPyType))

			BandIndex+=1

		# go through each row sampling data
		OutputRowIndex=OutputRowStart
		while (OutputRowIndex<OutputRowEnd):

			print("Processing row "+format(OutputRowIndex))

			# find the row in the input to get a sample for the output
			InputRowIndex=math.floor(OutputRowIndex*RowRate+InputRowStart)

			if ((InputRowIndex>=0) and (InputRowIndex<InputHeightInPixels)):

				OutputColumnIndex=OutputColumnStart
				while (OutputColumnIndex<OutputColumnEnd):

					InputColumnIndex=math.floor(OutputColumnIndex*ColumnRate+InputColumnStart)

					# Copy each of pixels into the input raster from the nearest output raster pixel
					if ((InputColumnIndex>=0) and (InputColumnIndex<InputWidthInPixels)):

						# only copy the data if there is no mask or the mask pixel is non-zero
						if ((InputMask==None) or (InputMask[InputRowIndex][InputColumnIndex]!=0)):

							# if there is a mask, set it to opaque
							if (OutputMask!=None):

								TheOutputMask[OutputRowIndex][OutputColumnIndex]=100

							BandIndex=0
							while (BandIndex<NumBands):
								OutputBand=OutputBands[BandIndex]
								InputBand=InputBands[BandIndex]

								OutputBand[OutputRowIndex][OutputColumnIndex]=InputBand[InputRowIndex][InputColumnIndex]

								BandIndex+=1

					OutputColumnIndex+=1

			OutputRowIndex+=1

		# add the new band to the output dataset
		OutputDataset.TheBands=OutputBands

		return(OutputDataset)

############################################################################################
# One-line functions
############################################################################################
def Load(Path1):
	
	TheDataset=SpaRasters.SpaDatasetRaster()
	TheDataset.Load(Path1)
	return(TheDataset)

def Resample(Input1, ZoomFactor):
	"""
	Resamples a raster based based on a specific zoom factor

	Parameters:
		Input1: SpaDatasetRaster object OR a string representing the path to the raster file

		ZoomFactor: A float representing the resample rate. Values <1 will 'zoom in', values >1 will 'zoom out'

	Returns:
		A SpaDatasetRaster object resampled to the given parameters

	"""
	Input1=SpaPy.GetInput(Input1)
	TheResampler=SpaRasters.SpaResample()
	return(TheResampler.Scale(Input1, ZoomFactor))

def ReclassifyDiscrete(Input1,InputClasses,OutputClasses):
	"""
	Resamples a raster into classes which represent a discrete set of values

	Parameters:
		Input1: SpaDatasetRaster object OR a string representing the path to the raster file

		Input classes: A discrete set of values ex:(10,20,30)
		
		Output classes: The desired classes ex:(1,2,3)

	Returns:
		A SpaDatasetRaster object

	"""	
	Input1=SpaPy.GetInput(Input1)
	return(Input1.Reclassify(InputClasses,OutputClasses,"discrete"))

def ReclassifyRange(Input1,InputClasses,OutputClasses):
	
	"""
	Resamples a raster into classes which represent a range of values

	Parameters:
		Input1: SpaDatasetRaster object OR a string representing the path to the raster file

		Input classes: the range of values to be reclassified ex:[(-1000,1),(1,3),(3,10000)]
		
		Output classes: The desired classes  ex:(1,2,3)
	Returns:
		A SpaDatasetRaster object

	"""		
	Input1=SpaPy.GetInput(Input1)
	return(Input1.Reclassify(InputClasses,OutputClasses,"range"))

def Crop(Input1,Bounds):
	"""
	Crops a raster to a specified extent using gdal.Translate()
	
	Parameters:
		Input1: SpaDatasetRaster object OR a string representing the path to the raster file
		
		Bounds: The desired extent formatted as [x1,y1,x2,y2]
	Returns:
		A SpaDatasetRaster object
	"""
	Input1=SpaPy.GetInput(Input1)
	TheResampler=SpaRasters.SpaResample()
	return(TheResampler.Crop(Input1,Bounds))

def NumpyCrop(Input1,Bounds):
	"""
	Crops a raster to a specified extent without using gdal
	
	Parameters:
		Input1: SpaDatasetRaster object OR a string representing the path to the raster file
		
		Bounds: The desired extent formatted as [x1,y1,x2,y2]
	Returns:
		A SpaDatasetRaster object
	"""
	Input1=SpaPy.GetInput(Input1)
	TheResampler=SpaRasters.SpaResample()
	return(TheResampler.NumpyCrop(Input1,Bounds))

