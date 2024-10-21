#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 21 12:44 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/add_spindb_crossing_columns.py

@author: Dylan Neff, Dylan
"""

import subprocess


def main():
    # Database connection details
    db_name = 'spinDB'

    # Add columns to the table
    add_columns(db_name)

    print('donzo')


def add_columns(db_name):
    # List of columns to be added along with their types
    columns_to_add = [
        ('crossingangle', 'REAL'),
        ('crossanglestd', 'REAL'),
        ('crossanglemin', 'REAL'),
        ('crossanglemax', 'REAL')
    ]

    # Loop through columns and add them to the table
    for column_name, column_type in columns_to_add:
        # Create the ALTER TABLE command
        alter_table_command = f"ALTER TABLE spin ADD COLUMN {column_name} {column_type};"

        # Command to execute via psql
        psql_command = [
            'psql',
            '-d', db_name,
            '-c', alter_table_command
        ]

        try:
            # Execute the psql command
            subprocess.run(psql_command, check=True)
            print(f"Added column {column_name} to the spin table")

        except subprocess.CalledProcessError as e:
            print(f"Error adding column {column_name}: {e}")


if __name__ == '__main__':
    main()
