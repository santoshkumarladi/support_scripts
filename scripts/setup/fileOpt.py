#!/usr/bin/python

import sys, getopt,os,re
import random
import string


def fillFiles (path):
    print 'Create /append data to files '
    for root, dirs, files in os.walk(path):
        dir_content = []
        for filea in files:
            abs_path  = os.path.dirname(os.path.relpath(filea))
            #print 'abs_path -> ',abs_path
            go_inside = os.path.join(abs_path, filea)
            #print "go_inside -> ",go_inside
            if  os.path.exists(abs_path):  
                appendDtr(go_inside,"10K","1K")

def Test1(rootDir): 
    list_dirs = os.walk(rootDir) 
    for root, dirs, files in list_dirs: 
        for f in files:
            #print os.path.join(root, f) 
            bpath = os.path.join(root, f)
            appendDtr(bpath,"10KB","1KB")

def get_bytes(fsize):
    match = re.match(r"^([0-9]+)([a-zA-Z]+)$",fsize,re.I)
    (size,suffix) =  match.groups()
    size = int(float(size))
    suffix = suffix.lower()

    if suffix == 'kb' or suffix == 'kib':
        return size << 10
    elif suffix == 'mb' or suffix == 'mib':
        return size << 20
    elif suffix == 'gb' or suffix == 'gib':
        return size << 30

    return False

def appendDtr(filP,fsize,bsize):
    fs = get_bytes(fsize)
    bs = get_bytes(bsize)
    print 'Update data on the file -> ',filP
    data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits + string.punctuation ) for _ in range(bs))
    isFile = os.path.isfile(filP)
    if isFile:
        #print 'The file path -> '+filP+' of file size '+str(fs)+' of block size '+str(bs)
        total = 0
        f = open(filP,"w")
        while total < fs:
            f.write(data)
            total = total+bs
        f.close()
          
def main(argv):
    inputpath = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:d:b:",["ipath=","depth=","breadth="])
    except getopt.GetoptError:
        print 'test.py -i <inputpath> -d <depth> -b <breadth>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -i <inputpath> -d <depth> -b <breadth>'
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputpath = arg
        elif opt in ("-d", "--depth"):
            depth = int(arg)
        elif opt in ("-b", "--breadth"):
            breadth = int(arg)

    print 'Input path is "', inputpath
    Test1(inputpath)

if __name__ == "__main__":
    main(sys.argv[1:])
