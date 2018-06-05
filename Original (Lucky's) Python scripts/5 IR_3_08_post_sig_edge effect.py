##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Edge effect"

# path to classified rasters
classified_rasters = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Classified rasters"

# county subregion
region = "IR_3"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new" + "/" + region + ".shp"

# list of edge sizes in meters
buff = [10, 20, 30, 40]

##*************************************************##

# import modules
import arcpy, os, xlrd, xlwt, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create folders in Directional folder
os.makedirs(path + r"\Classified rasters")
os.makedirs(path + r"\Output tables\Excel")

# read names of classified rasters into a list
env.workspace = classified_rasters
data = arcpy.ListDatasets("*rf*", "Raster")

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified raster different size edges
for dist in buff:
    arcpy.Buffer_analysis(citrus, path + "/" + region + "_" + year + "_" + str(dist) + "m_erase.shp", "-" + str(dist) + " Meters")
    arcpy.Erase_analysis(citrus, path + "/" + region + "_" + year + "_" + str(dist) + "m_erase.shp",\
                     path + "/" + region + "_" + year + "_" + str(dist) + "m.shp")
    inMaskData = path + "/" + region + "_" + year + "_" + str(dist) + "m.shp"
    for classifiedRaster in data:
        outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)
        out_raster = path + "/Classified rasters/" + str(dist)[0] + classifiedRaster
        outExtractByMask.save(out_raster)
        zoneField = "F_index"
        classField = "VALUE"
        processingCellSize = 1
        outTable = path + "/Output tables/" + str(dist) + classifiedRaster + ".dbf"
        TabulateArea(inMaskData, zoneField, out_raster, classField, outTable, processingCellSize)
        out_xls = path + "/Output tables/Excel/"+ str(dist) + classifiedRaster +".xls"
        arcpy.TableToExcel_conversion(outTable, out_xls)
        

# Combine all output excel files into one file

# read file names
ex = path + "/Output tables/Excel"
xlsfiles = [filename for root, dir, files in os.walk(ex, topdown=False)
			for filename in files
                                if filename.endswith('.xls')]

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
                        outsheet.write(outrow_idx, 2, "Edge_meters")
                        outsheet.write(outrow_idx, 3, "Reject_fraction")
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx,col_idx + 4, insheet.cell_value(row_idx, col_idx))
                        outrow_idx += 1
                if row_idx > 0:
                        outsheet.write(outrow_idx, 0, int("20" + year))
                        outsheet.write(outrow_idx, 1, region)
                        outsheet.write(outrow_idx, 2, int(f[0:2]))
                        outsheet.write(outrow_idx, 3, float("0." + f.split(".")[0].split("_")[3][2:]))
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx, col_idx + 4, insheet.cell_value(row_idx, col_idx))    
                        outrow_idx += 1

wkbk.save(ex + "/" + region + "_" + year + "_rf_all_edge.xls")

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)





