# Script for benchmarking.
# Immediate remit is to take a log file and calculate the total time running

import argparse
from pathlib import Path
from datetime import datetime
import shutil 
import itertools

import matplotlib.pyplot as plt
import numpy as np

def sweep_current_dir(purge_dirs: bool = False):
    # Run through all runX directories in this directory

    dirs = (Path(".").glob("./*"))
    #for dir_name in dirs:

    runs = {}
    
    for dir_name in dirs:
        if not dir_name.name == "runN":
            print(dir_name.name)
            runs[dir_name.name] = read_one_dir_time(dir_name.name, purge_dirs)

    for key in runs:
        if  not runs[key]: continue
        print(f"{key} | "
              f" {runs[key][2] - runs[key][0]} |", end="")
        if runs[key][1]:
            print(f" {runs[key][2] - runs[key][1]} |")
        else:
            print(" - |")

def purge_results(in_dir: str):
    # Removes the results dierctory from a run, to save quota

    results_dir = Path(in_dir) / "share" / "output"

    if results_dir.is_dir():
        shutil.rmtree(results_dir)

def read_datetime_from_fileline(in_line: str):
    # Convert the first part of a line to a datetime

    # Strip the information from the line
    in_time = in_line.split(" ")[0]

    try:
        time = datetime.strptime(in_time,
                                 "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print("An error occured in stripping time")
        return 0

    return time

def get_time_from_log_line(in_log : Path, read_line: str):
    # Read the time of a specific line in the log file. If not log exists or the entry is not there, returns "-"

    if not in_log.exists():
        return "--"
    
    with open(in_log) as in_file:
        for line in in_file:
            if read_line in line:
                return read_datetime_from_fileline(line)
    
    return "-"

def plot_timing_dict(timings):
    # Plot timing metrics from the dict

    for res in timings.keys():
        #Make one plot per res
        x_arrays = {}
        y_arrays = {}
        for n_runs in timings[res]:
            mpi_parts_list = list(timings[res][n_runs].keys())
            mpi_parts_list.sort()
            x_arrays[n_runs] = []
            y_arrays[n_runs] = []
            for mpi_parts in mpi_parts_list:
                x_arrays[n_runs].append(int(mpi_parts[1:]))
                y_arrays[n_runs].append(timings[res][n_runs][mpi_parts].seconds)

        print(x_arrays)
        print(y_arrays)
        fig, ax = plt.subplots()

        n_run_list = list(x_arrays.keys())
        n_run_list.sort()
        for n_runs in n_run_list:
            ax.plot(x_arrays[n_runs],y_arrays[n_runs],label=f"{n_runs[1:]} runs")
        plt.legend()
        ax.set_xlabel("MPI partitions")
        ax.set_ylabel("Run time (s)")

        ax.set_title(f"Run time for {res}")
        plt.show()
        
#        for 
    
def sort_benchmarks(timings):
    # Take the confusingly titled benchmark IDs and sort them into their parts

    # Sorted benchmarks. Dict of timining[res][n_jobs][mpi_parts]
    sorted_timings = {}
    
    for benchmark_id in timings.keys():
        id_sections = benchmark_id.split("-")
        if not id_sections[0] in sorted_timings: sorted_timings[id_sections[0]] = {}
        if not id_sections[1] in sorted_timings[id_sections[0]]: sorted_timings[id_sections[0]][id_sections[1]] = {}
        sorted_timings[id_sections[0]][id_sections[1]][id_sections[2]] = timings[benchmark_id]

    return sorted_timings
        
def scan_dirs_for_benchmarks(in_dir_str: str, purge_dirs: bool = False):
    # Run over a list of input dirs with multiple jobs in them

    timings = {}

    in_dirs = in_dir_str.split(",")
    
    for in_dir in in_dirs:
        read_one_runs_dirs(in_dir, timings, purge_dirs)

    full_timings = {}
    for benchmark_id in timings.keys():
        time_values = timings[benchmark_id]
        print_value = "-"
        if time_values[0] == "-": print_value = "DNS"
        elif time_values[1] == "-": print_value = "DNF"
        elif time_values[0] == "--" or time_values[1] == "--": print_value = "No log"
        else:
            print_value = time_values[1] - time_values[0]
            full_timings[benchmark_id] = print_value
        print(f"{benchmark_id} | {print_value}")

    sorted_timing = sort_benchmarks(full_timings)

    res_list = (list(sorted_timing.keys()))
    print(res_list)
    res_list.sort()
    print(res_list)
    for res in res_list:
        print(res)
        njob_list = list(sorted_timing[res].keys())
        njob_list.sort()
        for n_jobs in njob_list:
            print(f"{n_jobs}")
            mpi_parts_list = list(sorted_timing[res][n_jobs].keys())
            mpi_parts_list.sort()
            for mpi_parts in mpi_parts_list:
                print(f"{mpi_parts} | {sorted_timing[res][n_jobs][mpi_parts]}")
    plot_timing_dict(sorted_timing)
    
def read_one_runs_dirs(in_dir: str, timings, purge_dirs: bool = False):
    # Read multiple jobs in one directory that we're in

    print(in_dir)
    
    log_dir_path = Path(in_dir) / "log" / "job" / "1" 
    
    log_dirs = [f for f in log_dir_path.glob("*run_lfric*")]

    for log_dir in log_dirs:
        benchmark_id = str(log_dir).split("gj1214b-")[1].split("_")[0]
        if not benchmark_id in timings.keys(): timings[benchmark_id] = ["-","-"]
        n_jobs = int(benchmark_id.split("-n")[1].split("-")[0])
        if n_jobs == 1 or str(log_dir).split("crun")[1] == "0":
            start_time = get_time_from_log_line(log_dir / "01" / "job.out", "INFO - started")
            timings[benchmark_id][0] = start_time
        if n_jobs == 1 or str(log_dir).split("crun")[1] == str(n_jobs-1):
            end_time = get_time_from_log_line(log_dir / "01" / "job.out", "INFO - succeeded")
            timings[benchmark_id][1] = end_time

    if purge_dirs:
        purge_results(in_dir)
        
    return timings
    


def read_one_dir_time(in_dir: str, purge_dirs: bool = False):
    # Calculate the time spent running the job in one cylc run

    in_log = Path(in_dir) / "log" / "scheduler" / "01-start-01.log"

    if not in_log.is_file():
        print(f"No log found at {in_log}!")
        return

    with open(in_log) as in_file:
        # The first line in nonsense, skip it.
        skip_line = in_file.readline()
        start_time = read_datetime_from_fileline(in_file.readline())
        run_time_start = 0
        for line in in_file:
            if run_time_start == 0 and "run_lfric_atm" in line and " => waiting(queued)" in line:
                run_time_start = read_datetime_from_fileline(line)
            if "INFO - DONE" in line:
                end_time = read_datetime_from_fileline(line)

        print (start_time, run_time_start, end_time)
        print (f"Full job: {end_time - start_time}")
        if run_time_start:
            print (f"From first run submission: {end_time - run_time_start}")
        else:
            print ("No run time start detected, probably crashed before running")

    if purge_dirs:
        purge_results(in_dir)

    return (start_time, run_time_start, end_time)

def edit_cylc_config(in_file: str, out_file: str, payload: {str:str}):
    # Edit a single version of the cylc config with the given parameters

    in_file_path = Path("rose-stem") / "site" / "common" / " lfric_atm"

    replace_lines = False

    with open(in_file_path / "tmp.cylc", "w") as out_file:
        with open(in_file_path / "tasks_lfric_atm.cylc") as in_file:
            for line in in_file:
                if "camembert_case3_gj1214b" in line:
                    replace_lines = True
                if "}) %}" in line:
                    replace_lines = False
                if replace_lines: 
                    for payload_item in payload:
                        if payload_item in line:
                            print("found payload")
                            line = f"{line.split(':')[0]}: {payload[payload_item]},\n"
                out_file.write(line)


def define_workflows():
    # Define the benchmarking workflows that we're going to run

    # The parameters that we're going to vary
    parameters = {
        "cruns" : ["1","5","10"],
        "mpi_nparts" : ["2", "4", "6", "12", "24"],
    }
    
    file_path = Path("rose-stem") / "site" / "common" / " lfric_atm"

    in_file = file_path / "tasks_lfric_atm.cylc"
    out_file = file_path / "tmp.cylc"

    parameter_list = list(parameters)
    
    for values in itertools.product(*map(parameters.get,parameter_list)):
        print(dict(zip(parameter_list,values)))
#    edit_cylc_config(in_file, out_file, p

                     
def main(in_dir: str, purge_dirs: bool = False, all_dirs: bool = False, run_workflows: bool = False, multirun_dir: bool = False):

    if all_dirs:
        sweep_current_dir(purge_dirs)
    elif run_workflows:
        define_workflows()
    elif multirun_dir:
        scan_dirs_for_benchmarks(multirun_dir,purge_dirs)
    else:
        read_one_dir_time(in_dir, purge_dirs)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="lfric_benchmarking",
        description="Benchmarking tools",
    )
    parser.add_argument("--indir", "-i", default=".", help="Which directory to read in")
    parser.add_argument("--purge_dirs", "-p", default=False,action="store_true", help="Removes the results folder from the directory")
    parser.add_argument("--all_dirs", "-a", default=False,action="store_true", help="Runs over all 'runX' directories here")
    parser.add_argument("--run_workflows", "-r", default=False, action="store_true", help="Run the configuration workflows")
    parser.add_argument("--multirun_dir", "-m", default="", help="List of dirs to run which contain multiple runs each")
        
    args = parser.parse_args()
    
    main(
        args.indir,
        args.purge_dirs,
        args.all_dirs,
        args.run_workflows,
        args.multirun_dir,
    )
