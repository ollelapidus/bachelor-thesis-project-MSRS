#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: ./test_visualize.sh <algorithm_file.py> <test_file.txt>"
    exit 1
fi

XX=$1  # First argument (Python script to run)
YY=$2  # Second argument (Input file)

# Run first Python script and save output to temp.txt
echo "Running algo: $XX with input file $YY"
python3 "$XX" < "$YY" --write 

# Run second Python script (visualization)
echo "Running vis"
python3 utils/visualize_by_time_machine.py

# Remove temp file
rm temp.txt