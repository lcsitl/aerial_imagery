"""
Name: 4_AerialImage_processing_directional_analysis_part_2of2 (aka script 4)
    
This script will extract the image classification data by four sections of each citrus polygon
and then output the final results to an excel file.

Authored by: lucky mehra
"""

##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder (Directional folder)
path = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\Directional"

# path to classified rasters
classified_raster = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\Classified raster"

# county subregion
region = "HeSm"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\HeSm.shp"

##*************************************************##
##                                                 ##
## No need to changet the script below this        ##
##                                                 ##
##*************************************************##

# import modules
import arcpy, os, xlrd, xlwt, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create folders in Directional folder
os.makedirs(path + r"\Classified raster")
os.makedirs(path + r"\Output tables\Excel")

# import CustomGrid Toolbox
arcpy.ImportToolbox(r"U:\Gottwald_Lab\LMehra\1.1_Aerial_Imagery\CustomGridTools.tbx")

# create labels for quarter sections
# 1 = NW, 2 = NE, 3 = SW, 4 = SE
arcpy.CreateQLabels_CustomGridTools(citrus, "1, 2, 3, 4", path + "/" + region + "_" + year + "_directional.shp",\
                                    path + "/" + region + "_" + year + "_directional_labels.shp")
print "hot potatoes"

# add new field to attribute table
inFeatures = path + "/" + region + "_" + year + "_directional_labels.shp"
fieldName = "F_ID_LABEL"
fieldType = "LONG"

arcpy.AddField_management(inFeatures, fieldName, fieldType)
arcpy.CalculateField_management(inFeatures, fieldName, "int(str(!F_index!) + str(!GridLabel!))", "PYTHON_9.3")

# name of the classified raster
env.workspace = classified_raster
classifiedRaster = classified_raster + "/" + region + "_" + year + ".tif"

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified raster by Q sections
# Set local variables
inMaskData = path + "/" + region + "_" + year + "_directional_labels.shp"

#Execute ExtractByMask
outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)
print "stuff"


# Save the output
out_raster=path+"/Classified raster/"+ region + "_" + year + ".tif"
outExtractByMask.save(out_raster)

# Set environment settings for tabulate area
env.workspace = path + "/Classified raster"
print "more stuff"

# Change field type of 'CLASSVALUE'. It is set to 'double' by default, TabulateArea only takes integer or string
fieldName = "CLASSVALUE"
fieldType = "LONG"

arcpy.AddField_management(inFeatures, fieldName, fieldType)
arcpy.CalculateField_management(inFeatures, fieldName, "int(str(!CLASSVALUE!))", "PYTHON_9.3")

# Set local variables
inZoneData = inFeatures
zoneField = "F_ID_LABEL"
data = out_raster
classField = "VALUE"
processingCellSize = 1
outTable = path + "/Output tables/"+ region + "_" + year +".dbf"
print "past earlier problem"

# Execute TabulateArea
arcpy.env.overwriteOutput = True
TabulateArea(inZoneData, zoneField, data, classField, outTable, processingCellSize)

# Export table to excel
out_xls = path + "/Output tables/Excel/"+ region + "_" + year +".xls"
arcpy.TableToExcel_conversion(outTable,out_xls)

# add some additional column and a sheet

# open a sheet in temp workbook
wkbk = xlwt.Workbook()
outsheet = wkbk.add_sheet('Sheet1')

outrow_idx = 0
insheet = xlrd.open_workbook(out_xls).sheets()[0]
for row_idx in xrange(insheet.nrows):
        if row_idx == 0:
                outsheet.write(outrow_idx, 0, "Year")
                outsheet.write(outrow_idx, 1, "County_subregion")
                outsheet.write(outrow_idx, 2, "F_INDEX")
                outsheet.write(outrow_idx, 3, "Grove_area")
                outsheet.write(outrow_idx, 4, "OID")
                outsheet.write(outrow_idx, 5, "F_ID_LABEL")
                outsheet.write(outrow_idx, 6, "VALUE_1")
                outsheet.write(outrow_idx, 7, "VALUE_2")
                outsheet.write(outrow_idx, 8, "VALUE_3")
                outrow_idx += 1
        if row_idx > 0:
                outsheet.write(outrow_idx, 0, int("20" + year))
                outsheet.write(outrow_idx, 1, region)
                outsheet.write(outrow_idx, 2, int(str(int(insheet.cell_value(row_idx, 1)))[:-1]))
                outsheet.write(outrow_idx, 3, int(str(int(insheet.cell_value(row_idx, 1)))[-1:]))
                for col_idx in xrange(insheet.ncols):
                        outsheet.write(outrow_idx, col_idx + 4, insheet.cell_value(row_idx, col_idx))    
                outrow_idx += 1

wkbk.save(path + "/Output tables/Excel/" + "/" + region + "_" + year + "_rf_directional.xls")

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)


