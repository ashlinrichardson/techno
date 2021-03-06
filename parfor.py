''' evaluate function in parallel, collecting the results'''
def parfor(my_function, my_inputs):
    import multiprocessing as mp
    pool = mp.Pool(mp.cpu_count())
    result = pool.map(my_function, my_inputs)
    return(result)