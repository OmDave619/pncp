# Filter and Bakery Lock Comparison

## Overview

This project compares the performance of two locking algorithms—Filter Lock and Bakery Lock—in a concurrent programming environment. The comparison is based on metrics such as throughput, average entry time, and worst-case entry time, measured under varying numbers of threads and critical section entries.

## File and Structure

### C++ Files

- **Bakery-CO22BTECH11006.cpp**: Implements the Bakery Lock algorithm.
- **Filter-CO22BTECH11006.cpp**: Implements the Filter Lock algorithm.

### Data and Config Files

- **input.txt**: Contains input parameters for the program (number of threads, number of times each thread enters the critical section, time delays for critical section and remainder section).
- **output_filter.txt**: Stores the results for the Filter Lock algorithm.
- **output_bakery.txt**: Stores the results for the Bakery Lock algorithm.

## Input

The input file (`input.txt`) should contain four values:

```bash
n k lambdaCS lambdaRem
```

- `n`: Number of threads.
- `k`: Number of times each thread enters the critical section.
- `lambdaCS`: Average time delay in the critical section (milliseconds).
- `lambdaRem`: Average time delay in the remainder section (milliseconds).

## How to Run

### Compilation

To compile the C++ files:

```bash
g++ Bakery-CO22BTECH11006.cpp -o bakery
g++ Filter-CO22BTECH11006.cpp -o filter
```

### Execution

To run the compiled files:

```bash
./bakery
./filter
```

## Output

### The results are saved in:

- output_filter.txt: Results for Filter Lock.
- output_bakery.txt: Results for Bakery Lock.

### The output includes:

- Request and entry times for each thread.
- Request and exit times for each thread.
- Start time, end Time and Total time of code
- Throughput values
- Average and worst-case entry times.
- Logs for mutual exclusion violations (if any).
- Fairness value - Indication of FIFO

### Contact

For any questions or further information about this project, please contact:

**Om Dave**  
**CO22BTECH11006**  
Indian Institute of Technology, Hyderabad  
Email: co22btech11006@iith.ac.in
