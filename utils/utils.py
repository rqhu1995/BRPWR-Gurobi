import json
from typing import Union, List, Dict, Tuple
from parameters.dataloader import n_truck, n_repairer


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
    repairer_visits = [[] for _ in range(n_repairer)]

    truck_visits, repairer_visits = routing_extract(
        lines, truck_visits, repairer_visits
    )

    operation_extract(lines, truck_visits, repairer_visits)
    truck_visits, repairer_visits = amendment(truck_visits, repairer_visits)

    dissat = dissat_extract(lines)

    emission = emission_extract(lines)

    data = {
        "objective_value": objective_value,
        "truck_visits": truck_visits,
        "repairer_visits": repairer_visits,
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
    repairer_visits: List[List[Dict[str, Union[int, Tuple[int, int, int]]]]],
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

    new_repairer_visits = [[] for _ in range(n_repairer)]

    for m in range(n_repairer):
        idx = 0
        while idx < len(repairer_visits[m]):
            item = repairer_visits[m][idx]
            assert isinstance(item["ijt"], tuple), f"ijt is not a tuple: {item['ijt']}"
            i, j, t = item["ijt"]
            while (
                i == j
                and (idx != len(repairer_visits[m]) - 1)
                and not (i == 0 and j == 0)
            ):
                assert isinstance(item["repaired"], int | float)
                added_repaired = repairer_visits[m][idx + 1]["repaired"]
                current_repaired = item["repaired"]
                assert isinstance(added_repaired, int | float)
                assert isinstance(current_repaired, int | float)
                repairer_visits[m][idx + 1]["repaired"] = int(current_repaired) + int(
                    added_repaired
                )
                idx += 1
                item = repairer_visits[m][idx]
                assert isinstance(
                    item["ijt"], tuple
                ), f"ijt is not a tuple: {item['ijt']}"
                i, j, t = item["ijt"]
            new_repairer_visits[m].append(item)
            idx += 1
    repairer_visits = new_repairer_visits

    for truck_visit in truck_visits:
        for item in truck_visit:
            for operation_type in operation_types:
                if item[operation_type] == 0:
                    del item[operation_type]

    for repairer_visit in repairer_visits:
        for item in repairer_visit:
            if item["repaired"] == 0:
                del item["repaired"]
    return truck_visits, repairer_visits


def operation_extract(lines, truck_visits, repairer_visits):
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
            for item in repairer_visits[m]:
                if (
                    item["ijt"][0] == i
                    and item["ijt"][2] == t
                    and item["repaired"] == 0
                ):
                    item["repaired"] += value


def routing_extract(lines, truck_visits, repairer_visits):
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
                repairer_visits[m].append({"ijt": (i, j, t), "repaired": 0})
    # for every list inside truck_visits list, sort the element based on the value of t in the field "ijt"
    for i, truck_visit in enumerate(truck_visits):
        truck_visits[i] = sorted(truck_visit, key=lambda item: item["ijt"][2])

    for i, repairer_visit in enumerate(repairer_visits):
        repairer_visits[i] = sorted(repairer_visit, key=lambda item: item["ijt"][2])

    return truck_visits, repairer_visits


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