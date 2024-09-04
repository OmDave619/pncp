#include<bits/stdc++.h>
#include<pthread.h>
#include<sys/time.h>
using namespace std;

int n, k;   //size of matrix(n) and number of threads(k)
vector<vector<int>> A; //matrix A
vector<int> zeros_by_thread; //stores number of zeros counted by each thread
int zeros; //total number of zeros in matrix 
int s; //sparsity of matrix 
int rowInc;
atomic<int> C(0); // Atomic Shared counter to keep track of number of rows allocated

typedef struct ComputeArgs {    //struct for thread arguments
    int thread_id;
} ComputeArgs;

// Thread function to count number of zeros 
void* Compute_Dynamic(void* arg) {
    ComputeArgs* args = (ComputeArgs*)arg;
    int thread_id = args->thread_id;
    int local_zeros = 0;
    while (C <= n) {
        int start = C.fetch_add(rowInc); //Atomically returns the previous value of C counter and adds rowInc to it, basically gives the starting index for this to calculate
        int end = min(start + rowInc, n);

        for (int i = start; i < end; i++) {
            //computing row i of product matrix
            for (int j = 0; j < n; j++) {
                if (A[i][j] == 0) local_zeros++;
            }
        }
    }

    zeros_by_thread[thread_id] = local_zeros;

    free(args);
    pthread_exit(NULL);
}

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

    //creating k threads
    vector<pthread_t> threads(k);

    fprintf(output, "Dynamic method:\n");

    struct timespec start_time, end_time;
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    //creating k threads and passing the starting indices to each thread 
    for (int i = 0; i < k; i++) {
        ComputeArgs* args = (ComputeArgs*)malloc(sizeof(ComputeArgs));
        args->thread_id = i;
        pthread_create(&threads[i], NULL, Compute_Dynamic, (void*)args);
    }

    //joining all threads
    for (int i = 0; i < k; i++) {
        pthread_join(threads[i], NULL);
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);

    double chunk_time = (end_time.tv_sec - start_time.tv_sec) * 1e3 + (end_time.tv_nsec - start_time.tv_nsec) / 1e6;
    fprintf(output, "\nTotal time taken in Dynamic method: %f milliseconds\n", (chunk_time));

    int total_zeros = 0;
    for (int i = 0; i < k; i++) {
        total_zeros += zeros_by_thread[i];
    }

    fprintf(output, "Total Number of zero-valued elements in the matrix: %d\n", total_zeros);

    for (int i = 0; i < k; i++) {
        fprintf(output, "Number of zero-valued elements counted by thread%d: %d\n", i + 1, zeros_by_thread[i]);
    }

    double sparsity = 100 *(double)total_zeros / (n * n);
    cout << chunk_time << "ms " << sparsity << " " << s << "\n";

}




