from collections import namedtuple
from parameters.dataloader import (
    n_intervals,
    n_repairer,
    n_station,
    n_truck,
    end_period,
)

# sets and indices
S = [i for i in range(1, n_station + 1)]  # station set without the depot
S0 = [i for i in range(n_station + 1)]  # station set with the depot
K = [i for i in range(n_truck)]  # truck set
R = [i for i in range(n_repairer)]  # repairman set
T = [i for i in range(1, n_intervals + 1)]  # time period set

ijtk = [
    (i, j, t, k) for i in S0 for j in S0 for t in T for k in K
]  # arc time truck set
ijtm = [
    (i, j, t, m) for i in S0 for j in S0 for t in T for m in R
]  # arc time repairman set
itk = [(i, t, k) for i in S0 for t in T for k in K]  # station time truck set
itm = [(i, t, m) for i in S0 for t in T for m in R]  # station time repairman set
ik = [(i, k) for i in S0 for k in K]  # station truck set
im = [(i, m) for i in S0 for m in R]  # station repairman set
it = [(i, t) for i in S0 for t in T]  # station time set
wk = [(w, k) for w in range(1, end_period + 1) for k in K]  # period truck set
wm = [(w, m) for w in range(1, end_period + 1) for m in R]  # period repairman set

# export as a dictionary
Index = namedtuple(
    "Index",
    [
        "arc_t_truck",
        "arc_t_rpm",
        "node_t_truck",
        "node_t_rpm",
        "node_truck",
        "node_rpm",
        "node_t",
        "period_truck",
        "period_rpm",
    ],
)

indices = Index(ijtk, ijtm, itk, itm, ik, im, it, wk, wm)
