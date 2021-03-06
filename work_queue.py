'''for running a list of terminal commands in parallel..

each worker picks up one job, completes it, picks up another until queue is empty'''
import os
import sys
import time
import multiprocessing
from _thread import allocate_lock, start_new_thread

def err(m):
    print("Error: " + m)
    sys.exit(1)

args = sys.argv
if len(args) < 2:
    err('multicore.py:\nusage: multicore [text file: one sys cmd per line] # init one thread per cpu\nmulticore [text file: one syscmd per line] 1 # init one thread per job')

one_worker_per_job, n_workers = False, None
if len(args) > 2:
    one_worker_per_job = True if sys.argv[2] == "1" else False
    try:
        if int(sys.argv[2]) > 1:
            n_workers = int(sys.argv[2])  # workers specified
    except:
        pass

fn, ncpu = args[1], multiprocessing.cpu_count()
if not os.path.exists(fn): err('job file: ' + fn.strip() + ' not found')

task = open(fn).read().strip().split("\n")
tasks, n_task = [x.strip() for x in task], len(task)

if one_worker_per_job:
    ncpu = n_task
else:
    if n_workers and n_workers > 1:
        ncpu = n_workers

lock, p_lock = allocate_lock(), allocate_lock() # lock mechanism
threads_alive, next_j, j_max = ncpu, 0, n_task - 1

# printf with lock
def cprint(s):
    global p_lock
    p_lock.acquire()
    print(s)
    p_lock.release()

cprint("nworkers " + str(ncpu))

def threadfun(my_id):  # worker thread picks up task
    global next_j, j_max, lock, threads_alive, tasks
    job_times = []
    while True: 
        lock.acquire()
        j, next_j = next_j, next_j + 1  # pick up task idx
        lock.release()
	
        if(j > j_max):
            threads_alive -= 1  # kill thread if no work
            return

        if tasks[j].strip() == "":  # don't run empty task
            continue

        work = tasks[j].split(";")  # divide task into subtasks?
        for i in range(0, len(work)):
            cprint("worker(" + str(my_id) + "): " + work[i])
            os.popen(work[i]).read()
            cprint("\tworker(" + str(my_id) + ")")

def wait_to_finish():  # sleep a bit?
    poll_int = .01 # polling is bad, don't do too much
    while True:
        time.sleep(poll_int)
        if(threads_alive == 0):
            sys.exit(0)

for i in range(0, ncpu):
    start_new_thread(threadfun, (i, ))
wait_to_finish()
