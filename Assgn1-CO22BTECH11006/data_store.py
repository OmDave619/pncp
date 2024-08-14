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
num_runs = 5
def create_matrix(i, n, s):
    mat_file = f"./experiments/Experiment {i+1}/"
    if i == 2:
        mat_file += f"{s}.txt"
    else:
        mat_file += f"{n}.txt"
    
    with open(mat_file) as file:
        mat = []
        for line in file:
            mat.append(list(map(int, line.strip().split())))
        return mat        
    
def fill_data(i, n,s, k, rowInc):
    mat = create_matrix(i, n, s)
    with open('./input.txt', 'w') as file:
        string = f"{n} {s} {k} {rowInc}\n"
        file.write(string)
        for i in range(n):
            for j in range(n):
                file.write(f"{mat[i][j]} ")
            file.write("\n")

import regex
def match_time(string):
    return regex.findall(r"(\d+)", string)[0]

import subprocess
def run_test(i):
    data = question_data[i]
    print(f"Running Experiment {i}:") 
    out_data = dict(dict(dict(dict(dict()))))
    out_data = {file: {n : {s:{k: {rowInc: 0 for rowInc in data['rowInc']} for k in data['k']} for s in data['s']} for n in data['n']} for file in files}
    for n in data['n']:
        for s in data['s']:
            for k in data['k']:
                for rowInc in data['rowInc']:
                    fill_data(i, n, s, k ,rowInc)
                    print(f"    n={n}, s={s}, k={k}, rowInc={rowInc}")
                    
                    
                    for file in files:
                        print(f"        Running {file}")
                        time = 0
                        for run in range(num_runs):
                            # result = subprocess.run('./' + file)
                            result = subprocess.run(['./' + file], stdout=subprocess.PIPE)
                            print(result.stdout)
                            # print("\n\n\n\n\nHelloooo")
                            # return out_data
                            # print(result)
                            time += float(match_time(result.stdout.decode('utf-8')))
                        time /= num_runs
                        
                        out_data[file][n][s][k][rowInc] = time
    
    return out_data
                    
                      
if __name__=="__main__":
    answer_data = [1,2,3,4]
    for i, data in enumerate(question_data):
        if i == 3:
            files = ['Assgn1-Dynamic-CO22BTECH11006', 'Assgn1-Mixed-Chunk-CO22BTECH11006']
        
        answer_data[i] = run_test(i)
        
    import json
    with open("data.json", 'w') as file:
        json.dump(answer_data, fp=file, indent=2)