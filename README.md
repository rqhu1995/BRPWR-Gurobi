# Bike Repositioning Problem with Broken Bikes considering On-site Repairs (Gurobi)

<img width="300" alt="image" src="https://github.com/user-attachments/assets/e8944330-73f0-487c-bb94-db8f715a79cb">

## Description

This project contains codes for the paper "Repositioning in bike sharing systems with broken bikes considering on-site repairs". The detailed model and problem description can be found in the paper.

##### ⚠️The current project solves the problem using Python with gurobipy for the `<ins>`EXACT `</ins>` solutions (**Solver**).

##### ⚠️There is another project using Hybrid Genetic Search with Adaptive Diversity Control and Station Budget Constrained heuristic for efficiently obtaining the `<ins>`near-optimal `</ins>` solutions. The project can be found [here](https://github.com/rqhu1995/BRPWR-HGSADC-SBC).

## Table of Contents

- [Project structure](#project-structure)
  - [Main structure](#main-structure)
  - [Data Specification](#data-specification)
  - [Using the data](#using-the-data)
- [Execution](#execution)
  - [Prerequisites](#prerequisites)
  - [Run the project](#run-the-project)
    - [Download the project](#download-the-project)
    - [Install the dependencies](#install-the-dependencies)
    - [Run the code](#run-the-code)
  - [Check the solutions](#check-the-solutions)

## Project structure

### Main structure

The strucutre of the project is given as follows:

```
.
├── main.py
├── model
│   ├── __init__.py
│   ├── callback.py
│   ├── constraints.py
│   ├── model.py
│   ├── objective.py
│   └── variables.py
├── parameters
│   ├── __init__.py
│   ├── config.py
│   ├── dataloader.py
│   └── sets.py
├── resources
│   ├── datasets
│   └── solutions
├── scripts
└── utils
    └── utils.py
```

Folders `parameters`, `model`,  `utils` and `main.py` form the main project.

The external resources include the dataset and solutions are put in the folder `resources`. Additionally, the folder `scripts` contains shell scripts that can run batch experiments for testing without having to input the commands one by one.

### Data naming and format description

The folders `X_Y` provide data for different sizes (`X` stations). `Y` here is the instance number. Inside each folder `X_Y`, we have:

- `dissat_table_i.txt (i = 1, 2, ..., X)`: These are the extended user dissatisfaction table calculated with a size of $C_i \times C_i$, where $C_i$ is capacity of station $i$. The row index $p$ is the number of usable bikes, and the column index $b$ is the number of broken bikes at station $i$. For table cells $(p,b)$ where $p+b > C_i$, the values are uniformly set as 0.
- `linear_diss_i.txt (i = 1, 2, ..., X)`: These are the linearized user dissatisfaction values for station $i$. The values are calculated based on the dissatisfaction tables and the method described in the paper. Each line inside the file represents one combination of $p$ and $b$ sorted in the order of $p$ fixed and $b$ varying. The values are separated by commas as $p$, $b$, $\alpha$, $\beta$, $\gamma$, and $s$, where $\alpha$, $\beta$, and $\gamma$ are the coefficients in the linearized function, and $s$ is the deviation of the linearized function from the original EUDF value.
- `BCRFT_i.txt (i = 1, 2, ..., X)`: These are the beneficial over cost ratio function for trucks at station $i$. The values are calculated based on the method described in the paper. This is a table similar to the dissatisfaction table, except for the values are the beneficial over cost ratio for each combination of $p$ and $b$.
- `BCRFR_i.txt (i = 1, 2, ..., X)`: These are the beneficial over cost ratio function for repairers at station $i$. The values are calculated based on the method described in the paper. This is a table similar to the dissatisfaction table, except for the values are the beneficial over cost ratio for each combination of $p$ and $b$.
- `station_info_X.txt`: This file contains the information of stations inside an `X`-station BSS network. The first line is the header, and the following lines are the information of each station. The information includes the station id, the capacity of the station, the number of current usable bikes at the station, the number of target usable bikes at the station, and the number of current broken bikes at the station. The values are separated by `\t`. The station_id here is the station id in the original dataset, after the data is read, they are re-indexed to `1,2,...,X`.
- `time_matrix_X.txt`: This file contains the time matrix between stations inside an `X`-station BSS network. The unit is seconds. Note depot is included in the station list, so the size of the matrix is $(X+1) \times (X+1)$. The values are separated by `\t`. Also note the matrix is asymmetric, i.e., the time from station $i$ to station $j$ is not necessarily the same as the time from station $j$ to station $i$.

### Data specification on the correspondence to experiments in the paper

- `X_Y` with `X = 6, 10, 15` and `Y = 1, 2, 3, 4, 5` correspond to the experiments on small scale instances in Section 5.2 of the paper.
- `X_Y` with `X = 60, 90, 120, 200, 300, 400, 500` and `Y = 1` correspond to the experiments on large scale instances in Section 5.3 of the paper.

### Using the data

To use the data,  [pandas](https://pandas.pydata.org/) library is recommended. The following code snippet shows how to read the data:

```python
import pandas as pd
df_station_info = pd.read_csv('resources/6_1/station_info_6.txt', sep='\t', header=0)
df_time_matrix = pd.read_csv('resources/6_1/time_matrix_6.txt', sep='\t')
```

## Run the project

### Prerequisites

The project is developed using Python 3.11+. The following libraries are required to run the project:

- gurobipy
- pandas
- numpy

> To run any of the instances in this project, a **Gurobi commercial or academic license is needed**. The community license is not sufficient as it has a limit of solving models within 2000 variables and 2000 linear constraints.

### Execution

To run the code, the following steps are recommended:

#### Download the project

```bash
# Clone the repository
git clone https://github.com/rqhu1995/BRPWR-Gurobi
```

#### Install the dependencies

While we recommend using Anaconda to ensure the environment separability, any python package manager and environment (virtual env/miniconda) is supported. Below we show the installation of the required packages with `conda`. You can absolutely install with `pip` or other package managers.

```bash
# Install dependencies using pip or anaconda
conda install pandas
conda install numpy
conda config --add channels https://conda.anaconda.org/gurobi
conda install gurobipy
```

#### Run the code

```bash
# Navigate to the project directory
cd BRPWR-Gurobi
```

```bash
# check the arguments for the project
python main.py --help
```

| Argument                      | Description                                      | Default Value  | Value Type | Supported Values                                                                                                                                                                                                                                             |
| ----------------------------- | ------------------------------------------------ | -------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-h`, `--help`            | Show this help message and exit                  | N/A            | N/A        | N/A                                                                                                                                                                                                                                                          |
| `-S`, `--n_station`       | Number of stations                               | 6              | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-K`, `--n_truck`         | Number of trucks                                 | 1              | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-R`, `--n_repairer`      | Number of repairers                              | 1              | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-NT`, `--n_intervals`    | Number of intervals                              | 12             | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-tau`, `--time_interval` | Time interval in seconds                         | 600            | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-Q`, `--truck_capacity`  | Truck capacity                                   | 25             | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-tl`, `--t_load`         | Time to load a bike in seconds                   | 60             | Integer    | Integers ≤`--time_interval`                                                                                                                                                                                                                               |
| `-tr`, `--t_repair`       | Time to repair a bike in seconds                 | 300            | Integer    | Integers ≤`--time_interval`                                                                                                                                                                                                                               |
| `-r`, `--has_repairer`    | Whether to include repairers                     | True           | Boolean    | `True`, `False`                                                                                                                                                                                                                                          |
| `-i`, `--inst_no`         | Instance number                                  | 1              | Integer    | Integers ≥ 1                                                                                                                                                                                                                                                |
| `-e`, `--exp_label`       | Experiment label                                 | `default`    | String     | `default`, `repair_time`                                                                                                                                                                                                                                 |
| `-t`, `--num_threads`     | Number of threads used, based on CPU capacity    | 4              | Integer    | Up to the number of available threads, typically `os.cpu_count()`                                                                                                                                                                                          |
| `-heu`, `--heuristics`    | Time percentage that Gurobi spends on heuristics | 0.00           | Float      | Real numbers ≥ 0                                                                                                                                                                                                                                            |
| `-m`, `--mode`            | Running mode of the optimization                 | `time_limit` | String     | `exhaustive`, `time_limit`: `exhaustive` mode runs until the optimal solution is found, <br />with heuristic and threads setting follows the default setting of Gurobi (maximum threads + 0.05 heuristic),, `time_limit` stops at a specified limit. |

For example,

```bash
python main.py -S 6 -i 1 -NT 12 -m exhaustive
```

will run instance 1 with six stations under 12 periods time budget, terminating until optimal is found.

```bash
python main.py -S 200 -i 1 -NT 18 -m time_limit -K 1 -R 1
```

will run instance 1 with six stations under 18 periods time budget, terminating when the time limit of 2 hours is reached.

#### Script execution

To facilitate the testing of the results, we wrote scripts for automating the execution process for both small and large instances. To use the scripts, simply execute

```bash
./large.sh 18 # or 12, the number means the time budget
```

or

```bash
./small.sh
```

Note that for large instances, we utilized `GNU screen` to attach the process in the background and better manage the results. Hence [the installation of `screen`](https://www.gnu.org/software/screen/) is required to use the script `large.sh`.

### Check the solutions

Solutions will be saved in the folder `resources/solutions`. The first file for a solution is the gurobi solution file ending with `.sol`. The second file is the postprocessed results with routes and numerical information in json format. The timestamp information is also included in the file name to differentiate the solutions. Solutions under the same date will be put under the same folder.
