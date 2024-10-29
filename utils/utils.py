import json
from typing import Union, List, Dict, Tuple
from parameters.dataloader import n_truck, end_period, n_station, n_repairer, inst_no
import numpy as np
from gurobipy import GRB, Model as gp
import time


def parse_sol_file(filename):
    basepath = "/".join(filename.split("/")[:-1])
    with open(f"{basepath}/summary.txt", "r") as f:
        lines = f.readlines()
        # starting from the last line, find the line with "Solution time: "
        for line in reversed(lines):
            if "Solution time: " in line:
                break
        cpu_time = float(
            line.replace("Solution time: ", "").replace("\n", "").replace('"', "")
        )

    with open(filename, "r") as file:
        lines = file.readlines()

    objective_value = float(lines[0].split("=")[1])

    truck_visits = [[] for _ in range(n_truck)]
    repairman_visits = [[] for _ in range(n_repairer)]

    truck_visits, repairman_visits = routing_extract(
        lines, truck_visits, repairman_visits
    )

    operation_extract(lines, truck_visits, repairman_visits)
    truck_visits, repairman_visits = amendment(truck_visits, repairman_visits)

    dissat = dissat_extract(lines)

    emission = emission_extract(lines)

    # average_load, travel_dist, broken_carried = load_and_distance(truck_visits)

    # no_of_stations = no_of_stations_visited(truck_visits)

    data = {
        "objective_value": objective_value,
        "truck_visits": truck_visits,
        "repairman_visits": repairman_visits,
        "dissat": dissat,
        "emission": emission,
        "cpu_time": cpu_time,
    }
    #

    # # dump the data to a json file
    with open(f'{str(filename).replace(".sol", "")}.json', "w") as file:
        json.dump(data, file, indent=2)


#  truck_visits = [[{"x":y, "z": k, ...}, {"x":y, "z": k, ...}, ...],[{"x":y, "z": k, ...}, {"x":y, "z": k, ...}, ...],...,[{"x":y, "z": k, ...}, {"x":y, "z": k, ...}, ...]]
def amendment(
    truck_visits: List[List[Dict[str, Union[int, Tuple[int, int, int]]]]],
    repairman_visits: List[List[Dict[str, Union[int, Tuple[int, int, int]]]]],
):
    operation_types = [
        "reb_amount_usable+",
        "reb_amount_usable-",
        "reb_amount_broken+",
        "reb_amount_broken-",
    ]
    new_truck_visits = [[] for _ in range(n_truck)]

    for k in range(n_truck):
        idx = 0
        while idx < len(truck_visits[k]):
            item = truck_visits[k][idx]
            # if item["ijt"] is a 3-element tuple with int values, then unpack it
            # assert otherwise raise a ValueError
            assert isinstance(item["ijt"], tuple), f"ijt is not a tuple: {item['ijt']}"
            assert len(item["ijt"]) == 3, f"ijt has more than 3 elements: {item['ijt']}"
            assert all(
                isinstance(x, int) for x in item["ijt"]
            ), f"ijt contains non-int values: {item['ijt']}"
            i, j, t = item["ijt"]

            while (
                i == j and (idx != len(truck_visits[k]) - 1) and not (i == 0 and j == 0)
            ):
                for operation_type in operation_types:
                    added_val = truck_visits[k][idx + 1][operation_type]
                    current_val = item[operation_type]
                    assert isinstance(
                        current_val, int | float
                    ), f"current_val is not an int: {current_val}"
                    assert isinstance(
                        added_val, int | float
                    ), f"added_val is not an int: {added_val}"
                    truck_visits[k][idx + 1][operation_type] = int(current_val) + int(
                        added_val
                    )
                idx += 1  # skip the next item as it's already been aggregated
                item = truck_visits[k][idx]
                assert isinstance(
                    item["ijt"], tuple
                ), f"ijt is not a tuple: {item['ijt']}"
                i, j, t = item["ijt"]

            while i == 0 and j == 0 and (idx != len(truck_visits[k]) - 1):
                idx += 1
                for operation_type in operation_types:
                    current_val = int(truck_visits[k][idx][operation_type])
                    added_val = int(item[operation_type])
                    assert isinstance(current_val, int)
                    assert isinstance(added_val, int)
                    truck_visits[k][idx][operation_type] = current_val + added_val
                item = truck_visits[k][idx]
                assert isinstance(
                    item["ijt"], tuple
                ), f"ijt is not a tuple: {item['ijt']}"
                assert (
                    len(item["ijt"]) == 3
                ), f"ijt has more than 3 elements: {item['ijt']}"
                assert all(
                    isinstance(x, int) for x in item["ijt"]
                ), f"ijt contains non-int values: {item['ijt']}"
                i, j, t = item["ijt"]
            new_truck_visits[k].append(item)
            idx += 1
    truck_visits = new_truck_visits

    new_repairman_visits = [[] for _ in range(n_repairer)]

    for m in range(n_repairer):
        idx = 0
        while idx < len(repairman_visits[m]):
            item = repairman_visits[m][idx]
            assert isinstance(item["ijt"], tuple), f"ijt is not a tuple: {item['ijt']}"
            i, j, t = item["ijt"]
            while (
                i == j
                and (idx != len(repairman_visits[m]) - 1)
                and not (i == 0 and j == 0)
            ):
                assert isinstance(item["repaired"], int | float)
                added_repaired = repairman_visits[m][idx + 1]["repaired"]
                current_repaired = item["repaired"]
                assert isinstance(added_repaired, int | float)
                assert isinstance(current_repaired, int | float)
                repairman_visits[m][idx + 1]["repaired"] = int(current_repaired) + int(
                    added_repaired
                )
                idx += 1
                item = repairman_visits[m][idx]
                assert isinstance(
                    item["ijt"], tuple
                ), f"ijt is not a tuple: {item['ijt']}"
                i, j, t = item["ijt"]
            new_repairman_visits[m].append(item)
            idx += 1
    repairman_visits = new_repairman_visits

    for truck_visit in truck_visits:
        for item in truck_visit:
            for operation_type in operation_types:
                if item[operation_type] == 0:
                    del item[operation_type]

    for repairman_visit in repairman_visits:
        for item in repairman_visit:
            if item["repaired"] == 0:
                del item["repaired"]
    return truck_visits, repairman_visits


def operation_extract(lines, truck_visits, repairman_visits):
    operation_types = [
        "reb_amount_usable+",
        "reb_amount_usable-",
        "reb_amount_broken+",
        "reb_amount_broken-",
    ]
    for line in lines[1:]:
        variable, value = line.split()
        value = float(value)

        if value != 0:
            for operation_type in operation_types:
                if variable.startswith(operation_type):
                    i, t, k = map(int, variable[19:-1].split(","))
                    for item in truck_visits[k]:
                        if item["ijt"][0] == i and item["ijt"][2] == t:
                            item[operation_type] += value

        if variable.startswith("repaired_amount_man"):
            i, t, m = map(int, variable[20:-1].split(","))
            for item in repairman_visits[m]:
                if (
                    item["ijt"][0] == i
                    and item["ijt"][2] == t
                    and item["repaired"] == 0
                ):
                    item["repaired"] += value


def routing_extract(lines, truck_visits, repairman_visits):
    for line in lines[1:]:
        variable, value = line.split()
        value = float(value)

        if value == 1.0:
            if variable.startswith("visit_truck"):
                i, j, t, k = map(int, variable[12:-1].split(","))
                truck_visits[k].append(
                    {
                        "ijt": (i, j, t),
                        "reb_amount_usable+": 0,
                        "reb_amount_usable-": 0,
                        "reb_amount_broken+": 0,
                        "reb_amount_broken-": 0,
                    }
                )
            elif variable.startswith("visit_man"):
                i, j, t, m = map(int, variable[10:-1].split(","))
                repairman_visits[m].append({"ijt": (i, j, t), "repaired": 0})
    # for every list inside truck_visits list, sort the element based on the value of t in the field "ijt"
    for i, truck_visit in enumerate(truck_visits):
        truck_visits[i] = sorted(truck_visit, key=lambda item: item["ijt"][2])

    for i, repairman_visit in enumerate(repairman_visits):
        repairman_visits[i] = sorted(repairman_visit, key=lambda item: item["ijt"][2])

    return truck_visits, repairman_visits


def dissat_extract(lines):
    dissat = 0
    for line in lines[1:]:
        variable, value = line.split()
        value = float(value)
        if variable.startswith("dissat"):
            dissat += value
    return dissat


def emission_extract(lines):
    emission = 0
    for line in lines[1:]:
        variable, value = line.split()
        value = float(value)
        if variable.startswith("emission"):
            emission += value
    return emission


def load_and_distance(truck_visits):
    time_matrix = np.loadtxt(
        f"/home/runqiu/brpwr-refactor/resources/dataset/solver/{inst_no}/time_matrix_6.txt",
        dtype=int,
    )
    dist_matrix = time_matrix * 7 / 1000
    truck_inv = 0
    average_load = 0
    total_dist = 0.0
    broken_carried = 0
    keys = [
        "reb_amount_usable+",
        "reb_amount_usable-",
        "reb_amount_broken+",
        "reb_amount_broken-",
    ]
    for seg in truck_visits:
        i, j = seg["ijt"][0], seg["ijt"][1]

        for key in keys:
            if key in seg:
                # Adjust truck_inv based on whether the key ends with '+' or '-'
                adjustment = seg[key] if key.endswith("+") else -seg[key]
                truck_inv -= adjustment

                if key == "reb_amount_broken-":
                    broken_carried += seg[key]

        average_load += truck_inv * dist_matrix[i][j]
        total_dist += dist_matrix[i][j]

    return (average_load / total_dist), total_dist, broken_carried


def no_of_stations_visited(truck_visits):
    no = len(truck_visits) - 1
    final_seg = truck_visits[-1]
    if final_seg["ijt"][0] == 0 and final_seg["ijt"][1] == 0:
        no -= 1
    return no
