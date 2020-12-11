############################################################################
# One line raster math functions.  These functions do not require a loaded
# dataset and can operate with files, datasets, or scalar values.
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
import SpaPy
import SpaRasters
############################################################################
# Constants
############################################################################
# Basic Arithmatic
SPAMATH_ADD=1
SPAMATH_SUBTRACT=2
SPAMATH_MULTIPLY=3
SPAMATH_DIVIDE=4

# Rounding
SPAMATH_ROUND=100
SPAMATH_ROUND_INTEGER=101
SPAMATH_ROUND_FIX=102
SPAMATH_ROUND_FLOOR=103
SPAMATH_ROUND_CEIL=104
SPAMATH_ROUND_TRUNC=105

# Logical
SPAMATH_AND=201
SPAMATH_OR=202
SPAMATH_NOT=203
SPAMATH_LESS=204
SPAMATH_LESS_OR_EQUAL=205
SPAMATH_EQUAL=206
SPAMATH_NOT_EQUAL=207
SPAMATH_GREATER=208
SPAMATH_GREATER_OR_EQUAL=209

# Othermath
SPAMATH_NATURAL_LOG=300
SPAMATH_LOG=301
SPAMATH_EXPONENT=302
SPAMATH_SQUARE=303
SPAMATH_SQUARE_ROOT=304
SPAMATH_ABSOLUTE=305
SPAMATH_MAX=306
SPAMATH_MIN=307
SPAMATH_POWER=309
SPAMATH_CLIP_TOP=308
SPAMATH_CLIP_BOTTOM=309
# Trig

#######################################################################
# one line raster transforms
#######################################################################

#######################################################################
# Basic math
def Add(Input1,Input2):
        """
        Performs pixel-wise addition of two rasters OR of one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object where the value of each cell is equal to the sum of the values of the corresponding cells in each of the two inputs.
        """
        #allows for parameters to be in any order
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1 #switches the values of Input1 and Input2

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ADD,Input2))

def Subtract(Input1,Input2):
        """
        One-line function for pixel-wise subtraction of two rasters OR of one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object where the value of each cell is equal to the difference of the values of the corresponding cells in each of the two inputs.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1 

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_SUBTRACT,Input2))

def Multiply(Input1,Input2):
        """
        One-line function for pixel-wise multiplication of two rasters OR of one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object where the value of each cell is equal to the product of the values of the corresponding cells in each of the two inputs.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_MULTIPLY,Input2))

def Divide(Input1,Input2):
        """
        One-line function for pixel-wise division two rasters OR of one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object where the value of each cell is equal to the quotient of the values on the corresponding cells in each of the two inputs.
        """
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_DIVIDE,Input2))


#######################################################################
# Logical
def Equal(Input1,Input2):
        """
        One-line function for pixel-wise comparison between two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is equal to Input2 and 0 for cells where it is not.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_EQUAL,Input2))

def NotEqual(Input1,Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is not equal to Input2 and 0 for cells where it is.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1    
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_NOT_EQUAL,Input2))


def LessThan(Input1,Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is less than Input2 and 0 for cells where it is not.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1 

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_LESS,Input2))

def GreaterThan(Input1,Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is greater than Input2 and 0 for cells where it is not
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_GREATER,Input2))

def LessThanOrEqual(Input1,Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is less than or equal to Input2 and 0 for cells where it is not.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_LESS_OR_EQUAL,Input2))

def GreaterThanOrEqual(Input1,Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object with values of 1 for cells where Input1 is greater than or equal to Input2 and 0 for cells where it is not.
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_GREATER_OR_EQUAL,Input2))


def Maximum(Input1, Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: A SpaDatasetRaster object OR a string represening the path to the raster file.

        	Input2: Same as above OR a constant value as an integer or a float.

        Returns
        	A SpaDatasetRaster object where each cell is equal to the greater value of the corresponding cells in each of the two inputs
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1    
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_MAX,Input2))

def Minimum(Input1, Input2):
        """
        One-line function for pixel-wise comparison of two rasters OR between one raster and a constant. The order of the parameters does not matter.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        	Input2: SpaDatasetRaster object OR a string representing the path to the raster file OR a number as a float.

        Returns
        	A SpaDatasetRaster object where each cell is equal to lesser of the corresponding cells in each of the two inputs
        """	
        if isinstance(Input1,(int,float)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_MIN,Input2))
def And(Input1,Input2):
        """
        One-line function for logical operation between two boolean rasters OR between one boolean raster and a constant boolean value. The order of the parameters does not matter.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        	Input2: Same as above, or a boolean or an int.

        Returns
        	A SpaDatasetRaster object where each cell true if the corresponding cells in both inputs are true. 
        """	
        if isinstance(Input1,(bool,int)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_AND,Input2))

def Or(Input1,Input2):
        """
        One-line function for logical operation between two boolean rasters OR between one boolean raster and a constant boolean value. The order of the parameters does not matter.

        Parameters:
            Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        	Input2: Same as above, or a boolean or an int.

        Returns
        	A SpaDatasetRaster object where each cell true if the corresponding cells in either inputs are true. 
        """	
        if isinstance(Input1,(bool,int)):
                Input1, Input2 = Input2, Input1

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_OR,Input2))

def Not(Input1):
        """
        One-line function for logical operation between two boolean rasters OR between one boolean raster and a constant boolean value. The order of the parameters does not matter.

        Parameters:
            Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        	Input2: Same as above, or a boolean or an int.

        Returns
        	A SpaDatasetRaster object where each cell has the opposite value of the input. 
        """	  

        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_NOT,0))


#######################################################################
# Rounding
def Round(Input1, Precision):
        """
        One-line function for rounding a raster to a specified precision.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.
        	Precision: An integer representing the number of decimal places to be rounded too (dafualt = 0)
        Returns
        	A SpaDatasetRaster object where each cell has been rounded to the specified degree of precision.
        """		
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND, Precision))

def RoundInteger(Input1):
        """
        One-line function for rounding a raster. 

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object where each cell has been rounded to the nearest integer.
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND_INTEGER,0))

def RoundFix(Input1):
        """
        One-line function for rounding a raster 

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object where each cell has been rounded to the nearest integer torwards zero.
        """		
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND_FIX,0))
def RoundFloor(Input1):
        """
        One-line function for rounding a raster 

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object where each cell has been rounded to the nearest integer less than or equal to the input.
        """		
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND_FLOOR,0))
def RoundCeiling(Input1):
        """
        One-line function for rounding a raster 

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object where each cell has been rounded to the nearest integer greater than or equal to the input.
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND_CEIL,0))
def Truncate(Input1):
        """
        One-line function for rounding a raster 

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object where the decimal portion of the input has been discarded	
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ROUND_TRUNC,0))

#######################################################################
#Unary Math

def NaturalLog(Input1):
        """
        Computes the natural logarithm of a raster.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_NATURAL_LOG,0))

def Log(Input1):
        """
        Computes the base ten logarithm of a raster.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_NATURAL_LOG,0))

def Exponential(Input1):
        """
        Computes the exponential of a raster.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_EXPONENT,0))

def Power(Input1, Power):
        """
        Raises the raster to the specified power.

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        	Power: The power to be raised to, as a float (or integer)

        Returns
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_POWER, Power))

def Square(Input1):
        """
        Computes the square of a raster

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns
        	A SpaDatasetRaster object
        """
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_SQUARE,0))

def SquareRoot(Input1):
        """
        Computes the square root of a raster

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns:
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_SQUARE_ROOT,0))

def AbsoluteValue(Input1):
        """
        Computes the absolute value of a raster

        Parameters:
        	Input1: SpaDatasetRaster object OR a string representing the path to the raster file.

        Returns:
        	A SpaDatasetRaster object
        """	
        Input1=SpaPy.GetInput(Input1)
        return(Input1.Math(SPAMATH_ABSOLUTE,0))

