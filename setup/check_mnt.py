import os

MOUNT_POINT = "/mnt/archive"

if os.path.ismount(MOUNT_POINT):
    print "mount point exsits"+MOUNT_POINT
else:
    print "mount point dosenot exsits"+MOUNT_POINT

