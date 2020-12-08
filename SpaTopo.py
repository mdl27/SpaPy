############################################################################
# Classes and functions for performing topographic functions on 
# spatially referenced raster data.
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
import numpy
import scipy
import ogr
import scipy.ndimage
from osgeo import osr
import gdal

# SpaPy libraries
import SpaPy
import SpaRasters
import SpaRasterMath

###############################################################################
# Class definition
###############################################################################
class SpaTopoTools(SpaPy.SpaTransform):
	#adapted from https://www.neonscience.org/create-hillshade-py
	def __init__(self):
		super().__init__()


	def Hillshade(self,Input1,azimuth=315,altitude=45):

		"""
		Creates a hillshade layer from a digital elevation model by determining hypothetical illumination
		values for each cell based on provided azimuth and altitude values

		Parameters:
			Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

		Return:
			A SpaDatasetRaster object depicting hillshade
		"""

		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(Input1)

		array=Input1.TheBands[0]
		azimuth = 360.0 - azimuth

		x, y = numpy.gradient(array)
		slope = numpy.pi/2. - numpy.arctan(numpy.sqrt(x*x + y*y))
		aspect = numpy.arctan2(-x, y)
		azimuthrad = azimuth*numpy.pi/180.
		altituderad = altitude*numpy.pi/180.

		shaded = numpy.sin(altituderad)*numpy.sin(slope) + numpy.cos(altituderad)*numpy.cos(slope)*numpy.cos((azimuthrad - numpy.pi/2.) - aspect)
		shaded = 255*(shaded + 1)/2

		NewDataset.TheBands=[shaded]
		return(NewDataset)

	def Slope(self,Input1):
		"""
		Creates a slope layer from a digital elevation model by calculating the steepness of each cell
		(returns with a value between 0-90 degrees)

		Parameters:
			Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

		Return:
			A SpaDatasetRaster object depicting slope
		"""

		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(Input1)

		GDALDataset = Input1.GDALDataset
		#GDALDataset = gdal.DEMProcessing('', GDALDataset, format="MEM", projWin = Bounds)
		gdal.DEMProcessing("./Temp/Test.tif", GDALDataset, 'slope')
		NewDataset.Load("./Temp/Test.tif")

		#TheBand=Input1.TheBands[0]
		#x,y = numpy.gradient(TheBand)
		#slope=numpy.pi/2. - numpy.arctan(numpy.sqrt(x*x +y*y))

		#NewDataset.TheBands = [slope]
		return(NewDataset)

	def Aspect(self,Input1):
		"""
		Creates an aspect layer from a digital elevation model by identifing the compass
		direction that the downhill slope faces for each location (returns with a value between 0-360 degrees)


		Parameters:
			Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

		Return:
			A SpaDatasetRaster object depicting aspect	
		"""

		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(Input1)

		GDALDataset = Input1.GDALDataset
		#GDALDataset = gdal.DEMProcessing('', GDALDataset, format="MEM", projWin = Bounds)
		gdal.DEMProcessing("./Temp/Test.tif", GDALDataset, 'aspect')
		NewDataset.Load("./Temp/Test.tif")
		#TheBand=Input1.TheBands[0]
		#x,y = numpy.gradient(TheBand)
		#aspect = numpy.arctan2(-x, y)
		#NewDataset.TheBands=[aspect]
		
		return(NewDataset)
	
	def gdaldem(self,Input1,Operation):
		
		"""
		Creates an aspect layer from a digital elevation model by identifing the compass
		direction that the downhill slope faces for each location (returns with a value between 0-360 degrees)


		Parameters:
			Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

		Return:
			A SpaDatasetRaster object depicting aspect	
		"""
		Input1=SpaPy.GetInput(Input1)
		
		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(Input1)

		GDALDataset1 = Input1.GDALDataset
		gdal.DEMProcessing("./Temp/Test.tif", GDALDataset1, Operation)
		NewDataset.Load("./Temp/Test.tif")
		NewDataset.NoDataValue=-9999
		
		return(NewDataset)

	
	def Contour(self,Input1,ContourInterval=100,contourBase=0,OutputFilePath=None):
		
		"""
		Creates a vector dataset with contour lines from a DEM.

		Parameters:
			Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

		Return:
			A SpaDatasetRaster object depicting aspect	
		"""
		Input1=SpaPy.GetInput(Input1)
		
		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(Input1)

		UseNoData=0
		NoDataValue=0
		if (Input1.GetNoDataValue()!=None):
			UseNoData=1
			NoDataValue=Input1.GetNoDataValue()
			
		TheBand = Input1.GDALDataset.GetRasterBand(1)
		
		#Generate layer to save Contourlines in
		ogr_ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(OutputFilePath)
		contour_shp = ogr_ds.CreateLayer('contour')
	
		field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
		contour_shp.CreateField(field_defn)
		field_defn = ogr.FieldDefn("elev", ogr.OFTReal)
		contour_shp.CreateField(field_defn)

		#ContourGenerate(Band srcBand, double contourInterval, double contourBase, int fixedLevelCount, int useNoData, double noDataValue, Layer dstLayer, int idField, int elevField, GDALProgressFunc callback=0, void * callback_data=None)
		gdal.ContourGenerate(TheBand, ContourInterval, contourBase, [], UseNoData,NoDataValue, contour_shp, 0, 1)
		
		return(NewDataset)

###############################################################################
# One line functions
###############################################################################
def Hillshade(Input1):
	"""
	Creates a hillshade from a digital elevation model by determining hypothetical illumination
	values for each cell based on given azimuth and altitude values

	Parameters:
		Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

	Return:
		A SpaDatasetRaster object
	"""

	Input1=SpaPy.GetInput(Input1)
	TheTopoTools=SpaTopoTools()
	return(TheTopoTools.Hillshade(Input1))

def Slope(Input1):
	"""
	Creates a slope layer from a digital elevation model by calculating the steepness of each cell
	(returns with a value between 0-90 degrees)

	Parameters:
	Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

	Return:
	A SpaDatasetRaster object depicting slope
	"""

	Input1=SpaPy.GetInput(Input1)
	TheTopoTools=SpaTopoTools()
	return(TheTopoTools.Slope(Input1))


def Aspect(Input1):
	"""
	Creates an aspect layer from a digital elevation model by identifing the compass
	direction that the downhill slope faces for each location (returns with a value between 0-360 degrees)

	Parameters:
		Input1: An SpaDatasetRaster object OR a string representing the path to the raster file

	Return:
		A SpaDatasetRaster object depicting aspect	
	"""	
	Input1=SpaPy.GetInput(Input1)
	TheTopoTools=SpaTopoTools()
	return(TheTopoTools.Aspect(Input1))

def TRI(Input1):
	TheTopoTools=SpaTopoTools()
	TheResult=TheTopoTools.gdaldem(Input1,"TRI")
	return(TheResult)

def TPI(Input1):
	TheTopoTools=SpaTopoTools()
	TheResult=TheTopoTools.gdaldem(Input1,"TPI")
	return(TheResult)

def Roughness(Input1):
	TheTopoTools=SpaTopoTools()
	TheResult=TheTopoTools.gdaldem(Input1,"roughness")
	return(TheResult)
	