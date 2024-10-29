from .config import parser
import pandas as pd
import numpy as np

args = parser.parse_args()

# set the random seed to be the same as the instance number
np.random.seed(args.inst_no)

n_station = args.n_station
n_truck = args.n_truck
n_repairer = args.n_repairer
n_intervals = args.n_intervals
single_truck_capacity = args.truck_capacity
time_interval = args.time_interval
t_load = args.t_load
t_repair = args.t_repair
inst_no = args.inst_no
end_period = n_intervals
has_repairer = args.has_repairer
heuristics = args.heuristics
mode = args.mode
exp_label = args.exp_label
n_threads = args.num_threads

data_file = f"resources/datasets/{n_station}_{inst_no}/station_info_{n_station}.txt"
time_matrix_file = (
    f"resources/datasets/{n_station}_{inst_no}/time_matrix_{n_station}.txt"
)
dissat_file = [
    f"resources/datasets/{n_station}_{inst_no}/linear_diss_{i}.txt"
    for i in range(1, n_station + 1)
]

station_info = pd.read_csv(data_file, sep="\t", header=0)
time_matrix = pd.read_csv(time_matrix_file, sep="\t", header=None).to_numpy()

station_capacity = [10000] + station_info.iloc[:, 1].to_list()
station_inventory_usable = [10000] + list(station_info.iloc[:, 2].values)

station_target = [0] + list(station_info.loc[:, "targetUsable"].values)
truck_capacity = [single_truck_capacity] * n_truck

station_inventory_broken = [0] + list(station_info.loc[:, "curBroken"].values)

trip_time = time_matrix
trip_time_man = np.ceil(trip_time * 1.68)
trip_time_interval = np.ceil(trip_time / time_interval).astype(int)
trip_time_interval[trip_time_interval == 0] = 1
trip_time_man_interval = np.ceil(trip_time_man / time_interval).astype(int)
trip_time_man_interval[trip_time_man_interval == 0] = 1
