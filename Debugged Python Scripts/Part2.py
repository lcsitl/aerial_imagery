"""
Name: 2_AerialImage_processing_post_training_sample.py (aka script 2)

Using the training features created (using the output of script 1) and segemented raster, this script will create a .ecd (classifier
definition fiel) file using random forest (trees) algorithms, and then that .ecd file will be used to classify the raster. Once the
raster is classified, raster data will be written to an excel file. This excel file can be imported to R for further statistical
analysis.

Authored by: lucky mehra
"""

##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# location of citrus polygons
citrus = r"C:\Users\leigh.sitler\Desktop\Polk_08_completed\Po_2.shp"

# the path to current folder (that contains 'Citrus only' folder)
path = r"C:\Users\leigh.sitler\Desktop\Polk_08_completed\Polk_2008_1"

# citrus only raster name
citrus_raster = "po_1_08"

# location of a blank arcmap document
blank_map = r"C:\Users\leigh.sitler\Desktop\Aerial\Blank map.mxd"

##*************************************************##
##                                                 ##
## Definitely need to change the script below              ##
##                                                 ##
##*************************************************##

# Import system modules
import arcpy, xlrd, xlwt, os, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create new folders in "path"
os.makedirs(path + r"\ecd")
os.makedirs(path + r"\Classified raster")
os.makedirs(path + r"\Output tables\Excel")
os.makedirs(path + r"\Directional") # to be used in later scripts
os.makedirs(path + r"\Edge effect") # to be used in later scripts

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# parameters for training random tree classifier
inSegRaster = path + r"\Citrus" + "\\" + citrus_raster + ".tif"
train_features = path + r"\training" + "\\" + citrus_raster + ".shp"
out_definition = path + r"\ecd" + "\\" + citrus_raster + "_RT.ecd"
in_additional_raster = path + r"\Segment" + "\\" + citrus_raster + ".tif"
maxNumTrees = "100"
maxTreeDepth = "30"
maxSampleClass = "1000"
attributes = "COLOR;MEAN;STD;COUNT;COMPACTNESS;RECTANGULARITY"
print "Ready,"

# Execute
TrainRandomTreesClassifier(inSegRaster, train_features,
                           out_definition, in_additional_raster, maxNumTrees,
                           maxTreeDepth, maxSampleClass, attributes)

# Classify a raster
arcpy.env.workspace = path + r"\Classified raster"
classifiedraster = ClassifyRaster(inSegRaster, out_definition, in_additional_raster)
out_raster= path + r"\Classified raster" + "\\" + citrus_raster + ".tif"
print "set,"

# save output
classifiedraster.save(out_raster)

# Set local variables
inZoneData = citrus
zoneField = "F_index"
inClassData = out_raster
classField = "Classvalue"
processingCellSize = 1
outTable = path + r"\Output tables" +"\\" + citrus_raster + ".dbf"
print "let's go!"

# Execute TabulateArea
arcpy.env.overwriteOutput = True
TabulateArea(inZoneData, zoneField, inClassData, classField, outTable, processingCellSize)

# Export table to excel
out_xls = path + r"\Output tables\Excel" + "\\" + citrus_raster + ".xls"
arcpy.TableToExcel_conversion(outTable,out_xls)

# add some additional column and a sheet

# open a sheet in temp workbook
wkbk = xlwt.Workbook()
outsheet = wkbk.add_sheet('Sheet1')
outsheet1 = wkbk.add_sheet('Sheet3')

outrow_idx = 0
insheet = xlrd.open_workbook(out_xls).sheets()[0]
for row_idx in xrange(insheet.nrows):
        if row_idx == 0:
                outsheet.write(outrow_idx, 0, "Year")
                outsheet.write(outrow_idx, 1, "County_subregion")
                outsheet.write(outrow_idx, 2, "Grove_area")
                outsheet1.write(outrow_idx, 0, insheet.cell_value(row_idx,1))
                outsheet1.write(outrow_idx, 1, "Polygon_quality")
                for col_idx in xrange(insheet.ncols):
                        outsheet.write(outrow_idx, col_idx + 3, insheet.cell_value(row_idx, col_idx))
                outrow_idx += 1
        if row_idx > 0:
                outsheet1.write(outrow_idx, 0, insheet.cell_value(row_idx,1))
                outsheet.write(outrow_idx, 0, int("20" + citrus_raster.split("_")[-1]))
                outsheet.write(outrow_idx, 1, citrus_raster.split("_")[0] + "_" + citrus_raster.split("_")[1])
                outsheet.write(outrow_idx, 2, "Entire_block")
                for col_idx in xrange(insheet.ncols):
                        outsheet.write(outrow_idx, col_idx + 3, insheet.cell_value(row_idx, col_idx))
                outrow_idx += 1

wkbk.save(path + r"\Output tables\Excel" + "\\" + citrus_raster + "_rf.xls")

# add the classified rasters to arcmap document and save
print "moving along"

# set the workspace
arcpy.env.workspace = path

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True

# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layer
citrus_lyr = arcpy.mapping.Layer(citrus)
print "almost there..."

# add layers to the map
arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(path + r"\Citrus" + "\\" + citrus_raster + ".tif", citrus_raster + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "AUTO_ARRANGE")

# get names of classified rasters into one list
env.workspace = path + r"\Classified raster"
classified_raster = out_raster
print "wrapping up."

# add these rasters into map
cr = arcpy.MakeRasterLayer_management(classified_raster, "O_" + citrus_raster)
cr1 = cr.getOutput(0)
arcpy.mapping.AddLayer(df, cr1, "AUTO_ARRANGE")

# save the map document
mxd.saveACopy(path + "\\" + citrus_raster + "_post_sig.mxd")

# open the map document                           
os.startfile(path + "\\" + citrus_raster + "_post_sig.mxd")        
  
# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)


                
