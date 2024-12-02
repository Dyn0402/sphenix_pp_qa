#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 31 6:33 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/read_spindb_csv.py

@author: Dylan Neff, Dylan
"""

import ast
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas as pd


def main():
    spin_db_file = 'spin_db.csv'
    run_info_file = 'pp_crossing_angles/run_info.csv'
    spin_db_df = pd.read_csv(spin_db_file)
    run_info_df = pd.read_csv(run_info_file)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')

    non_phys_runs = spin_db_df[spin_db_df['Type'] != 'physics']
    print(f'Non physics runs: {len(non_phys_runs)}')
    print(non_phys_runs.head())

    spin_db_df = spin_db_df[spin_db_df['Type'] == 'physics']
    spin_db_df = spin_db_df[spin_db_df['badrunqa'] == 0]

    print(spin_db_df['badrunqa'])
    # Get all unique values of badrunqa
    print(spin_db_df['badrunqa'].unique())
    # input('Enter to continue')

    plot_crossing_angles(spin_db_df)

    print('donzo')


def plot_crossing_angles(spin_db_df):
    """
    Plot crossing angles vs run number
    :param spin_db_df:
    :return:
    """

    # Get crossing angles and stds
    crossing_angles, crossing_angle_stds = spin_db_df['crossingangle'], spin_db_df['crossanglestd']

    # Get run numbers
    run_numbers = spin_db_df['runnumber']
    start_time, end_time = spin_db_df['Start'], spin_db_df['End']

    # Plot crossing angles
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.errorbar(run_numbers, crossing_angles, yerr=crossing_angle_stds, fmt='o', color='green')
    ax.set_xlabel('Run Number')
    ax.set_ylabel('Crossing Angle [mrad]')
    ax.set_title('Crossing Angles vs Run Number')
    ax.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
