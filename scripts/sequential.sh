#!/bin/bash

cd ..

for size in 60 90 120 200 300 400 500; do
    for n_trk in 1 2; do
        for n_rpm in 1 2; do
            python main.py -S $size -K $n_trk -R $n_rpm -NT 12
        done
    done
done
