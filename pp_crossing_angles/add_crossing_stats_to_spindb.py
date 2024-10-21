#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 21 4:30 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/add_crossing_stats_to_spindb.py

@author: Dylan Neff, Dylan
"""

import pandas as pd
import subprocess


def main():
    # Filepath to your CSV file
    run_crossing_csv = 'run_crossing_stats.csv'

    # Read the CSV file into a DataFrame
    run_crossing_df = pd.read_csv(run_crossing_csv)

    # Database connection details
    db_name = 'spinDB'

    # Update the database with the crossing angle values
    update_database(db_name, run_crossing_df)

    print('donzo')


def update_database(db_name, df):
    # Loop through the DataFrame rows
    for index, row in df.iterrows():
        run_number = row['run']
        crossing_angle = row['relative_mean']
        crossing_angle_std = row['relative_std']
        crossing_angle_min = row['relative_min']
        crossing_angle_max = row['relative_max']

        if crossing_angle == 'nan':
            crossing_angle = 'NULL'
        if crossing_angle_std == 'nan':
            crossing_angle_std = 'NULL'
        if crossing_angle_min == 'nan':
            crossing_angle_min = 'NULL'
        if crossing_angle_max == 'nan':
            crossing_angle_max = 'NULL'

        # SQL command to update the row for the specific run_number
        update_query = f"""
        UPDATE spin
        SET crossingangle = {crossing_angle},
            crossanglestd = {crossing_angle_std},
            crossanglemin = {crossing_angle_min},
            crossanglemax = {crossing_angle_max}
        WHERE runnumber = {run_number};
        """

        # Command to execute via psql
        psql_command = [
            'psql',
            '-d', db_name,
            '-c', update_query
        ]

        try:
            # Execute the psql command
            subprocess.run(psql_command, check=True)
            print(f"Updated run_number {run_number} in the database")

        except subprocess.CalledProcessError as e:
            print(f"Error updating run_number {run_number}: {e}")



if __name__ == '__main__':
    main()
