# use argparse to set values for n_station, n_truck, n_repairman, n_intervals, end_period

import argparse
import os


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=80)


parser = argparse.ArgumentParser(
    formatter_class=CustomFormatter,
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
parser.add_argument(
    "-p",
    "--is_prop",
    type=lambda x: x == "True",
    default=False,
    help="the broken bike inventories is set proportionally to the deviation from the target usable bike inventory",
    choices=[True, False],
)
parser.add_argument(
    "-rb",
    "--ratio_broken",
    type=float,
    default=0.5,
    help="the proportion set for the number of broken bikes",
)
parser.add_argument("-i", "--inst_no", type=int, default=1, help="instance number")
parser.add_argument(
    "-e",
    "--exp_label",
    type=str,
    default="default",
    help="experiment label",
    choices=["default", "bb_prop", "repair_time"],
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
    "-l",
    "--log_on",
    type=lambda x: x == "True",
    default=True,
    help="whether to log the optimization process",
    choices=[True, False],
)

parser.add_argument(
    "-m",
    "--mode",
    type=str,
    default="optimal",
    choices=["optimal", "stop_at_feasible"],
    help="the running mode of the optimization. Optimal mode will run until the optimal solution is found, \
        while stop_at_feasible will try to find the optimal at the first two hours, then continue running \
        and stop at the first feasible solution found.",
)

args = parser.parse_args()
