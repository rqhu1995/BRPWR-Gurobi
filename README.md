# Bike Repositioning Problem with Broken Bikes considering On-site Repairs (Gurobi)

<img width="300" alt="image" src="https://github.com/user-attachments/assets/e8944330-73f0-487c-bb94-db8f715a79cb">



## Description

This project contains codes for the paper "Repositioning in bike sharing systems with broken bikes considering on-site repairs". The detailed model and problem description can be found in the paper. 

##### ⚠️The current project solves the problem using Python with gurobipy for the <ins>EXACT</ins> solutions (**Solver**).
##### ⚠️There is another project using Hybrid Genetic Search with Adaptive Diversity Control and Station Budget Constrained heuristic for efficiently obtaining the <ins>near-optimal</ins> solutions. The project can be found [here](https://github.com/rqhu1995/BRPWR-HGSADC-SBC).

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

### Data Specification

The folders `X_Y` provide data for different sizes (`X` stations). `Y` here is the instance number. Inside each folder `X_Y`, we have:

- `dissat_table_i.txt (i=1, 2, ..., X)`: These are the extended user dissatisfaction table calculated with a size of $C_i \times C_i$, where $C_i$ is capacity of station $i$. The row index $p$ is the number of usable bikes, and the column index $b$ is the number of broken bikes at station $i$. For table cells $(p,b)$ where $p+b > C_i$, the values are uniformly set as 0.
- `linear_diss_i.txt (i=1, 2, ..., X)`: These are the linearized user dissatisfaction values for station $i$. The values are calculated based on the dissatisfaction tables and the method described in the paper. Each line inside the file represents one combination of $p$ and $b$ sorted in the order of $p$ fixed and $b$ varying. The values are separated by commas as $p$, $b$, $\alpha$, $\beta$, $\gamma$, and $s$, where $\alpha$, $\beta$, and $\gamma$ are the coefficients in the linearized function, and $s$ is the deviation of the linearized function from the original EUDF value.
- `BCRFT_i.txt (i=1, 2, ..., X)`: These are the beneficial over cost ratio function for trucks at station $i$. The values are calculated based on the method described in the paper. This is a table similar to the dissatisfaction table, except for the values are the beneficial over cost ratio for each combination of $p$ and $b$.
- `BCRFR_i.txt (i=1, 2, ..., X)`: These are the beneficial over cost ratio function for repairers at station $i$. The values are calculated based on the method described in the paper. This is a table similar to the dissatisfaction table, except for the values are the beneficial over cost ratio for each combination of $p$ and $b$.
- `station_info_X.txt`: This file contains the information of stations inside an `X`-station BSS network. The first line is the header, and the following lines are the information of each station. The information includes the station id, the capacity of the station, the number of current usable bikes at the station, the number of target usable bikes at the station, and the number of current broken bikes at the station. The values are separated by `\t`. The station_id here is the station id in the original dataset, after the data is read, they are re-indexed to `1,2,...,X`.
- `time_matrix_X.txt`: This file contains the time matrix between stations inside an `X`-station BSS network. The unit is seconds. Note depot is included in the station list, so the size of the matrix is $(X+1) \times (X+1)$. The values are separated by `\t`. Also note the matrix is asymmetric, i.e., the time from station $i$ to station $j$ is not necessarily the same as the time from station $j$ to station $i$.

### Using the data

To use the data,  [pandas](https://pandas.pydata.org/) library is recommended. The following code snippet shows how to read the data:

```python
import pandas as pd
df_station_info = pd.read_csv('resources/15_1/station_info_15.txt', sep='\t', header=0)
df_time_matrix = pd.read_csv('resources/15_1/time_matrix_15.txt', sep='\t')
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
git clone https://github.com/rqhu1995/brpwr.git
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
cd brpwr
```

```bash
# check the arguments for the project
python main.py --help
```

| Argument             | Description                                                               | Default Value | Value Type | Supported values                                                                                                                                                                                             |
| -------------------- | ------------------------------------------------------------------------- | ------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `-h`, `--help`   | Show this help message and exit                                           | N/A           | N/A        | N/A                                                                                                                                                                                                          |
| `--n_station`      | Number of stations                                                        | 10            | Integer    | the number of stations should be set as the values that exist in the dataset directory                                                                                                                      |
| `--n_truck`        | Number of trucks                                                          | 1             | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--n_repairman`    | Number of repairmen                                                       | 1             | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--n_intervals`    | Number of intervals                                                       | 12            | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--truck_capacity` | Truck capacity                                                            | 25            | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--model_type`     | The type of the model                                                     | wr            | String     | `wr`: the model with repairmen<br />`nr`: the model without repairmen                                                                                                                                  |
| `--ratio_broken`   | Ratio of broken bikes calculated by:</br> $\frac{b}{q-p}$ if $q>p$ otherwise 0 | 0.5           | Float      | Real numbers $\ge$ 0                                                                                                                                                                                        |
| `--time_interval`  | Time interval in seconds                                                  | 600           | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--t_load`         | Time to load a bike in seconds                                            | 60            | Integer    | Integers $\le$ `--time_inteval`                                                                                                                                                                              |
| `--t_repair`       | Time to repair a bike                                                     | 300           | Integer    | Integers $\le$ `--time_inteval`                                                                                                                                                             |
| `--inst_no`        | Instance number                                                           | 1             | Integer    | Integers $\ge$ 1                                                                                                                                                                                            |
| `--is_prop`        | Whether the experiment for proportion is conducted                        | 0             | {0,1}      | If it is set to 0, the broken bikes quantities will be set based on the dataset files;<br />If it is set to 1, the broken bikes quantities will be set using the proportion specified in `--ratio_broken` |

### Check the solutions

Solutions will be saved in the folder `resources/solutions`. The first file for a solution is the gurobi solution file ending with `.sol`. The second file is the postprocessed results with routes and numerical information in json format. The timestamp information is also included in the file name to differentiate the solutions. Solutions under the same date will be put under the same folder.
