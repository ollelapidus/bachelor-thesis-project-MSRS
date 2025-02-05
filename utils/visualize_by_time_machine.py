import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import random


# Read data from file
with open("temp.txt", "r") as f:
    lines = f.readlines()

# Parse n and m
n, m = map(int, lines[0].split())

# Initialize lists
time_assign, machine_assign, job_time, job_class = [], [], [], []

# Parse job details
for line in lines[1:]:
    t, mach, dur, cls = line.split()
    time_assign.append(float(t))
    machine_assign.append(int(mach))
    job_time.append(float(dur))
    job_class.append(int(cls))

unique_classes = list(set(job_class))
random.shuffle(unique_classes)
num_classes = len(unique_classes)

# Compute the last end time (max end time of any job)
last_end_time = max(time_assign[i] + job_time[i] for i in range(n))

# Generate colors for job classes
cmap = plt.get_cmap("gist_ncar")

class_colors = {cls: cmap(i / num_classes) for i, cls in enumerate(unique_classes)}
#class_colors = {cls: cmap(cls % 10) for cls in set(job_class)}

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
    if m < 10:
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
#handles = [patches.Patch(color=class_colors[cls], label=f"Class {cls}") for cls in class_colors]
#ax.legend(handles=handles, loc="upper right")

plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

