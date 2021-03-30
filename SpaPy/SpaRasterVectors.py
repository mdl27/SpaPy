###############################################################################################
# Seems like this should be part of SpaRasters
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
from SpaPy import SpaBase

############################################################################################

def Polygonize(Input1):
    """ 
    Converts a raster to a polygon feature set.  Each contiguous area of the raster
    (i.e. ajoining pixels that have the same value) are grouped as one polygon.  

    Parameters:
    	An SpaDatasetRaster object OR a string representing the path to the raster file
    Returns:
    	A RasterDataset
    """	
    Input1=SpaBase.GetInput(Input1)
    return(Input1.Polygonize())

