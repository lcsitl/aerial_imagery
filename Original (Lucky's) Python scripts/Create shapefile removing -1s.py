# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:49:15 2017

@author: lucky.mehra
"""

# Location of excel and shape files

# excel file with polygon_quality of each citrus polygon
xl = r"C:\Users\leigh.sitler\Desktop\Aerial\DeSoto\DeSoto_2006_1\Output tables\Excel\ds_06_1_rf_all.xls"
sheet = "Sheet3"

# location of citrus polygon shapefile, where we need to make selection
citrus = r"C:\Users\leigh.sitler\Desktop\Aerial\DeSoto\DeSoto20_1.shp"

# location and name of new shapefile that will have only selected polygons
new_citrus = r"C:\Users\leigh.sitler\Desktop\Aerial\DeSoto\DeSoto_2014_1\DeSoto_2006_1s.shp"


#################################
##    Script starts here       ##
#################################

# Impport modules
import pandas as pd
import arcpy, time
start_time = time.time()

# Read excel file from previous year using pandas
df = pd.read_excel(open(xl, 'rb'), sheetname = sheet)

# Select all the rows where polygon_quality is not -1
df1 = df.loc[df['Polygon_quality'] == -1]

# Create a where clause to go into Select_analysis
string = ','.join([str(x) for x in df1['F_INDEX'].tolist()])
where_clause = '"F_index" in (%s)' % string

# Make the selection
arcpy.Select_analysis(citrus, new_citrus, where_clause)

# get time used by computer to run the script
print "Mission complete in hours:minutes:seconds"
seconds = time.time() - start_time
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

