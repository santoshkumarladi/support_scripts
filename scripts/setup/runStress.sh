#!/bin/bash

if [ $# -lt 2 ]; then
    echo "usage:$0 dev output_dir [iodepth]"
    exit 1
fi

OUTDIR="$1"
SIZE="$2"

if [ ! -d $OUTDIR ]; then
    mkdir -p $OUTDIR
fi

RUNTIME=30
BLOCK_SIZES=(512 4K 8K 16K 64K 128K 256K 512K)


run_test() 
{
    outdir=$1
    block_size=$2
    path="$path/$block_size"
    sudo mkdir -p $path
    
    cmd = "sudo /home/nutanix/clSc/zombFileMulN1 pathname=$path fs=1000K bs=$block_size nc=1000000 "
    nohup $cmd &
    cmd = "sudo /home/nutanix/clSc/fop -H 4 -W 4 -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd -s 10000M -t 15 -n 1 $path"
    nohup $cmd &
    cmd = " sudo /home/nutanix/clSc/fop -H 4 -W 4 -W 10,100,500,1000  -o cwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastdcwrnastd  -f 10k,20,20,10 -n 300 -s 10k,20,10k,100k -t 10 -O RD $path "
    nohup $cmd &
    cmd = "sudo /home/nutanix/clSc/zombFileMulCnt pathname=$path fs=100K bs=$block_size nc=1000000 rm=0 "
    nohup $cmd &
    # ./smallFiles pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
    cmd = "sudo /home/nutanix/clSc/smallFiles pathname=$path sz=$block_size bs=$block_size nf=1000000 "
    nohup $cmd &
    #Usage: ./lotSmall pathname=<name of the dir> bs=<block size> sz=<file size> nf=<no of files>
    cmd = "sudo /home/nutanix/clSc/lotSmall pathname=$path sz=$block_size bs=$block_size nf=1000000 "
    nohup $cmd &
    echo "sudo ln -v /home/nutanix/dst.1597252208 $path/testBigFile"
    sudo ln -v /home/nutanix/dst.1597252208 $path/testBigFile
    #Usage: ./createLargeF srcpath=<src file> dstpath=<dst file> bs=<block size> dfs=<destination filesize> rd=<random copy>
    cmd = "sudo /home/nutanix/clSc/createLargeF srcpath=/home/nutanix/dst.1597252208  dstpath=$path bs=$block_size dfs=$file_size rd=0 "
    nohup $cmd &
}

# run all the jobs
for block_size in "${BLOCK_SIZES[@]}"
do
    echo "run $OUTDIR in $block_size, $SIZE"
    run_test $OUTDIR $block_size $SIZE
done

