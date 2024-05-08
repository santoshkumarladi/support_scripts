#!/usr/bin/python

from __future__ import division
import sys, getopt,os,re
import random,time
import string
import threading

def renameDir (path):
    print 'Rename dir on all mounts path'
    for root, dirs, files in os.walk(path):
        for dirN in dirs:
            data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits ) for _ in range(80))
            srcPath = os.path.join(root,dirN)
            dstPath = os.path.join(root,data)
            print srcPath +" "+dstPath
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
                print go_inside +" "+dstPath
                try:
                    os.rename(go_inside,dstPath)
                except:
                    print "file rename failed "

def remFiles(rootDir): 
    list_dirs = os.walk(rootDir) 
    for root, dirs, files in list_dirs: 
        for d in dirs: 
            print os.path.join(root, d)
        for f in files: 
            print os.path.join(root, f) 
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

def createfile(f,fseek,fs,bs):
    print "write File"
    data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits + string.punctuation ) for _ in range(bs))
    f.seek(fseek, 0)
    total = 0
    while total < fs:
        f.write(data)
        total = total+bs
    os.system('sync')

def readfil(f,fseek,fs):
    print "Read File -> "+str(fs)
    f.seek(fseek, 0)
    while True:
        data = f.read(fs)
        print data
        if not data:
            break
        yield data

def readfile(f,fseek,fs,bs):
    print "Read File -> "+str(fs)
    time.sleep(120)
    f.seek(fseek, 0)
    total = 0
    while total < fs:
        data = f.read(bs)
        total = total+bs

def main(argv):
    inputpath = ''
    outputfile = ''
    wthreads = []
    rthreads = []
    block = ["4kb","8kb","16kb","32kb","64kb"]
    try:
        opts, args = getopt.getopt(argv,"hi:r:s:n:",["ipath=","size=","rp=","nothr="])
    except getopt.GetoptError:
        print 'fops.py -i <inputpath> -b <bs> -n <nothreads>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'fops.py -i <inputpath> -b <bs> -n <nothreads>'
            sys.exit()
        elif opt in ("-i", "--ipath"):
            inputpath = arg
        elif opt in ("-s", "--size"):
            size = arg
        elif opt in ("-r", "--rp"):
            rp = int(arg)
        elif opt in ("-n", "--nothr"):
            nothr = int(arg)

    fseek = 0
    j=k=w=0

    readp = int(rp* (nothr/100))
    fs = int(get_bytes(size)/nothr)-1024
    fileName = inputpath+"/testBigFile"+str(random.randint(100,128908))

    print "Read Percentage is -> "+str(readp)
    fd = open(fileName,"w+")
    fd.seek(get_bytes(size)-1)
    fd.write(b"\0")
    

    cmd = "sudo /home/nutanix/scripts/automation/brkntest pathname="+fileName+" bs=64K </dev/null>/dev/null 2>&1 &"
    print cmd
    os.system(cmd)


    print "Create file "+fileName+" of size "+str(fs)
    for i in range(nothr):
        bsize = get_bytes(block[j])
        if w <nothr-readp:
            t = threading.Thread(target=createfile, args=(fd,fseek,fs,bsize,))
            wthreads.append(t)
            t.start()
            w = w+1

        fseek = fs+fseek
        if j > len(block)-2: 
            j=0
        else :
            j = j+1

    for x in wthreads: 
        x.join()

    sleep(120)

    fseek = 0
    j=k=w=0
    for i in range(nothr):
        bsize = get_bytes(block[j])
        if k < readp:
            t = threading.Thread(target=readfile, args=(fd,fseek,fs,bsize,))
            rthreads.append(t)
            k = k+1

        fseek = fs+fseek
        if j > len(block)-2: 
            j=0
        else :
            j = j+1

    for x in rthreads:
        x.start()
        time.sleep(2)

    for v in rthreads: 
        v.join()

    fd.close()

if __name__ == "__main__":
    main(sys.argv[1:])
