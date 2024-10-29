from parameters.sets import indices, S, K, T, R
from parameters.dataloader import has_repairer
from gurobipy import GRB


def addRouteVars(solver):
    solver.xt = solver.m.addVars(
        indices.arc_t_truck, vtype=GRB.BINARY, name="visit_truck"
    )
    if has_repairer:
        solver.xr = solver.m.addVars(
            indices.arc_t_rpm, vtype=GRB.BINARY, name="visit_man"
        )


def addInventoryVars(solver):
    solver.p = solver.m.addVars(
        indices.node_t, vtype=GRB.CONTINUOUS, lb=0, name="station_inv_usable"
    )
    solver.b = solver.m.addVars(
        indices.node_t, vtype=GRB.CONTINUOUS, lb=0, name="station_inv_broken"
    )
    solver.psiu = solver.m.addVars(
        indices.arc_t_truck, vtype=GRB.CONTINUOUS, name="prev_truck_inv_usable"
    )
    solver.psib = solver.m.addVars(
        indices.arc_t_truck, vtype=GRB.CONTINUOUS, name="prev_truck_inv_broken"
    )


def addLoadingQuantityVars(solver):
    solver.yuplus = solver.m.addVars(
        indices.node_t_truck, vtype=GRB.INTEGER, name="reb_amount_usable+"
    )
    solver.yuminus = solver.m.addVars(
        indices.node_t_truck, vtype=GRB.INTEGER, name="reb_amount_usable-"
    )
    solver.ybplus = solver.m.addVars(
        indices.node_t_truck, vtype=GRB.INTEGER, name="reb_amount_broken+"
    )
    solver.ybminus = solver.m.addVars(
        indices.node_t_truck, vtype=GRB.INTEGER, name="reb_amount_broken-"
    )
    if has_repairer:
        solver.g = solver.m.addVars(
            indices.node_t_rpm, vtype=GRB.INTEGER, name="repaired_amount_man"
        )


def addAuxiliaryVars(solver):
    solver.upper_bound = solver.m.addVars(
        indices.period_truck, vtype=GRB.CONTINUOUS, name="upper_bound"
    )
    solver.lower_bound = solver.m.addVars(
        indices.period_truck, vtype=GRB.CONTINUOUS, name="lower_bound"
    )
    if has_repairer:
        solver.upper_bound_man = solver.m.addVars(
            indices.period_rpm, vtype=GRB.CONTINUOUS, name="upper_bound_man"
        )
        solver.lower_bound_man = solver.m.addVars(
            indices.period_rpm, vtype=GRB.CONTINUOUS, name="lower_bound_man"
        )
    solver.stop_time = solver.m.addVars(K, vtype=GRB.INTEGER, name="stop_time")
    solver.aux_stop = solver.m.addVars(T, K, vtype=GRB.BINARY, name="aux_stop")
    if has_repairer:
        solver.stop_time_rpm = solver.m.addVars(
            R, vtype=GRB.INTEGER, name="stop_time_rpm"
        )
        solver.aux_stop_rpm = solver.m.addVars(
            T, R, vtype=GRB.BINARY, name="aux_stop_rpm"
        )
        solver.operating_time_repairer = solver.m.addVars(
            R, vtype=GRB.CONTINUOUS, name="operating_time_rpm"
        )
    solver.operating_time_truck = solver.m.addVars(
        K, vtype=GRB.CONTINUOUS, name="operating_time_truck"
    )


def addObjVars(solver):
    solver.e = solver.m.addVars(
        indices.arc_t_truck, vtype=GRB.CONTINUOUS, name="emission"
    )
    solver.F = solver.m.addVars(S, vtype=GRB.CONTINUOUS, name="dissat")
