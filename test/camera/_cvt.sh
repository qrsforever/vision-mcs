#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

cnt=1

cameras=('cam1' 'cam2' 'cam3' 'cam4')

for cam in ${cameras[@]}
do
    mkdir -p datasets/$cam
done


for f in $(ls out/cam1)
do
    img=$(printf "%03d" $cnt)
    for cam in ${cameras[@]}
    do
        cp out/$cam/$f datasets/$cam/$img.png
    done
    (( cnt = cnt + 1 ))
done
