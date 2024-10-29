#!/bin/bash
cd ..

# Assign the first argument passed to the script to the variable tb
tb=$1
max_parallel_jobs=4

for n_station in 60 90 120 200 300 400 500; do

    # Run all combinations of n_trk and n_rpm for the current station size
    for n_trk in 1 2; do
        for n_rpm in 1 2; do
            # Calculate the session name
            session_name="${n_station}-${n_trk}-${n_rpm}_$((tb * 600 / 3600))h"

            # Start a new screen session and run the commands
            screen -dmS "$session_name" bash -c "
                conda activate gurobi311;
                python main.py -S '$n_station' -K '$n_trk' -R '$n_rpm' -i 1 -m time_limit -NT '$tb';
                exit
            "

        done
    done

    # Wait for all screen sessions for this station size to finish
    while [ "$(screen -ls | grep -c $n_station)" -ge "$max_parallel_jobs" ]; do
        echo "currently running $max_parallel_jobs jobs for $n_station stations"
        sleep 1800 # Check every 1800 seconds (half an hour) if the sessions are finished
    done
done
