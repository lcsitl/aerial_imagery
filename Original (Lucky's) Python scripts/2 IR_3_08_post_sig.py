##*************************************************##
##                                                 ##
## Parameters or variables that need to be changed ##
## before running the script                       ##
##                                                 ##
##*************************************************##

# location of citrus polygons
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\IR_3.shp"

# the path to current folder (that contains 'Citrus only' folder)
path = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new"

# citrus only raster name
citrus_raster = "IR_3_08"

# location of a blank arcmap document
blank_map = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\blank map.mxd"

##*************************************************##

# Import system modules
import arcpy, xlrd, xlwt, os, time
from arcpy import env
from arcpy.sa import *
start_time = time.time()

# create new folders in "path"
os.makedirs(path + r"\Classified rasters")
os.makedirs(path + r"\Output tables\Excel")
os.makedirs(path + r"\Directional") # to be used in further later scripts
os.makedirs(path + r"\Edge effect") # to be used in further later scripts

# Set local variables
inRaster = path + "/Citrus only/" + citrus_raster
sigFile = path + "/Signature file/" + citrus_raster + "_O.gsg"
aPrioriWeight = "EQUAL"
aPrioriFile = ""
outConfidence = ""

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Create the loop to perform the image classification based on different reject fractions

pth=["0", "05", "1", "25", "5"]

for probThreshold in pth:
        mlcOut = MLClassify(inRaster, sigFile, "0." + probThreshold, aPrioriWeight, aPrioriFile, outConfidence)  
        # Save the output
        out_raster= path + "/Classified rasters/" + citrus_raster + "_rf" +probThreshold
        mlcOut.save(out_raster)

# Set environment settings for tabulate area
env.workspace = path+"/Classified rasters"

# Set local variables
inZoneData = citrus
zoneField = "F_index"
data = arcpy.ListDatasets("*rf*", "Raster")
classField = "VALUE"
processingCellSize = 1

#create the loop to output all classified rasters as excel files
for classifiedRaster in data:
	inClassData = classifiedRaster
	outTable = path + "/Output tables/"+ classifiedRaster +".dbf"
	# Execute TabulateArea
	TabulateArea(inZoneData, zoneField, inClassData, classField, outTable, processingCellSize)
	out_xls = path + "/Output tables/Excel/"+ classifiedRaster +".xls"
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
outsheet1 = wkbk.add_sheet('Sheet3')


outrow_idx = 0
for f in xlsfiles:
        insheet = xlrd.open_workbook(ex + "/" + f).sheets()[0]
        for row_idx in xrange(insheet.nrows):
                if row_idx == 0 and f == xlsfiles[0]:
                        outsheet.write(outrow_idx, 0, "Year")
                        outsheet.write(outrow_idx, 1, "County_subregion")
                        outsheet.write(outrow_idx, 2, "Reject_fraction")
                        outsheet1.write(outrow_idx, 0, insheet.cell_value(row_idx,1))
                        outsheet1.write(outrow_idx, 1, "Optimum_rf1")
                        outsheet1.write(outrow_idx, 2, "Optimum_rf2")
                        outsheet1.write(outrow_idx, 3, "Polygon_quality")
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx,col_idx + 3, insheet.cell_value(row_idx, col_idx))
                        outrow_idx += 1
                if row_idx > 0 and f == xlsfiles[0]:
                        outsheet1.write(outrow_idx, 0, insheet.cell_value(row_idx,1))
                if row_idx > 0:
                        outsheet.write(outrow_idx, 0, int("20" + citrus_raster.split("_")[-1]))
                        outsheet.write(outrow_idx, 1, citrus_raster.split("_")[0] + "_" + citrus_raster.split("_")[1])
                        outsheet.write(outrow_idx, 2, float("0." + f.split(".")[0].split("_")[-1][2:]))
                        for col_idx in xrange(insheet.ncols):
                                outsheet.write(outrow_idx, col_idx + 3, insheet.cell_value(row_idx, col_idx))
                                
                        outrow_idx += 1

wkbk.save(ex + "/" + citrus_raster + "_rf_all.xls")

# add the classified rasters to arcmap document and save

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

# add layers to the map
arcpy.mapping.AddLayer(df, citrus_lyr, "AUTO_ARRANGE")

#add citrus only raster to map
citrus_only = arcpy.MakeRasterLayer_management(path + r"\Citrus only" +"\\" + citrus_raster, citrus_raster + "_O")
citrus_only1 = citrus_only.getOutput(0)
arcpy.mapping.AddLayer(df, citrus_only1, "AUTO_ARRANGE")

# get names of classified rasters into one list
env.workspace = path + "/Classified rasters"
classified_rasters = arcpy.ListDatasets("*rf*", "Raster")

# add these rasters into map
for dataset in classified_rasters:
        cr = arcpy.MakeRasterLayer_management(path + "/Classified rasters/" + dataset, "O_" + dataset)
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


                
