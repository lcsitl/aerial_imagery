"""
Name: 5_AerialImage_processing_edge_analysis (aka script 5)
    
This script will extract one-by-one outer 10, 20, 30, 40 m of the citrus polygon and will calculate how much citrus is on edges. 
The resulting numbers will be written to an excel file.

Authored by: lucky mehra
"""

##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder (EDGE EFFECT)
path = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\Edge effect"

# path to MAIN classified rasters FOLDER
classified_raster = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\Classified raster"

# county subregion
region = "HeSm"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\HeSm.shp"

# list of edge sizes in meters
buff = [10, 20, 30, 40]

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
print "work please"
# name of the classified raster
env.workspace = classified_raster
classifiedRaster = classified_raster + "/" + region + "_" + year + ".tif"

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified raster different size edges
for dist in buff:
    arcpy.Buffer_analysis(citrus, path + "/" + region + "_" + year + "_" + str(dist) + "m_erase.shp", "-" + str(dist) + " Meters")
    arcpy.Erase_analysis(citrus, path + "/" + region + "_" + year + "_" + str(dist) + "m_erase.shp",\
                     path + "/" + region + "_" + year + "_" + str(dist) + "m.shp")
    inMaskData = path + "/" + region + "_" + year + "_" + str(dist) + "m.shp"
    
    print "keep working"

    #Execute ExtractByMask
    outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)
    out_raster = path + "/Classified raster/" + str(dist)[0] + region + "_" + year + ".tif"
    outExtractByMask.save(out_raster)
    # set parameters for TabulateArea
    zoneField = "F_index"
    classField = "VALUE"
    processingCellSize = 1
    outTable = path + "/Output tables/"+ str(dist) + region + "_" + year +".dbf"
    TabulateArea(inMaskData, zoneField, out_raster, classField, outTable, processingCellSize)
    out_xls = path + "/Output tables/Excel/"+ str(dist) + region + "_" + year + ".xls"
    arcpy.TableToExcel_conversion(outTable, out_xls)        

# Combine all output excel files into one file

# read file names
ex = path + "/Output tables/Excel"
xlsfiles = [filename for root, dir, files in os.walk(ex, topdown=False)
			for filename in files
                                if filename.endswith('.xls')]
print "don't stop here"

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

wkbk.save(ex + "/" + region + "_" + year + "_rf_edge.xls")

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)





