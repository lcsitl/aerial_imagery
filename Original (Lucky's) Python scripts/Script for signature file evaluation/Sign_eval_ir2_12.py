# -*- coding: utf-8 -*-
"""
Created on Tue Jun 27 07:24:24 2017

@author: lucky.mehra
"""

"""
Variables and folders paths that need to be updated
"""

# location of shapefiles created by leigh, these files contain ground truth polygons
ind_shp = r"U:\Gottwald_Lab\LMehra\Aerial Imagery\Signature file testing\Indian River\2012"

# current folder
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_2\2012\Signature_file_eval"

# location of classified rasters
classified_rasters = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_2\2012\Classified rasters"

# unique name to help name several files that will be created when the script runs
file_id = "ir_2_12"

# citrus blocks/polygons for this particular subregion
citrus_polygons = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_2\IR_2.shp"

"""
Main script starts below
"""

# import modules
import arcpy, os, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create new folders in path
os.makedirs(path + r"\Classified rasters")
os.makedirs(path + r"\RasterToPoints")
os.makedirs(path + r"\Intersect")

"""
Merge shapefiles created by Leigh
"""
env.workspace = ind_shp
env.overwriteOutput = True
image = ["citrus", "shadow", "background"]

# merge polygon shapefiles
for i in image:
    data = arcpy.ListFeatureClasses("*%s*" % i)
    data
    
    arcpy.Merge_management(data, path + "/" + i + ".shp")
    #arcpy.AddField_management(path + "/" + i + ".shp", "Name", "TEXT")
    #arcpy.CalculateField_management(path + "/" + i + ".shp", "Name", '"%s" % i', "PYTHON_9.3")
    arcpy.AddField_management(path + "/" + i + ".shp", "Value", "LONG")
    if i == 'citrus':
        num = 3
    elif i == 'shadow':
        num = 2
    else:
        num = 1
    arcpy.CalculateField_management(path + "/" + i + ".shp", "Value", num, "PYTHON_9.3")

# merge citrus, shadow, and background
env.workspace = path
env.overwriteOutput = True

csb = arcpy.ListFeatureClasses()
csb

actual_class = path + "/" + file_id +".shp"
arcpy.Merge_management(csb, actual_class)

"""
Extract the ground truth area from classified rasters
"""

# read names of classified rasters into a list
env.workspace = classified_rasters
data = arcpy.ListDatasets("*rf*", "Raster")

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified rasters polygons in actual_class
for classifiedRaster in data:
    #Execute ExtractByMask
    outExtractByMask = ExtractByMask(classifiedRaster, actual_class)

    # Save the output
    out_raster=path+"/Classified rasters/"+classifiedRaster
    outExtractByMask.save(out_raster)
    
"""
Execute raster to point, and intersect on above extracted rasters
"""

# get only F_index from citrus_polygons
citrus_polygons1 = path + "/IR_2_Fid.shp"
arcpy.CopyFeatures_management(citrus_polygons, citrus_polygons1)
fields = arcpy.ListFields(citrus_polygons1)
keepFields = ["FID", "Shape","F_index"]
dropFields = [x.name for x in fields if x.name not in keepFields]
arcpy.DeleteField_management(citrus_polygons1, dropFields)

# execute RasterToPoint on reject_fraction 0 raster
env.workspace = path + "/Classified rasters"
field = "VALUE"

data1 = arcpy.ListDatasets("*rf*", "Raster")

# name the output point shapefile
outPoint = path + "/RasterToPoints/" + data1[0] + ".shp"

# RasterToPoint
arcpy.RasterToPoint_conversion(data1[0], outPoint, field)

# intersect it with actual_class shapefile
inFeatures = [actual_class, outPoint, citrus_polygons1]
intersectOutput = path + "/Intersect/" + data1[0] + ".shp"
arcpy.Intersect_analysis(inFeatures, intersectOutput, "NO_FID")

### Extract values to points for remaining reject fractions
inPointFeatures = intersectOutput
arcpy.CheckOutExtension("Spatial")
for inRaster in data1[1:]:
    outPointFeatures = path + "/Intersect/" + inRaster + ".shp"
    ExtractValuesToPoints(inPointFeatures, inRaster, outPointFeatures)
    arcpy.AddField_management(outPointFeatures, inRaster.split("_")[len(inRaster.split("_")) -1], 'SHORT')
    arcpy.CalculateField_management(outPointFeatures, inRaster.split("_")[len(inRaster.split("_")) -1], "!RASTERVALU!", "PYTHON_9.3")
    arcpy.DeleteField_management(outPointFeatures, "RASTERVALU")
    inPointFeatures = outPointFeatures

"""
Export
"""

#import Excel and CSV Conversion Tools toolbox
arcpy.ImportToolbox(r"U:\Gottwald_Lab\LMehra\Aerial Imagery\Excel_and_CSV_Conversion_Tools\ExcelTools\Excel and CSV Conversion Tools.tbx", 'tableconversion')
out_csv = path + "/" + file_id + "_rf_all.csv"
arcpy.TableToCSV_tableconversion(outPointFeatures, out_csv, 'COMMA')

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)    

    
