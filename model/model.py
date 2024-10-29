from pathlib import Path
import platform
import time
import gurobipy as gp
from gurobipy import GRB
from .callback import soft_stop
from parameters.dataloader import (
    has_repairer,
    ratio_broken,
    t_repair,
    is_prop,
    n_intervals,
    mode,
    n_threads,
    heuristics,
    exp_label,
    n_repairer,
    n_truck,
    log_on,
)
from .variables import (
    addAuxiliaryVars,
    addInventoryVars,
    addLoadingQuantityVars,
    addObjVars,
    addRouteVars,
)
from .constraints import *
from .objective import addObjective


class Solver:

    def __init__(self):
        self.m = gp.Model()
        self.start_time = 0

    def addVars(self):
        addRouteVars(self)
        addInventoryVars(self)
        addAuxiliaryVars(self)
        addLoadingQuantityVars(self)
        addObjVars(self)

    def addConstrs(self):
        addRouteConstraints(self)
        addLoadingQuantityConstraints(self)
        addInventoryConstraints(self)
        addTimeConstraints(self)
        addAuxiliaryConstraints(self)

    def setObj(self):
        addObjective(self)

    def setMIPStart(self):
        # Set initial values for xr and xt to zero for MIP start
        for i in S0:
            for j in S:
                for t in T:
                    if j != 1:
                        self.xr[i, j, t, 0].start = 0  # type: ignore
                    if n_repairer > 1 and j != 2:
                        self.xr[i, j, t, 1].start = 0  # type: ignore

        for i in S0:
            for j in S:
                for t in T:
                    for k in K:
                        self.xt[i, j, t, k].start = 0  # type: ignore

    def optimize(self):
        self.m.setParam("Threads", n_threads)
        self.m.setParam("MIPGap", 1e-5)
        self.m.setParam("Heuristics", heuristics)
        self.m.setParam("SolutionLimit", 1e9)
        if log_on:
            self.m.setParam(
                "LogFile",
                f"resources/logs/{n_station}_t{n_truck}_r{n_repairer}_T{600*n_intervals/3600}.log",
            )
        self.setMIPStart()
        self.m._start_time = time.time()
        if mode == "stop_at_feasible":
            self.m.optimize(callback=soft_stop)
        else:
            self.m.optimize()
        # record the solution time
        self.sol_time = self.m.Runtime
        # record the objective value
        self.obj = self.m.objVal
        # record the solution status
        self.sol_status = self.m.status
        self.lb = self.m.ObjBound
        # record the solution
        self.sol = {}

    def save_result(self, dfname=None):
        current_time = time.strftime("%H:%M:%S").replace(":", "_")
        datafilename = dfname
        # check the system type
        if platform.system().lower() == "windows":
            sep = "\\"
        else:
            sep = "/"

        time_dir = f"resources{sep}solutions{sep}{time.strftime('%Y-%m-%d')}{sep}{datafilename}"
        Path(time_dir).mkdir(parents=True, exist_ok=True)
        if not is_prop:
            self.sol_path = f"{time_dir}{sep}{datafilename}_{current_time}.sol"
        else:
            self.sol_path = (
                f"{time_dir}{sep}{datafilename}_{current_time}_r{ratio_broken}.sol"
            )
        if exp_label == "repair_time":
            self.sol_path = f"{time_dir}{sep}{datafilename}_rt{t_repair}.sol"
        if self.m.SolCount > 0:
            self.m.write(self.sol_path)
        # save the solution time, objective value and solution status
        with open(f"{time_dir}{sep}summary.txt", "a+") as f:
            model_type = "wr" if has_repairer else "nr"
            f.write(f"======{current_time},{model_type},{datafilename}======\n")
            f.write(f"Solution time: {self.sol_time}\n")
            if self.obj not in [None, ""]:
                f.write(f"Objective value: {self.obj}\n")
            f.write(f"Lower bound: {self.lb}\n")
            f.write(f"running using {n_threads} threads, under {mode} mode\n")
            f.write(f"Solution status: {self.sol_status}\n")
