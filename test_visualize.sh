#!/bin/bash

# Run first Python script and save output to temp.txt
echo "Running algo"
python3 algos/5_over_3.py < tests/sample2.txt --write


# Run second Python script with temp.txt as input
echo "Running vis"
python3 utils/visualize_by_time_machine.py

# Remove temp file
rm temp.txt