# -*- coding: utf-8 -*-
"""
Created on Thu May 18 11:49:15 2017

@author: lucky.mehra
"""

# Location of excel and shape files

# excel file with polygon_quality of each citrus polygon
xl = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\Output tables\Excel\IR_3_08_rf_all.xls"
sheet = "Sheet3"

# location of citrus polygon shapefile, where we need to make selection
citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2008 new\IR_3.shp"

# location and name of new shapefile that will have only selected polygons
new_citrus = r"C:\Users\lucky.mehra\Desktop\Aerial Imagery\Indian_River\IR_3\2012\IR_3_12.shp"

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
df1 = df.loc[df['Polygon_quality'] != -1]

# Creat a where clause to go into Select_analysis
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

