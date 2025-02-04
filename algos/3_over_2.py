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

## Simplify problem instance by combining jobs ##

combined_jobs = []
combined_jobs_time = []
class2combined = {}
class_time = []

c_h = set()
c_3_4 = set()
c_b = set()
c_1_2 = set()
c_small = set()

combined_jobs_count = 0
def add_combined_jobs(combo):
    global combined_jobs_count
    combined_jobs.append(combo)
    combined_jobs_time.append(
        sum(job_time[id] for id in combo)
    )
    combined_jobs_count += 1
    return combined_jobs_count - 1 ## pointer to added

def rotate_load(machine_id):
    from_front[machine_id], from_back[machine_id] = from_back[machine_id], from_front[machine_id]


for c in classes:
    biggest = max(job_time[id] for id in class2ids[c])
    total_time = sum(job_time[id] for id in class2ids[c])
    class_time.append(total_time)

    if biggest > (3/4) * T:
        combo = [id for id in class2ids[c]]
        class2combined[c] = [add_combined_jobs(combo)]
        c_h.add(c)
    
    elif total_time > (3/4) * T:
        c1 = []
        c2 = []

        c1_time = 0
        for id in class2ids[c]:
            if c1_time + job_time[id] <= (3/4) * T:
                c1.append(id)
                c1_time += job_time[id]
            else:
                c2.append(id)
        if c1_time > total_time - c1_time: # we want c1 <= c2
            c1, c2 = c2, c1
        i = add_combined_jobs(c1)
        j = add_combined_jobs(c2)
        class2combined[c] = [i, j]
        c_3_4.add(c)

    elif total_time > (1/2) * T and biggest > (1/2) * T:
        biggest_id = class2ids[c][0]
        for id in class2ids[c]:
            if job_time[id] > job_time[biggest_id]:
                biggest_id = id
        i = add_combined_jobs([id for id in class2ids[c] if id != biggest_id])
        j = add_combined_jobs([biggest_id])
        class2combined[c] = [i, j]
        c_b.add(c)

    elif total_time > (1/2) * T:
        c1 = []
        c2 = []

        c1_time = 0
        for id in class2ids[c]:
            if c1_time + job_time[id] <= (1/2) * T:
                c1.append(id)
                c1_time += job_time[id]
            else:
                c2.append(id)
        if c1_time > total_time - c1_time: # we want c1 <= c2
            c1, c2 = c2, c1
        i = add_combined_jobs(c1)
        j = add_combined_jobs(c2)
        class2combined[c] = [i, j]
        c_1_2.add(c)

    else:
        class2combined[c] = [add_combined_jobs([id for id in class2ids[c]])]
        c_small.add(c)


from_front = [[] for i in range(m)]
from_back = [[] for i in range(m)]
open_machines = [i for i in range(m-1,-1,-1)]
total_time = [0] * m

u = True
def schedule_combined_job(machine_id, combined_job_id, from_start_bool):
    global u
    for id in combined_jobs[combined_job_id]:
        assert (id != 95 or (u))
        if id == 95: u = False
        if from_start_bool:
            from_front[machine_id].append(id)
        else:
            from_back[machine_id].append(id)
    total_time[machine_id] += combined_jobs_time[combined_job_id]
    assert(total_time[machine_id] <= 3/2 * T)

## Handle large jobs ##
M_h = []
to_check_rotate = set()

while len(c_h) > 0: # Step 2
    x = c_h.pop()
    M = open_machines.pop()
    schedule_combined_job(M, class2combined[x][0], True)
    M_h.append(M)
M_h = M_h[::-1]
while len(M_h) > 0: # Step 3
    if len(c_small) == 0:
        break

    M = M_h.pop()
    while total_time[M] < T:
        if len(c_small) == 0:
            break
        cs = c_small.pop()
        schedule_combined_job(M, class2combined[cs][0], True)
    
    if total_time[M] < t:
        M_h.append(M)

while len(M_h) >= 2 and len(c_1_2) >= 1: # Step 4
    mh1 = M_h.pop()
    mh2 = M_h.pop()
    cm = c_1_2.pop()

    rotate_load(mh2)
    schedule_combined_job(mh1, class2combined[cm][0], False)
    schedule_combined_job(mh1, class2combined[cm][1], True)

if len(M_h) == 1: # Step 5
    mh = M_h.pop()
    c = None
    if len(c_3_4) > 0:
        c = c_3_4.pop()
    elif len(c_1_2) > 0:
        c = c_1_2.pop()
    if c is not None:
        i = 0
        if (1/4) * T < combined_jobs_time[class2combined[c][1]] <= (1/2) * T:
            i = 1
        schedule_combined_job(mh, class2combined[c][i], False)
        to_check_rotate.add(mh)
    
    class2combined[c] = [class2combined[c][1-i]]
    if combined_jobs_time[class2combined[c][0]] > (1/2) * T:
        c_1_2.add(c)
    else:
        c_small.add(c)

c_b_1_2 = set([c for c in c_b if class_time[c] < (3/4) * T])
c_b_3_4 = set([c for c in c_b if class_time[c] >= (3/4) * T])
while len(M_h) >= 1 and len(c_b_1_2) >= 1 and len(c_3_4) >= 1: # Step 6
    m1 = M_h.pop()
    b = c_b_1_2.pop()
    c_b.remove(b)
    c = c_3_4.pop()

    m2 = open_machines.pop()

    schedule_combined_job(m1, class2combined[c][0], False)
    schedule_combined_job(m2, class2combined[c][1], True)
    schedule_combined_job(m2, class2combined[b][0], False)
    schedule_combined_job(m2, class2combined[b][1], False)

while len(M_h) >= 2 and len(c_b_3_4) + len(c_3_4) >= 2: # Step 8
    m1 = M_h.pop()
    m2 = M_h.pop()
    c1 = c_b_3_4.pop() if len(c_b_3_4) > 0 else c_3_4.pop()
    c2 = c_b_3_4.pop() if len(c_b_3_4) > 0 else c_3_4.pop()

    if c1 in c_b:
        c_b.remove(c1)
    if c2 in c_b:
        c_b.remove(c2)

    rotate_load(m2)
    schedule_combined_job(m1, class2combined[c1][0], False)
    schedule_combined_job(m2, class2combined[c2][0], True)

    m3 = open_machines.pop()
    schedule_combined_job(m3, class2combined[c1][1], True)
    schedule_combined_job(m3, class2combined[c2][1], False)


while len(open_machines) > 0:
    M = open_machines.pop()
    if total_time[M] == 0:
        open_machines.append(M)
        break


## Algorithm_no_huge ##
c_3_4 = c_3_4.union(c_b_3_4)
c_1_2 = c_1_2.union(c_b_1_2)
while len(c_1_2) >= 2:
    c1 = c_1_2.pop()
    c2 = c_1_2.pop()
    M = open_machines.pop()
    schedule_combined_job(M, class2combined[c1][0], True)
    schedule_combined_job(M, class2combined[c1][1], True)
    schedule_combined_job(M, class2combined[c2][0], False)
    schedule_combined_job(M, class2combined[c2][1], False)


while len(c_3_4) >= 4:
    c1 = c_3_4.pop()
    c2 = c_3_4.pop()
    c3 = c_3_4.pop()
    c4 = c_3_4.pop()

    M1 = open_machines.pop()
    M2 = open_machines.pop()
    M3 = open_machines.pop()

    schedule_combined_job(M1, class2combined[c1][1], True)
    schedule_combined_job(M1, class2combined[c2][1], False)

    schedule_combined_job(M2, class2combined[c1][0], False)
    schedule_combined_job(M2, class2combined[c3][0], True)
    schedule_combined_job(M2, class2combined[c3][1], True)

    schedule_combined_job(M3, class2combined[c2][0], True)
    schedule_combined_job(M3, class2combined[c4][0], False)
    schedule_combined_job(M3, class2combined[c4][1], False)

if len(c_1_2) == 1 and len(c_3_4) >= 2:
    c1 = c_3_4.pop()
    c2 = c_3_4.pop()
    c3 = c_1_2.pop()

    M1 = open_machines.pop()
    M2 = open_machines.pop()

    schedule_combined_job(M1, class2combined[c1][1], False)
    schedule_combined_job(M1, class2combined[c3][0], True)

    schedule_combined_job(M2, class2combined[c1][0], True)
    schedule_combined_job(M2, class2combined[c2][0], False)
    schedule_combined_job(M2, class2combined[c2][1], False)


if len(c_1_2) + len(c_3_4) == 1:
    c = (c_1_2.union(c_3_4)).pop()
    M = open_machines.pop()
    for id in class2combined[c]:
        schedule_combined_job(M, id, True)
    open_machines.append(M)

elif len(c_1_2) == 1 and len(c_3_4) == 1:
    c1 = c_3_4.pop()
    c2 = c_1_2.pop()

    M1 = open_machines.pop()
    M2 = open_machines.pop()

    i,j = class2combined[c1]
    k, = class2combined[c2]

    if combined_jobs_time[i] + combined_jobs_time[j] + combined_jobs_time[k] <= (3/2) * T:
        schedule_combined_job(M1, i, True)
        schedule_combined_job(M1, j, True)
        schedule_combined_job(M1, k, True)
    else:
        schedule_combined_job(M1, i, True)
        schedule_combined_job(M1, k, True)
        schedule_combined_job(M2, j, False)
    open_machines.append(M2)

elif len(c_1_2) == 0 and len(c_3_4) == 2:
    c1 = c_3_4.pop()
    c2 = c_3_4.pop()
    i,j = class2combined[c1]
    k,l = class2combined[c2]

    M1 = open_machines.pop()
    M2 = open_machines.pop()

    if combined_jobs_time[j] + combined_jobs_time[l] <= T:
        schedule_combined_job(M1, k, True)
        schedule_combined_job(M1, l, True)
        schedule_combined_job(M1, j, False)
        schedule_combined_job(M2, i, True)
    else:
        schedule_combined_job(M1, j, True)
        schedule_combined_job(M2, i, False)
        schedule_combined_job(M1, l, False)
        schedule_combined_job(M2, k, True)
    open_machines.append(M2)

elif len(c_3_4) == 3:
    c1 = c_3_4.pop()
    c2 = c_3_4.pop()
    c3 = c_3_4.pop()

    if combined_jobs_time[class2combined[c2][1]] < combined_jobs_time[class2combined[c1][1]]:
        c1, c2 = c2, c1
    if combined_jobs_time[class2combined[c3][1]] < combined_jobs_time[class2combined[c1][1]]:
        c1, c3 = c3, c1
    
    M1 = open_machines.pop()
    M2 = open_machines.pop()
    # Now, c1 has smallest large job
    if combined_jobs_time[class2combined[c1][1]] < (1/2) * T:
        schedule_combined_job(M1, class2combined[c1][1], True)
        schedule_combined_job(M1, class2combined[c2][0], True)
        schedule_combined_job(M1, class2combined[c2][1], True)

        schedule_combined_job(M2, class2combined[c1][0], False)
        schedule_combined_job(M2, class2combined[c3][0], True)
        schedule_combined_job(M2, class2combined[c3][1], True)
    
    else:
        schedule_combined_job(M1, class2combined[c1][1], True)
        schedule_combined_job(M1, class2combined[c2][1], False)

        if (combined_jobs_time[class2combined[c1][0]] + 
            combined_jobs_time[class2combined[c2][0]] +
            combined_jobs_time[class2combined[c3][0]] +
            combined_jobs_time[class2combined[c3][1]]) < (3/2) * T:
            schedule_combined_job(M2, class2combined[c1][0], False)
            schedule_combined_job(M2, class2combined[c2][0], True)
            schedule_combined_job(M2, class2combined[c3][0], True)
            schedule_combined_job(M2, class2combined[c3][1], True)
        else:
            schedule_combined_job(M2, class2combined[c1][0], False)

            schedule_combined_job(M2, class2combined[c3][0], True)
            schedule_combined_job(M2, class2combined[c3][1], True)

            M3 = open_machines.pop()
            schedule_combined_job(M3, class2combined[c2][0], True)
            open_machines.append(M3)

while len(c_small) > 0:
    c = c_small.pop()
    M = open_machines.pop()
    schedule_combined_job(M, class2combined[c][0], True)
    if total_time[M] < T:
        open_machines.append(M)

assert(len(to_check_rotate)) <= 1
if len(to_check_rotate) == 1:
    rot = to_check_rotate.pop()
    for _ in range(2):
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
        possible = True
        for id in range(n):
            possible = possible and (
                0 <= machine_assign[id] < m and
                0 <= time_assign[id] <= (3/2) * T - job_time[id]
            )

            for id2 in range(n):
                if id == id2: continue

                # Jobs of same class or assigned to same machine must not run at same time
                if job_class[id] == job_class[id2] or machine_assign[id] == machine_assign[id2]:
                    possible = possible and (
                        time_assign[id] >= time_assign[id2] + job_time[id2] or
                        time_assign[id2] >= time_assign[id] + job_time[id]
                    )
        if possible:
            break
        rotate_load(rot)

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
        0 <= time_assign[id] <= (3/2) * T - job_time[id]
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


# Save data to file
if "--write" in sys.argv:
    with open("temp.txt", "w") as f:
        f.write(f"{n} {m}\n")  # First line: n and m
        for i in range(n):
            f.write(f"{time_assign[i]} {machine_assign[i]} {job_time[i]} {job_class[i]}\n")
    f.close()
