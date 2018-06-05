"""
Name: 1_AerialImage_processing_pre_training_sample.py

this script will combine (mosaic) 6 mi by 6 mi image grids, extract only citrus
polygons from it, and apply segmentation to the extracted image.
Then, it will create 40 random polygons in the extracted images's extent. these
random polygons will be used to draw training areas (features) that will be used in image
classification

Authored by: lucky mehra
"""



##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current workspace (county folder with subdivided shape files)
path = r"C:\Users\drew.posny\Desktop\Aerial\Martin"

# citrus shape file abbreviated county name + subregion (eg HeSm)
region = "Martin_1"

# two digit year
year = "06"

# location of sid files
# this is the location of raw image files
sid_loc = r"C:\Users\drew.posny\Desktop\Aerial\Martin\sid\2006"

# Florida aerial grid
# Florida has three aerial grids: east, west, and north. this will change depending upon which region the county lies in
grid = r"C:\Users\drew.posny\Desktop\AerialPhotographygrids_2015\FLorida_East_NAD83_2011_USft.shp"

# identify which column number contains the Old_SPE_ID/Old_SPW_ID that is needed to create names of sid files
# if it is fifth column in attribute table, enter 3 (5-2) below
# East=3, West=4, North=3
columnidx = 3

# location of a blank arcmap document
blank_map = r"C:\Users\drew.posny\Desktop\Blank_Map.mxd"

##*************************************************##
##                                                 ##
## Shouldn't need any changes below                ##
##                                                 ##
##*************************************************##

# citrus raster name
loc_id = region + "_" + year

# citrus shape file
citrus = path + "\\" + region + ".shp"

# MAX number of random polygons to create --- note shortest distance btwn is set to 100 meters
numPoints = 40

##################################################

#import modules
import arcpy, os, random, xlrd, time, shutil
from arcpy.sa import *
from datetime import datetime
start_time = time.time()

print "Hello and welcome. You have initiated Part 1 for " + loc_id
print "And so it begins.." + str(datetime.now())
print "Please secure your tray tables, things could get dicey."

try:
    os.makedirs(path + r"\20" + year)
    print "Created 20" + year + " folder"
except:
    print "There can only be one!"
    print "20" + year + " folder was created earlier"

# update path string
path = path + r"\20" + year

os.makedirs(path + "\\" + region)
print "Created " + region + " folder"

# update path string
path = path + "\\" + region

##################################################

### No change needed below this, in most cases ##

# variables to create names of sid files
front_str = "OP20" + year + "_nc_"
back_str =  "_24.sid"

#%%
# create new folders in "path"
try:
    print "Creating additional subfolders.."
    os.makedirs(path + r"\Citrus")
    os.makedirs(path + r"\training")
    os.makedirs(path + r"\Segment")
except:
    print "Live dangerously - we will be overwriting existing folders."
    
os.makedirs(path + r"\fileGDB")  ## these get deleted at end
os.makedirs(path + r"\Merged")

# set the workspace
arcpy.env.workspace = path

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True

print "Initiating blank map.."

# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

citrus_lyr = arcpy.mapping.Layer(citrus)

grid = arcpy.mapping.Layer(grid) 

print "Adding citrus layer to map.."

arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")

print "Selecting intersecting grids.."

arcpy.MakeFeatureLayer_management(grid, 'grid_sel') 
arcpy.SelectLayerByLocation_management('grid_sel', 'intersect', citrus)
arcpy.CopyFeatures_management('grid_sel', 'grid_sel_layer') # save selected grids into new layer

print "Exporting selected grids to excel.."
arcpy.TableToExcel_conversion(path + r"\grid_sel_layer.shp", path + r"\grids.xls")

#import the excel file back to python
workbook = xlrd.open_workbook(path + r"\grids.xls")
sheet = workbook.sheet_by_index(0)

# put grid ids in a list
a = sorted(sheet.col_values(columnidx)[1:])
c = [str(int(i)) for i in a]
    
name =[]
for i in range(len(c)):
    if int(year)<12:
        if len(c[i])==6:
            name.append(front_str + c[i] + back_str)
        else:
            name.append(front_str + "0" + c[i] + back_str)
    else:
        if len(c[i])==6:
            east = int(c[i][0]) + 1
            west = int(c[i][0]) + 3
            ##north = int(c[i][0]) + 5
            name.append(front_str + str(east) + c[i][1:] + back_str)
            name.append(front_str + str(west) + c[i][1:] + back_str)
            ##name.append(front_str + str(north) + c[i][1:] + back_str)
        else:    
            name.append(front_str + "1" + c[i] + back_str)
            name.append(front_str + "3" + c[i] + back_str)
            ##name.append(front_str + "5" + c[i] + back_str)

# create a file geodatabase to save mosaic dataset
out_folder_path = path + r"\fileGDB"
out_name = "fGDB.gdb"
arcpy.CreateFileGDB_management(out_folder_path, out_name)

print "Creating mosaic.."

# create empty mosaic dataset in fGDB.gdb
gdbname = path + r"\fileGDB\fGDB.gdb"
mdname = "mosaicds"
coordinate = "NAD 1983 StatePlane Florida East FIPS 0901 (US Feet)"
noband = "3"
pixtype = "8_BIT_UNSIGNED"
pdef = "NONE"
wavelength = ""

arcpy.CreateMosaicDataset_management(gdbname, mdname, coordinate, noband, pixtype, pdef, wavelength)

# Add rasters to mosaic dataset
arcpy.env.workspace = sid_loc

print "Adding rasters.."

mdname = gdbname + "/" + mdname
rastype = "Raster Dataset"
input_rasters = ";".join(name)
updatecs = "UPDATE_CELL_SIZES"
updatebnd = "UPDATE_BOUNDARY"

arcpy.AddRastersToMosaicDataset_management(mdname, rastype, input_rasters, updatecs, updatebnd)
print "Merging.."

# Copy mosaic dataset to raster
merged_raster = path + r"\Merged" + "\\" +  loc_id + ".tif"
arcpy.CopyRaster_management(mdname, merged_raster)
print "..done."

desc = arcpy.Describe(mdname)
SR = desc.spatialReference
arcpy.DefineProjection_management(merged_raster, SR)

arcpy.env.extent = desc.extent  ######## DP --- this should fix it. again.

# get time used by computer to run the script
print "Merged rasters in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

# Project citrus shapefile FIRST before running 'extract by mask' or 'clip' tool
arcpy.env.workspace = path + r"\Citrus"

inMaskData = path + "\\" + region + "_prj.shp"
arcpy.Project_management(citrus, inMaskData, SR)

print "Extracting.."
arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(merged_raster, inMaskData)
out_raster = path + r"\Citrus" + "\\" + loc_id + ".tif"
print "..saving.."
outExtractByMask.save(out_raster)
print "..done.."
arcpy.CheckInExtension("Spatial")
    
# get time used by computer to run the script
print "..in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(out_raster, loc_id + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "TOP")

print "Creating up to " + str(numPoints) + " random polys.."
# Create random polygons on citrus polygon layer

# dissolve citrus shapefile
arcpy.Dissolve_management(citrus, path + r"\citrus_dissolved")

# create random points
outName = "random_points"
conFC = path + r"\citrus_dissolved.shp"

arcpy.CreateRandomPoints_management(path, outName, conFC, "", numPoints, "100 Meters", "", "")

# draw a circle around points using buffer tool
arcpy.Buffer_analysis(path + r"\random_points.shp", path + r"\random_circles", "20 Meters")

# draw polygons around the circles
arcpy.FeatureEnvelopeToPolygon_management(path + r"\random_circles.shp", path + r"\random_polygons")

# add random polygons layer to map document

# create a new layer
randomPoly = arcpy.mapping.Layer(path + r"\random_polygons.shp")

# add layers to the map
arcpy.mapping.AddLayer(df, randomPoly, "TOP")
     
# save the map document
mxd.saveACopy(path + "\\" + loc_id + "_pre_seg.mxd")

# get time used by computer to run the script
print "End of Side A - something may have completed in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

print "Opening arcmap for next steps.."

# open the map document                           
os.startfile(path + "\\" + loc_id + "_pre_seg.mxd")

