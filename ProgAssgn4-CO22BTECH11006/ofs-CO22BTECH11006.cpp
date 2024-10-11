#include<bits/stdc++.h>
#include<pthread.h>
#include<chrono>
#include<sys/time.h>
#include<random>
#include<atomic>

using namespace std;

int nw; //writer threads
int ns; //scanner threads
double muw;  //avg time to write the value
double mus;  //avg time to take the snapshot
int M; //number of locations / Register size
int k; //number of snapshots taken by each thread

exponential_distribution<double> distribution_writer;
exponential_distribution<double> distribution_snap;

// Global random engine, seeded with current time
std::default_random_engine generator(std::chrono::system_clock::now().time_since_epoch().count());

// Termination signal for writer threads
atomic<bool> term(false);

// Mutex for writing to the log
pthread_mutex_t log_mutex = PTHREAD_MUTEX_INITIALIZER;

FILE* output;

// Global start time
chrono::high_resolution_clock::time_point start_time;

template <typename T>
class StampedValue {
public:
    int stamp;
    T value;
    // Default constructor
    StampedValue() : stamp(0), value(T()) {}

    // Parameterized constructor
    StampedValue(int ts, T v) : stamp(ts), value(v) {}

    //define custom comparator function 
    bool operator==(const StampedValue& other) const {
        return (stamp == other.stamp && value == other.value);
    }
};

template <typename T>
class ObstructionFreeSnapshot {
private:
    vector<atomic<StampedValue<T>>> a_table; // Array of atomic MRMW registers

    vector<StampedValue<T>> collect() {
        vector<StampedValue<T>> copy(a_table.size());
        for (int i = 0; i < a_table.size(); i++) {
            copy[i] = a_table[i].load();
        }
        return copy;
    }

public:
    ObstructionFreeSnapshot(int capacity) {
        a_table = vector<atomic<StampedValue<T>>>(capacity);
        for (int i = 0; i < capacity; i++) {
            a_table[i].store(StampedValue<T>(0, T()));
        }
    }

    void update(int location, T value) {
        StampedValue<T> oldStampedValue = a_table[location].load();
        long oldstamp = oldStampedValue.stamp;
        long newstamp = oldstamp + 1;
        a_table[location].store(StampedValue<T>(newstamp, value));
    }

    vector<T> scan() {
        vector<StampedValue<T>> oldCopy, newCopy;

        oldCopy = collect();

        while (true) {
            newCopy = collect();
            bool flag = true;
            for (int i = 0; i < a_table.size(); i++) {
                if (oldCopy[i] == newCopy[i]) continue;
                flag = false;
                break;
            }
            if (flag) break;     //both arrays are equal break out of while loop 
            oldCopy = newCopy;
        }
        vector<T> result(a_table.size());
        for (int i = 0; i < a_table.size(); i++) {
            result[i] = newCopy[i].value;
        }
        return result;
    }
};

typedef struct ComputeArgs {    // Struct for thread arguments
    int thread_id;
    ObstructionFreeSnapshot<int>* snap;
} ComputeArgs;

//thread function for writer thread
void* writer(void* arg) {
    ComputeArgs *args = (ComputeArgs*) arg;
    int thread_id = args->thread_id;
    ObstructionFreeSnapshot<int>* snap = args->snap;

    while(!term) {
        int v = 10 + thread_id*10;
        int loc = rand()%M;
        auto current_time = chrono::high_resolution_clock::now();
        double current_time_sec = chrono::duration<double>(current_time- start_time).count();

        snap->update(loc, v);
        
        //lock the mutex and update the log file 
        pthread_mutex_lock(&log_mutex);
        fprintf(output, "Writer %d: Value %d written to location %d at %lf\n",
                thread_id, v, loc, current_time_sec);
        pthread_mutex_unlock(&log_mutex);

        usleep(static_cast<useconds_t>(distribution_writer(generator)));
    }

    pthread_exit(NULL);
}

//thread function for snapshot thread
void *snapshot(void *arg) {
    ComputeArgs *args = (ComputeArgs*) arg;
    int thread_id = args->thread_id;
    ObstructionFreeSnapshot<int>* snap = args->snap;

    for(int i = 0; i < k; i++) {
        auto begin_collect = chrono::high_resolution_clock::now();
        
        vector<int> result = snap->scan();

        auto end_collect = chrono::high_resolution_clock::now();
        
        double begin_collect_sec = chrono::duration<double>(begin_collect - start_time).count();         
        double end_collect_sec = chrono::duration<double>(end_collect - start_time).count();
        double time_collect = end_collect_sec - begin_collect_sec;

        pthread_mutex_lock(&log_mutex);
        fprintf(output, "Snapshot %d: [ ", thread_id);
        for (int j = 0; j < M; j++) {
            fprintf(output, "%d / ", result[j]);
        }
        fprintf(output, "] collected at %lf, duration: %lf microseconds\n",
                begin_collect_sec, time_collect);
        pthread_mutex_unlock(&log_mutex);

        usleep(static_cast<useconds_t>(distribution_snap(generator)));

    }
    pthread_exit(NULL);
}

int main() {

    FILE* input = fopen("./input.txt", "r");
    if (!input) {
        cout << "Input File not found\n";
        return 1;
    }
    fscanf(input, "%d %d %d %lf %lf %d", &nw, &ns, &M, &muw, &mus, &k);

    distribution_writer = exponential_distribution<double>(1 / muw);
    distribution_snap = exponential_distribution<double>(1 / mus);

    output = fopen("./output_ofs.txt", "w");
    if (output == NULL) {
        cout << "Output file could not be created" << endl;
        return 1;
    }

    // Initialize the start time
    start_time = chrono::high_resolution_clock::now();

    // Create the snapshot object
    ObstructionFreeSnapshot<int> OFsnapshot(M);

    //create nw writer threads
    vector<pthread_t> writer_threads(nw);
    for(int i = 0; i < nw; i++) {
        ComputeArgs *args = new ComputeArgs;
        args->thread_id = i;
        args->snap = &OFsnapshot;
        pthread_create(&writer_threads[i], NULL, writer, args);
    }

    //create ns snapshot threads
    vector<pthread_t> snapshot_threads(ns);
    for(int i = 0; i < ns; i++) {
        ComputeArgs *args = new ComputeArgs;
        args->thread_id = i;
        args->snap = &OFsnapshot;
        pthread_create(&snapshot_threads[i], NULL, snapshot, args);
    }

    //join the snapshot threads
    for(int i = 0; i < ns; i++) {
        pthread_join(snapshot_threads[i], NULL);
    }

    // Signal termination to writer threads
    term = true;

    // Wait for all writer threads to finish
    for(int i = 0; i < nw; i++) {
        pthread_join(writer_threads[i], NULL);
    }

    fclose(output);
    fclose(input);
    return 0;

}





