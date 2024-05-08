#!/usr/bin/python

import sys, getopt,os,re
import random,time
import string
import threading

def createDir(dirPath,count,d,bre):
    #print 'Start creating the dir tree @' , dirPath
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
            #print 'Dir create failed -> ',srcPath
            cmd = "mkdir -p "+srcPath
            os.system(cmd)



def createTree(path,dep,bre):
    totalB = 1
    basePath = path
    srcPath = ''
    dirName = ''
    for d in range(dep):
        totalB = pow(bre,totalB)
        #print "TotalB -> ",str(totalB)
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
            createDir(go_inside,10,2,bre)
            #cmd = 'touch '+go_inside+'/testFile{1..10000}'
            #os.system(cmd)

def fillFiles (path):
    print 'Create /append data to files '
    for root, dirs, files in os.walk(path):
        dir_content = []
        for filea in files:
            abs_path  = os.path.dirname(os.path.relpath(filea))
            go_inside = os.path.join(abs_path, filea)
            if  os.path.exists(abs_path):  
                appendDtr(go_inside,"10K","1K")

def renameDir (path):
    print 'Rename dir on all mounts path'
    for root, dirs, files in os.walk(path):
        for dirN in dirs:
            data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits ) for _ in range(80))
            srcPath = os.path.join(root,dirN)
            dstPath = os.path.join(root,data)
            #print srcPath +" "+dstPath
            try:
                os.rename(srcPath,dstPath)
                cmd = 'touch '+dstPath+'/testNewFile{1..1000}'
                os.system(cmd)
            except:
                print "dirs rename failed "


def renameFile(path):
    print 'Rename fil on all mounts path'
    for root, dirs, files in os.walk(path):
        for filea in files:
            abs_path  = os.path.dirname(os.path.relpath(filea))
            go_inside = os.path.join(abs_path, filea)
            if  os.path.exists(abs_path):
                data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits ) for _ in range(80))
                dstPath = os.path.join(abs_path,data)
                #print go_inside +" "+dstPath
                try:
                    os.rename(go_inside,dstPath)
                except:
                    print "file rename failed "

def remFiles(rootDir): 
    print 'Remove files  all mounts path', rootDir
    list_dirs = os.walk(rootDir) 
    for root, dirs, files in list_dirs: 
        for f in files: 
            if f != 'testBigFile':
                #print os.path.join(root, f) 
                bpath = os.path.join(root, f)
                try:
                    os.remove(bpath)
                except:
                    print "file delete failed "

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
            #print 'Write data of -> ',str(bs)
            f.write(data)
            total = total+bs
        f.close()

def main(argv):
    inputpath = ''
    outputfile = ''
    threads = []
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

    cmd = "mount | grep \""+inputpath+"\""
    print cmd 
    os.system(cmd)
    mpaths  = (os.popen(cmd).read()).split('\n')
     
    for path in mpaths :
        if path:
            rp = path.split()
            path = rp[2]+"/testDirTest"+str(random.randint(100,128908))
            print "Input path is "+path
            t = threading.Thread(target=createTree, args=(path,depth,breadth,))
            threads.append(t)
            t = threading.Thread(target=fillFiles, args=(path,))
            threads.append(t)
            t = threading.Thread(target=renameDir, args=(path,))
            threads.append(t)
            t = threading.Thread(target=renameFile, args=(path,))
            threads.append(t)
            t = threading.Thread(target=remFiles, args=(path,))
            threads.append(t)
    if len(threads) ==0:
        exit()
    for x in threads:
        x.start()
        time.sleep(5)

    for x in threads: 
        x.join()


if __name__ == "__main__":
    while(1):
        main(sys.argv[1:])
