# Creates an empty file (to use as check after reboot)
# silentReboot - to be less verbose at start time
# successfulBoot - to avoid entering setup mode
# apMode - to check if ap_if should be turned off
def registerFile(filename):
    try:
        open(filename,"x").close()
    except:
        print("Couldn't create register file", filename)


# Returns true if file exists at the removal time
def checkAndRemoveFile(filename):
    import os
    try:
        os.remove(filename)
        success = True
    except:
        success = False
    del os
    return success
