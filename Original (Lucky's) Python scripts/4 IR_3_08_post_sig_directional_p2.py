##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Directional"

# path to classified rasters
classified_rasters = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Classified rasters"

# county subregion
region = "IR_3"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new" + "/" + region + ".shp"

##*************************************************##

# import modules
import arcpy, os, xlrd, xlwt, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create folders in Directional folder
os.makedirs(path + r"\Classified rasters")
os.makedirs(path + r"\Output tables\Excel")

# import CustomGrid Toolbox
arcpy.ImportToolbox(r"U:\Gottwald_Lab\LMehra\Aerial Imagery\CustomGridTools.tbx")

# create labels for quarter sections
# 1 = NW, 2 = NE, 3 = SW, 4 = SE
arcpy.CreateQLabels_CustomGridTools(citrus, "1, 2, 3, 4", path + "/" + region + "_" + year + "_directional.shp",\
                                    path + "/" + region + "_" + year + "_directional_labels.shp")

# add new field to attribute table
inFeatures = path + "/" + region + "_" + year + "_directional_labels.shp"
fieldName = "F_ID_LABEL"
fieldType = "LONG"

arcpy.AddField_management(inFeatures, fieldName, fieldType)
arcpy.CalculateField_management(inFeatures, fieldName, "int(str(!F_index!) + str(!GridLabel!))", "PYTHON_9.3")

# read names of classified rasters into a list
env.workspace = classified_rasters
data = arcpy.ListDatasets("*rf*", "Raster")

# check out spatial analyst extension
arcpy.CheckOutExtension("Spatial")

# extract data from classified raster by Q sections
for classifiedRaster in data:
    # Set local variables
    inMaskData = path + "/" + region + "_" + year + "_directional_labels.shp"
    #Execute ExtractByMask
    outExtractByMask = ExtractByMask(classifiedRaster, inMaskData)
    # Save the output
    out_raster=path+"/Classified rasters/"+classifiedRaster
    outExtractByMask.save(out_raster)

# Set environment settings for tabulate area
env.workspace = path+"/Classified rasters"

# Set local variables
inZoneData = inFeatures
zoneField = "F_ID_LABEL"
data = arcpy.ListDatasets("*rf*", "Raster")
classField = "VALUE"
processingCellSize = 1

#create the loop to output all classified rasters as excel files
for classifiedRaster1 in data:
	outTable = path + "/Output tables/"+ classifiedRaster1 +".dbf"
	# Execute TabulateArea
	TabulateArea(inZoneData, zoneField, classifiedRaster1, classField, outTable, processingCellSize)
	out_xls = path + "/Output tables/Excel/"+ classifiedRaster1 +".xls"
	arcpy.TableToExcel_conversion(outTable,out_xls)

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
                        outsheet.write(outrow_idx, 2, "F_INDEX")
                        outsheet.write(outrow_idx, 3, "Grove_area")
                        outsheet.write(outrow_idx, 4, "Reject_fraction")
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx,col_idx + 5, insheet.cell_value(row_idx, col_idx))
                        outrow_idx += 1
                if row_idx > 0:
                        outsheet.write(outrow_idx, 0, int("20" + year))
                        outsheet.write(outrow_idx, 1, region)
                        outsheet.write(outrow_idx, 2, int(str(int(insheet.cell_value(row_idx, 1)))[:-1]))
                        outsheet.write(outrow_idx, 3, int(str(int(insheet.cell_value(row_idx, 1)))[-1:]))
                        outsheet.write(outrow_idx, 4, float("0." + f.split(".")[0].split("_")[3][2:]))
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx, col_idx + 5, insheet.cell_value(row_idx, col_idx))    
                        outrow_idx += 1

wkbk.save(ex + "/" + region + "_" + year + "_rf_all_dir.xls")

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)


