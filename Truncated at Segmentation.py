"""
Name: 1_AerialImage_processing_pre_training_sample.py

this script will combine (mosaic) 6 mi by 6 mi image grids, extract only citrus
polygons from it, and apply segmentation to the extracted image.
Then, it will create 40 random polygons in the extracted images's extent. these
random polygons will be used to draw training areas (features) that will be used in image
classification

Authored by: lucky mehra
"""

#%%
#import modules
import arcpy, os, random, xlrd, time, shutil
import multiprocessing as mp
from arcpy.sa import *
start_time = time.time()

#%%
##################################################
##################################################
## Parameters or variables that need to be changed
## before running the script

# Florida aerial grid
# Florida has three aerial grids: east, west, and north. this will change
# depending upon which region the county lies in
grid = r"C:\Users\leigh.sitler\Desktop\Aerial\AerialPhotographygrids_2015\FLorida_East_NAD83_2011_USft.shp"

# location of citrus polygons
# this shapefile will need to be created from a shapefile that contains all florida
# citrus. this is a subset of whole florida file.
citrus = r"C:\Users\leigh.sitler\Desktop\Hendry\He4\He4.shp"

# the path to current workspace (folder)
path = r"C:\Users\leigh.sitler\Desktop\Hendry\He4"

# location of sid files
# this is the location of raw image files
sid_loc = r"C:\Users\leigh.sitler\Desktop\Hendry\2008_sid_files\sid"

# varibles to create names of sid files
front_str1 = "OP2008_nc_0"
front_str2 = "OP2008_nc_"
back_str =  "_24.sid"

# identify which column number contains the Old_SPE_ID/Old_SPW_ID that is needed to create names of sid files
# if it is fifth column in attribute table, enter 3 (5-2) below
columnidx = 3

# merged raster name
# choose a name that is descriptive, in this instance, SL = Saint Lucie, 3 = subregion
# 3 of the Saint Lucie county, 06 = year 2006
merged_raster_name = "He_4_08"

# location of a blank arcmap document
blank_map = r"C:\Users\leigh.sitler\Desktop\Blank_Map.mxd"

##################################################
##################################################

### No change needed below this, in most cases ##

#%%
# create new folders in "path"
os.makedirs(path + r"\Citrus only")
os.makedirs(path + r"\fileGDB")
os.makedirs(path + r"\Merged rasters")
os.makedirs(path + r"\training_features")
os.makedirs(path + r"\Segment")
print "1"

# set the workspace
arcpy.env.workspace = path
print "2"

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True
print "3"

# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)
print "4"

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
print "5"

# create a new layer
citrus_lyr = arcpy.mapping.Layer(citrus)
grid = arcpy.mapping.Layer(grid) 
print "6"

# add citrus layer to the map
arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")
print "7"

# select the grids that intersect with citrus polygons
arcpy.MakeFeatureLayer_management(grid, 'grid_sel') 
arcpy.SelectLayerByLocation_management('grid_sel', 'intersect', citrus)
print "8"

# save selected grids into new layer
arcpy.CopyFeatures_management('grid_sel', 'grid_sel_layer')
print "9"

# export the selected grids to an excel file
arcpy.TableToExcel_conversion(path + r"\grid_sel_layer.shp", path + r"\grids.xls")
print "10"

#import the excel file back to python
workbook = xlrd.open_workbook(path + r"\grids.xls")
sheet = workbook.sheet_by_index(0)
print "11"

# put grid ids in a list
a = sorted(sheet.col_values(columnidx)[1:])
c = [str(int(i)) for i in a]
d = c + c
print "12"

# concatenate text to front and back of ids, so that these can be automatically
# selected from the folder that contains sid files
front1 = [front_str1 * 1 for i in c]
front2 = [front_str2 * 1 for i in c]
front = front1 + front2
back = [back_str * 1 for i in d]

name =[]
for i in range(len(d)):
    name.append(front[i] + d[i] + back[i])
print "13"

#%%
# create a file geodatabase to save mosaic dataset
out_folder_path = path + r"\fileGDB"
out_name = "fGDB.gdb"
arcpy.CreateFileGDB_management(out_folder_path, out_name)
print "14"

# create empty mosaic dataset in fGDB.gdb
gdbname = path + r"\fileGDB\fGDB.gdb"
mdname = "mosaicds"
coordinate = "NAD 1983 StatePlane Florida East FIPS 0901 (US Feet)"
noband = "3"
pixtype = "8_BIT_UNSIGNED"
pdef = "NONE"
wavelength = ""

arcpy.CreateMosaicDataset_management(gdbname, mdname, coordinate, noband, 
                                     pixtype, pdef, wavelength)
print "15"

# Add rasters to mosaic dataset
arcpy.env.workspace = sid_loc

mdname = gdbname + "/" + mdname
rastype = "Raster Dataset"
input_rasters = ";".join(name)
updatecs = "UPDATE_CELL_SIZES"
updatebnd = "UPDATE_BOUNDARY"

arcpy.AddRastersToMosaicDataset_management(mdname, rastype, input_rasters, updatecs,updatebnd)
print "16"

# Copy mosaic dataset to raster
merged_raster = path + r"\Merged rasters" + "\\" +  merged_raster_name + ".tif"
arcpy.CopyRaster_management(mdname, merged_raster)
desc = arcpy.Describe(mdname)
SR = desc.spatialReference
arcpy.DefineProjection_management(merged_raster, SR)
print "17"

# get time used by computer to run the script
print "Merged rasters in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

#%%
# Extract by mask
# Project citrus shapefile before running 'extract by mask' tool
arcpy.env.workspace = path + r"\Citrus only"
print "18"

inMaskData = path + "\\" + merged_raster_name.split("_")[0] + "_prj.shp"
arcpy.Project_management(citrus, inMaskData, SR)
arcpy.CheckOutExtension("Spatial")
print "19"

outExtractByMask = ExtractByMask(merged_raster, inMaskData)
out_raster = path + r"\Citrus only" +"\\" + merged_raster_name + ".tif"
outExtractByMask.save(out_raster)
print "20"

# get time used by computer to run the script
print "Extracted citrus mask in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(out_raster, merged_raster_name + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "AUTO_ARRANGE")
print "21"
print "Complete - Run Segmentation in ArcMap"
