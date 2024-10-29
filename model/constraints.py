from parameters.sets import S0, S, K, R, T, n_station
import gurobipy as gp
import parameters.dataloader as dataloader
from parameters.dataloader import dissat_file, has_repairer


def addInventoryConstraints(solver):
    # region constr (3) - (7)

    if has_repairer:
        # (3)
        solver.m.addConstrs(
            constrs=(
                solver.p[i, 1]
                == (
                    dataloader.station_inventory_usable[i]
                    - gp.quicksum(solver.yuminus[i, 1, k] for k in K)
                    + gp.quicksum(solver.yuplus[i, 1, k] for k in K)
                    + gp.quicksum(solver.g[i, 1, m] for m in R)
                )
                for i in S0
            )
        )

        # (4)
        solver.m.addConstrs(
            constrs=(
                solver.p[i, t]
                == (
                    solver.p[i, t - 1]
                    - gp.quicksum(solver.yuminus[i, t, k] for k in K)
                    + gp.quicksum(solver.yuplus[i, t, k] for k in K)
                    + gp.quicksum(solver.g[i, t, m] for m in R)
                )
                for i in S0
                for t in T[1:]
            )
        )

        # (5)
        solver.m.addConstrs(
            constrs=(
                solver.b[i, 1]
                == (
                    dataloader.station_inventory_broken[i]
                    - gp.quicksum(solver.ybminus[i, 1, k] for k in K)
                    + gp.quicksum(solver.ybplus[i, 1, k] for k in K)
                    - gp.quicksum(solver.g[i, 1, m] for m in R)
                )
                for i in S0
            )
        )

        # (6)
        solver.m.addConstrs(
            constrs=(
                solver.b[i, t]
                == (
                    solver.b[i, t - 1]
                    - gp.quicksum(solver.ybminus[i, t, k] for k in K)
                    + gp.quicksum(solver.ybplus[i, t, k] for k in K)
                    - gp.quicksum(solver.g[i, t, m] for m in R)
                )
                for i in S0
                for t in T[1:]
            )
        )
    else:
        # (3)
        solver.m.addConstrs(
            constrs=(
                solver.p[i, 1]
                == (
                    dataloader.station_inventory_usable[i]
                    - gp.quicksum(solver.yuminus[i, 1, k] for k in K)
                    + gp.quicksum(solver.yuplus[i, 1, k] for k in K)
                )
                for i in S0
            )
        )

        # (4)
        solver.m.addConstrs(
            constrs=(
                solver.p[i, t]
                == (
                    solver.p[i, t - 1]
                    - gp.quicksum(solver.yuminus[i, t, k] for k in K)
                    + gp.quicksum(solver.yuplus[i, t, k] for k in K)
                )
                for i in S0
                for t in T[1:]
            )
        )

        # (5)
        solver.m.addConstrs(
            constrs=(
                solver.b[i, 1]
                == (
                    dataloader.station_inventory_broken[i]
                    - gp.quicksum(solver.ybminus[i, 1, k] for k in K)
                    + gp.quicksum(solver.ybplus[i, 1, k] for k in K)
                )
                for i in S0
            )
        )

        # (6)
        solver.m.addConstrs(
            constrs=(
                solver.b[i, t]
                == (
                    solver.b[i, t - 1]
                    - gp.quicksum(solver.ybminus[i, t, k] for k in K)
                    + gp.quicksum(solver.ybplus[i, t, k] for k in K)
                )
                for i in S0
                for t in T[1:]
            )
        )

    # (7)
    solver.m.addConstrs(
        constrs=(
            solver.p[i, t] + solver.b[i, t] <= dataloader.station_capacity[i]
            for i in S
            for t in T
        )
    )
    # endregion

    # region constr (8) - (15)
    # (8)
    solver.m.addConstrs(
        constrs=(
            gp.quicksum(solver.psiu[0, j, 1, k] for j in S0)
            == solver.yuminus[0, 1, k] - solver.yuplus[0, 1, k]
            for k in K
        )
    )

    # (9)
    solver.m.addConstrs(
        constrs=(
            gp.quicksum(solver.psiu[i, j, t, k] for j in S0)
            == gp.quicksum(
                solver.psiu[j, i, t - dataloader.trip_time_interval[j, i], k]
                for j in S0
                if t > dataloader.trip_time_interval[j, i]
            )
            - solver.yuplus[i, t, k]
            + solver.yuminus[i, t, k]
            for i in S0
            for t in T[1:]
            for k in K
        )
    )

    # # (10)
    solver.m.addConstrs(
        constrs=(
            solver.psiu[i, j, dataloader.end_period, k] == 0
            for i in S0
            for j in S0
            for k in K
        )
    )

    # (11)
    solver.m.addConstrs(
        constrs=(
            solver.psiu[i, j, t, k]
            <= dataloader.truck_capacity[k] * solver.xt[i, j, t, k]
            for i in S0
            for j in S0
            for t in T
            for k in K
        )
    )

    # (12)
    solver.m.addConstrs(
        constrs=(solver.psib[i, j, 1, k] == 0 for i in S0 for j in S0 for k in K)
    )

    # (13)
    solver.m.addConstrs(
        constrs=(
            gp.quicksum(solver.psib[i, j, t, k] for j in S0)
            == gp.quicksum(
                solver.psib[j, i, t - dataloader.trip_time_interval[j, i], k]
                for j in S0
                if t > dataloader.trip_time_interval[j, i]
            )
            - solver.ybplus[i, t, k]
            + solver.ybminus[i, t, k]
            for i in S0
            for t in T[1:]
            for k in K
        )
    )

    # (14)
    solver.m.addConstrs(
        constrs=(
            solver.psib[i, j, dataloader.end_period, k] == 0
            for i in S0
            for j in S0
            for k in K
        )
    )

    # (15)
    solver.m.addConstrs(
        constrs=(
            solver.psib[i, j, t, k]
            <= dataloader.truck_capacity[k] * solver.xt[i, j, t, k]
            for i in S0
            for j in S0
            for t in T
            for k in K
        )
    )

    # (16)
    solver.m.addConstrs(
        constrs=(
            solver.psiu[i, j, t, k] + solver.psib[i, j, t, k]
            <= dataloader.truck_capacity[k]
            for i in S0
            for j in S0
            for t in T
            for k in K
        )
    )
    # endregion


def addLoadingQuantityConstraints(solver):
    # region constr (17) - (25)
    # (17)
    solver.m.addConstrs(
        constrs=(
            solver.yuplus[i, t, k]
            <= gp.quicksum(solver.xt[i, j, t, k] for j in S0)
            * min(dataloader.station_capacity[i], dataloader.truck_capacity[k])
            for i in S0
            for t in T
            for k in K
        )
    )
    # np.floor(data.time_interval/data.t_load).astype(int)

    # (18)
    solver.m.addConstrs(
        constrs=(
            solver.yuminus[i, t, k]
            <= gp.quicksum(solver.xt[i, j, t, k] for j in S0)
            * min(dataloader.station_capacity[i], dataloader.truck_capacity[k])
            for i in S
            for t in T
            for k in K
        )
    )

    solver.m.addConstrs(
        constrs=(
            gp.quicksum(solver.yuminus[i, t, k] for t in T for k in K)
            <= max(
                dataloader.station_inventory_usable[i] - dataloader.station_target[i], 0
            )
            for i in S
        )
    )

    # np.floor(data.time_interval/data.t_load).astype(int)

    # (19)
    solver.m.addConstrs(
        solver.ybplus[0, t, k]
        <= gp.quicksum(solver.xt[0, j, t, k] for j in S0) * dataloader.truck_capacity[k]
        for t in T
        for k in K
    )
    # np.floor(data.time_interval/data.t_load).astype(int)

    # (20)
    solver.m.addConstrs(solver.ybplus[i, t, k] == 0 for i in S for t in T for k in K)

    # (21)
    solver.m.addConstrs(constrs=(solver.ybminus[0, t, k] == 0 for t in T for k in K))

    # (22)
    solver.m.addConstrs(
        constrs=(
            solver.ybminus[i, t, k]
            <= gp.quicksum(solver.xt[i, j, t, k] for j in S0)
            * min(dataloader.station_inventory_broken[i], dataloader.truck_capacity[k])
            for i in S
            for t in T
            for k in K
        )
    )

    if has_repairer:
        # (23)
        solver.m.addConstrs(solver.g[0, t, m] == 0 for t in T for m in R)

        # (24)
        solver.m.addConstrs(
            constrs=(
                solver.g[i, t, m]
                <= gp.quicksum(solver.xr[i, j, t, m] for j in S0)
                * dataloader.station_inventory_broken[i]
                for i in S
                for t in T
                for m in R
            )
        )

    if has_repairer:
        # (25)
        solver.m.addConstrs(
            constrs=(
                gp.quicksum(solver.ybminus[i, t, k] for t in T for k in K)
                + gp.quicksum(solver.g[i, t, m] for t in T for m in R)
                <= dataloader.station_inventory_broken[i]
                for i in S
            )
        )
    else:
        # (25)
        solver.m.addConstrs(
            constrs=(
                gp.quicksum(solver.ybminus[i, t, k] for t in T for k in K)
                <= dataloader.station_inventory_broken[i]
                for i in S
            )
        )
    # endregion


def addRouteConstraints(solver):
    # region constr (26) - (31), (36) - (38)
    # (26)
    solver.m.addConstrs(
        constrs=(gp.quicksum(solver.xt[0, j, 1, k] for j in S0) == 1 for k in K)
    )
    if has_repairer:
        # (27)
        solver.m.addConstrs(
            constrs=(gp.quicksum(solver.xr[0, j, 1, m] for j in S) == 1 for m in R)
        )

    # (28)
    solver.m.addConstrs(
        constrs=(
            gp.quicksum(
                solver.xt[
                    i, 0, dataloader.end_period - dataloader.trip_time_interval[i, 0], k
                ]
                for i in S0
                if dataloader.end_period > dataloader.trip_time_interval[i, 0]
            )
            == 1
            for k in K
        )
    )
    if has_repairer:
        # (29)
        solver.m.addConstrs(
            constrs=(
                gp.quicksum(
                    solver.xr[
                        i,
                        0,
                        dataloader.end_period - dataloader.trip_time_man_interval[i, 0],
                        m,
                    ]
                    for i in S0
                    if dataloader.end_period > dataloader.trip_time_man_interval[i, 0]
                )
                == 1
                for m in R
            )
        )

    # (30)
    solver.m.addConstrs(
        constrs=(
            (
                gp.quicksum(
                    solver.xt[j, i, t - dataloader.trip_time_interval[j, i], k]
                    for j in S0
                    if t - dataloader.trip_time_interval[j, i] > 0
                )
                == gp.quicksum(solver.xt[i, u, t, k] for u in S0)
                for i in S0
                for t in T[1:]
                for k in K
            )
        )
    )

    if has_repairer:
        # (31)
        solver.m.addConstrs(
            constrs=(
                (
                    gp.quicksum(
                        solver.xr[j, i, t - dataloader.trip_time_man_interval[j, i], m]
                        for j in S0
                        if t - dataloader.trip_time_man_interval[j, i] > 0
                    )
                    == gp.quicksum(solver.xr[i, u, t, m] for u in S0)
                    for i in S0
                    for t in T[1:]
                    for m in R
                )
            )
        )
    # endregion


def addTimeConstraints(solver):
    # region const(32) - (35)
    # (32)
    solver.m.addConstrs(
        constrs=(
            solver.aux_stop[t, k]
            >= (t - solver.stop_time[k] + 1) / dataloader.end_period
            for t in T
            for k in K
        )
    )

    # (33)
    solver.m.addConstrs(
        constrs=(
            solver.aux_stop[t, k]
            <= (t - solver.stop_time[k] + 0.5) / dataloader.end_period + 1
            for t in T
            for k in K
        )
    )
    if has_repairer:
        # (34)
        solver.m.addConstrs(
            constrs=(
                solver.aux_stop_rpm[t, m]
                >= (t - solver.stop_time_rpm[m] + 1) / dataloader.end_period
                for t in T
                for m in R
            )
        )

        # (35)
        solver.m.addConstrs(
            constrs=(
                solver.aux_stop_rpm[t, m]
                <= (t - solver.stop_time_rpm[m] + 0.5) / dataloader.end_period + 1
                for t in T
                for m in R
            )
        )

    # upper bound truck
    solver.m.addConstrs(
        constrs=(
            solver.upper_bound[w, k]
            == gp.quicksum(
                dataloader.trip_time[i, j]
                * solver.xt[i, j, t - dataloader.trip_time_interval[i, j], k]
                # data.trip_time[i, j] * solver.xt[i, j, t, k]
                for i in S0
                for j in S0
                for t in [i for i in range(1, w + 1)]
                if t - dataloader.trip_time_interval[i, j] > 0
            )
            + gp.quicksum(
                dataloader.t_load
                * (
                    solver.yuplus[i, t, k]
                    + solver.yuminus[i, t, k]
                    + solver.ybplus[i, t, k]
                    + solver.ybminus[i, t, k]
                )
                for i in S0
                for t in [i for i in range(1, w + 1)]
            )
            for w in T
            for k in K
        )
    )

    # lower bound truck
    solver.m.addConstrs(
        constrs=(
            solver.lower_bound[w, k]
            == gp.quicksum(
                dataloader.trip_time[i, j] * solver.xt[i, j, t, k]
                for i in S0
                for j in S0
                for t in [i for i in range(1, w + 1)]
            )
            + gp.quicksum(
                dataloader.t_load
                * (
                    solver.yuplus[i, t, k]
                    + solver.yuminus[i, t, k]
                    + solver.ybplus[i, t, k]
                    + solver.ybminus[i, t, k]
                )
                for i in S0
                for t in [i for i in range(1, w + 1)]
            )
            for w in T
            for k in K
        )
    )
    if has_repairer:
        # upper bound repairer
        solver.m.addConstrs(
            constrs=(
                solver.upper_bound_man[w, m]
                == gp.quicksum(
                    dataloader.trip_time_man[i, j]
                    * solver.xr[i, j, t - dataloader.trip_time_man_interval[i, j], m]
                    for i in S0
                    for j in S0
                    for t in [i for i in range(1, w + 1)]
                    if t - dataloader.trip_time_man_interval[i, j] > 0
                )
                + gp.quicksum(
                    dataloader.t_repair * solver.g[i, t, m]
                    for i in S0
                    for t in [i for i in range(1, w + 1)]
                )
                for w in T
                for m in R
            )
        )

        # lower bound repairer
        solver.m.addConstrs(
            constrs=(
                solver.lower_bound_man[w, m]
                == gp.quicksum(
                    dataloader.trip_time_man[i, j] * solver.xr[i, j, t, m]
                    for i in S0
                    for j in S0
                    for t in [i for i in range(1, w + 1)]
                )
                + gp.quicksum(
                    dataloader.t_repair * solver.g[i, t, m]
                    for i in S0
                    for t in [i for i in range(1, w + 1)]
                )
                for w in T
                for m in R
            )
        )

    # region constr (36) - (39)
    # (36)
    solver.m.addConstrs(
        constrs=(
            solver.upper_bound[w, k] <= w * dataloader.time_interval
            for w in T
            for k in K
        )
    )

    # (37)
    solver.m.addConstrs(
        solver.lower_bound[w, k]
        >= (w - 2) * dataloader.time_interval
        - dataloader.end_period * dataloader.time_interval * solver.aux_stop[w, k]
        for w in T
        for k in K
    )
    if has_repairer:
        # (38)
        solver.m.addConstrs(
            constrs=(
                solver.upper_bound_man[w, m] <= w * dataloader.time_interval
                for w in T
                for m in R
            )
        )

        # (39)
        solver.m.addConstrs(
            constrs=(
                solver.lower_bound_man[w, k]
                >= (w - 2) * dataloader.time_interval
                - dataloader.end_period
                * dataloader.time_interval
                * solver.aux_stop_rpm[w, k]
                for w in T
                for k in R
            )
        )
    # endregion
    # endregion

    # (40)
    solver.m.addConstrs(
        constrs=(
            solver.xt[0, 0, t, k]
            <= 1 - (solver.aux_stop[t + 1, k] - solver.aux_stop[t, k])
            for t in T
            for k in K
            if t < dataloader.end_period
        )
    )
    if has_repairer:
        # (41)
        solver.m.addConstrs(
            constrs=(
                solver.xr[0, 0, t, m]
                <= 1 - (solver.aux_stop_rpm[t + 1, m] - solver.aux_stop_rpm[t, m])
                for t in T
                for m in R
                if t < dataloader.end_period
            )
        )

    # (42)
    solver.m.addConstrs(
        solver.xt[i, i, t, k]
        <= solver.yuplus[i, t, k]
        + solver.yuminus[i, t, k]
        + solver.ybplus[i, t, k]
        + solver.ybminus[i, t, k]
        + 100 * solver.aux_stop[t, k]
        for i in S
        for t in T
        for k in K
    )
    if has_repairer:
        # (43)
        solver.m.addConstrs(
            solver.xr[i, i, t, m] <= solver.g[i, t, m] + 100 * solver.aux_stop_rpm[t, m]
            for i in S
            for t in T
            for m in R
        )

    solver.m.addConstrs(
        constrs=(solver.xt[0, 0, t, k] >= solver.aux_stop[t, k] for t in T for k in K)
    )
    if has_repairer:
        solver.m.addConstrs(
            constrs=(
                solver.xr[0, 0, t, m] >= solver.aux_stop_rpm[t, m] for t in T for m in R
            )
        )


def addAuxiliaryConstraints(solver):
    # (44)
    solver.m.addConstrs(
        constrs=(
            gp.quicksum(solver.xt[i, j, t, k] for i in S0 for j in S0) <= 1
            for t in T
            for k in K
        )
    )
    if has_repairer:
        # (45)
        solver.m.addConstrs(
            constrs=(
                gp.quicksum(solver.xr[i, j, t, m] for i in S0 for j in S0) <= 1
                for t in T
                for m in R
            )
        )

        # (46)
        solver.m.addConstrs(
            constrs=(
                gp.quicksum(
                    solver.xr[j, i, t - dataloader.trip_time_man_interval[j, i], m]
                    for j in S0
                    if i != j
                    for t in T
                    if t > dataloader.trip_time_man_interval[j, i]
                    for m in R
                )
                <= 1
                for i in S
            )
        )

    # (47) emission
    solver.m.addConstrs(
        constrs=(
            solver.e[i, j, t, k]
            == 2.61
            * (
                0.252 * solver.xt[i, j, t, k]
                + 0.0003 * (solver.psib[i, j, t, k] + solver.psiu[i, j, t, k])
            )
            * dataloader.trip_time[i, j]
            / 3600
            * 25.2
            for i in S0
            for j in S0
            for t in T
            for k in K
        )
    )

    solver.m.addConstrs(
        constrs=(
            solver.operating_time_truck[k]
            == gp.quicksum(
                (
                    solver.yuplus[i, t, k]
                    + solver.yuminus[i, t, k]
                    + solver.ybplus[i, t, k]
                    + solver.ybminus[i, t, k]
                )
                * dataloader.t_load
                for i in S0
                for t in T
            )
            for k in K
        )
    )
    if has_repairer:
        solver.m.addConstrs(
            constrs=(
                solver.operating_time_repairer[m]
                == gp.quicksum(
                    (solver.g[i, t, m]) * dataloader.t_repair for i in S0 for t in T
                )
                for m in R
            )
        )

    # region: for each station, the dissatisfaction is <= alpha * p + beta * b + gamma
    # where alpha, beta and gamma are read from the file "diss_linear_i.txt" with i stands for the station id

    for i in S:
        with open(dissat_file[i - 1], "r") as f:
            for line in f.readlines():
                alpha, beta, gamma = (
                    line.split(",")[2],
                    line.split(",")[3],
                    line.split(",")[4],
                )
                solver.m.addConstr(
                    solver.F[i]
                    >= float(alpha) * solver.p[i, dataloader.n_intervals]
                    + float(beta) * solver.b[i, dataloader.n_intervals]
                    + float(gamma)
                )
    # endregion
