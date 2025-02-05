import random
import numpy as np

import sys

random.seed(sys.argv[-1])
np.random.seed(random.randint(0, 123456789))

machine_count = random.randint(10, 30)
T = random.randint(5, 100)
average_job_time = random.randint(5, T)
ans = [[-1]*T for i in range(machine_count)]

class_global = [set() for i in range(T)]

def mex(s):
    for i in range(1, machine_count * T + 2):
        if i not in s:
            return i
        
remain = [(i, j) for i in range(machine_count) for j in range(T)]

jobs = []

while remain:
    i, j = random.choice(remain)
    
    l, = np.random.poisson(average_job_time-1, 1) + 1
    
    l = min(l, T - j)
    cg = set()
    for k in range(j, j+l):
        if ans[i][k] != -1:
            l = k-j
            break
        cg = cg.union(class_global[k])
    
    c = mex(cg)
    jobs.append((l, c))

    for k in range(j, j+l):
        ans[i][k] = c
        class_global[k].add(c)
        remain.remove((i, k))

print(machine_count)
for job_time, job_class in jobs:
    print(job_time, job_class)