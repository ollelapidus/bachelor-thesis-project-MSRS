import sys
import random

random.seed(123)

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

class_time = {c : sum(job_time[i] for i in class2ids[c]) for c in classes}
T_low = max(class_time.values())
T_high = sum(job_time)

result = (1e18, [])

for iter in range(1000):
    random.shuffle(classes)
    for i in range(200):
        T = (T_low + T_high) / 2
        cur = 0
        closed = 0
        for c in classes:
            if cur + class_time[c] > T:
                cur = class_time[c]
                closed += 1
            else:
                cur += class_time[c]
        if closed < m:
            T_high = T
        else:
            T_low = T
    T = T_high
    result = min(result, (T, [i for i in classes]))

T, classes = result

## Generate assignments
time_assign = [None] * n
machine_assign = [None] * n

machine_id = 0
time = 0
for c in classes:
    if time + class_time[c] > T:
        machine_id += 1
        time = 0
    
    for id in class2ids[c]:
        machine_assign[id] = machine_id
        time_assign[id] = time
        time += job_time[id]


# Save data to file
if "--write" in sys.argv:
    with open("temp.txt", "w") as f:
        f.write(f"{n} {m}\n")  # First line: n and m
        for i in range(n):
            f.write(f"{time_assign[i]} {machine_assign[i]} {job_time[i]} {job_class[i]}\n")
    f.close()