#include<bits/stdc++.h>
#include<pthread.h>
#include<sys/time.h>
#include<random>
using namespace std;

int n; //number of threads
int k; //number of times a thread enteres CS
double lambdaCS;   //avg time delays in critical section (exponential distribution)
double lambdaRem;  //avg time delays in Remainder section (exponential distribution)
exponential_distribution<double> distribution_cs;   //exponential distribution for critical section delay
exponential_distribution<double> distribution_rem; //exponential distribution for remainder section delay
double throughput;
double total_wait_time = 0;
double worst_case_wait_time = 0;
double average_wait_time;
int entry_attempts = 0;

// Global random engine, seeded with current time
std::default_random_engine generator(std::chrono::system_clock::now().time_since_epoch().count());

FILE* output;

class FilterLock {
private:
    vector<int> level;
    vector<int> victim;
public:
    FilterLock(int n) {
        level = vector<int>(n, 0);      //stores the level of ith thread, 0 initially
        victim = vector<int>(n, -1);     //stores the victim for ith level 
    }

    void lock(int id) {
        //converting 1 based thread ids into 0 based ids
        id--;
        for (int i = 1; i < n; i++) { //trying to enter ith level 
            level[id] = i;
            victim[i] = id;
            //spin while conflict exists
            while (victim[i] == id) {
                bool flag = false;
                for (int k = 0; k < n; k++) {
                    if (k == id) continue;
                    if (level[k] >= i) {
                        flag = true;
                        break;
                    }
                }
                if (!flag) break;       //stop waiting when there is no thread ahead or you are not victim 
            }
        }
    }

    void unlock(int id) {
        //converting 1 based thread ids into 0 based ids
        id--;
        level[id] = 0;
    }
};

typedef struct ComputeArgs {    //struct for thread arguments
    int thread_id;
    FilterLock *test;
} ComputeArgs;

void* testCS(void* arg) {

    ComputeArgs* args = (ComputeArgs*)arg;
    int id = args->thread_id;
    FilterLock *test = args->test;

    double reqEnterTime, actEnterTime, reqExitTime, actExitTime;

    for (int i = 0; i < k; i++) {

        // Request entry time
        double reqEnterTime = clock() / (double)CLOCKS_PER_SEC * 1e3;
        ::printf("%dth CS Entry Request at %lf by thread %d\n", i + 1, reqEnterTime, id);
        ::fprintf(output, "%dth CS Entry Request at %lf by thread %d\n", i + 1, reqEnterTime, id);

        //acquire the lock 
        test->lock(id);

        // Simulate critical section delay (pretend lock acquired)
        actEnterTime = clock() / (double)CLOCKS_PER_SEC * 1e3;
        ::printf("%dth CS Entry at %lf by thread %d\n", i + 1, actEnterTime,  id);
        ::fprintf(output, "%dth CS Entry at %lf by thread %d\n", i + 1, actEnterTime,  id);

        total_wait_time += actEnterTime - reqEnterTime;
        worst_case_wait_time = max(worst_case_wait_time, actEnterTime - reqEnterTime);    
        entry_attempts++;

        usleep(distribution_cs(generator)*1e3);  // Sleep for t1 (Critical Section delay)

        // Request exit time
        double reqExitTime = clock() / (double)CLOCKS_PER_SEC * 1e3;
        ::printf("%dth CS Exit Request at %lf by thread %d\n", i + 1, reqExitTime, id);
        ::fprintf(output, "%dth CS Exit Request at %lf by thread %d\n", i + 1, reqExitTime, id);

        //release the lock 
        test->unlock(id);

        // Simulate remainder section delay (pretend lock released)
        actExitTime = clock() / (double)CLOCKS_PER_SEC * 1e3;
        ::printf("%dth CS Exit at %lf by thread %d\n", i + 1, actExitTime, id);
        ::fprintf(output, "%dth CS Exit at %lf by thread %d\n", i + 1, actExitTime, id);
        usleep(distribution_rem(generator)*1e3);  // Sleep for t2 (Remainder Section delay)
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

    double start_time, end_time;
    start_time = clock() / (double)CLOCKS_PER_SEC * 1e3;

    printf("The start time is: %lf\n", start_time);
    fprintf(output, "The start time is: %lf\n", start_time);

    //creating n threads
    vector<pthread_t> threads(n);

    for (int i = 0; i < n; i++) {
        ComputeArgs* args = new ComputeArgs;
        args->thread_id = i + 1;
        args->test = &test;
        pthread_create(&threads[i], NULL, testCS, (void*)args);
    }
    
    for(int i = 0; i < n; i++) {
        pthread_join(threads[i], NULL);
    }

    end_time = clock() / (double)CLOCKS_PER_SEC * 1e3;

    printf("The end time is: %lf\n", end_time);
    fprintf(output, "The end time is: %lf\n\n", end_time);

    double total_time = end_time - start_time;

    printf("Total time taken: %lf ms\n", total_time);
    fprintf(output, "Total time taken: %lf ms\n", total_time);

    throughput = (k*n) / total_time;
    average_wait_time = entry_attempts > 0 ? total_wait_time / entry_attempts : 0;

    printf("Throughput: %lf\n", throughput);
    fprintf(output, "Throughput: %lf\n\n", throughput);

    printf("Average wait time: %lf ms\n", average_wait_time);
    fprintf(output, "Average wait time: %lf ms\n", average_wait_time);

    printf("Worst case wait time: %lf ms\n", worst_case_wait_time);
    fprintf(output, "Worst case wait time: %lf ms\n", worst_case_wait_time);
}