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

def write_input(n: int, k: int):
    with open('input.txt', 'w') as file:
        file.write(f"{n} {k} 1 2\n")
        

import regex
def match_floats(string):
    return regex.findall(r"(\d+\.\d+)", string)

import subprocess
num_runs = 5



def run_test(i):
    data = question_data[i]

    print(f"Running Experiment {i+1}:") 
    out_data = dict(dict())
    out_data = {file:{n : {k: 0  for k in data['k']} for n in data['n']} for file in files}
    for file in files:
        print(f"\tRunning {file}")
        for n in data['n']:
            for k in data['k']:
                print(f"\t\tn={n}, k={k}")
                write_input(n, k)
                for _ in range(num_runs):
                    print(f"\t\t\tRun {_+1}")
                    out = subprocess.run(["./" + file], capture_output=True)
                    dat = match_floats(out.stdout.decode())
                    print(dat[len(dat)-3])
                    print(dat[len(dat)-2])
                    print(dat[len(dat)-1])
                    if i == 0 or i == 1:
                        out_data[file][n][k] += float(dat[len(dat)-3])
                    else: 
                        if type(out_data[file][n][k]) == int:
                            out_data[file][n][k] = [0,0]
                        out_data[file][n][k][0] += float(dat[len(dat)-2])
                        out_data[file][n][k][1] += float(dat[len(dat)-1])
                
                if i == 0 or i == 1:
                    out_data[file][n][k] /= num_runs
                else:
                    out_data[file][n][k] = [x/num_runs for x in out_data[file][n][k]]
                
    return out_data

                    
if __name__=="__main__":
    answer_data = [1,2,3,4]
    for i, data in enumerate(question_data):
        answer_data[i] = run_test(i)
        
    import json
    with open("data.json", 'w') as file:
        json.dump(answer_data, fp=file, indent=2)