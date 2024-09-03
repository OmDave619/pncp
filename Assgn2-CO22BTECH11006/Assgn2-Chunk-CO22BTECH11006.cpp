#include<bits/stdc++.h>
#include<pthread.h>
#include<iostream>
#include<sys/time.h>
#include<omp.h>
using namespace std;

int n, k;   //size of matrix(n) and number of threads(k)
vector<vector<int>> A; //matrix A
int chunk;  //size of chunks (n/k) (number of rows computed by each thread)
vector<int> zeros_by_thread; //stores number of zeros counted by each thread
int zeros; //total number of zeros in matrix 
int s; //sparsity of matrix 
int rowInc;

int main() {
    FILE* input = fopen("./input.txt", "r");
    if (!input) {
        cout << "Input File not found\n";
        return 1;
    }
    fscanf(input, "%d %d %d %d", &n, &s, &k, &rowInc);

    //resizing matrix according to sizes
    A.resize(n, vector<int>(n, 0));
    zeros_by_thread.resize(k, 0);

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            fscanf(input, "%d", &A[i][j]);
        }
    }

    FILE* output = fopen("./output.txt", "w");
    if (output == NULL) {
        cout << "Output file not found" << endl;
        return 1;
    }

    fprintf(output, "Chunk method:\n");

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    chunk = max(n / k, 2);  //using minimum chunk size as 2 other wise method would reduce to mixed
    int total_zeros = 0;

    #pragma omp parallel num_threads(k)
    {
        int id = omp_get_thread_num();
        int total_zeros_local = 0;

        #pragma omp for schedule(static,chunk)
        for(int i = 0; i < n; i++) {
            // if(id==1) printf("Thread %d processing row %d\n", id, i);  // Log the distribution
            for(int j = 0; j < n; j++) {
                if(A[i][j] == 0) {
                    total_zeros_local++;
                }
            }
        }
        zeros_by_thread[id] = total_zeros_local;
        
        #pragma omp atomic
        total_zeros += total_zeros_local;
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double chunk_time = (end_time.tv_sec - start_time.tv_sec) * 1e3 + (end_time.tv_nsec - start_time.tv_nsec) / 1e6;
    fprintf(output, "\nTotal time taken in chunk method: %f milliseconds\n", (chunk_time));

    fprintf(output, "Total Number of zero-valued elements in the matrix: %d\n", total_zeros);

    for (int i = 0; i < k; i++) {
        fprintf(output, "Number of zero-valued elements counted by thread%d: %d\n", i + 1, zeros_by_thread[i]);
    }

    double sparsity = 100 *(double)total_zeros / (n * n);
    cout << chunk_time << "ms " << sparsity << " " << s << "\n";
}




