#include <bits/stdc++.h>
#include <pthread.h>
#include <sys/time.h>
#include <random>
#include <chrono>
#include <atomic>

using namespace std;

int n; // number of threads
int k; // number of times a thread enters CS
double lambdaCS;   // avg time delays in critical section (exponential distribution)
double lambdaRem;  // avg time delays in Remainder section (exponential distribution)
exponential_distribution<double> distribution_cs;   // exponential distribution for critical section delay
exponential_distribution<double> distribution_rem;  // exponential distribution for remainder section delay
double throughput;
double total_wait_time = 0;
double worst_case_wait_time = 0;
double average_wait_time;
int entry_attempts = 0;

// Global variables for tracking FIFO order
vector<int> request_order;
vector<int> entry_order;
int in_order_entries = 0;
// Mutex for synchronizing access to request_order and entry_order
pthread_mutex_t order_mutex;

// Global random engine, seeded with current time
default_random_engine generator(chrono::system_clock::now().time_since_epoch().count());

FILE* output;

// Atomic counter for detecting mutual exclusion violations
atomic<int> cs_counter(0);

// Global start time
chrono::high_resolution_clock::time_point start_time;

class FilterLock {
private:
    vector<atomic<int>> level;
    vector<atomic<int>> victim;
public:
    FilterLock(int n) {
        level = vector<atomic<int>>(n);   
        victim = vector<atomic<int>>(n);  
        for(int i = 0; i < n; i++) { 
            level[i].store(0); //stores the level of each thread, 0 initially
            victim[i].store(-1); //stores victim for each level 
        }
    }

    void lock(int id) {
        // converting 1-based thread IDs into 0-based IDs
        id--;
        for (int i = 1; i < n; i++) { // trying to enter level i
            level[id].store(i, memory_order_relaxed);
            victim[i].store(id, memory_order_relaxed);
            // spin while conflict exists
            while (true) {
                bool conflict = false;
                for (int k = 0; k < n; k++) {
                    if (k == id) continue;
                    if (level[k].load(memory_order_acquire) >= i) {
                        conflict = true;
                        break;
                    }
                }
                if (victim[i].load(memory_order_acquire) != id || !conflict) {
                    break;
                }
                // Else, spin
            }
        }
    }

    void unlock(int id) {
        // converting 1-based thread IDs into 0-based IDs
        id--;
        level[id].store(0, memory_order_release);
    }
};

typedef struct ComputeArgs {    // struct for thread arguments
    int thread_id;
    FilterLock* test;
} ComputeArgs;

void* testCS(void* arg) {
    ComputeArgs* args = (ComputeArgs*)arg;
    int id = args->thread_id;
    FilterLock* test = args->test;

    for (int i = 0; i < k; i++) {
        // Request entry time
        auto reqEnterTime = chrono::high_resolution_clock::now();
        double reqEnterTime_sec = chrono::duration<double>(reqEnterTime - start_time).count();
        printf("%dth CS Entry Request at %lf by thread %d\n", i + 1, reqEnterTime_sec, id);
        fprintf(output, "%dth CS Entry Request at %lf by thread %d\n", i + 1, reqEnterTime_sec, id);

        // Record the request order
        pthread_mutex_lock(&order_mutex);
        request_order.push_back(id);
        pthread_mutex_unlock(&order_mutex);

        // Acquire the lock 
        test->lock(id);

        // Record the entry order
        pthread_mutex_lock(&order_mutex);
        entry_order.push_back(id);
        pthread_mutex_unlock(&order_mutex);

        // Actual entry time
        auto actEnterTime = chrono::high_resolution_clock::now();
        double actEnterTime_sec = chrono::duration<double>(actEnterTime - start_time).count();
        printf("%dth CS Entry at %lf by thread %d\n", i + 1, actEnterTime_sec, id);
        fprintf(output, "%dth CS Entry at %lf by thread %d\n", i + 1, actEnterTime_sec, id);

        total_wait_time += actEnterTime_sec - reqEnterTime_sec;
        worst_case_wait_time = max(worst_case_wait_time, actEnterTime_sec - reqEnterTime_sec);
        entry_attempts++;

        // Increment cs_counter to detect mutual exclusion violations
        int cs_count = cs_counter.fetch_add(1);
        if (cs_count > 0) {
            printf("Mutual exclusion violated by thread %d\n", id);
            fprintf(output, "Mutual exclusion violated by thread %d\n", id);
        }

        usleep(distribution_cs(generator) * 1e3);  // Sleep for t1 (Critical Section delay)

        // Decrement cs_counter
        cs_counter.fetch_sub(1);

        // Request exit time
        auto reqExitTime = chrono::high_resolution_clock::now();
        double reqExitTime_sec = chrono::duration<double>(reqExitTime - start_time).count();
        printf("%dth CS Exit Request at %lf by thread %d\n", i + 1, reqExitTime_sec, id);
        fprintf(output, "%dth CS Exit Request at %lf by thread %d\n", i + 1, reqExitTime_sec, id);

        // Release the lock 
        test->unlock(id);

        // Actual exit time
        auto actExitTime = chrono::high_resolution_clock::now();
        double actExitTime_sec = chrono::duration<double>(actExitTime - start_time).count();
        printf("%dth CS Exit at %lf by thread %d\n", i + 1, actExitTime_sec, id);
        fprintf(output, "%dth CS Exit at %lf by thread %d\n", i + 1, actExitTime_sec, id);

        usleep(distribution_rem(generator) * 1e3);  // Sleep for t2 (Remainder Section delay)
    }

    pthread_exit(NULL);
}

int main() {
    FILE* input = fopen("./input.txt", "r");
    if (!input) {
        cout << "Input File not found\n";
        return 1;
    }
    fscanf(input, "%d %d %lf %lf", &n, &k, &lambdaCS, &lambdaRem);

    distribution_cs = exponential_distribution<double>(1 / lambdaCS);
    distribution_rem = exponential_distribution<double>(1 / lambdaRem);

    output = fopen("./output_filter.txt", "w");
    if (output == NULL) {
        cout << "Output file not found" << endl;
        return 1;
    }

    printf("n = %d, k = %d, lambdaCS = %lf, lambdaRem = %lf\n", n, k, lambdaCS, lambdaRem);
    fprintf(output, "n = %d, k = %d, lambdaCS = %lf, lambdaRem = %lf\n", n, k, lambdaCS, lambdaRem);

    FilterLock test(n);

    // Start time
    start_time = chrono::high_resolution_clock::now();

    // Creating n threads
    vector<pthread_t> threads(n);

    for (int i = 0; i < n; i++) {
        ComputeArgs* args = new ComputeArgs;
        args->thread_id = i + 1;
        args->test = &test;
        pthread_create(&threads[i], NULL, testCS, (void*)args);
    }

    for (int i = 0; i < n; i++) {
        pthread_join(threads[i], NULL);
    }

    auto end_time = chrono::high_resolution_clock::now();

    double start_time_sec = chrono::duration<double>(start_time - start_time).count();
    double end_time_sec = chrono::duration<double>(end_time - start_time).count();

    printf("The start time is: %lf\n", start_time_sec);
    fprintf(output, "The start time is: %lf\n", start_time_sec);

    printf("The end time is: %lf\n", end_time_sec);
    fprintf(output, "The end time is: %lf\n\n", end_time_sec);

    double total_time = chrono::duration<double>(end_time - start_time).count();

    printf("Total time taken: %lf seconds\n", total_time);
    fprintf(output, "Total time taken: %lf seconds\n", total_time);

    throughput = (k * n) / total_time;
    average_wait_time = entry_attempts > 0 ? total_wait_time / entry_attempts : 0;

    printf("Throughput: %lf operations per second\n", throughput);
    fprintf(output, "Throughput: %lf operations per second\n\n", throughput);

    printf("Average wait time: %lf seconds\n", average_wait_time);
    fprintf(output, "Average wait time: %lf seconds\n", average_wait_time);

    printf("Worst case wait time: %lf seconds\n", worst_case_wait_time);
    fprintf(output, "Worst case wait time: %lf seconds\n", worst_case_wait_time);

    // Verify FIFO order
    bool fifo_order = true;
    if (request_order.size() != entry_order.size()) {
        fifo_order = false;
    }
    else {
        for (int i = 0; i < request_order.size(); i++) {
            if (request_order[i] != entry_order[i]) {
                fifo_order = false;
                break;
            }
        }
    }

    if (fifo_order) {
        printf("FIFO order is maintained.\n");
        fprintf(output, "FIFO order is maintained.\n");
    }
    else {
        printf("FIFO order is NOT maintained.\n");
        fprintf(output, "FIFO order is NOT maintained.\n");
    }
    // // Calculate fairness score
    // double fairness_score = 0.0;
    // if (request_order.size() == entry_order.size()) {
    //     for (int i = 0; i < request_order.size(); i++) {
    //         if (request_order[i] == entry_order[i]) {
    //             in_order_entries++;
    //         }
    //     }
    //     fairness_score = (double)in_order_entries / request_order.size();
    // }
    // printf("Fairness Score: %lf\n", fairness_score);
    // fprintf(output, "Fairness Score: %lf\n", fairness_score);
    // // Optionally, print mismatched entries for debugging
    // printf("\nDetailed Request and Entry Orders:\n");
    // fprintf(output, "\nDetailed Request and Entry Orders:\n");
    // printf("Request Order:\n");
    // fprintf(output, "Request Order:\n");
    // for (auto id : request_order) {
    //     printf("%d ", id);
    //     fprintf(output, "%d ", id);
    // }
    // printf("\nEntry Order:\n");
    // fprintf(output, "\nEntry Order:\n");
    // for (auto id : entry_order) {
    //     printf("%d ", id);
    //     fprintf(output, "%d ", id);
    // }
    // printf("\n");
    // fprintf(output, "\n");

    // Clean up
    fclose(output);
    pthread_mutex_destroy(&order_mutex);
}
