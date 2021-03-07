''' evaluate function in parallel, collecting the results'''
def parfor(my_function, my_inputs):
    import multiprocessing as mp
    pool = mp.Pool(mp.cpu_count())
    result = pool.map(my_function, my_inputs)
    return(result)

    # for i, _ in enumerate(p.imap_unordered(do_work, xrange(num_tasks)), 1):
    #    sys.stderr.write('\rdone {0:%}'.format(i/num_tasks))