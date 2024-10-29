#!/bin/bash
cd ..

for ns in 6 10 15; do
    for i in {1..5}; do
        python main.py -S "$ns" -i "$i" -NT 12 -m exhaustive
    done
done
