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

// Global start time
chrono::high_resolution_clock::time_point start_time;

vector<vector<double>> updateOperationTime; // Stores the update times taken by each thread
vector<vector<double>> scanOperationTime; // Stores the snapshot times taken by each thread

template <typename T>
class StampedValue {
public:
    int stamp;
    T value;
    int tid;
    // Default constructor
    StampedValue() : stamp(0), value(T()) , tid(-1)  {}

    // Parameterized constructor
    StampedValue(int ts, T v, int thread_id) : stamp(ts), value(v), tid(thread_id) {}

    //define custom comparator function 
    bool operator==(const StampedValue& other) const {
        return (stamp == other.stamp && value == other.value && tid == other.tid);
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
            a_table[i].store(StampedValue<T>(0, T(), -1));
        }
    }

    void update(int thread_id, int location, T value) {
        StampedValue<T> oldStampedValue = a_table[location].load();
        int oldstamp = oldStampedValue.stamp;
        int newstamp = oldstamp + 1;
        a_table[location].store(StampedValue<T>(newstamp, value, thread_id));
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

// Struct for log entries
struct LogEntry {
    double timestamp;
    string message;
};

// Comparator function for sorting log entries
bool compareLogEntries(const LogEntry& a, const LogEntry& b) {
    return a.timestamp < b.timestamp;
}

// Thread function for writer thread
void* writer(void* arg) {
    ComputeArgs *args = (ComputeArgs*) arg;
    int thread_id = args->thread_id;
    ObstructionFreeSnapshot<int>* snap = args->snap;

    // Local log storage
    vector<LogEntry>* logs = new vector<LogEntry>();

    while(!term) {
        int v = 1 + (rand() % 101);
        int loc = rand()%M;
        auto current_time = chrono::high_resolution_clock::now();
        double current_time_sec = chrono::duration<double>(current_time- start_time).count();

        snap->update(thread_id, loc, v);

        auto end_time  = chrono::high_resolution_clock::now();
        double end_time_sec = chrono::duration<double>(end_time- start_time).count();
        double time_taken = (end_time_sec - current_time_sec) * 1e6; // Convert to microseconds

        updateOperationTime[thread_id].push_back(time_taken);

        // Create log message
        string msg = "Writer " + to_string(thread_id) + ": Value " + to_string(v) + " written to location " + to_string(loc) + " at " + to_string(current_time_sec) + "\n";
        // Create LogEntry
        LogEntry entry;
        entry.timestamp = current_time_sec;
        entry.message = msg;
        logs->push_back(entry);

        usleep(static_cast<useconds_t>(distribution_writer(generator)));
    }

    pthread_exit(logs);
}

// Thread function for snapshot thread
void *snapshot(void *arg) {
    ComputeArgs *args = (ComputeArgs*) arg;
    int thread_id = args->thread_id;
    ObstructionFreeSnapshot<int>* snap = args->snap;

    // Local log storage
    vector<LogEntry>* logs = new vector<LogEntry>();

    for(int i = 0; i < k; i++) {
        auto begin_collect = chrono::high_resolution_clock::now();

        vector<int> result = snap->scan();

        auto end_collect = chrono::high_resolution_clock::now();

        double begin_collect_sec = chrono::duration<double>(begin_collect - start_time).count();         
        double end_collect_sec = chrono::duration<double>(end_collect - start_time).count();
        double time_collect = (end_collect_sec - begin_collect_sec) * 1e6; // Convert to microseconds

        scanOperationTime[thread_id].push_back(time_collect);

        // Create log message
        stringstream ss;
        ss << "\nSnapshot " << thread_id << ": [ ";
        for (int j = 0; j < M; j++) {
            ss << result[j] << " / ";
        }
        ss << "]\nstarted at: " << to_string(begin_collect_sec) << ", ended at: " << to_string(end_collect_sec) << "\n\n";

        // Create LogEntry
        LogEntry entry;
        entry.timestamp = end_collect_sec;
        entry.message = ss.str();
        logs->push_back(entry);

        usleep(static_cast<useconds_t>(distribution_snap(generator)));
    }
    pthread_exit(logs);
}


int main() {

    FILE* input = fopen("./input.txt", "r");
    if (!input) {
        cout << "Input File not found\n";
        return 1;
    }
    fscanf(input, "%d %d %d %lf %lf %d", &nw, &ns, &M, &muw, &mus, &k);

    distribution_writer = exponential_distribution<double>(1 / muw);    //gives distribution in microseconds
    distribution_snap = exponential_distribution<double>(1 / mus);  //gives distribution in microseconds

    FILE* output = fopen("./output_ofs.txt", "w");
    if (output == NULL) {
        cout << "Output file could not be created" << endl;
        return 1;
    }

    // Initialize the start time
    start_time = chrono::high_resolution_clock::now();

    // Create the snapshot object
    ObstructionFreeSnapshot<int> OFsnapshot(M);

    // Create nw writer threads
    vector<pthread_t> writer_threads(nw);
    vector<ComputeArgs> writer_args(nw);
    updateOperationTime.resize(nw);
    for(int i = 0; i < nw; i++) {
        writer_args[i].thread_id = i;
        writer_args[i].snap = &OFsnapshot;
        pthread_create(&writer_threads[i], NULL, writer, &writer_args[i]);
    }

    // Create ns snapshot threads
    vector<pthread_t> snapshot_threads(ns);
    vector<ComputeArgs> snapshot_args(ns);
    scanOperationTime.resize(ns);
    for(int i = 0; i < ns; i++) {
        snapshot_args[i].thread_id = i;
        snapshot_args[i].snap = &OFsnapshot;
        pthread_create(&snapshot_threads[i], NULL, snapshot, &snapshot_args[i]);
    }

    // Collect logs from snapshot threads
    vector<LogEntry> all_logs;
    for(int i = 0; i < ns; i++) {
        void* status;
        pthread_join(snapshot_threads[i], &status);
        vector<LogEntry>* logs = static_cast<vector<LogEntry>*>(status);
        all_logs.insert(all_logs.end(), logs->begin(), logs->end());
        delete logs;
    }

    // Signal termination to writer threads
    term = true;

    // Collect logs from writer threads
    for(int i = 0; i < nw; i++) {
        void* status;
        pthread_join(writer_threads[i], &status);
        vector<LogEntry>* logs = static_cast<vector<LogEntry>*>(status);
        all_logs.insert(all_logs.end(), logs->begin(), logs->end());
        delete logs;
    }

    // Sort all logs by timestamp
    sort(all_logs.begin(), all_logs.end(), compareLogEntries);

    // Write all logs to output file
    for (const auto& entry : all_logs) {
        fprintf(output, "%s", entry.message.c_str());
    }

    // Compute average and worst case operation times 
    int num_updates = 0;
    double average_update_time = 0, worst_update_time = 0;
    for(int i = 0; i < nw; i++) {
        num_updates += updateOperationTime[i].size();
        average_update_time += accumulate(updateOperationTime[i].begin(), updateOperationTime[i].end(), 0.0);
        worst_update_time = max(worst_update_time, *max_element(updateOperationTime[i].begin(), updateOperationTime[i].end()));
    }

    int num_scans = 0;
    double average_scan_time = 0, worst_scan_time = 0;
    for(int i = 0; i < ns; i++) {
        num_scans += scanOperationTime[i].size();
        average_scan_time += accumulate(scanOperationTime[i].begin(), scanOperationTime[i].end(), 0.0);
        worst_scan_time = max(worst_scan_time, *max_element(scanOperationTime[i].begin(), scanOperationTime[i].end()));
    }

    double total_time = average_update_time + average_scan_time;
    average_update_time /= num_updates;
    average_scan_time /= num_scans;
    double average_time = total_time / (num_updates + num_scans);
    double worst_time = max(worst_update_time, worst_scan_time);

    // Print results to output file
    fprintf(output, "\nAverage update time: %.2lf microseconds\n", average_update_time);
    fprintf(output, "Worst update time: %.2lf microseconds\n", worst_update_time);
    fprintf(output, "Average scan time: %.2lf microseconds \n", average_scan_time);
    fprintf(output, "Worst scan time: %.2lf microseconds \n", worst_scan_time);
    fprintf(output, "Average time: %.2lf microseconds \n", average_time);
    fprintf(output, "Worst time: %.2lf microseconds \n", worst_time);

    printf("Average update time: %.2lf microseconds\n", average_update_time);
    printf("Worst update time: %.2lf microseconds\n", worst_update_time);
    printf("Average scan time: %.2lf microseconds \n", average_scan_time);
    printf("Worst scan time: %.2lf microseconds \n", worst_scan_time);
    printf("Average time: %.2lf microseconds \n", average_time);
    printf("Worst time: %.2lf microseconds \n", worst_time);

    fclose(output);
    fclose(input);
    return 0;
}
