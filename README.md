# AI-HomeWork
# Homework: Solving the Generalized 15-Puzzle
**Artificial Intelligence Course (2025/2026)** **Author:** Samuele Costantinopoli  
**Matricola:** 2271799

## Overview
This project compares two Artificial Intelligence approaches to solve the Generalized $N \times N$ Sliding Tile Puzzle (e.g., 8-puzzle, 15-puzzle):
1.  **Custom A* Search:** A Python implementation using the Manhattan Distance heuristic.
2.  **Automated Planning (PDDL):** A modeling approach using PDDL domain/problem files solved by the **Fast Downward** planner.

The project includes the source code for the solvers, a benchmarking script to gather performance metrics, and tools to visualize the results.

## Project Structure
* `homework_main.py`: Contains the core logic (PuzzleState class), the A* implementation, and the PDDL generator.
* `benchmark.py`: Runs a battery of tests (varying grid size and difficulty), executes both solvers, and saves results to CSV.
* `generate_plots.py`: Reads the CSV results and generates comparative plots (PNG images).
* `benchmark_results.csv`: The dataset collected from the experiments.
* `report.pdf`: The final detailed report of the project.

## Prerequisites

### 1. Python Libraries
The code is written in **Python 3**. You need to install the following dependencies for data analysis and plotting:

``bash
pip install pandas matplotlib

### 2. Fast Downward Planner

This project requires the Fast Downward planner to be installed and compiled on your machine. If you don't have it, follow these steps (on Linux/Ubuntu):
# Install dependencies
sudo apt install cmake g++ git make python3 python3-dev

# Clone the repository
git clone [https://github.com/aibasel/downward.git](https://github.com/aibasel/downward.git) fast-downward

# Compile
`cd fast-downward`
`./build.py`

Configuration

Before running the code, you must update the path to the planner.

1. Open homework_main.py (and benchmark.py).

2. Locate the variable PLANNER_PATH or the function call to run_planner_and_parse.

3. Change the path to point to your local fast-downward.py executable.

# In benchmark.py
`PLANNER_PATH = "/path/to/your/folder/fast-downward/fast-downward.py"`

How to Run
1. Single Instance Test

To run a simple test (Generate instance -> Solve with A* -> Solve with Planner):

Bash
`python3 homework_main.py`

2. Run Benchmarks

To execute the full suite of experiments (this may take a few minutes depending on the difficulty settings):

Bash
`python3 benchmark.py`

This will create/update the benchmark_results.csv file.

3. Generate Plots
To visualize the results from the CSV file:

Bash
`python3 generate_plots.py`

This will save plot_8-Puzzle.png and plot_15-Puzzle.png in the current directory.
