from gurobipy import GRB
import time


def soft_stop(model, where):
    # read from the heuristic solutions, if the current best solution is better than the one from the heuristic, stop the optimization
    if where == GRB.Callback.MIP or where == GRB.Callback.PRESOLVE:
        runtime = time.time() - model._start_time
        try:
            best_int = model.cbGet(GRB.Callback.MIP_OBJBST)
            best_bound = model.cbGet(GRB.Callback.MIP_OBJBND)
        except:
            best_int = None
            best_bound = None

        # record the best integer solution every day (86400 seconds), write it to the log file
        if (
            runtime >= 7200
            and best_int is not None
            and best_bound is not None
        ):
            mip_gap = (best_int - best_bound) / best_int * 100
            # round the mip gap to 2 decimal places
            mip_gap = round(mip_gap, 2)
            # create if the model._log_file does not exist
            with open(model._log_file, "a") as f:
                # format of the log file: current time yyyy-mm-dd HH:MM:SS, runtime, best integer solution, Lower bound, mip gap, separated by tab
                f.write(
                    f"{time.strftime('%Y-%m-%d %H:%M:%S')}\t{runtime}\t{best_int}\t{best_bound}\t{mip_gap}%\n"
                )
        # terminate the optimization process if run time is over a week
        if runtime >= 604800:
            model.terminate()
