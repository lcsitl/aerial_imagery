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

# the path to current workspace (COUNTY folder)
path = r"C:\Users\drew.posny\Desktop\Aerial\Hendry"

# citrus shape file abbreviated county name + subregion (eg He2)
region = "HeSm"

# two digit year
year = "08"

# location of a blank arcmap document
blank_map = r"C:\Users\drew.posny\Desktop\Blank_Map.mxd"

##*************************************************##
##                                                 ##
## Shouldn't need any changes below                ##
##                                                 ##
##*************************************************##

# Import system modules
import arcpy, xlrd, xlwt, os, time
from arcpy import env
from arcpy.sa import *
from datetime import datetime
print str(datetime.now())
start_time = time.time()

# import CustomGrid Toolbox ########### Note: need imports first, but not sure where you guys saved this
arcpy.ImportToolbox(r"B:\Aerial Imagery\Data\CustomGridTools.tbx") #############################

# citrus raster name
loc_id = region + "_" + year

# location of citrus polygon shapefile
citrus = path + "\\" + region + ".shp"

# update path string
path = path + r"\20" + year + "\\" + region

# parameters for training random tree classifier
inRaster = path + r"\Citrus" + "\\" + loc_id + ".tif"
train_features = path + r"\training" + "\\" + loc_id + ".shp"
segRaster = path + r"\Segment" + "\\" + loc_id + ".tif"

print "Oh. It's you again. Ugh - initiating Part 2 for " + loc_id

# create new folders
try:
        print "Creating more subfolders.."
        os.makedirs(path + r"\ecd")
        os.makedirs(path + r"\Classified")
        os.makedirs(path + r"\Output\Excel")
except:
        print "Folders already exist - whatever, will overwrite"

# parameters for training random tree classifier
out_definition = path + r"\ecd" + "\\" + loc_id + "_RT.ecd"
maxNumTrees = "100"
maxTreeDepth = "30"
maxSampleClass = "1000"
attributes = "COLOR;MEAN;STD;COUNT;COMPACTNESS;RECTANGULARITY"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

print "Random tree classifier.."
TrainRandomTreesClassifier(inRaster, train_features,
                           out_definition, segRaster, maxNumTrees,
                           maxTreeDepth, maxSampleClass, attributes)

print "..classifying.."
# Classify a raster
arcpy.env.workspace = path + r"\Classified"
classifiedraster = ClassifyRaster(inRaster, out_definition, segRaster)
out_raster= path + r"\Classified" + "\\" + loc_id + ".tif"

print ".. saving"
# save output
classifiedraster.save(out_raster)

# Set local variables
inZoneData = citrus
zoneField = "F_index"
inClassData = out_raster
classField = "Classvalue"
processingCellSize = 1
outTable = path + r"\Output" + "\\" + loc_id + ".dbf"

print "Tabulate area"
# Execute TabulateArea
arcpy.env.overwriteOutput = True
TabulateArea(inZoneData, zoneField, inClassData, classField, outTable, processingCellSize)

arcpy.CheckInExtension("Spatial")

# Export table to excel
out_xls = path + r"\Output\Excel" + "\\" + loc_id + ".xls"
arcpy.TableToExcel_conversion(outTable,out_xls)

# add some additional column and a sheet

# open a sheet in temp workbook
wkbk = xlwt.Workbook()
outsheet = wkbk.add_sheet('Sheet1')
outsheet1 = wkbk.add_sheet('Sheet3')

print "Writing to excel file.."
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
                outsheet.write(outrow_idx, 0, int("20" + loc_id.split("_")[-1]))
                outsheet.write(outrow_idx, 1, loc_id.split("_")[0] + "_" + loc_id.split("_")[1])
                outsheet.write(outrow_idx, 2, "Entire_block")
                for col_idx in xrange(insheet.ncols):
                        outsheet.write(outrow_idx, col_idx + 3, insheet.cell_value(row_idx, col_idx))
                outrow_idx += 1

wkbk.save(path + r"\Output\Excel" + "\\" + loc_id + "_rf.xls")

# add the classified rasters to arcmap document and save

# set the workspace
arcpy.env.workspace = path

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True

print "Constructing map document and adding layers.."
# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layer
citrus_lyr = arcpy.mapping.Layer(citrus)

# add layers to the map
arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(path + r"\Citrus" + "\\" + loc_id + ".tif", loc_id + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "AUTO_ARRANGE")

# get names of classified rasters into one list
env.workspace = path + r"\Classified"
classified_raster = out_raster

# add these rasters into map
cr = arcpy.MakeRasterLayer_management(classified_raster, "O_" + loc_id)
cr1 = cr.getOutput(0)
arcpy.mapping.AddLayer(df, cr1, "AUTO_ARRANGE")

print "..saving"
# save the map document
mxd.saveACopy(path + "\\" + loc_id + "_post_sig.mxd")    
  
# get time used by computer to run the script
print "Finally. 2 of 5 complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

"""
Name: 3_AerialImage_processing_directional_analysis_part_1of2 (aka script 3)
    
This script divides each polygon in to four sections (NE, NW, SE, and SW). 
Once this script finishes, an ArcMap document will open.

Code for this script came from:
http://ianbroad.com/creating-quarter-quarter-section-grid-python/

Authored by: lucky mehra
"""

print "Fine. Let's continue with Part 3."

try:
        os.makedirs(path + r"\Directional")
except:
        os.remove(path + "\\" + loc_id + "_dir.shp")
        print "Ready"

# update path string to directional
path = path + r"\Directional"

inFeatures = path + "\\" + loc_id + "_dir.shp"

arcpy.CopyFeatures_management(citrus, inFeatures)

outFeatures = path + "\\" + loc_id + "_Envelope.shp"

arcpy.MinimumBoundingGeometry_management(inFeatures, outFeatures, "ENVELOPE", "NONE") ######## DP

print "Dividing into directional quadrants with polylines.."
#create polyline feature
arcpy.CreateQSections_CustomGridTools(outFeatures, path + "\\" + loc_id + "_polylines.shp", 0.0005)

# set the workspace
arcpy.env.workspace = path

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True

# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layer
envelopes = arcpy.mapping.Layer(path + "\\" + loc_id + "_Envelope.shp")
sections = arcpy.mapping.Layer(path + "\\" + loc_id + "_dir.shp")
lines = arcpy.mapping.Layer(path + "\\" + loc_id + "_polylines.shp") 

# add layers to the map
arcpy.mapping.AddLayer(df, envelopes, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, sections, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, lines, "AUTO_ARRANGE")

# save the map document
mxd.saveACopy(path + "\\" + loc_id + "_post_sig_dir.mxd")

print "Once the ArcMap document opens, use split polygon tool to create new polygon features using the polyline class to complete Part 3..."

print "1. Editor toolbar > Start editing"
print "2. Right click '*_polylines' layer > Selection > Select all"
print "3. Advanced Editing toolbar > Split polygons"
print "4. Target layer = '*_dir.shp' > OK"
print "5. Editor toolbar > Stop editing & save edits"
print "6. Close map document"

# open the map document                           
os.startfile(path + "\\" + loc_id + "_post_sig_dir.mxd")

