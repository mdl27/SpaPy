############################################################################
# Test File for the Spatial (Spa) libraries
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

# Spa Libraries
sys.path.append("./venv/Lib/site-packages/SpaPy")
import SpaPy
from SpaPy import SpaPlot
from SpaPy import SpaVectors
from SpaPy import SpaView
from SpaPy import SpaReferencing
from SpaPy import SpaDensify
from SpaPy import SpaTransform
from SpaPy import SpaTopo
from SpaPy import SpaRasterMath
import SpaView

############################################################################
# Globals
############################################################################

CountriesFilePath="./Examples/Data/NaturalEarth/ne_110m_admin_0_countries.shp"
RiversFilePath="./Examples/Data/NaturalEarth/ne_110m_rivers_lake_centerlines.shp"
CitiesFilePath="./Examples/Data/NaturalEarth/ne_110m_populated_places_simple.shp"

OutputFolderPath="."

RasterFilePath="./Examples/Data/MtStHelens/MtStHelensPostEruptionDEMInt16.tif"
#RasterFilePath2="../Data/MtStHelens/Mt St Helens PreEruption DEM Float32.tif"

Path1="./Examples/Data/MtStHelens/MtStHelensPreEruptionDEMFloat32.tif"
#Path2="../Data/MtStHelens/Mt St Helens Post Eruption DEM.tif"

############################################################################
# SpaView Tests
############################################################################
File1="Two Polygons1.shp"
File2="Two Polygons2.shp"

File1="Melody/Buffer/River_Buffer.shp"
File2="Melody/TPZ_UTM.shp"

TheDataset=SpaVectors.Intersection(File1,File2) #create a new layer
TheDataset.Save("Intersection1.shp")

SpaView.Show(TheDataset)

# Show a vector shapefile
#SpaView.Show(CountriesFilePath)