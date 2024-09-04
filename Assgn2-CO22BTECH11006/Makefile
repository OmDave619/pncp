# Compiler
CC = g++

# Compiler flags
CFLAGS = -fopenmp -pthread

# Executable names
files = chunk-omp mixed-omp dynamic-omp mixedchunk-omp chunk mixed dynamic mixedchunk

# Source files
CHUNK_OMP_SRC = Assgn2-Chunk-OpenMP-CO22BTECH11006.cpp
MIXED_OMP_SRC = Assgn2-Mixed-OpenMP-CO22BTECH11006.cpp
DYNAMIC_OMP_SRC = Assgn2-Dynamic-OpenMP-CO22BTECH11006.cpp
MIXEDCHUNK_OMP_SRC = Assgn2-Mixed-Chunk-OpenMP-CO22BTECH11006.cpp

CHUNK_PTHREAD_SRC = Assgn2-Chunk-PThreads-CO22BTECH11006.cpp
MIXED_PTHREAD_SRC = Assgn2-Mixed-PThreads-CO22BTECH11006.cpp
DYNAMIC_PTHREAD_SRC = Assgn2-Dynamic-PThreads-CO22BTECH11006.cpp
MIXEDCHUNK_PTHREAD_SRC = Assgn2-Mixed-Chunk-PThreads-CO22BTECH11006.cpp

# Targets and corresponding source files
all: $(files)

chunk-omp: $(CHUNK_OMP_SRC)
	$(CC) $(CFLAGS) -o $@ $<

mixed-omp: $(MIXED_OMP_SRC)
	$(CC) $(CFLAGS) -o $@ $<

dynamic-omp: $(DYNAMIC_OMP_SRC)
	$(CC) $(CFLAGS) -o $@ $<

mixedchunk-omp: $(MIXEDCHUNK_OMP_SRC)
	$(CC) $(CFLAGS) -o $@ $<

chunk: $(CHUNK_PTHREAD_SRC)
	$(CC) $(CFLAGS) -o $@ $<

mixed: $(MIXED_PTHREAD_SRC)
	$(CC) $(CFLAGS) -o $@ $<

dynamic: $(DYNAMIC_PTHREAD_SRC)
	$(CC) $(CFLAGS) -o $@ $<

mixedchunk: $(MIXEDCHUNK_PTHREAD_SRC)
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(files)
