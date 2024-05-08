file=$1
count=`wc -l $file | awk '{print $1}'`
echo "Total egroups: $count"

ii=0
for i in `cat $file`; do
ii=$((ii+1))
pct=$((ii*100/count))
echo -ne "\rProgress: $pct%"
done
