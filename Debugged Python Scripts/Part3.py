"""
Name: 3_AerialImage_processing_directional_analysis_part_1of2 (aka script 3)
    
This script divides each polygon in to four sections (NE, NW, SE, and SW). 
Once this script finishes, an ArcMap document will open.

Code for this script came from:
http://ianbroad.com/creating-quarter-quarter-section-grid-python/

Authored by: lucky mehra
"""

##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder (Directional folder, I think)
path = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\Directional"

# county subregion
region = "HeSm"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\HeSm\HeSm.shp"

# location of a blank arcmap document
blank_map = r"C:\Users\leigh.sitler\Desktop\Aerial Imagery\blank_map.mxd"


##*************************************************##


# create a copy of citrus shapefile in path folder
import arcpy, os, time
start_time = time.time()

arcpy.CopyFeatures_management(citrus, path + "/" + region + "_" + year + "_directional.shp")

# import CustomGrid Toolbox
arcpy.ImportToolbox(r"U:\Gottwald_Lab\LMehra\1.1_Aerial_Imagery\CustomGridTools.tbx")

#create polyline feature
arcpy.CreateQSections_CustomGridTools (citrus, path + "/" + region + "_" + year + "_polylines.shp", 0.0005)

# set the workspace
arcpy.env.workspace = path
print "and then..."

# set the overwrite to TRUE to save the existing map document
arcpy.env.overwriteOutput = True

# get the map document
mxd = arcpy.mapping.MapDocument(blank_map)

# get the data frame
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

# create a new layer

sections = arcpy.mapping.Layer(path + "/" + region + "_" + year + "_directional.shp")
lines = arcpy.mapping.Layer(path + "/" + region + "_" + year + "_polylines.shp") 

# add layers to the map
arcpy.mapping.AddLayer(df, sections, "AUTO_ARRANGE")
arcpy.mapping.AddLayer(df, lines, "AUTO_ARRANGE")
print "almost there"

# save the map document
mxd.saveACopy(path + "\\" + region + "_" + year + "_post_sig_dir.mxd")

# open the map document                           
os.startfile(path + "\\" + region + "_" + year + "_post_sig_dir.mxd")

## ******************************************************##
## Once the ArcMap document opens,                       ##
## use split polygon tool to create new polygon features ##
## made by using above poly line class                   ##
##                                                       ##
## ******************************************************##

# 1. click 'start editing' (you may have to turn the Editor toolbar on), select all from "*_polylines" layer (right click the layer, go to Selection>Select All)
# 2. from advanced editing toolbar (you may have to turn the Advanced Editing toolbar on), click split polygons
# 3. choose "*_directional.shp" as target layer, Leave the cluster tolerance as default, click OK
# 4. On the Editor toolbar, click 'save edits', and 'stop editing'. Close the map document.

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

