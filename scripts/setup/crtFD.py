#!/usr/bin/python

import sys, getopt,os,re
import random
import string

def createDir(dirPath,count,d,bre):
    print 'Start creating the dir tree @' , dirPath
    stack = 1
    b = 0
    for i in range (count):
        if stack < bre :
            stack = stack+1
        else :
            b = b+1
        dirName = "dirTree"+str(d)+"_"+str(b)
        srcPath = os.path.join(dirPath,dirName)
        try :
            os.mkdir(srcPath)
        except :
            print 'Dir create failed -> ',srcPath
            cmd = "mkdir -p "+srcPath
            os.system(cmd)

        cmd = 'touch '+srcPath+'/testNewFile{1..10000}'
        os.system(cmd)


def createTree(path,dep,bre):
    totalB = 1
    basePath = path
    srcPath = ''
    dirName = ''
    for d in range(dep):
        totalB = pow(bre,totalB)
        print "TotalB -> ",str(totalB)
        for b in range(totalB):
            dirName = "dirTree"+str(d)+"_"+str(b)
            createDir(path,totalB,d,bre)
            srcPath = os.path.join(path,dirName)
            path = srcPath
    recreateDir(basePath,bre)

def recreateDir(path,bre):
    print 'Inside path ->  @' , path
    for root, dirs, files in os.walk(path):
        dir_content = []
        for dir in dirs:
            go_inside = os.path.join(path, dir)
            print "go_inside -> ",go_inside
            createDir(go_inside,10,2,bre)
            #cmd = 'touch '+go_inside+'/testFile{1..10000}'
            #os.system(cmd)

def fillFiles (path):
    print 'Create /append data to files '
    for root, dirs, files in os.walk(path):
        dir_content = []
        for dir in dirs:
            if  os.path.exists(dir):  
                go_inside = os.path.join(path, dir)
                print "go_inside -> ",go_inside
                appendDtr(go_inside,"10K","1K")

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

def appendDtr(dirP,fsize,bsize):
    fs = get_bytes(fsize)
    bs = get_bytes(bsize)

    data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits + string.punctuation ) for _ in range(bs))
    for entry in os.listdir(dirP):
        isFile = os.path.isfile(entry)
        folder=os.path.dirname(entry)  
        if os.path.exists(folder):  
            print 'Folder --> ',folder
        if isFile:
            src_path = os.path.join(dirP, entry)
            print 'The file path -> ',src_path
            total = 0
            f = open(src_path,"w")
            while total < fs:
                f.write(data)
                total = total+bs
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
    createTree(inputpath,depth,breadth)
    fillFiles(inputpath)

if __name__ == "__main__":
    main(sys.argv[1:])
