import arcpy, os, random, xlrd, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()
##################################################
##################################################
## Parameters or variables that need to be changed
## before running the script           ###########

# Florida aerial grid
grid = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\AerialPhotographygrids_2015\FLorida_East_NAD83_2011_USft.shp"

# location of citrus polygons
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\IR_3.shp"

# the path to current workspace
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new"

# location of sid files
sid_loc = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_1\2008\sid"

# varibles to create names of sid files
front_str = "OP2008_nc_0"
back_str =  "_24.sid"

# identify which column number contains the Old_SPE_ID that is needed to create names of sid files
# if it is fifth column in attribute table, enter 5-2 below
columnidx = 3

# merged raster name
merged_raster_name = "IR_3_08"

# location of a blank arcmap document
blank_map = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\blank map.mxd"

##################################################
##################################################

# create new folders in "path"
os.makedirs(path + r"\Citrus only")
os.makedirs(path + r"\Merged rasters")
os.makedirs(path + r"\Signature file")

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
grid = arcpy.mapping.Layer(grid) 

# add layers to the map
arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")
#arcpy.mapping.AddLayer(df, grid, "AUTO_ARRANGE")

# select grids that intersect with citrus polygons
arcpy.MakeFeatureLayer_management(grid, 'grid_sel') 
arcpy.SelectLayerByLocation_management('grid_sel', 'intersect', citrus)
 
# save selected grids into new layer
arcpy.CopyFeatures_management('grid_sel', 'grid_sel_layer')

# add new layer to the arcmap
grid_sel_layer = arcpy.mapping.Layer(path + r"\grid_sel_layer.shp")
#arcpy.mapping.AddLayer(df, grid_sel_layer, "AUTO_ARRANGE")

# export the selected grids to an excel file
arcpy.TableToExcel_conversion(path + r"\grid_sel_layer.shp", path + r"\grids.xls")

#import the excel file back to python
workbook = xlrd.open_workbook(path + r"\grids.xls")
sheet = workbook.sheet_by_index(0)

# put grid ids in a list
a = sorted(sheet.col_values(columnidx))
len(a)
b = a[0:len(a)-1]
c = [str(int(i)) for i in b]

front = [front_str * 1 for i in c]
back = [back_str * 1 for i in c]

name =[]
for i in range(len(c)):
    name.append(front[i] + c[i] + back[i])

len(name)
name

# Mosaic to new raster
input_rasters = ";".join(name)
output_location = path + r"\Merged rasters"
raster_dataset_name_with_extension = merged_raster_name
coordinate_system_for_the_raster = ""
pixel_type = "8_BIT_UNSIGNED"
cellsize = ""
number_of_bands ="3"
mosaic_method = "LAST"
mosaic_colormap_mode = "FIRST"

try:
    arcpy.env.workspace = sid_loc
    arcpy.MosaicToNewRaster_management(input_rasters, output_location, raster_dataset_name_with_extension,\
                                       coordinate_system_for_the_raster, pixel_type, cellsize, number_of_bands,\
                                       mosaic_method, mosaic_colormap_mode)
except:
    print "Mosaic To New Raster failed."
    print arcpy.GetMessages()

# assign a name to location of merged raster
merged_raster = output_location + "\\" +  merged_raster_name


# Extract by mask
inMaskData = citrus
arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(merged_raster, inMaskData)
out_raster = path + r"\Citrus only" +"\\" + merged_raster_name
outExtractByMask.save(out_raster)

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(out_raster, merged_raster_name + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "AUTO_ARRANGE")

# Create 40 random polygons on citrus polygon layer

# dissolve IR_3
arcpy.Dissolve_management(citrus, path + r"\citrus_dissolved")

# create random points
outName = "random_points"
conFC = path + r"\citrus_dissolved.shp"
numPoints = 40

arcpy.CreateRandomPoints_management(path, outName, conFC, "", numPoints, "100 Meters", "", "")

# draw a circle around points using buffer tool
arcpy.Buffer_analysis(path + r"\random_points.shp", path + r"\random_circles", "20 Meters")

# draw polygons around the circles
arcpy.FeatureEnvelopeToPolygon_management(path + r"\random_circles.shp", path + r"\random_polygons")



# add random polygons layer to map document

# create a new layer
randomPoly = arcpy.mapping.Layer(path + r"\random_polygons.shp")

# add layers to the map
arcpy.mapping.AddLayer(df, randomPoly, "AUTO_ARRANGE")
    
# save the map document
mxd.saveACopy(path + "\\" + merged_raster_name + "_pre_sig.mxd")

# open the map document                           
os.startfile(path + "\\" + merged_raster_name + "_pre_sig.mxd")

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)


 
