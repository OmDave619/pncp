#include<bits/stdc++.h>
#include<pthread.h>
#include<sys/time.h>
#include<omp.h>
using namespace std;

int n, k;   //size of matrix(n) and number of threads(k)
vector<vector<int>> A; //matrix A
vector<int> zeros_by_thread; //stores number of zeros counted by each thread
int zeros; //total number of zeros in matrix 
int s; //sparsity of matrix 
int rowInc;
atomic<int> C(0); // Atomic Shared counter to keep track of number of rows allocated

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

    int total_zeros = 0;

    fprintf(output, "Dynamic method:\n");

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    #pragma omp parallel num_threads(k)
    {
        int id = omp_get_thread_num();

    #pragma omp for schedule(dynamic,1) reduction(+:total_zeros)
        for (int i = 0; i < n; i++) {
            // if(id==1) printf("Thread %d processing row %d\n", id, i);
            for (int j = 0; j < n; j++) {
                if (A[i][j] == 0) {
                    total_zeros++;
                }
            }
        }
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double chunk_time = (end_time.tv_sec - start_time.tv_sec) * 1e3 + (end_time.tv_nsec - start_time.tv_nsec) / 1e6;
    fprintf(output, "\nTotal time taken in Dynamic method: %f milliseconds\n", (chunk_time));


    fprintf(output, "Total Number of zero-valued elements in the matrix: %d\n", total_zeros);

    for (int i = 0; i < k; i++) {
        fprintf(output, "Number of zero-valued elements counted by thread%d: %d\n", i + 1, zeros_by_thread[i]);
    }

    double sparsity = 100 * (double)total_zeros / (n * n);
    cout << chunk_time << "ms " << sparsity << " " << s << "\n";

}




