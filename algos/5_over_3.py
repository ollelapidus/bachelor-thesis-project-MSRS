import sys


## Read input ##
job_class = [] # [i] --> class of i:th job
job_time = [] # [i] --> duration of i:th job
class2ids = {} # [c] --> list of id:s of jobs in class c

data = sys.stdin.readlines()
m = int(data[0]) # Number of machines
n = 0 # Number of jobs
for id, line in enumerate(data[1:]):
    line = line.strip()
    if line == "":
        break
    t, c = [int(i) for i in line.split()]
    job_time.append(t)
    job_class.append(c)
    n += 1

    if c not in class2ids.keys():
        class2ids[c] = []
    
    class2ids[c].append(id)

classes = list(class2ids.keys())


## Algorithm begins ##

# Lower bound for optimal solution
T = max(
    1/m * sum(job_time),
    max(
        [sum([job_time[x] for x in class2ids[c]]) for c in classes]
    ),
    sum(sorted(job_time)[m-1:m+1])
)

print(f"Lower bound for optimal solution: {T}")

# Scheduling lists on each machine. 
from_front = [[] for i in range(m)] # Jobs are either schedules starting from 0 forwards,
from_back = [[] for i in range(m)] # or from 5/3 backwards.

cb = set() # Classes with one big job
for c in classes:
    for id in class2ids[c]:
        if 2 * job_time[id] > T:
            cb.add(c)
c_2 = set() # Classses with processing time > 2/3, with no big job
for c in classes:
    processing_time = sum([job_time[id] for id in class2ids[c]])
    if processing_time > (2/3) * T and c not in cb:
        c_2.add(c)
c_3 = set() # All other classes
for c in classes:
    if c not in cb and c not in c_2:
        c_3.add(c)


closed_machines = set()
total_used = [0] * m
i = 0
for c in cb:
    for id in class2ids[c]:
        from_front[i].append(id)
        total_used[i] += job_time[id]
    i += 1

i = 0
for c in c_2:
    processing_time = sum([job_time[id] for id in class2ids[c]])

    if total_used[i] + processing_time <= (5/3) * T:
        for id in class2ids[c]:
            from_front[i].append(id)
            total_used[i] += job_time[id]
        closed_machines.add(i)
        i += 1
    else:
        c1 = set()
        c2 = set()
        # Target: c = c1 + c2, p(c2) <= p(c1) <= 2/3 T
        # Start with all in c2, move greedily to c1
        c1_time = 0
        c2_time = processing_time

        # Sort just to add largest first -- inefficient, can be improved
        class2ids[c] = sorted(class2ids[c], 
                              key = lambda id: job_time[id],
                              reverse=True
                              )

        for id in class2ids[c]:
            if c1_time <= (2/3) * T and c2_time <= (2/3) * T:
                c2.add(id)
            else:
                c1.add(id)
                c1_time += job_time[id]
                c2_time -= job_time[id]
        if c1_time < processing_time - c1_time:
            c1, c2 = c2, c1
        # Target reached!

        for id in c1:
            from_back[i].append(id)
            total_used[i] += job_time[id]
        
        closed_machines.add(i)
        i += 1
        for id in c2:
            from_front[i].insert(0, id) # inefficient, can be improved
            total_used[i] += job_time[id]
        if total_used[i] > T:
            closed_machines.add(i)
            i += 1

for c in c_3:
    for id in class2ids[c]:
        from_front[i].append(id)
        total_used[i] += job_time[id]

        if total_used[i] >= T:
            closed_machines.add(i)
            i += 1

for i in range(m):
    print(from_front[i], from_back[i])
    