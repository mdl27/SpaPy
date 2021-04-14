"""
Nicholas Klein-Baer
Created 3/15/19
Updated 3/26/19
Assignment 8 - Part 1
Batch Processing lidar data w/ arcpy
"""

# Open source spatial libraries
import sys
sys.path.append("../../SpaPy")

#dependencies
import SpaRasters
import os

InputPath = "../Data/"
OutputPath = "../Temp/"

List=os.listdir(InputPath)

for File in List:
    #FileName, FileExtension = os.path.split(File) #for some reason os.path.split is not working here in 3.6.1 ...
    try:
        FileName, FileExtension = File.split(".")
    except:
        continue

    InputFilePath = InputPath + FileName + "." + FileExtension
    print(InputFilePath)
    if (FileExtension == "tif"):
            print("Found a file to process:" + InputFilePath)
            
            Reclass = SpaRasters.ReclassifyRange(InputFilePath,[(-1000,1),(1,3),(3,10000)],[1,2,3])
            Reclass.Save(OutputPath + "{0}Reclass.tif".format(FileName))
            Grass = SpaRasters.LessThan(InputFilePath,1)
            Grass.Save(OutputPath + "{0}Grass.tif".format(FileName))
            
            Trees = SpaRasters.GreaterThan(InputFilePath,4)
            Trees.Save(OutputPath + "{0}Trees.tif".format(FileName))
            
            #No Boolean functions, so this is a little work around
            NotGrass = SpaRasters.GreaterThan(InputFilePath,1)
            NotTrees = SpaRasters.LessThan(InputFilePath,4)
            Shrubs = SpaRasters.Multiply(NotGrass,NotTrees)
            Shrubs.Save(OutputPath + "{0}Shrubs.tif".format(FileName))
            
            ShrubClass = SpaRasters.Multiply(Shrubs, 2)
            ShrubClass.Save(OutputPath + "{0}ShrubClass.tif".format(FileName))
            OtherShrubClass = SpaRasters.ReclassifyDiscrete(Shrubs,[0,1],[0,2])
            OtherShrubClass.Save(OutputPath + "{0}OtherShrubClass.tif".format(FileName))
            
            TreeClass = SpaRasters.Multiply(Trees,3)
            TreeClass.Save(OutputPath + "{0}TreeClass.tif".format(FileName))
            
            ClassRaster = SpaRasters.Add(Grass,TreeClass)
            ClassRaster = SpaRasters.Add(ClassRaster,ShrubClass)
            ClassRaster.Save(OutputPath + "{0}ClassRaster.tif".format(FileName))
            
           
            ResampleRaster = SpaRasters.Resample(ClassRaster, 1/30)
            ResampleRaster.Save(OutputPath + "{0}ResampleRaster.tif".format(FileName))
         
            ResampleRaster = SpaRasters.SpaDatasetRaster()
            ResampleRaster.Load(OutputPath + "{0}ResampleRaster.tif".format(FileName))
            ResampleRaster.Polygonize(OutputPath+"{0}PolygonizedRaster.tif".format(FileName))
           
"""
***************************************************************************
 Copyright (C) 2020, Humboldt State University, Jim Graham

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software  Foundation, either version 3 of the License, or (at your
option) any later  version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License for more details.

A copy of the GNU General Public License is available at
<http://www.gnu.org/licenses/>.
***************************************************************************
"""