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

print(f"Lower bound for optimal solution: T = {T}")

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


## Generate assignments
time_assign = [None] * n
machine_assign = [None] * n
for i in range(m):
    time = 0
    for id in from_front[i]:
        machine_assign[id] = i
        time_assign[id] = time
        time += job_time[id]
    time = (3/2) * T
    for id in from_back[i]:
        machine_assign[id] = i
        time_assign[id] = time - job_time[id]
        time -= job_time[id]


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


import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


# Compute the last end time (max end time of any job)
last_end_time = max(time_assign[i] + job_time[i] for i in range(n))

# Generate colors for job classes
cmap = plt.get_cmap("tab10")
class_colors = {cls: cmap(cls % 10) for cls in set(job_class)}

fig, ax = plt.subplots(figsize=(10, 6))

# Define machine width (eliminate spacing)
machine_width = 1.0

# Plot jobs
for i in range(n):
    rect = patches.Rectangle(
        (machine_assign[i] * machine_width, time_assign[i]),  # (x, y) position
        machine_width,  # Width (full width, no spacing)
        job_time[i],  # Height
        linewidth=1,
        edgecolor='black',
        facecolor=class_colors[job_class[i]],
        alpha=0.8
    )
    ax.add_patch(rect)
    
    # Add text inside the job block
    ax.text(
        machine_assign[i] * machine_width + machine_width / 2, 
        time_assign[i] + job_time[i] / 2, 
        f"id = {i}",  # Updated text format
        ha='center', va='center', fontsize=10, color='white'
    )

# Bounding box around all jobs (from time 0 to last job end time)
bounding_rect = patches.Rectangle(
    (0, 0),  # Start from time 0
    m * machine_width,  # Total width covering all machines
    last_end_time,  # Total height from 0 to the last job end time
    linewidth=3, edgecolor='black', facecolor='none'
)
ax.add_patch(bounding_rect)

# Draw thin vertical lines between machines
for i in range(1, m):
    ax.axvline(i * machine_width, color='black', linestyle='-', linewidth=1.5)

# Add y-ticks, including last end time
yticks = list(range(0, int(last_end_time) + 5, 5))
if last_end_time not in yticks:  # Ensure last_end_time is included if it's not an integer
    yticks.append(last_end_time)
yticks = sorted(yticks)

# Labels and formatting
ax.set_xlabel("Machines")
ax.set_ylabel("Time")
ax.set_xticks(np.arange(m) * machine_width + machine_width / 2)
ax.set_xticklabels(range(m))
ax.set_yticks(yticks)
ax.set_title("Job Scheduling Visualization")
ax.invert_yaxis()  # Time flows downward
ax.set_xlim(0, m * machine_width)
ax.set_ylim(0, last_end_time)

# Add legend
handles = [patches.Patch(color=class_colors[cls], label=f"Class {cls}") for cls in class_colors]
ax.legend(handles=handles, loc="upper right")

plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()