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
import gdal

# Spa Libraries
sys.path.append(".")
import SpaPlot
import SpaView
import SpaRasters
import SpaTopo
import SpaRasterVectors

############################################################################
# Globals
############################################################################

RasterFilePath="./Examples/Data/MtStHelens/MtStHelensPreEruptionDEMFloat32.tif"

TempFolderPath="./Temp/"

#########################################################################
# Raster opterations
#########################################################################

TheDataset =SpaRasters.SpaDatasetRaster()
TheDataset.Load(RasterFilePath)

print("____________________________________")
print("Loading Raster: "+RasterFilePath)

print(TheDataset.GetDriverNames())

print("Width in pixels: "+format(TheDataset.GetWidthInPixels()))

print("Height in pixels: "+format(TheDataset.GetHeightInPixels()))

print("Pixel Type: "+format(TheDataset.GetType()))

print("Projection:".format(TheDataset.GetProjection()))

TheBounds=TheDataset.GetBounds()
print("TheBounds="+format(TheBounds))
Xmin,Ymax = TheDataset.XMin, TheDataset.YMax
print("TheXmin="+format(Xmin))
print("TheYmax="+format(Ymax))

TheBand=TheDataset.GetBandInfo(1) # band numbers start at 1
print("TheBandInfo="+format(TheBand))

# Run this function to execute tests
#######################################################################
# Get information on an existing raster and save it to a new name

if (True): #for toggling code on/off for debugging

	TheDataset =SpaRasters.SpaDatasetRaster()
	TheDataset.Load(RasterFilePath)

	print("____________________________________")
	print("Loading Raster: "+RasterFilePath)

	print(TheDataset.GetDriverNames())

	print(TheDataset.GDALDataset.GetMetadata()) # empty

	print("Width in pixels: "+format(TheDataset.GetWidthInPixels()))

	print("Height in pixels: "+format(TheDataset.GetHeightInPixels()))

	print("Num Bands: "+format(TheDataset.GetNumBands()))

	print("Pixel Type: "+format(TheDataset.GetType()))

	print("Projection: "+format(TheDataset.GetProjection()))

	print("Resolution (x,y): "+format(TheDataset.GetResolution()))

	TheBounds=TheDataset.GetBounds()
	print("TheBounds (XMin,YMin,YMax,XMax): "+format(TheBounds))

	TheBandStats=TheDataset.GetBandInfo(1)
	print("TheBandStats="+format(TheBandStats))

	TheWKT=TheDataset.TheWKT
	print("TheWKT="+format(TheBandStats))

	#TheBand=TheDataset.GetBandAsArray(1)
	#print("TheBands: "+format(TheBand))

	TheDataset.Save(TempFolderPath+"CopiedRaster.tif")
#######################################################################
# Test writing out a new raster

if (True):
	WidthInPixels=100
	HeightInPixels=100

	TheDataset=SpaRasters.SpaDatasetRaster()
	TheDataset.SetWidthInPixels(WidthInPixels)
	TheDataset.SetHeightInPixels(HeightInPixels)
	TheDataset.SetType(gdal.GDT_Float32)

	TheBands=TheDataset.AllocateArray()
	TheBands=TheBands[0]

	Row=0
	while (Row<HeightInPixels):
		Column=0
		while (Column<WidthInPixels):
			TheBands[Row][Column]=Column
			Column+=1
		Row+=1
	print(TheBands)

	TheDataset.SetUTM(10)
	TheDataset.SetNorthWestCorner(400000,4000000)
	TheDataset.SetResolution(30,30)
	TheDataset.Save(TempFolderPath+"NewRaster.tif")


#######################################################################
# Transform an existing raster

# Clone
if (True):
	TheDataset=SpaRasters.SpaDatasetRaster()
	TheDataset.Load(RasterFilePath)
	NewDataset=TheDataset.Clone()
	NewDataset.Save(TempFolderPath+"ClonedRaster.tif")

# Basic Math
if (True):
	NewDataset=SpaRasters.Add(TheDataset,10)
	NewDataset.Save(TempFolderPath+"Raster_Add10.tif")

	NewDataset=SpaRasters.Subtract(TheDataset,10)
	NewDataset.Save(TempFolderPath+"Raster_SUBTRACT10.tif")

	NewDataset=SpaRasters.Multiply(TheDataset,10)
	NewDataset.Save(TempFolderPath+"Raster_MULTIPLY_10.tif")

	NewDataset=SpaRasters.Divide(TheDataset,10)
	NewDataset.Save(TempFolderPath+"Raster_DIVIDE_10.tif")

if (True):
	TheDataset=SpaRasters.SpaDatasetRaster()
	TheDataset.Load(RasterFilePath)

	TheSampler=SpaRasters.SpaResample()

	# resize the raster
	NewDataset=TheSampler.Scale(TheDataset,0.2) # really fast
	NewDataset.Save(TempFolderPath+"Zoomed.tif")

	# extract a portion of the raster
	NewDataset1=TheSampler.ExtractByPixels(TheDataset,15,30,30,100) # really fast
	NewDataset1.Save(TempFolderPath+"Extraction.tif")

#Test Comparison Operators
if (True):
	RasterFile2 = SpaRasters.LessThan(RasterFilePath,5)
	NewDataset=SpaRasters.LessThan(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"LessThan.tif")

	NewDataset=SpaRasters.GreaterThan(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"GreaterThan.tif")

	NewDataset=SpaRasters.LessThanOrEqual(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"LessThanOrEqual.tif")

	NewDataset=SpaRasters.GreaterThanOrEqual(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"GreaterThanOrEqual.tif")

	NewDataset=SpaRasters.Equal(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"Equal.tif")

	NewDataset=SpaRasters.Maximum(RasterFilePath, RasterFile2)
	NewDataset.Save(TempFolderPath + "Maximum.tif")

	NewDataset=SpaRasters.Minimum(RasterFilePath, RasterFile2)
	NewDataset.Save(TempFolderPath + "Minimum.tif")


#Test Arthmetic Operator
if (True):

	RasterFile2 = SpaRasters.LessThan(RasterFilePath,5)
	NewDataset=SpaRasters.Add(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"Add.tif")
	NewDataset=SpaRasters.Add(RasterFilePath,2)
	NewDataset.Save(TempFolderPath+"Add1.tif")
	NewDataset=SpaRasters.Add(2,RasterFilePath)
	NewDataset.Save(TempFolderPath+"Add2.tif")

	NewDataset=SpaRasters.Subtract(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"Subtract.tif")
	NewDataset=SpaRasters.Subtract(RasterFilePath,2)
	NewDataset.Save(TempFolderPath+"Subtract1.tif")
	NewDataset=SpaRasters.Subtract(1,RasterFile2)
	NewDataset.Save(TempFolderPath+"Subtract2.tif")

	NewDataset=SpaRasters.Divide(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"divide.tif")
	NewDataset=SpaRasters.Divide(RasterFilePath,3)
	NewDataset.Save(TempFolderPath+"divide1.tif")
	NewDataset=SpaRasters.Divide(1,RasterFile2)
	NewDataset.Save(TempFolderPath+"divide2.tif")

	NewDataset=SpaRasters.Multiply(RasterFilePath,RasterFile2)
	NewDataset.Save(TempFolderPath+"Multiple.tif")
	NewDataset=SpaRasters.Multiply(RasterFilePath,3)
	NewDataset.Save(TempFolderPath+"Multiple1.tif")
	NewDataset=SpaRasters.Multiply(1.0,RasterFile2)
	NewDataset.Save(TempFolderPath+"Multiple2.tif")

#Test Logical Operators
if (True):
	#create some boolean rasters to work with
	RasterFile2 =SpaRasters.LessThan(RasterFilePath,5)
	BoolRaster1=SpaRasters.GreaterThan(RasterFilePath,RasterFile2)
	BoolRaster2=SpaRasters.LessThan(RasterFilePath,RasterFile2)

	NewDataset=SpaRasters.And(BoolRaster1,BoolRaster2)
	NewDataset.Save(TempFolderPath + "And.tif")

	NewDataset=SpaRasters.Or(BoolRaster1,BoolRaster2)
	NewDataset.Save(TempFolderPath + "Or.tif")

	NewDataset=SpaRasters.Not(BoolRaster1)
	NewDataset.Save(TempFolderPath + "Not.tif")

#Test Rounding Functions:
if (True):
	#create a raster with decimal numbers
	DecimalRaster=SpaRasters.Divide(RasterFilePath,RasterFile2)
	DecimalRaster.Save(TempFolderPath + "Divide.tif")

	NewDataset=SpaRasters.Round(DecimalRaster, 1)
	NewDataset.Save(TempFolderPath + "Round.tif")

	NewDataset=SpaRasters.RoundInteger(DecimalRaster)
	NewDataset.Save(TempFolderPath + "Int.Tif")

	NewDataset=SpaRasters.RoundFix(DecimalRaster)
	NewDataset.Save(TempFolderPath + "Fix.tif")

	NewDataset=SpaRasters.RoundFloor(DecimalRaster)
	NewDataset.Save(TempFolderPath + "Floor.tif")

	NewDataset=SpaRasters.RoundCeiling(DecimalRaster)
	NewDataset.Save(TempFolderPath + "Ceiling.tif")

	NewDataset=SpaRasters.Truncate(DecimalRaster)
	NewDataset.Save(TempFolderPath + "Truncate.tif")

#test other math function

if (True):

	NewDataset=SpaRasters.NaturalLog(RasterFilePath)
	NewDataset.Save(TempFolderPath + "NatLog.tif")

	NewDataset=SpaRasters.Log(RasterFilePath)
	NewDataset.Save(TempFolderPath + "Log.tif")

	NewDataset=SpaRasters.Exponential(RasterFilePath)
	NewDataset.Save(TempFolderPath + "Exponential.tif")

	NewDataset=SpaRasters.Power(RasterFilePath, 2)
	NewDataset.Save(TempFolderPath + "Power.tif")

	NewDataset=SpaRasters.Square(RasterFilePath)
	NewDataset.Save(TempFolderPath + "Square.tif")

	NewDataset=SpaRasters.SquareRoot(RasterFilePath)
	NewDataset.Save(TempFolderPath + "SquareRoot.tif")

	NewDataset=SpaRasters.AbsoluteValue(RasterFilePath)
	NewDataset.Save(TempFolderPath + "Abs.tif")


# test resampler
if (True):
	NewDataset=SpaRasters.Resample(RasterFilePath,0.5)
	NewDataset.Save(TempFolderPath + "Resampled.tif")

# test reclassify
if (True):
	NewDataset=SpaRasters.ReclassifyRange(RasterFilePath,[(-1000,1),(1,3),(3,10000)],[1,2,3])
	NewDataset.Save(TempFolderPath + "Reclassed.tif")

#test crop
if (True):
	print("*** Performing crop tests")
	NewDataset=SpaRasters.Crop(RasterFilePath,[543826,4257679,543924,4257589])
	NewDataset.Save(TempFolderPath+"Cropped.tif")

	NewDataset=SpaRasters.NumpyCrop(RasterFilePath,[543826,4257679,543924,4257589])
	NewDataset.Save(TempFolderPath+"NumpyCropped.tif")

if (True):
	print("*** Performing polygonize test")
	NewDataset=SpaRasterVectors.Polygonize(RasterFilePath)
	NewDataset.Save(TempFolderPath + "Polygonize.shp")

# topographic transforms
if (True):
	print("*** Performing topography tests")
	NewDataset=SpaTopo.Hillshade(RasterFilePath)
	NewDataset.Save(TempFolderPath+"Hillshade.tif")

	NewDataset=SpaTopo.Slope(RasterFilePath)
	NewDataset.Save(TempFolderPath+"Slope.tif")

	NewDataset=SpaTopo.Aspect(RasterFilePath)
	NewDataset.Save(TempFolderPath+"Aspect.tif")



print("DONE")

