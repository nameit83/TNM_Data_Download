import arcpy
import os
import traceback
import sys


## ====================================================================================================================


def print_exception():
    try:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        theMsg = "\t" + traceback.format_exception(exc_type, exc_value, exc_traceback)[1] + "\n\t" + \
                 traceback.format_exception(exc_type, exc_value, exc_traceback)[-1]

        if theMsg.find("exit") > -1:
            AddMsgAndPrint("\n\n")
            pass
        else:
            AddMsgAndPrint("\n----------------------------------- ERROR Start -----------------------------------", 2)
            AddMsgAndPrint(theMsg, 2)
            AddMsgAndPrint("------------------------------------- ERROR End -----------------------------------\n", 2)

    except:
        AddMsgAndPrint("Unhandled error in print_exception method", 2)
        pass


## ===================================================================================================================


def AddMsgAndPrint(msg, severity=0):
    # prints message to screen if run as a python script
    # Adds tool message to the geoprocessor
    # Split the message on  \n first, so that if it's multiple lines, a GPMessage will be added for each line

    # print(msg)

    try:
        f = open(textFilePath, 'a+')
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


arcpy.env.overwriteOutput = True
arcpy.env.parallelProcessingFactor = "75%"

if __name__ == '__main__':

    try:
        if arcpy.CheckExtension("spatial") == "Available":
            arcpy.CheckOutExtension("spatial")
        else:
            arcpy.AddError(
                "\nSpatial Analyst Extension not enabled. Please enable Spatial Analyst and try again. Exiting...\n")
            sys.exit()

        inRasters = arcpy.GetParameterAsText(0)
        outFilename = arcpy.GetParameterAsText(1)
        saveLocation = arcpy.GetParameterAsText(2)

        arcpy.env.workspace = saveLocation

        outFilename += ".tif"

        arcpy.AddMessage(os.getcwd())

        saveLocation = os.path.join(saveLocation, "Mosaic")

        arcpy.AddMessage(saveLocation)

        if not os.path.exists(saveLocation):
            os.mkdir(saveLocation)
            arcpy.AddMessage("Created a new file named Mosaic")

        arcpy.MosaicToNewRaster_management(inRasters, saveLocation, outFilename, "", "32_BIT_FLOAT", "", 1, "LAST",
                                           "MATCH")

        arcpy.AddMessage(inRasters)

        del inRasters





    except:
        print_exception()
