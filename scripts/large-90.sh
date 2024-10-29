#!/bin/bash
cd ..

# Assign the first argument passed to the script to the variable tb
tb=$1

for n_station in 90; do
    if [ $n_station -eq 60 ]; then
        inst_no=4
    else
        inst_no=1
    fi

    # Run all combinations of n_trk and n_rpm for the current station size
    for n_trk in 1 2; do
        for n_rpm in 1 2; do
            # Calculate the session name
            session_name="${n_station}-${n_trk}-${n_rpm}_$((tb * 600 / 3600))h"

            # Start a new screen session and run the commands
            screen -dmS "$session_name" bash -c "
                conda activate gurobi311;
                python main.py -S '$n_station' -K '$n_trk' -R '$n_rpm' -i '$inst_no' -m stop_at_feasible -NT '$tb';
                exit
            "

        done
    done

    # Wait for all screen sessions for this station size to finish
    while screen -list | grep -q "${n_station}-"; do
        sleep 10 # Check every 10 seconds if the sessions are finished
    done
done
