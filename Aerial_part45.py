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

# the path to current workspace (COUNTY folder)
path = r"C:\Users\drew.posny\Desktop\Aerial\Hendry"

# citrus shape file abbreviated county name + subregion (eg He2)
region = "HeSm"

# two digit year
year = "08"

##*************************************************##
##                                                 ##
## Shouldn't need any changes below                ##
##                                                 ##
##*************************************************##

# import modules
import arcpy, os, xlrd, xlwt, time
from arcpy import env
from arcpy.sa import *
from datetime import datetime
print str(datetime.now())
start_time = time.time()

# import CustomGrid Toolbox ########### Note: need imports first, but not sure where you guys saved this
arcpy.ImportToolbox(r"B:\Aerial Imagery\Data\CustomGridTools.tbx") #############################

# list of edge sizes in meters
buff = [10, 20, 30, 40]

# citrus raster name
loc_id = region + "_" + year

# citrus shape file
citrus = path + "\\" + region + ".shp"

# update path string
path = path + r"\20" + year + "\\" + region

# path to classified rasters
classified_raster = path + r"\Classified"

# update path string to directional
path = path + r"\Directional"

##################################################
##################################################

print "Ok, let's do this. Part 4 - we're coming for you"

# create new folders
try:
        print "Creating folders.."
        os.makedirs(path + r"\Classified")
        os.makedirs(path + r"\Output\Excel")
except:
        print "Overwrite"

# create labels for quarter sections
# 1 = NW, 2 = NE, 3 = SW, 4 = SE
arcpy.CreateQLabels_CustomGridTools(citrus, "1, 2, 3, 4", path + "\\" + loc_id + "_dir.shp",path + "\\" + loc_id + "_dir_labels.shp")

# add new field to attribute table
inFeatures = path + "\\" + loc_id + "_dir_labels.shp"
fieldName = "F_ID_LABEL"
fieldType = "LONG"

arcpy.AddField_management(inFeatures, fieldName, fieldType)
arcpy.CalculateField_management(inFeatures, fieldName, "int(str(!F_index!) + str(!GridLabel!))", "PYTHON_9.3")

# name of the classified raster
env.workspace = classified_raster
classifiedRaster = classified_raster + "\\" + loc_id + ".tif"

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified raster by Q sections
# Set local variables
inMaskData = path + "\\" + loc_id + "_dir_labels.shp"

print "Extracting.."
#Execute ExtractByMask
outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)

# Save the output
out_raster = path + r"\Classified" + "\\" + loc_id + ".tif"
outExtractByMask.save(out_raster)

# Set environment settings for tabulate area
env.workspace = classified_raster

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
outTable = path + r"\Output" + "\\" + loc_id + ".dbf"

print "Tabulate area"
arcpy.env.overwriteOutput = True
TabulateArea(inZoneData, zoneField, data, classField, outTable, processingCellSize)

# check out spatial analyst extension
arcpy.CheckInExtension("Spatial")

print "Writing to excel file.."
# Export table to excel
out_xls = path + r"\Output\Excel" + "\\" + loc_id + ".xls"
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

wkbk.save(path + r"\Output\Excel" + "\\" + loc_id + "_rf_dir.xls")

# get time used by computer to run the script
print "Completed 4 of 5 in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)


"""
Name: 5_AerialImage_processing_edge_analysis (aka script 5)
    
This script will extract one-by-one outer 10, 20, 30, 40 m of the citrus polygon and will calculate how much citrus is on edges. 
The resulting numbers will be written to an excel file.

Authored by: lucky mehra
"""

print "What comes after Part 4??"

print "Part 5."

# revert path string back to year
path = path.split(r"\Directional")[0]

os.makedirs(path + r"\Edge")
        
# update path string
path = path + r"\Edge"

try:
        print "Creating Edge folders.."
        os.makedirs(path + r"\Classified")
        os.makedirs(path + r"\Output\Excel")
except:
        print "Overwrite"

# name of the classified raster
env.workspace = classified_raster
classifiedRaster = classified_raster + "\\" + loc_id + ".tif"

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

print "Extracting edges.."
# extract data from classified raster different size edges
for dist in buff:
    arcpy.Buffer_analysis(citrus, path + "\\" + loc_id + "_" + str(dist) + "m_erase.shp", "-" + str(dist) + " Meters")
    arcpy.Erase_analysis(citrus, path + "\\" + loc_id + "_" + str(dist) + "m_erase.shp",
                     path + "\\" + loc_id + "_" + str(dist) + "m.shp")
    inMaskData = path + "\\" + loc_id + "_" + str(dist) + "m.shp"
    

    #Execute ExtractByMask
    outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)
    out_raster = path + r"\Classified" + str(dist)[0] + loc_id + ".tif"
    outExtractByMask.save(out_raster)
    # set parameters for TabulateArea
    zoneField = "F_index"
    classField = "VALUE"
    processingCellSize = 1
    outTable = path + r"\Output"+ str(dist) + loc_id + ".dbf"
    TabulateArea(inMaskData, zoneField, out_raster, classField, outTable, processingCellSize)
    out_xls = path + r"\Output\Excel" + "\\" + str(dist) + loc_id + ".xls"
    arcpy.TableToExcel_conversion(outTable, out_xls)        


arcpy.CheckInExtension("Spatial")

# Combine all output excel files into one file

# read file names
ex = path + r"\Output\Excel"
xlsfiles = [filename for root, dir, files in os.walk(ex, topdown=False)
			for filename in files
                                if filename.endswith('.xls')]

print "Writing to excel file.."
# open a sheet in temp workbook
wkbk = xlwt.Workbook()
outsheet = wkbk.add_sheet('Sheet1')

outrow_idx = 0
for f in xlsfiles:
        insheet = xlrd.open_workbook(ex + "/" + f).sheets()[0]
        for row_idx in xrange(insheet.nrows):
                if row_idx == 0 and f == xlsfiles[0]:
                        outsheet.write(outrow_idx, 0, "Year")
                        outsheet.write(outrow_idx, 1, "County_subregion")
                        outsheet.write(outrow_idx, 2, "Grove_area")
                        outsheet.write(outrow_idx, 3, "OID")
                        outsheet.write(outrow_idx, 4, "F_INDEX")
                        outsheet.write(outrow_idx, 5, "VALUE_1")
                        outsheet.write(outrow_idx, 6, "VALUE_2")
                        outsheet.write(outrow_idx, 7, "VALUE_3")
                        outrow_idx += 1
                if row_idx > 0:
                        outsheet.write(outrow_idx, 0, int("20" + year))
                        outsheet.write(outrow_idx, 1, region)
                        outsheet.write(outrow_idx, 2, f[0:2] + "m_edge")
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx, col_idx + 3, insheet.cell_value(row_idx, col_idx))    
                        outrow_idx += 1

wkbk.save(ex + "\\" + loc_id + "_rf_edge.xls")

# get time used by computer to run the script
print "Completed 5 of 5 in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

print "Good day"

print "I said good day."

print "No, you hang up"

print "Okay bye."
