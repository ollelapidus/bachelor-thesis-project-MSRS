import sys
import random


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

T = max(
    1/m * sum(job_time),
    max(
        [sum([job_time[x] for x in class2ids[c]]) for c in classes]
    ),
    sum(sorted(job_time)[m-1:m+1])
)

print(f"Lower bound for optimal solution: T = {T}")


## Enqueue
order = [i for i in range(n)]
random.shuffle(order)

last_placed_on_machine = [-1]*m
machine_load = [0]*m

machine_assign = [-1]*n
time_assign = [-1]*n

for i in order:
    cid = job_class[i]
    mid = 0
    for j in range(m):
        if last_placed_on_machine[j] == cid:
            mid = j
            break
        if machine_load[j] < machine_load[mid]:
            mid = j
    machine_assign[i] = mid
    time_assign[i] = machine_load[mid]
    machine_load[mid] += job_time[i]
    last_placed_on_machine[mid] = cid



## Verify possilbility
for id in range(n):
    assert (
        0 <= machine_assign[id] < m and
        0 <= time_assign[id] <= (5/3) * T - job_time[id]
    )

    for id2 in range(n):
        if id == id2: continue

        # Jobs of same class or assigned to same machine must not run at same time
        if job_class[id] == job_class[id2] or machine_assign[id] == machine_assign[id2]:
            assert (
                time_assign[id] >= time_assign[id2] + job_time[id2] or
                time_assign[id2] >= time_assign[id] + job_time[id]
            )

print("Assignment works.")
makespan = 0
for id in range(n):
    makespan = max(makespan, time_assign[id] + job_time[id])

fraction = makespan / T

print(f"Makspan: {makespan}")
print(f"Fraction: {fraction:.3f}")
print(f"Percentage over: {(fraction-1)*100:.2f}%")
# Save data to file
if "--write" in sys.argv:
    with open("temp.txt", "w") as f:
        f.write(f"{n} {m}\n")  # First line: n and m
        for i in range(n):
            f.write(f"{time_assign[i]} {machine_assign[i]} {job_time[i]} {job_class[i]}\n")
    f.close()