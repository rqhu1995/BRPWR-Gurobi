import gurobipy as gp
from parameters.sets import S0, S, K, T, R
from parameters.dataloader import trip_time, trip_time_man, has_repairer


def addObjective(solver):
    if has_repairer:
        solver.m.setObjective(
            2 * gp.quicksum(solver.F[i] for i in S)
            + 0.06
            * gp.quicksum(
                solver.e[i, j, t, k] for i in S0 for j in S0 for t in T for k in K
            )
            + 0.00000001
            * (
                gp.quicksum(solver.operating_time_truck[k] for k in K)
                + gp.quicksum(solver.operating_time_repairer[m] for m in R)
                + gp.quicksum(
                    solver.xr[i, j, t, m] * trip_time_man[i, j]
                    for i in S0
                    for j in S0
                    for t in T
                    for m in R
                )
                + gp.quicksum(
                    solver.xt[i, j, t, k] * trip_time[i, j]
                    for i in S0
                    for j in S0
                    for t in T
                    for k in K
                )
            ),
            gp.GRB.MINIMIZE,
        )
    else:
        solver.m.setObjective(
            2 * gp.quicksum(solver.F[i] for i in S)
            + 0.06
            * gp.quicksum(
                solver.e[i, j, t, k] for i in S0 for j in S0 for t in T for k in K
            )
            + 0.00000001
            * (
                gp.quicksum(solver.operating_time_truck[k] for k in K)
                + gp.quicksum(
                    solver.xt[i, j, t, k] * trip_time[i, j]
                    for i in S0
                    for j in S0
                    for t in T
                    for k in K
                )
            ),
            gp.GRB.MINIMIZE,
        )
