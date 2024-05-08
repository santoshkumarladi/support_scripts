#! /bin/bash
set -x

allssh ()
{
    CMDS=$@;
    OPTS="-q -t -o LogLevel=ERROR -o StrictHostKeyChecking=no";
    for i in `svmips`;
    do
        echo "================== "$i" =================";
        /usr/bin/ssh $OPTS $i "source /etc/profile;$@";
    done
}

allssh ls 
#for ip in `svmips`; do echo $ip; ssh -q $ip mv "${DIR1}"/star*INFO* "${DIR2}"/$ip/"${DIR1}"/;done;
