#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 31 6:33 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/read_spindb_csv.py

@author: Dylan Neff, Dylan
"""

import numpy as np
import matplotlib.pyplot as plt
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

    # Get distinct blue and yellow spin patterns
    blue_fill_patterns = spin_db_df['spinpatternblue'].unique()
    yellow_fill_patterns = spin_db_df['spinpatternyellow'].unique()

    print(f'Blue fill patterns: {len(blue_fill_patterns)}')
    print(f'Yellow fill patterns: {len(yellow_fill_patterns)}')

    # For each blue and yellow distinct fill patterns, assign an index and make a histogram showing how many runs for
    # each spin pattern

    # Count the number of runs for each fill pattern
    blue_fill_pattern_counts = spin_db_df['spinpatternblue'].value_counts()
    yellow_fill_pattern_counts = spin_db_df['spinpatternyellow'].value_counts()

    # Plot histograms as bar graphs
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex='all')
    ax[0].bar(range(len(blue_fill_pattern_counts.index)), blue_fill_pattern_counts.values, color='blue',
              label='Blue Spin Patterns')
    ax[0].set_ylabel('Number of Runs')
    ax[1].bar(range(len(yellow_fill_pattern_counts.index)), yellow_fill_pattern_counts.values, color='orange',
              label='Yellow Spin Patterns')
    ax[1].set_xlabel('Spin Pattern')
    ax[1].set_ylabel('Number of Runs')

    # Set xticks to each integer value
    ax[0].set_xticks(range(len(blue_fill_pattern_counts.index)))
    ax[1].set_xticks(range(len(yellow_fill_pattern_counts.index)))

    ax[0].legend()
    ax[1].legend()

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.0)

    plt.show()

    print('donzo')


if __name__ == '__main__':
    main()
