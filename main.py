from model.model import Solver
from parameters.dataloader import (
    inst_no,
    n_station,
    ratio_broken,
    has_repairer,
    n_truck,
    n_repairer,
    n_intervals,
    time_interval,
)
from utils.utils import parse_sol_file

if __name__ == "__main__":
    brpwr_model = Solver()
    brpwr_model.addVars()
    brpwr_model.addConstrs()
    brpwr_model.setObj()
    brpwr_model.optimize()
    model_type = "wr" if has_repairer else "nr"
    time_budget = int(n_intervals * time_interval / 3600)
    brpwr_model.save_result(
        f"{n_station}_{inst_no}_{ratio_broken}_{model_type}_t{n_truck}_r{n_repairer}_T{time_budget}"
    )
    parse_sol_file(brpwr_model.sol_path)
