#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 21 12:53 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/read_spindb_col_names.py

@author: Dylan Neff, Dylan
"""

import subprocess


def main():
    # Database connection details
    db_name = 'spinDB'

    get_table_info(db_name)

    print('donzo')


def get_table_info(db_name):
    # SQL query to get column information
    query = """
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_name = 'spin';
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

        # Print the result (the output of the SQL query)
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Error retrieving table info: {e}")


if __name__ == '__main__':
    main()
