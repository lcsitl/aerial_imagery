##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# the path to current folder
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Directional"

# county subregion
region = "IR_3"

# two digit year
year = "08"

# location of citrus polygon shapefile
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new" + "/" + region + ".shp"

# location of a blank arcmap document
blank_map = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\blank map.mxd"


##*************************************************##


# create a copy of citrus shapefile in path folder
import arcpy, os, time
start_time = time.time()

arcpy.CopyFeatures_management(citrus, path + "/" + region + "_" + year + "_directional.shp")

# import CustomGrid Toolbox
arcpy.ImportToolbox(r"U:\Gottwald_Lab\LMehra\Aerial Imagery\CustomGridTools.tbx")

#create polyline feature
arcpy.CreateQSections_CustomGridTools (citrus, path + "/" + region + "_" + year + "_polylines.shp", 0.0005)

# set the workspace
arcpy.env.workspace = path

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

# 1. click 'start editing', select all from "*_polylines" layer
# 2. from advanced editing toolbar, click split polygons
# 3. choose "*_directional.shp" as target layer
# 4. click 'save edits', and 'stop editing'

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

