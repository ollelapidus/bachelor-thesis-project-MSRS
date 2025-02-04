import random

machine_count = random.randint(20, 30)
job_count = random.randint(machine_count + 1, 10 * machine_count)
class_count = random.randint(machine_count + 1, job_count)

print(machine_count)
for i in range(job_count):
    job_time = random.randint(1, 10)
    job_class = random.randint(1, class_count)
    print(job_time, job_class)