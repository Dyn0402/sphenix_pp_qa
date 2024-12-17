#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on December 17 3:54 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/find_good_runs.py

@author: Dylan Neff, Dylan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta


def main():
    spin_db_csv = '../spin_db.csv'
    run_info_csv = '../pp_crossing_angles/run_info.csv'

    run_type = 'physics'
    spin_badrunqa = 0
    run_range = [0, 1000000]
    # crossing_angle_range = [-0.05, 0.2]
    crossing_angle_range = [0.037, 0.041]
    events_range = [2.7e7, 3.5e7]
    duration_range = [59.5, 61]

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')
    spin_db_df['duration'] = pd.to_datetime(spin_db_df['End']) - pd.to_datetime(spin_db_df['Start'])
    spin_db_df['duration'] = spin_db_df['duration'].apply(lambda x: x.total_seconds() / 60)

    print(spin_db_df.columns)

    spin_db_df = spin_db_df[spin_db_df['Type'] == run_type]
    spin_db_df = spin_db_df[spin_db_df['badrunqa'] == spin_badrunqa]
    # spin_db_df = spin_db_df[(spin_db_df['runnumber'] >= run_range[0]) & (spin_db_df['runnumber'] <= run_range[1])]
    spin_db_df = spin_db_df[(spin_db_df['crossingangle'] >= crossing_angle_range[0]) &
                            (spin_db_df['crossingangle'] <= crossing_angle_range[1])]
    spin_db_df = spin_db_df[(spin_db_df['Events'] >= events_range[0]) & (spin_db_df['Events'] <= events_range[1])]
    spin_db_df = spin_db_df[(spin_db_df['duration'] >= duration_range[0]) & (spin_db_df['duration'] <= duration_range[1])]

    # Plot hist of crossing angles
    crossing_angles = spin_db_df['crossingangle']
    crossing_angles = crossing_angles[~np.isnan(crossing_angles)]
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(crossing_angles, bins=100)
    ax.set_xlabel('Crossing Angle')

    # Plot hist of run numbers
    run_numbers = spin_db_df['runnumber']
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(run_numbers, bins=100)
    ax.set_xlabel('Run Number')

    # Plot hist of run durations
    durations = spin_db_df['duration']
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(durations, bins=100)
    ax.set_xlabel('Run Duration [min]')

    # Plot hist of number of events
    events = spin_db_df['Events']
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(events, bins=100)
    ax.set_xlabel('Number of Events')

    for index, row in spin_db_df.iterrows():
        print(f'Run: {row["runnumber"]}, Angle: {row["crossingangle"]}, Events: {row["Events"]}, Duration: {row["duration"]}')

    # Print unique run numbers
    run_list = [int(x) for x in spin_db_df['runnumber'].unique()]
    run_list.sort()
    print(run_list)
    for run in run_list:
        print(run)

    plt.show()

    print('donzo')


if __name__ == '__main__':
    main()
