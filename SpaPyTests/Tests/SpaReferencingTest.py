############################################################################
# Test File for the Spatial (Spa) libraries.  This file runs a series of tests
# for the spatial referencing (e.g. SRS, CRS) functions in SpaPy.
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
from osgeo import gdal
import math
import random

# SpaPy libraries
from SpaPy import SpaBase
from SpaPy import SpaPlot
from SpaPy import SpaVectors
from SpaPy import SpaView
from SpaPy import SpaReferencing
from SpaPy import SpaDensify
from SpaPy import SpaView
from SpaPy import SpaRasters
from SpaPy import SpaTopo
from SpaPy import SpaRasterVectors

CountriesFilePath="../Data/NaturalEarth/ne_110m_admin_0_countries.shp"

OverlayFile="../Data/Overlay/Box.shp"

HumbRiverPath="../Data/HumboldtCounty/hydrography/nhd24kst_l_ca023.shp"

HumbZoningPath="../Data/HumboldtCounty/humz55sp.shp"

Zoning_Bay="../Data/HumboldtCounty/Zoning_Bay.shp"

NASABlueMarble="../Data/NASA/BlueMarbleNG-TB_2004-12-01_rgb_1440x720.TIFF"

OutputFolderPath="../Temp/"

#########################################################################
AlbersEqualArea_Parameters={
	"datum":"WGS84",
	"proj":"aea",
	"lat_1":40,
	"lat_2":60
}

if (True):
	CountriesDataset=SpaVectors.SpaDatasetVector() #create a new layer
	CountriesDataset.Load(CountriesFilePath) # load the contents of the layer
	
	# Need to make sure each line segment has enough points to look good after being projected (i.e. the may curve)
	CountriesDataset=SpaDensify.Densify(CountriesDataset,5)
	
	# Clip the bounds of the geographic data to be within the possible bounds of the projection
	WestCoastDataset=SpaVectors.Clip(CountriesDataset,-156,-90,-90,90) # the zone is 6 degrees wide but we can go wider
	
	# WGS 84 / UTM zone 10N
	Dataset_UTMZone10North=SpaReferencing.Transform(WestCoastDataset,32610)
	SpaView.Show(Dataset_UTMZone10North)
	
	# Project from UTM to WGS 84
	UTMToGeographic=SpaReferencing.Transform(Dataset_UTMZone10North,4326)
	SpaView.Show(UTMToGeographic)
	
	UTMToGeographic.Save(OutputFolderPath+"Geographic.shp")
	
	# Project to NAD83 / California zone 1
	UTMToStatePlane=SpaReferencing.Transform(Dataset_UTMZone10North,26941)
	SpaView.Show(UTMToStatePlane)
	
	# Project to Albers Equal Area
	AlbersEqualArea=SpaReferencing.Transform(CountriesDataset,AlbersEqualArea_Parameters)
	SpaView.Show(AlbersEqualArea)

#######################################################################

BlueMarbleRaster=SpaRasters.SpaDatasetRaster() #create a new layer
BlueMarbleRaster.Load(NASABlueMarble) # load the contents of the layer

#SpaView.Show(BlueMarbleRaster)

# Currently, we are using a GDAL function that requires an output path for the projected raster file so there is a different function to projecting rasters
AlbersEqualArea=SpaReferencing.TransformRaster(BlueMarbleRaster,OutputFolderPath+"BlueMarble_Albers.tif",AlbersEqualArea_Parameters)
SpaView.Show(AlbersEqualArea)

# Project to UTM
AlbersEqualArea=SpaReferencing.TransformRaster(BlueMarbleRaster,OutputFolderPath+"BlueMarble_UTM.tif",32610)
SpaView.Show(AlbersEqualArea)