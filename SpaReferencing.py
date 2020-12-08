##############################################################################################################################
# Module with definitions for managing projections.
# 
# External Classes:
# - SpaProjector - base class for projectors
# - SpaProj - projector based on the proj4 engine
# - SpaProjectorGrid - grid based projector
#
# The easiest approach is to call the global function: Project(Input1,ProjectionCode,Parameters,LatNewPole)
# 1. Input1 can be a list of coordinate values, a polygon, 
# 2. ProjectionCode should be on of the Proj4 projection codes
# 3. Parameters is a dictionary with Key/Value pairs for the Proj4 parameters
# 4. LatNewPole is an optional parameter to shift the latitude of the north pole
#
# To use SpaProj:
# 1. Create an SpaProj object with: 
#    TheProjector=TheProjectorProj=SpaProj()
# 2. Set the projection settings by passing a dictionary object to SetSettings():
#
#		TheProjectorProj.SetSettings(SpaProj,{
#		    "ProjectionCode":ProjectionCode,
#		    "LatNewPole":LatNewPole, # optional
#		    "Parameters":Parameters,
#		})
#
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
import math
import os
import sys

# Open source spatial libraries
import pyproj
import shapely
import shapely.geometry
import gdal

# SpaPy libraries
import SpaVectors 
import SpaPy
import SpaRasters

################################################################
# Base class for projectors
################################################################
class SpaProjector(SpaPy.SpaBase):
	""" 
	Abstract class to define projectors
	"""
	def __init__(self):
		super().__init__()
		# below are the properties that make up a shapefile using Fiona for reading and writing from and to shapefiles
		self.TheProjection=None

	def ProjectFromGeographic(self,TheObject):
		""" 
		Abstract function to be overriden by subclasses.  Takes TheObject and converts
		its coordinates from Goegraphic to the specified spatial reference.
		
		Parameters:
			TheObject:
				raster or vector object to be projected
		Return:
			none
		"""

		Result=None
		
		return(Result)

############################################################################
# Public class to project based on the Proj4 library
############################################################################

class SpaProj(SpaProjector):
	""" 
	Class to manage the data associated with a spatial layer
	"""
	def __init__(self):
		super().__init__()
		# below are the properties that make up a shapefile using Fiona for reading and writing from and to shapefiles
		self.Reset()

		self.SetSettings(SpaProj,{
		    "LatNewPole":None, # optional
		    "Parameters":None,
		})
		self.ErrorMessages=""
		self.WarningMessages=""
		self.InfoMessages=""
	############################################################################
	# Private Functions
	############################################################################
	def AddToErrorMessages(self,TheMessage):
		self.ErrorMessages=self.ErrorMessages+", "+TheMessage

	def AddToWarningMessages(self,TheMessage):
		self.WarningMessages=self.WarningMessages+", "+TheMessage

	def AddToInfoMessages(self,TheMessage):
		self.InfoMessages=self.InfoMessages+", "+TheMessage

	############################################################################
	# SpaBase Functions
	############################################################################
	def SetSettings(self,Class,Settings):
		super().SetSettings(Class,Settings)

		self.Reset()

	############################################################################
	# SpaProjector Functions
	############################################################################
	def Reset(self):
		"""
		Resets the current projection
		
		Parameters:
			none
		Returns:
			none
		"""
		self.TheProjection=None

	def ProjectCoordinateFromGeographic(self,X,Y):
		""" 
		Projects a simple coordinate.  Can be overridden by subclasses to create new projectors
		"""

		TheCoordinate=self.TheProjection(X,Y)
		
		return(TheCoordinate)
	
	def ProjectFromGeographic(self,TheObject):
		""" 
		Handles projecting a wide variety of types of data
		
		This function will be called recursively for datasets and shapely geometries until coordiantes are
		reached and then ProjectCoordinateFromGeographic() will be called.  Shapely is very picky about
		the contents of geometries so anything that is not considered valid is not added to the result.
		
		Parameters:
			TheObject:
				Vector object to be projected
		Return:
			none
		""" 

		self.Initialize()

		Result=None

		if (isinstance(TheObject,SpaVectors.SpaDatasetVector)): # have a layer, make a duplicate and then project all the contents of the layer
			NewLayer=SpaVectors.SpaDatasetVector()
			NewLayer.CopyMetadata(TheObject)

			NumFeatures=TheObject.GetNumFeatures()
			FeatureIndex=0
			while (FeatureIndex<NumFeatures): # interate through all the features finding the intersection with the geometry
				TheGeometry=TheObject.TheGeometries[FeatureIndex]

				TheGeometry=self.ProjectFromGeographic(TheGeometry)

				if (TheGeometry!=None):
					NewLayer.AddFeature(TheGeometry,TheObject.TheAttributes[FeatureIndex])

				FeatureIndex+=1
				
			TheCRS=self.GetProjParametersFromSettings()
			
			NewLayer.SetCRS(TheCRS)
			
			Result=NewLayer

		elif (isinstance(TheObject,shapely.geometry.MultiPolygon)): # have a polygon, 
			ThePolygons=[]
			for ThePolygon in TheObject:
				NewPolygon=self.ProjectFromGeographic(ThePolygon) # deal with interior polys later
				if (NewPolygon!=None):
					ThePolygons.append(NewPolygon)
			if (len(ThePolygons)>0):
				Result=shapely.geometry.MultiPolygon(ThePolygons)

		elif (isinstance(TheObject,shapely.geometry.MultiLineString)): # have an array of line strings , 
			TheLineStrings=[]
			for TheLineString in TheObject:
				NewLineString=self.ProjectFromGeographic(TheLineString) # deal with interior polys later
				if (NewLineString!=None):
					TheLineStrings.append(NewLineString)
			if (len(TheLineStrings)>0):
				Result=shapely.geometry.MultiLineString(TheLineStrings)

		elif (isinstance(TheObject,shapely.geometry.Polygon)): # have a polygon, 
			TheCoordinates=self.ProjectFromGeographic(TheObject.exterior.coords) # deal with interior polys later
			if (TheCoordinates!=None):
				if (len(TheCoordinates)>=3): # polygon must have at least 3 coordinates
					Result=shapely.geometry.Polygon(TheCoordinates)

		elif (isinstance(TheObject,shapely.geometry.LineString)): # have a polygon, 
			TheCoordinates=self.ProjectFromGeographic(TheObject.coords) # deal with interior polys later
			if (len(TheCoordinates)>=2): # polygon must have at least 3 coordinates
				Result=LineString(TheCoordinates)

		elif (isinstance(TheObject,shapely.coords.CoordinateSequence)): # have an shapely coordinate sequence
			Result=[]
			for TheEntry in TheObject:
				Coordinate2=self.ProjectFromGeographic(TheEntry)
				if (Coordinate2!=None):
					Easting2=Coordinate2[0]
					Northing2=Coordinate2[1]

					if ((math.isnan(Easting2)==False) and (math.isnan(Northing2)==False) and (Easting2!=1e+30) and (Northing2!=1e+30)
					    and (math.isfinite(Northing2)) and (math.isfinite(Easting2))):
						Result.append((Easting2,Northing2))

		elif (isinstance(TheObject,SpaRasters.SpaDatasetRaster)): # have a raster
			raise("Sorry, you'll need to call ProjectRaster()")
			# 
			#raise Exception("Sorry, SpPy does not yet support projecting raster datasets")
		else: # should be two coordinate values		
			if (TheObject!=None) and (self.TheProjection!=None):
				
				Coordinate=TheObject
				
				if (len(Coordinate)>0):
					X=Coordinate[0]
					
					if (isinstance(X, (list, tuple, set))): # have an array of coordinate pairs
						Result=[]
						for TheCoordinate in Coordinate:
							TheCoordinate=self.ProjectCoordinateFromGeographic(TheCoordinate[0],TheCoordinate[1])
							Result.append(TheCoordinate)
							
					else: # Must be a single coordinate
						Y=Coordinate[1]
					
						Result=self.ProjectCoordinateFromGeographic(X,Y)


		return(Result)
	
	def ProjectRaster(self,TheObject,OutputFilePath): # Create the destination SRS
		"""
		Projects a raster dataset
		
		Parameters:
			TheRaster:
				Raster dataset to be projected
			OutputFilePath: 
				File path to location where output will be stored
		Returns:
			Projected raster dataset
		"""
		Settings=self.GetSettings(SpaProj)

		#self.TheProjection=GetProjection(,LatNewPole,Settings["Parameters"])
		#ProjectionCode=Settings["ProjectionCode"]
		Parameters=Settings["Parameters"]

		DesitnationSRS="" #"+proj="+ProjectionCode
		
		for key in Parameters:
			DesitnationSRS+=" +"+key+"="+format(Parameters[key])
			
		# Create the new dataset
		NewDataset=SpaRasters.SpaDatasetRaster()
		NewDataset.CopyPropertiesButNotData(TheObject)
		NewDataset.AllocateArray()
		NewDataset.Save(OutputFilePath) # this is ugly but it is the only way we could figure out to create a GDALDataset
		#NewDataset.Load(OutputFilePath)
		
		InputGDALDataset = TheObject.GDALDataset
		#OutputGDALDataset = NewDataset.GDALDataset
		GDALDataset = gdal.Warp(OutputFilePath,InputGDALDataset,dstSRS=DesitnationSRS)
		
		NewDataset.Load(OutputFilePath)
		
		return(NewDataset)
	############################################################################
	# SpaProj Protected Functions
	############################################################################
	def Initialize(self):
		if (self.TheProjection==None):
			#Settings=self.GetSettings(SpaProj)

			#LatNewPole=90
			#if (Settings["LatNewPole"]!=None): LatNewPole=Settings["LatNewPole"]

			# sets up the projection
			self.GetProjection() # sets the member variable this.TheProjection

	############################################################################
	# SpaProj Public Functions
	############################################################################
	def GetProjParametersFromSettings(self):
		# setup the parameters
		Settings=self.GetSettings(SpaProj)

		LatNewPole=90
		if (Settings["LatNewPole"]!=None): LatNewPole=Settings["LatNewPole"]

		#self.TheProjection=GetProjection(,LatNewPole,Settings["Parameters"])
		#ProjectionCode=Settings["ProjectionCode"]
		Parameters=Settings["Parameters"]

		if (isinstance(Parameters,int)): # must be an epsg code
			ProjParameters=Parameters
		else:
			# setup the Projectin parameters as a copy of the set parameters plus anything else we might need
			ProjParameters={}
			
			Flag=("no_defs" in Parameters.keys())
			
			if (Flag==False): 
				ProjParameters={ 'no_defs': True }
				#	ProjParameters["ellps"]=self.Datum
				#	ProjParameters["datum"]=self.Datum
					
			# Copy the rest of the parameters over
			if (Parameters!=None):
				for key in Parameters:
					ProjParameters[key]=Parameters[key]
				
			if (LatNewPole==90): # not oblique
				j=12
				#ProjParameters["proj"]=ProjectionCode
			else: # oblique with NewLatPole as the latitude of the new pole
				ProjParameters["o_proj"]=ProjParameters["proj"] # projection becomes the o_proj
				ProjParameters["proj"]="ob_tran"
				ProjParameters["o_lat_p"]=LatNewPole

		return(ProjParameters)
	
	def GetProjection(self):
		""" 
		Get a projection from the proj4 library
		
		Parameters:
			none
		Returns:
			Projection type of raster or vector dataset object
		        
		"""


		if (self.TheProjection==None):
			# setup the parameters
			#Settings=self.GetSettings(SpaProj)

			#LatNewPole=90
			#if (Settings["LatNewPole"]!=None): LatNewPole=Settings["LatNewPole"]

			##self.TheProjection=GetProjection(,LatNewPole,Settings["Parameters"])
			#ProjectionCode=Settings["ProjectionCode"]
			#Parameters=Settings["Parameters"]

			#if (LatNewPole==90): # not oblique
				#ProjParameters={ "proj":ProjectionCode,"ellps":'WGS84'}
			#else: # oblique with NewLatPole as the latitude of the new pole
				#ProjParameters={ "proj":"ob_tran","o_proj":ProjectionCode,"o_lat_p":LatNewPole,"ellps":'WGS84'}

			## get the parameters for the projection

			#if (Parameters!=None):
				#for key in Parameters:
					#ProjParameters[key]=Parameters[key]

			ProjParameters=self.GetProjParametersFromSettings()
			
			try:
				# Create the projection object from the parameters
				self.TheProjection=pyproj.Proj(projparams=ProjParameters) # 

			except Exception  as TheException:
				Message="Proj failed to create projector for: "+format(ProjParameters)+"\n\n "+format(TheException)
				print("**** "+Message)		
				self.AddToErrorMessages(Message)
				raise Exception(Message)

		return(self.TheProjection)


################################################################
# Public Utility functions
################################################################

def Project(Input1,Parameters,LatNewPole=90):
	"""
	Project just about anything to a new spatial reference.
	Currently, it is assume the inputs are in geographic coordinates and the datum does not change.
	
	Parameters:
		Input1: vector dataset object to be projected
		Parameters: input dataset parameters
		LatNewPole: Optional-input latitude of new pole if desired
	Returns:
	        Projected raster or vector dataset object
	"""
	Input1=SpaPy.GetInput(Input1)

	TheProjector=SpaProj()
	TheProjector.SetSettings(SpaProj,{
	    "LatNewPole":LatNewPole, # optional
	    "Parameters":Parameters,
	})
	#
	NewLayer=TheProjector.ProjectFromGeographic(Input1)
	return(NewLayer)

def ProjectRaster(Input1,Parameters,OutputFilePath=None):
	"""
	Project just about anything to a new spatial reference.
	Currently, it is assume the inputs are in geographic coordinates and the datum does not change.
	
	Parameters:
		Input1: raster or vector dataset object to be projected
		Parameters: input dataset parameters
	Returns:
	        Projected raster dataset object
	"""
	Input1=SpaPy.GetInput(Input1)

	TheProjector=SpaProj()
	TheProjector.SetSettings(SpaProj,{
	    "Parameters":Parameters,
	})
	#
	NewLayer=TheProjector.ProjectRaster(Input1,OutputFilePath)
	return(NewLayer)

