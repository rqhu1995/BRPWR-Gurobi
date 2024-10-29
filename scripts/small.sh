#!/bin/bash

getValues() {
    key=$1
    case $key in
    6)
        arr=(4 9 17 23 26)
        ;;
    10)
        arr=(1 33 51 60 75)
        ;;
    15)
        arr=(1 217 345 376 377)
        ;;
    *)
        arr=(4 9 17 23 26)
        ;;
    esac
}

cd ..

n_station="$1"
getValues "$n_station"
for inst_no in "${arr[@]}"; do
    python main.py -S "$n_station" -i "$inst_no" -m optimal
done
