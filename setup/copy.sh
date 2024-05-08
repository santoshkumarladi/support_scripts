#! /bin/bash

set -x
for i in `svmips`; do scp ~/config/*.gflags $i:~/config/; done
