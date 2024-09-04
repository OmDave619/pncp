# Matrix Sparsity Calculation using Multithreading: OpenMP vs PThreads

## Overview
This project aims to calculate the sparsity (the ratio of zero-valued elements) of a square matrix using multithreading. The matrix sparsity calculation is implemented using both OpenMP and PThreads, with three different parallelization techniques: Chunk, Mixed, and Dynamic. The program compares the performance of these techniques by measuring the time taken for different matrix sizes, thread counts, sparsity values, and row increments.

## Files and Structure

The project directory contains the following files:

### Source Code Files
- `Assgn2-Chunk-OpenMP-CO22BTECH11006.cpp`
- `Assgn2-Chunk-PThreads-CO22BTECH11006.cpp`
- `Assgn2-Dynamic-OpenMP-CO22BTECH11006.cpp`
- `Assgn2-Dynamic-PThreads-CO22BTECH11006.cpp`
- `Assgn2-Mixed-Chunk-OpenMP-CO22BTECH11006.cpp`
- `Assgn2-Mixed-Chunk-PThreads-CO22BTECH11006.cpp` 
- `Assgn2-Mixed-OpenMP-CO22BTECH11006.cpp`
- `Assgn2-Mixed-PThreads-CO22BTECH11006.cpp`

### Other Files
- `Makefile`: Script to compile all programs using the `make` command.
- `input.txt`: Sample input file for running the programs.
- `Figure_1.png`, `Figure_2.png`, `Figure_3.png`, `Figure_4.png`: Graphs for performance analysis.

## Compilation and Execution

### Compilation

To compile the programs, use the provided `Makefile`. Run the following command in the terminal:

```bash
    make
```

This will generate the following executables:
- `chunk-omp`: Chunk method using OpenMP.
- `mixed-omp`: Mixed method using OpenMP.
- `dynamic-omp`: Dynamic method using OpenMP.
- `mixedchunk-omp`: Mixed-Chunk method using OpenMP.
- `chunk`: Chunk method using PThreads.
- `mixed`: Mixed method using PThreads.
- `dynamic`: Dynamic method using PThreads.
- `mixedchunk`: Mixed-Chunk method using PThreads.

#### Manual Compilation 
You can also manually compile individual files. Below are example commands to compile each file separately:

For OpenMP versions:
```bash
g++ -fopenmp Assgn2-Chunk-OpenMP-CO22BTECH11006.cpp -o chunk-omp
g++ -fopenmp Assgn2-Mixed-OpenMP-CO22BTECH11006.cpp -o mixed-omp
g++ -fopenmp Assgn2-Dynamic-OpenMP-CO22BTECH11006.cpp -o dynamic-omp
g++ -fopenmp Assgn2-Mixed-Chunk-OpenMP-CO22BTECH11006.cpp -o mixedchunk-omp
```

For PThreads versions:
``` bash
g++ -pthread Assgn2-Chunk-PThreads-CO22BTECH11006.cpp -o chunk
g++ -pthread Assgn2-Mixed-PThreads-CO22BTECH11006.cpp -o mixed
g++ -pthread Assgn2-Dynamic-PThreads-CO22BTECH11006.cpp -o dynamic
g++ -pthread Assgn2-Mixed-Chunk-PThreads-CO22BTECH11006.cpp -o mixedchunk
```

### Input

The program reads matrix data and parameters from `input.txt`. The structure of the input file is as follows:
- **N**: Matrix size (NxN).
- **S**: Sparsity percentage (amount of zero values in the matrix).
- **K**: Number of threads to use.
- **rowInc**: Row increment for dynamic scheduling.
- **Matrix**: The NxN matrix values in row-major order.

An example of the `input.txt` file is provided in the project directory.

### Execution

After compiling, you can run the executables as follows:

For OpenMP versions:
```bash
    ./chunk-omp
    ./mixed-omp
    ./dynamic-omp
```

For PThreads versions:
```bash
    ./chunk
    ./mixed
    ./dynamic
```

### Output

The output will be written to `output.txt` and will contain:
- Time taken to compute the matrix sparsity.
- Total number of zero-valued elements.
- Number of zero-valued elements counted by each thread.

### Contact

For any questions or further information about this project, please contact:

**Om Dave**  
**CO22BTECH11006**  
Indian Institute of Technology, Hyderabad  
Email: co22btech11006@iith.ac.in
