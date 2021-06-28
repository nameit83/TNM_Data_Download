import sys
import arcpy
import os
import traceback
import requests
import json

## ====================================================================================================================


def print_exception():

    try:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        theMsg = "\t" + traceback.format_exception(exc_type, exc_value, exc_traceback)[1] + "\n\t" + traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]

        if theMsg.find("exit") > -1:
            AddMsgAndPrint("\n\n")
            pass
        else:
            AddMsgAndPrint("\n----------------------------------- ERROR Start -----------------------------------",2)
            AddMsgAndPrint(theMsg,2)
            AddMsgAndPrint("------------------------------------- ERROR End -----------------------------------\n",2)

    except:
        AddMsgAndPrint("Unhandled error in print_exception method", 2)
        pass

## ===================================================================================================================


def AddMsgAndPrint(msg, severity=0):
    # prints message to screen if run as a python script
    # Adds tool message to the geoprocessor
    # Split the message on  \n first, so that if it's multiple lines, a GPMessage will be added for each line

    #print(msg)

    try:
        f = open(textFilePath,'a+')
        f.write(msg + " \n")
        f.close
        del f

    except:
        pass

    if severity == 0:
        arcpy.AddMessage(msg)

    elif severity == 1:
        arcpy.AddWarning(msg)

    elif severity == 2:
        arcpy.AddError(msg)

## ====================================================================================================================


if __name__ == '__main__':

    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            AddMsgAndPrint(
                "\nSpatial Analyst Extension not enabled. Please enable Spatial Analyst from the Tools/Extensions menu. Exiting...\n",
                2)
            exit()

        fc = arcpy.GetParameterAsText(0)
        download_dir = arcpy.GetParameterAsText(1)




        arcpy.env.overwriteOutput = True
        arcpy.env.parallelProcessingFactor = "75%"

        desc = arcpy.Describe(fc)
        dscr_for_sr = arcpy.da.Describe(fc)['spatialReference']
        AddMsgAndPrint(arcpy.da.Describe(fc)['spatialReference'].type)
        if dscr_for_sr.type not in ['Geographic']:
            AddMsgAndPrint("Entered the IF")
            AddMsgAndPrint("The feature set is in Projected Coordinate System, Converting to Geographic Coordinate System")
            wkid =4326
            geog_proj = arcpy.SpatialReference(wkid)
            arcpy.management.Project(fc, 'reprojected' , geog_proj)
            # location = dscr_for_sr['catalogPath']
            # AddMsgAndPrint(location)
            # AddMsgAndPrint(desc_sr.name)
            # AddMsgAndPrint(geog_proj.name)
            description = arcpy.da.Describe(fc)['catalogPath']
            new_loc = '\\'.join(x for x in description.split('\\')[:len(description.split('\\'))-1]) + "\\reprojected"
            # if arcpy.Exists(new_loc):
            #     arcpy.Delete_management(new_loc)
            # desc = arcpy.Describe()
            AddMsgAndPrint(new_loc)
            desc = arcpy.Describe(new_loc)
        baseurl = "https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Digital%20Elevation%20Model%20(DEM)%201%20meter&prodFormats=GeoTIFF&outputFormat=JSON&bbox="
        minx = round(float(desc.extent.XMin), 4)
        miny = round(float(desc.extent.YMin), 4)
        maxx = round(float(desc.extent.XMax), 4)
        maxy = round(float(desc.extent.YMax), 4)

        if minx == maxx:
            maxx = maxx + 0.0001

        if miny == maxy:
            maxy = round(maxy + 0.0001, 4)

        queryurl = baseurl + str(minx) + "," + str(miny) + "," + str(maxx) + "," + str(maxy)
        AddMsgAndPrint(queryurl)


        response = requests.get(queryurl)

        json_string = json.loads(response.text)
        arcpy.AddMessage("Parsing completed")
        maximum = (json_string["total"])
        arcpy.AddMessage("Total files to be downloaded: " + str(maximum))
        counter = 0
        prodlist = []
        output = ''
        for i in range(0, maximum):
            output = os.path.join(download_dir, fc)
            if not os.path.exists(output):
                os.mkdir(output)
            tiffile = json_string["items"][i]["downloadURL"]
            arcpy.SetProgressorLabel("Downloading the TIF for " + json_string["items"][i]["title"])
            output = os.path.join(output, json_string["items"][i]["title"] + ".tif")
            # arcpy.AddMessage(tiffile)
            r = requests.get(tiffile)
            prodlist.append(json_string["items"][i]["title"])
            with open(output, 'wb') as f:
                f.write(r.content)
            arcpy.AddMessage("Download Complete for " + json_string["items"][i]["title"] + "\nTotal Files: " + str(counter+1)+ " out of " + str(maximum))
            counter = counter + 1

        arcpy.AddMessage("Total DEMs from server:" + str(maximum))
        arcpy.AddMessage("Total Downloaded Files:" + str(counter))
        arcpy.AddMessage("All files were downloaded to " + download_dir)

        del json_string
        del prodlist
        del response


    except:
        print_exception()



