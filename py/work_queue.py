'''for running a list of terminal commands in parallel..

each worker picks up one job, completes it, picks up another until queue is empty'''
import os
import sys
import time
import subprocess
import multiprocessing
from _thread import allocate_lock, start_new_thread

def err(m):
    print("Error: " + m)
    sys.exit(1)


class work_queue:
    def __init__(self):
        self.jobs = []

    def add(self, job):
        self.jobs.append(job)

    def clear(self):
        self.jobs = []

    # printf with lock
    def cprint(self, s):
        self.p_lock.acquire()
        print(s)
        self.p_lock.release()

    def run(self, ncpu = multiprocessing.cpu_count()):
        #print("run() queue:")
        #for job in self.jobs:
        #    print(job)
        #print("end() queue")

        n_task = len(self.jobs)
        self.lock, self.p_lock = allocate_lock(), allocate_lock() # lock mechanism
        self.threads_alive, self.next_j, self.j_max = ncpu, 0, n_task - 1

        self.cprint("nworkers " + str(ncpu))

        def threadfun(my_id):  # worker thread picks up task
            # global next_j, j_max, lock, threads_alive, jobs
            job_times = [] # fill this in later
            while True:
                self.lock.acquire()
                j, self.next_j = self.next_j, self.next_j + 1  # pick up task idx
                self.lock.release()

                if(j > self.j_max):
                    self.threads_alive -= 1  # kill thread if no work
                    return

                if self.jobs[j].strip() == "":  # don't run empty task
                    continue

                work = self.jobs[j].split(";")  # divide task into subtasks?
                print("work", work)
                for i in range(0, len(work)):
                    self.cprint("worker(" + str(my_id) + "): " + work[i])
                    #pp = subprocess.Popen(work[i].split())
                    #pp.wait()
                    result = os.popen(work[i]).read()
                    # open(str(my_id) + "_" + str(j) + ".txt", "wb").write(result.encode())
                    #a = os.system(work[i])
                    #self.cprint(a)
                    self.cprint("\tworker(" + str(my_id) + ")")

        def wait_to_finish():  # sleep a bit?
            poll_int = .01 # polling is bad, don't do too much
            while True:
                time.sleep(poll_int)
                if(self.threads_alive == 0):
                    return

        for i in range(0, ncpu):
            start_new_thread(threadfun, (i, ))

        wait_to_finish()
        self.clear()


if __name__ == "__main__":
    args = sys.argv

    if len(args) < 2:
        err('multicore.py:\nusage:\n\tmulticore [text file: one sys cmd per line] # init one thread per cpu' +
            '\n\tmulticore [text file: one syscmd per line] 1 # init one thread per job' +
            '\n\tmulticore [text file: one syscmd per line] 4 # init 4 threads')

    one_worker_per_job, n_workers, fn = False, None, args[1]

    if len(args) > 2:
        one_worker_per_job = True if args[2] == "1" else False
        try:
            if int(args[2]) > 1:
                n_workers = int(args[2])  # workers specified
        except:
            pass

    if not os.path.exists(fn):
        err('job file: ' + fn.strip() + ' not found')

    tasks = open(fn).read().strip().split("\n")
    jobs, n_task = [x.strip() for x in tasks], len(tasks)

    if one_worker_per_job:
        ncpu = n_task
    else:
        if n_workers and n_workers > 1:
            ncpu = n_workers

    w_q = work_queue()
    w_q.jobs = tasks # generally would use add() for each job
    w_q.run()