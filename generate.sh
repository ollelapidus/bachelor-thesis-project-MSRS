#!/bin/bash

# List of Python scripts and their labels
declare -A script_labels=(
    ["generate_uniform_test.py"]="uniform"
)

# Number of times each script should run
N=5

# Seed for reproducible random numbers
SEED=42

# Function to generate a deterministic random filename
generate_seeded_name() {
    local label=$1
    local index=$2
    local seed=$SEED
    # Use awk to generate a deterministic random number based on the seed and index
    local random_part=$(awk -v seed=$((seed + index)) 'BEGIN { srand(seed); printf("%d", rand() * 1000000) }')
    echo "${label}_${random_part}"
}

# Iterate over each Python script
for script in "${!script_labels[@]}"; do
    label=${script_labels[$script]}
    echo "Running $script ($label) $N times with seed $SEED..."
    for ((i=1; i<=N; i++)); do
        random_name=$(generate_seeded_name "$label" "$i").txt
        python3 "utils/$script" --seed "$SEED" > "tests/$random_name"
        echo "Output saved to tests/$random_name"
    done
done

echo "All scripts executed."
