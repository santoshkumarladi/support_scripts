#!/usr/bin/python

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
    data = ''.join(random.choice(string.ascii_letters + string.ascii_uppercase + string.ascii_lowercase + string.digits + string.hexdigits + string.punctuation ) for _ in range(bs))
    f.seek(fseek, 0)
    total = 0
    while total < fs:
        print "Write -> "+str(total)
        f.write(data)
        total = total+bs
        os.system(sync)

def readFile(f,fseek,fs):
    f.seek(fseek, 0)
    while True:
        data = file_object.read(fs)
        if not data:
            break
        yield data

def main(argv):
    inputpath = ''
    outputfile = ''
    threads = []
    block = ["4kb","8kb","16kb","32kb","64kb"]
    try:
        opts, args = getopt.getopt(argv,"hi:b:s:n:",["ipath=","size=","bs=","nothr="])
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

    fs = int(get_bytes(size)/nothr)-1024
    fseek = 0
    fileName = inputpath+"/testBigFile"+str(random.randint(100,128908))
    fd = open(fileName,"w+")
    fd.seek(get_bytes(size)-1)
    fd.write(b"\0")
    readp = int(rp*(nothr/100))
    print "Read Percentage is -> "+str(readp)
    print "Create file "+fileName+" of size "+str(fs)
    j=k=0
    for i in range(nothr):
        bsize = get_bytes(block[j])
        t = threading.Thread(target=createfile, args=(fd,fseek,fs,bsize,))
        fseek = fs+fseek
        threads.append(t)
        if k < readp:
            t = threading.Thread(target=readFile, args=(fd,fseek,fs))
            threads.append(t)
            k = k+1

        if j > len(block)-1 : 
            j=0
        else :
            j = j+1


    if len(threads) ==0:
        exit()
    for x in threads:
        x.start()
        time.sleep(2)

    for x in threads: 
        x.join()

    fd.close()

if __name__ == "__main__":
    main(sys.argv[1:])
