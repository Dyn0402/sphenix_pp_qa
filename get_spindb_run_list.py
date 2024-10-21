#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 21 4:14 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/get_spindb_run_list.py

@author: Dylan Neff, Dylan
"""

import subprocess


def main():
    # Database connection details
    db_name = 'spinDB'

    # Read and write run numbers to CSV
    read_run_numbers(db_name, 'runnumbers.csv')

    print('donzo')


def read_run_numbers(db_name, output_file):
    # SQL query to get all runnumber values
    query = "SELECT runnumber FROM spin;"

    # Command to execute via psql
    psql_command = [
        'psql',
        '-d', db_name,
        '-c', query
    ]

    try:
        # Execute the psql command and capture output
        result = subprocess.run(psql_command, capture_output=True, text=True, check=True)

        # Extract the run numbers from the result and write to a CSV file
        run_numbers = result.stdout.splitlines()[2:-2]  # Skip header and footer from psql output

        # Write to the CSV file
        with open(output_file, 'w') as f:
            f.write('runnumber\n')  # Write CSV header
            for runnumber in run_numbers:
                f.write(f"{runnumber.strip()}\n")

    except subprocess.CalledProcessError as e:
        print(f"Error retrieving run numbers: {e}")


if __name__ == '__main__':
    main()
