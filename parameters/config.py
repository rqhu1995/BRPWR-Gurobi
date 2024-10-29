# use argparse to set values for n_station, n_truck, n_repairer, n_intervals, end_period

import argparse
import os

formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=80)

parser = argparse.ArgumentParser(
    formatter_class=formatter,
    description="Set values for basic parameters of the experiment",
)
parser.add_argument("-S", "--n_station", type=int, default=6, help="number of stations")
parser.add_argument("-K", "--n_truck", type=int, default=1, help="number of trucks")
parser.add_argument(
    "-R", "--n_repairer", type=int, default=1, help="number of repairers"
)
parser.add_argument(
    "-NT", "--n_intervals", type=int, default=12, help="number of intervals"
)
parser.add_argument(
    "-tau", "--time_interval", type=int, default=600, help="time interval"
)
parser.add_argument(
    "-Q", "--truck_capacity", type=int, default=25, help="truck capacity"
)
parser.add_argument("-tl", "--t_load", type=int, default=60, help="time to load a bike")
parser.add_argument(
    "-tr", "--t_repair", type=int, default=300, help="time to repair a bike"
)
parser.add_argument(
    "-r",
    "--has_repairer",
    type=lambda x: x == "True",
    default=True,
    help="whether to include repairers",
    choices=[True, False],
)

parser.add_argument("-i", "--inst_no", type=int, default=1, help="instance number")

parser.add_argument(
    "-e",
    "--exp_label",
    type=str,
    default="default",
    help="experiment label",
    choices=["default", "repair_time"],
)
parser.add_argument(
    "-t",
    "--num_threads",
    type=int,
    default=4,
    help=f"number of threads used, based on your CPU, you may use up to {os.cpu_count()} threads",
)

parser.add_argument(
    "-heu",
    "--heuristics",
    type=float,
    default=0.00,
    help="the time percentage that Gurobi spends on heuristics",
)

parser.add_argument(
    "-m",
    "--mode",
    type=str,
    default="time_limit",
    choices=["exhaustive", "time_limit"],
    help="the running mode of the optimization. Exhaustive mode will run until the optimal solution is found, \
        while time_limit mode will stop at the time limit and report the best solution found",
)

args = parser.parse_args()
