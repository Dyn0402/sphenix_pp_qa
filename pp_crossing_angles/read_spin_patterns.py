#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 31 2:26 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/read_spin_patterns.py

@author: Dylan Neff, Dylan
"""

import subprocess

import numpy as np
import matplotlib.pyplot as plt


def main():
    """
    Read spin database and write spin patterns to file with run number and pattern.
    :return:
    """
    # Database connection details
    db_name = 'spinDB'
    spin_patterns = read_spin_patterns(db_name)

    # Write spin patterns to csv
    with open('spin_patterns.csv', 'w') as file:
        file.write(spin_patterns)

    print('donzo')


def read_spin_patterns(db_name):
    """
    Read spin patterns from spin database.
    :param db_name: Name of database to connect to.
    :return: List of tuples with run number and spin pattern.
    """
    # SQL query to get column information
    query = """
    SELECT runnumber, spinpatternblue, spinpatternyellow
    FROM spin;
    """

    # Command to execute via psql
    psql_command = [
        'psql',
        '-d', db_name,
        '-c', query
    ]

    try:
        # Execute the psql command and capture output
        result = subprocess.run(psql_command, capture_output=True, text=True, check=True)

        # return the result (the output of the SQL query)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error retrieving table info: {e}")


if __name__ == '__main__':
    main()
