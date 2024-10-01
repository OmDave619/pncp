question_data = [
    {
        "n" : [2**i for i in range(1, 7)],
        "k" : [15]
    },
    {
        "n" : [16],
        "k" : [5*i for i in range(1, 6)],
    },
    {
        "n" : [2**i for i in range(1, 7)],
        "k" : [10],
    },
    {
        "n": [16],
        "k": [5*i for i in range(1, 6)],
    }
]
files = ["Filter-CO22BTECH11006" , "Bakery-CO22BTECH11006"]
file_map = ["Filter Lock", "Bakery Lock"]
data = []

import json
with open("data.json", 'r') as file:
    data = json.load(file)

import matplotlib.pyplot as plt
import numpy as np
def plot_graph1():
    dat = data[0]
    k = question_data[0]["k"][0]
    
    collected_data = {file: [] for file in files}   
    
    for n in question_data[0]["n"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(k)])
            
    x = np.array(question_data[0]["n"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='o', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)])
    print(collected_data)    
    plt.xlabel("Number of Rows in Matrix (n)", fontsize=12)
    plt.ylabel("Throughput", fontsize=12)
    plt.xscale('log', base=2)
    plt.title("Throughtput vs Number of Threads", fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph2():
    dat = data[1]
    n = question_data[1]["n"][0]
    
    collected_data = {file: [] for file in files}   
    
    for k in question_data[1]["k"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(k)])
            
    x = np.array(question_data[1]["k"])
    print(collected_data)
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='s', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)])
        
    plt.xlabel("Number of Tasks (k)", fontsize=12)
    plt.ylabel("Throughtput", fontsize=12)
    plt.xticks(x)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Throughput vs Number of Tasks", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph3():
    dat = data[2]
    k = question_data[2]["k"][0]
    
    collected_data = {file: {"Average": [], "Worst" : []} for file in files}   
    
    for n in question_data[2]["n"]:
        for file in files:
            collected_data[file]["Average"].append(dat[file][str(n)][str(k)][0])
            collected_data[file]["Worst"].append(dat[file][str(n)][str(k)][1])
    print(collected_data)
    
    x = np.array(question_data[2]["n"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file]["Average"], marker='^', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)]+" (Average)")
        plt.plot(x, collected_data[file]["Worst"], marker='v', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)]+" (Worst)")
        
    plt.xlabel("Number of Threads (n)", fontsize=12)
    plt.ylabel("Entry Time (seconds)", fontsize=12)
    plt.xticks(x)
    plt.xscale('log', base =2)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Entry Time vs Number of Threads", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph4():
    dat = data[3]
    n = question_data[3]["n"][0]
    collected_data = {file:{"Average": [], "Worst" : []}  for file in files}   
    
    for k in question_data[3]["k"]:
        for file in files:
            collected_data[file]["Average"].append(dat[file][str(n)][str(k)][0])
            collected_data[file]["Worst"].append(dat[file][str(n)][str(k)][1])
    print(collected_data)
    
    x = np.array(question_data[3]["k"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file]["Average"], marker='D', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)]+" (Average)")
        plt.plot(x, collected_data[file]["Worst"], marker='P', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)]+" (Worst)")
        
    plt.xlabel("Number of Tasks (k)", fontsize=12)
    plt.ylabel("Entry Time (seconds)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Entry Time vs Number of Tasks", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    plot_graph1()
    plot_graph2()
    plot_graph3()
    plot_graph4()