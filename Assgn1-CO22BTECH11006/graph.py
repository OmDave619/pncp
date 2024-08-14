import matplotlib.pyplot as plt
import numpy as np
question_data = [
    {
        "n" : [1000,2000,3000,4000,5000],
        "s" : [40],
        "rowInc" : [50],
        "k" : [16] 
    },
    {
        "n" : [5000],
        "s" : [40],
        "rowInc" : [50],
        "k" : [1,2,4,8,16,32] 
    },
    {
        "n" : [5000],
        "s" : [20,40,60,80],
        "rowInc" : [50],
        "k" : [16] 
    },
    {
        "n" : [5000],
        "s" : [40],
        "rowInc" : [10,20,30,40,50],
        "k" : [16] 
    },
]
files = ["Assgn1-Chunk-CO22BTECH11006", "Assgn1-Mixed-CO22BTECH11006", "Assgn1-Dynamic-CO22BTECH11006", "Assgn1-Mixed-Chunk-CO22BTECH11006"]
file_map = ["Chunk", "Mixed", "Dynamic", "Mixed Chunk"]
data = True
import json
with open("data.json", 'r') as file:
    data = json.load(file)

def plot_graph1():
    dat = data[0]
    s = question_data[0]["s"][0]
    rowInc = question_data[0]["rowInc"][0]
    k = question_data[0]["k"][0]
    
    collected_data = {file: [] for file in files}   
    
    for n in question_data[0]["n"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(s)][str(k)][str(rowInc)])
            
    x = np.array(question_data[0]["n"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='o', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)])
        
    plt.xlabel("Number of Rows in Matrix (n)", fontsize=12)
    plt.ylabel("Time (ms)", fontsize=12)
    plt.title("Time vs Number of Rows in Matrix", fontsize=14)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph2():
    dat = data[1]
    n = question_data[1]["n"][0]
    s = question_data[1]["s"][0]
    rowInc = question_data[1]["rowInc"][0]
    
    collected_data = {file: [] for file in files}   
    
    for k in question_data[1]["k"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(s)][str(k)][str(rowInc)])
            
    x = np.array(question_data[1]["k"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='s', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)])
        
    plt.xlabel("Number of Threads (k)", fontsize=12)
    plt.ylabel("Time (ms)", fontsize=12)
    plt.xticks(x)
    plt.xscale("log", base=2)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Time vs Number of Threads", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph3():
    dat = data[2]
    n = question_data[2]["n"][0]
    k = question_data[2]["k"][0]
    rowInc = question_data[2]["rowInc"][0]
    
    collected_data = {file: [] for file in files}   
    
    for s in question_data[2]["s"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(s)][str(k)][str(rowInc)])
            
    x = np.array(question_data[2]["s"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='^', linestyle='-', linewidth=2, markersize=6, label=file_map[files.index(file)])
        
    plt.xlabel("Sparsity of Matrix (s)", fontsize=12)
    plt.ylabel("Time (ms)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Time vs Sparsity of Matrix", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()

def plot_graph4():
    dat = data[3]
    n = question_data[3]["n"][0]
    s = question_data[3]["s"][0]
    k = question_data[3]["k"][0]
    files = ['Assgn1-Dynamic-CO22BTECH11006', 'Assgn1-Mixed-Chunk-CO22BTECH11006']
    new_file_map = ['Dynamic', 'Mixed-Chunk']
    collected_data = {file: [] for file in files}   
    
    for rowInc in question_data[3]["rowInc"]:
        for file in files:
            collected_data[file].append(dat[file][str(n)][str(s)][str(k)][str(rowInc)])
            
    x = np.array(question_data[3]["rowInc"])
    
    plt.figure(figsize=(10, 6))
    for file in files:
        plt.plot(x, collected_data[file], marker='D', linestyle='-', linewidth=2, markersize=6, label=new_file_map[files.index(file)])
        
    plt.xlabel("Number of Consecutive Rows (rowInc)", fontsize=12)
    plt.ylabel("Time (ms)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.title("Time vs Number of Consecutive Rows", fontsize=14)
    plt.legend(fontsize=10)
    plt.tight_layout()
    plt.show()
if __name__ == "__main__":
    plot_graph1()
    plot_graph2()
    plot_graph3()
    plot_graph4()
