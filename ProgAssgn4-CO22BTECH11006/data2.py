import subprocess
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import time
import sys

# Constants
NUM_RUNS = 5
INPUT_FILE = 'input.txt'
OFS_EXEC = './ofs-CO22BTECH11006'
WFS_EXEC = './wfs-CO22BTECH11006'
DELAY_BETWEEN_RUNS = 0.01  # seconds

# Function to compile C++ files
def compile_cpp():
    print("Compiling C++ files...")
    compile_commands = [
        ['g++', 'ofs-CO22BTECH11006.cpp', '-o', 'ofs-CO22BTECH11006', '-latomic'],
        ['g++', 'wfs-CO22BTECH11006.cpp', '-o', 'wfs-CO22BTECH11006', '-latomic']
    ]
    for cmd in compile_commands:
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Compilation failed for {' '.join(cmd)}")
            print(result.stderr.decode())
            sys.exit(1)
        else:
            print(f"Successfully compiled {' '.join(cmd)}")
    print("Compilation successful.\n")

# Function to write input.txt
def write_input(nw, ns, M, muw, mus, k):
    with open(INPUT_FILE, 'w') as f:
        f.write(f"{nw} {ns} {M} {muw} {mus} {k}\n")
    print(f"Written to {INPUT_FILE}: nw={nw}, ns={ns}, M={M}, muw={muw}, mus={mus}, k={k}")

# Function to parse the output from C++ programs
def parse_output(output):
    timings = {}
    patterns = {
        'average_update_time': r"Average update time: ([\d.]+) microseconds",
        'worst_update_time': r"Worst update time: ([\d.]+) microseconds",
        'average_scan_time': r"Average scan time: ([\d.]+) microseconds",
        'worst_scan_time': r"Worst scan time: ([\d.]+) microseconds",
        'average_time': r"Average time: ([\d.]+) microseconds",
        'worst_time': r"Worst time: ([\d.]+) microseconds"
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            timings[key] = float(match.group(1))
        else:
            timings[key] = None  # Handle missing data
    return timings

# Function to run a single experiment run
def run_single_run(nw, ns, M, muw, mus, k):
    write_input(nw, ns, M, muw, mus, k)
    
    # Run Obstruction-Free
    ofs_timings = {}
    try:
        print(f"Running {OFS_EXEC} with nw={nw}, ns={ns}")
        ofs_proc = subprocess.run([OFS_EXEC], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        if ofs_proc.returncode != 0:
            print(f"Error running {OFS_EXEC}")
            print(ofs_proc.stderr.decode())
            ofs_timings = {key: None for key in ['average_update_time', 'worst_update_time',
                                                'average_scan_time', 'worst_scan_time',
                                                'average_time', 'worst_time']}
        else:
            ofs_output = ofs_proc.stdout.decode()
            ofs_timings = parse_output(ofs_output)
            print(f"{OFS_EXEC} completed successfully.")
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {OFS_EXEC}")
        ofs_timings = {key: None for key in ['average_update_time', 'worst_update_time',
                                            'average_scan_time', 'worst_scan_time',
                                            'average_time', 'worst_time']}
    
    # Introduce a small delay to ensure the process has fully terminated
    time.sleep(DELAY_BETWEEN_RUNS)
    
    # Run Wait-Free
    wfs_timings = {}
    try:
        print(f"Running {WFS_EXEC} with nw={nw}, ns={ns}")
        wfs_proc = subprocess.run([WFS_EXEC], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        if wfs_proc.returncode != 0:
            print(f"Error running {WFS_EXEC}")
            print(wfs_proc.stderr.decode())
            wfs_timings = {key: None for key in ['average_update_time', 'worst_update_time',
                                                'average_scan_time', 'worst_scan_time',
                                                'average_time', 'worst_time']}
        else:
            wfs_output = wfs_proc.stdout.decode()
            wfs_timings = parse_output(wfs_output)
            print(f"{WFS_EXEC} completed successfully.")
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {WFS_EXEC}")
        wfs_timings = {key: None for key in ['average_update_time', 'worst_update_time',
                                            'average_scan_time', 'worst_scan_time',
                                            'average_time', 'worst_time']}
    
    # Introduce a small delay before the next run
    time.sleep(DELAY_BETWEEN_RUNS)
    
    return {'ofs': ofs_timings, 'wfs': wfs_timings}

# Function to compute average of lists, handling None
def average(lst):
    filtered = [x for x in lst if x is not None]
    return sum(filtered)/len(filtered) if filtered else None

# Function to compute maximum of lists, handling None
def maximum(lst):
    filtered = [x for x in lst if x is not None]
    return max(filtered) if filtered else None

# Function to perform Experiment 1 and 2 (Scalability)
def experiment_scalability(is_average_case=True):
    experiment_num = 1 if is_average_case else 2
    print(f"Starting Experiment {experiment_num} - {'Average-Case' if is_average_case else 'Worst-Case'} Scalability")
    
    # Define the varying number of writer threads
    nw_values = [4, 8, 16, 32]
    M = 40
    muw = 0.5
    mus = 0.5
    k = 5
    ratio = 4  # Fixed ratio nw/ns=4
    
    # Data structure: {nw: {'ofs': {'update': [], 'scan': [], 'all': []}, 'wfs': {...}}}
    data = defaultdict(lambda: {'ofs': {'update': [], 'scan': [], 'all': []},
                                'wfs': {'update': [], 'scan': [], 'all': []}})
    
    for nw in nw_values:
        ns = nw // ratio  # Ensures nw/ns=4
        if nw % ratio != 0:
            print(f"Warning: nw={nw} is not perfectly divisible by ratio={ratio}. Setting ns={ns}")
        if ns == 0:
            ns = 1  # Ensure at least one snapshot thread
            print(f"Adjusted ns to 1 for nw={nw} to avoid division by zero.")
        
        print(f"\nConfiguration: nw={nw}, ns={ns}, M={M}, muw={muw}, mus={mus}, k={k}")
        
        for run in range(1, NUM_RUNS + 1):
            print(f"  Run {run}/{NUM_RUNS}")
            run_data = run_single_run(nw, ns, M, muw, mus, k)
            if run_data:
                # Obstruction-Free
                ofs = run_data['ofs']
                if is_average_case:
                    data[nw]['ofs']['update'].append(ofs['average_update_time'])
                    data[nw]['ofs']['scan'].append(ofs['average_scan_time'])
                    data[nw]['ofs']['all'].append(ofs['average_time'])
                else:
                    data[nw]['ofs']['update'].append(ofs['worst_update_time'])
                    data[nw]['ofs']['scan'].append(ofs['worst_scan_time'])
                    data[nw]['ofs']['all'].append(ofs['worst_time'])
                
                # Wait-Free
                wfs = run_data['wfs']
                if is_average_case:
                    data[nw]['wfs']['update'].append(wfs['average_update_time'])
                    data[nw]['wfs']['scan'].append(wfs['average_scan_time'])
                    data[nw]['wfs']['all'].append(wfs['average_time'])
                else:
                    data[nw]['wfs']['update'].append(wfs['worst_update_time'])
                    data[nw]['wfs']['scan'].append(wfs['worst_scan_time'])
                    data[nw]['wfs']['all'].append(wfs['worst_time'])
            else:
                print(f"  Run {run} failed and was skipped.")
    
    # Aggregate data
    aggregated_data = defaultdict(lambda: {'ofs': {'update': None, 'scan': None, 'all': None},
                                           'wfs': {'update': None, 'scan': None, 'all': None}})
    for nw in nw_values:
        for algo in ['ofs', 'wfs']:
            for metric in ['update', 'scan', 'all']:
                if is_average_case:
                    aggregated_data[nw][algo][metric] = average(data[nw][algo][metric])
                else:
                    aggregated_data[nw][algo][metric] = maximum(data[nw][algo][metric])  # Use maximum for worst-case
                
    # Plotting
    plt.figure(figsize=(12, 8))
    markers = {'update': 'o', 'scan': 's', 'all': '^'}
    linestyles = {'ofs': '-', 'wfs': '--'}
    
    for algo in ['ofs', 'wfs']:
        for metric in ['update', 'scan']:
            y_values = [aggregated_data[nw][algo][metric] for nw in nw_values]
            label = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - {metric.capitalize()}"
            plt.plot(nw_values, y_values, label=label, marker=markers[metric], linestyle=linestyles[algo])
        
        # Handle 'all' metric separately
        if not is_average_case:
            y_values_all = [aggregated_data[nw][algo]['all'] for nw in nw_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Worst)"
            plt.scatter(nw_values, y_values_all, label=label_all, marker=markers['all'])
        else:
            y_values_all = [aggregated_data[nw][algo]['all'] for nw in nw_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Average)"
            plt.plot(nw_values, y_values_all, label=label_all, marker=markers['all'], linestyle=linestyles[algo])
    
    plt.xlabel('Number of Writer Threads (nw)')
    plt.ylabel('Average Time (μs)' if is_average_case else 'Worst Time (μs)')
    plt.title(f"Experiment {experiment_num}: {'Average-Case' if is_average_case else 'Worst-Case'} Scalability")
    plt.legend()
    plt.grid(True)
    plt.xticks(nw_values)
    plt.savefig(f"Experiment{experiment_num}_{'Average' if is_average_case else 'Worst'}_Scalability.png")
    plt.show()
    print(f"Experiment {experiment_num} completed.\n")

# Function to perform Experiment 3 and 4 (Impact of Update on Scan)
def experiment_impact_on_scan(is_average_case=True):
    experiment_num = 3 if is_average_case else 4
    print(f"Starting Experiment {experiment_num} - {'Average-Case' if is_average_case else 'Worst-Case'} Impact of Update on Scan")
    
    # Define the varying ratios
    ratios = [10, 8, 6, 4, 2, 1]
    ns_fixed = 4
    M = 20
    muw = 0.5
    mus = 0.5
    k = 5
    
    # Calculate corresponding nw values based on the ratio
    nw_values = [ratio * ns_fixed for ratio in ratios]
    
    # Data structure: {ratio: {'ofs': {'update': [], 'scan': [], 'all': []}, 'wfs': {...}}}
    data = defaultdict(lambda: {'ofs': {'update': [], 'scan': [], 'all': []},
                                'wfs': {'update': [], 'scan': [], 'all': []}})
    
    for ratio, nw in zip(ratios, nw_values):
        ns = ns_fixed  # Fixed
        print(f"\nConfiguration: ratio={ratio}, nw={nw}, ns={ns}, M={M}, muw={muw}, mus={mus}, k={k}")
        
        for run in range(1, NUM_RUNS + 1):
            print(f"  Run {run}/{NUM_RUNS}")
            run_data = run_single_run(nw, ns, M, muw, mus, k)
            if run_data:
                # Obstruction-Free
                ofs = run_data['ofs']
                if is_average_case:
                    data[ratio]['ofs']['update'].append(ofs['average_update_time'])
                    data[ratio]['ofs']['scan'].append(ofs['average_scan_time'])
                    data[ratio]['ofs']['all'].append(ofs['average_time'])
                else:
                    data[ratio]['ofs']['update'].append(ofs['worst_update_time'])
                    data[ratio]['ofs']['scan'].append(ofs['worst_scan_time'])
                    data[ratio]['ofs']['all'].append(ofs['worst_time'])
                
                # Wait-Free
                wfs = run_data['wfs']
                if is_average_case:
                    data[ratio]['wfs']['update'].append(wfs['average_update_time'])
                    data[ratio]['wfs']['scan'].append(wfs['average_scan_time'])
                    data[ratio]['wfs']['all'].append(wfs['average_time'])
                else:
                    data[ratio]['wfs']['update'].append(wfs['worst_update_time'])
                    data[ratio]['wfs']['scan'].append(wfs['worst_scan_time'])
                    data[ratio]['wfs']['all'].append(wfs['worst_time'])
            else:
                print(f"  Run {run} failed and was skipped.")
    
    # Aggregate data
    aggregated_data = defaultdict(lambda: {'ofs': {'update': None, 'scan': None, 'all': None},
                                           'wfs': {'update': None, 'scan': None, 'all': None}})
    for ratio in ratios:
        for algo in ['ofs', 'wfs']:
            for metric in ['update', 'scan', 'all']:
                if is_average_case:
                    aggregated_data[ratio][algo][metric] = average(data[ratio][algo][metric])
                else:
                    aggregated_data[ratio][algo][metric] = maximum(data[ratio][algo][metric])
    
    # Plotting
    plt.figure(figsize=(12, 8))
    markers = {'update': 'o', 'scan': 's', 'all': '^'}
    linestyles = {'ofs': '-', 'wfs': '--'}
    
    for algo in ['ofs', 'wfs']:
        for metric in ['update', 'scan']:
            y_values = [aggregated_data[ratio][algo][metric] for ratio in ratios]
            label = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - {metric.capitalize()}"
            plt.plot(ratios, y_values, label=label, marker=markers[metric], linestyle=linestyles[algo])
        
        # Handle 'all' metric separately
        if not is_average_case:
            y_values_all = [aggregated_data[ratio][algo]['all'] for ratio in ratios]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Worst)"
            plt.scatter(ratios, y_values_all, label=label_all, marker=markers['all'])
        else:
            y_values_all = [aggregated_data[ratio][algo]['all'] for ratio in ratios]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Average)"
            plt.plot(ratios, y_values_all, label=label_all, marker=markers['all'], linestyle=linestyles[algo])
    
    plt.xlabel('Ratio of nw/ns')
    plt.ylabel('Average Time (μs)' if is_average_case else 'Worst Time (μs)')
    plt.title(f"Experiment {experiment_num}: {'Average-Case' if is_average_case else 'Worst-Case'} Impact of Update on Scan")
    plt.legend()
    plt.grid(True)
    plt.xticks(ratios)
    plt.savefig(f"Experiment{experiment_num}_{'Average' if is_average_case else 'Worst'}_Impact_on_Scan.png")
    plt.show()
    print(f"Experiment {experiment_num} completed.\n")

# Function to perform Experiment 5 and 6 (Varying M)
def experiment_varying_M(is_average_case=True):
    experiment_num = 5 if is_average_case else 6
    print(f"Starting Experiment {experiment_num} - {'Average-Case' if is_average_case else 'Worst-Case'} Varying M")
    
    # Define varying M values
    M_values = [5, 10, 20, 40, 100, 200, 500, 1000]
    nw = 20
    ns = 2
    muw = 0.5
    mus = 0.5
    k = 10
    
    # Data structure: {M: {'ofs': {'update': [], 'scan': [], 'all': []}, 'wfs': {...}}}
    data = defaultdict(lambda: {'ofs': {'update': [], 'scan': [], 'all': []},
                                'wfs': {'update': [], 'scan': [], 'all': []}})
    
    for M in M_values:
        print(f"\nConfiguration: nw={nw}, ns={ns}, M={M}, muw={muw}, mus={mus}, k={k}")
        
        for run in range(1, NUM_RUNS + 1):
            print(f"  Run {run}/{NUM_RUNS}")
            run_data = run_single_run(nw, ns, M, muw, mus, k)
            if run_data:
                # Obstruction-Free
                ofs = run_data['ofs']
                if is_average_case:
                    data[M]['ofs']['update'].append(ofs['average_update_time'])
                    data[M]['ofs']['scan'].append(ofs['average_scan_time'])
                    data[M]['ofs']['all'].append(ofs['average_time'])
                else:
                    data[M]['ofs']['update'].append(ofs['worst_update_time'])
                    data[M]['ofs']['scan'].append(ofs['worst_scan_time'])
                    data[M]['ofs']['all'].append(ofs['worst_time'])
                
                # Wait-Free
                wfs = run_data['wfs']
                if is_average_case:
                    data[M]['wfs']['update'].append(wfs['average_update_time'])
                    data[M]['wfs']['scan'].append(wfs['average_scan_time'])
                    data[M]['wfs']['all'].append(wfs['average_time'])
                else:
                    data[M]['wfs']['update'].append(wfs['worst_update_time'])
                    data[M]['wfs']['scan'].append(wfs['worst_scan_time'])
                    data[M]['wfs']['all'].append(wfs['worst_time'])
            else:
                print(f"  Run {run} failed and was skipped.")
    
    # Aggregate data
    aggregated_data = defaultdict(lambda: {'ofs': {'update': None, 'scan': None, 'all': None},
                                           'wfs': {'update': None, 'scan': None, 'all': None}})
    for M in M_values:
        for algo in ['ofs', 'wfs']:
            for metric in ['update', 'scan', 'all']:
                if is_average_case:
                    aggregated_data[M][algo][metric] = average(data[M][algo][metric])
                else:
                    aggregated_data[M][algo][metric] = maximum(data[M][algo][metric])
    
    # Plotting
    plt.figure(figsize=(14, 8))
    markers = {'update': 'o', 'scan': 's', 'all': '^'}
    linestyles = {'ofs': '-', 'wfs': '--'}
    
    for algo in ['ofs', 'wfs']:
        for metric in ['update', 'scan']:
            y_values = [aggregated_data[M][algo][metric] for M in M_values]
            label = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - {metric.capitalize()}"
            plt.plot(M_values, y_values, label=label, marker=markers[metric], linestyle=linestyles[algo])
        
        # Handle 'all' metric separately
        if not is_average_case:
            y_values_all = [aggregated_data[M][algo]['all'] for M in M_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Worst)"
            plt.scatter(M_values, y_values_all, label=label_all, marker=markers['all'])
        else:
            y_values_all = [aggregated_data[M][algo]['all'] for M in M_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Average)"
            plt.plot(M_values, y_values_all, label=label_all, marker=markers['all'], linestyle=linestyles[algo])
    
    plt.xlabel('Number of Locations (M)')
    plt.ylabel('Average Time (μs)' if is_average_case else 'Worst Time (μs)')
    plt.title(f"Experiment {experiment_num}: {'Average-Case' if is_average_case else 'Worst-Case'} Performance with Varying M")
    plt.legend()
    plt.grid(True)
    plt.xscale('log')  # Use logarithmic scale for better visualization with large M
    plt.xticks(M_values, M_values)  # Ensure all M_values are shown as ticks
    plt.savefig(f"Experiment{experiment_num}_{'Average' if is_average_case else 'Worst'}_Varying_M.png")
    plt.show()
    print(f"Experiment {experiment_num} completed.\n")

# Function to perform Experiment 5 and 6 (Varying M)
def experiment_varying_M(is_average_case=True):
    experiment_num = 5 if is_average_case else 6
    print(f"Starting Experiment {experiment_num} - {'Average-Case' if is_average_case else 'Worst-Case'} Varying M")
    
    # Define varying M values
    M_values = [5, 10, 20, 40, 100, 200, 500, 1000]
    nw = 20
    ns = 2
    muw = 0.5
    mus = 0.5
    k = 10
    
    # Data structure: {M: {'ofs': {'update': [], 'scan': [], 'all': []}, 'wfs': {...}}}
    data = defaultdict(lambda: {'ofs': {'update': [], 'scan': [], 'all': []},
                                'wfs': {'update': [], 'scan': [], 'all': []}})
    
    for M in M_values:
        print(f"\nConfiguration: nw={nw}, ns={ns}, M={M}, muw={muw}, mus={mus}, k={k}")
        
        for run in range(1, NUM_RUNS + 1):
            print(f"  Run {run}/{NUM_RUNS}")
            run_data = run_single_run(nw, ns, M, muw, mus, k)
            if run_data:
                # Obstruction-Free
                ofs = run_data['ofs']
                if is_average_case:
                    data[M]['ofs']['update'].append(ofs['average_update_time'])
                    data[M]['ofs']['scan'].append(ofs['average_scan_time'])
                    data[M]['ofs']['all'].append(ofs['average_time'])
                else:
                    data[M]['ofs']['update'].append(ofs['worst_update_time'])
                    data[M]['ofs']['scan'].append(ofs['worst_scan_time'])
                    data[M]['ofs']['all'].append(ofs['worst_time'])
                
                # Wait-Free
                wfs = run_data['wfs']
                if is_average_case:
                    data[M]['wfs']['update'].append(wfs['average_update_time'])
                    data[M]['wfs']['scan'].append(wfs['average_scan_time'])
                    data[M]['wfs']['all'].append(wfs['average_time'])
                else:
                    data[M]['wfs']['update'].append(wfs['worst_update_time'])
                    data[M]['wfs']['scan'].append(wfs['worst_scan_time'])
                    data[M]['wfs']['all'].append(wfs['worst_time'])
            else:
                print(f"  Run {run} failed and was skipped.")
    
    # Aggregate data
    aggregated_data = defaultdict(lambda: {'ofs': {'update': None, 'scan': None, 'all': None},
                                           'wfs': {'update': None, 'scan': None, 'all': None}})
    for M in M_values:
        for algo in ['ofs', 'wfs']:
            for metric in ['update', 'scan', 'all']:
                if is_average_case:
                    aggregated_data[M][algo][metric] = average(data[M][algo][metric])
                else:
                    aggregated_data[M][algo][metric] = maximum(data[M][algo][metric])
    
    # Plotting
    plt.figure(figsize=(14, 8))
    markers = {'update': 'o', 'scan': 's', 'all': '^'}
    linestyles = {'ofs': '-', 'wfs': '--'}
    
    for algo in ['ofs', 'wfs']:
        for metric in ['update', 'scan']:
            y_values = [aggregated_data[M][algo][metric] for M in M_values]
            label = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - {metric.capitalize()}"
            plt.plot(M_values, y_values, label=label, marker=markers[metric], linestyle=linestyles[algo])
        
        # Handle 'all' metric separately
        if not is_average_case:
            y_values_all = [aggregated_data[M][algo]['all'] for M in M_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Worst)"
            plt.scatter(M_values, y_values_all, label=label_all, marker=markers['all'])
        else:
            y_values_all = [aggregated_data[M][algo]['all'] for M in M_values]
            label_all = f"{'Obstruction-Free' if algo == 'ofs' else 'Wait-Free'} - All (Average)"
            plt.plot(M_values, y_values_all, label=label_all, marker=markers['all'], linestyle=linestyles[algo])
    
    plt.xlabel('Number of Locations (M)')
    plt.ylabel('Average Time (μs)' if is_average_case else 'Worst Time (μs)')
    plt.title(f"Experiment {experiment_num}: {'Average-Case' if is_average_case else 'Worst-Case'} Performance with Varying M")
    plt.legend()
    plt.grid(True)
    plt.xscale('log')  # Use logarithmic scale for better visualization with large M
    plt.xticks(M_values, M_values)  # Ensure all M_values are shown as ticks
    plt.savefig(f"Experiment{experiment_num}_{'Average' if is_average_case else 'Worst'}_Varying_M.png")
    plt.show()
    print(f"Experiment {experiment_num} completed.\n")

# Main function to execute all experiments
def main():
    compile_cpp()
    
    # Experiment 1: Average-case Scalability
    experiment_scalability(is_average_case=True)
    
    # Experiment 2: Worst-case Scalability
    experiment_scalability(is_average_case=False)
    
    # Experiment 3: Impact of Update on Scan in average-case
    experiment_impact_on_scan(is_average_case=True)
    
    # Experiment 4: Impact of Update on Scan in worst-case
    experiment_impact_on_scan(is_average_case=False)
    
    # Experiment 5: Varying M - Average-case
    experiment_varying_M(is_average_case=True)
    
    # Experiment 6: Varying M - Worst-case
    experiment_varying_M(is_average_case=False)
    
    print("All experiments completed successfully.")

if __name__ == "__main__":
    main()
