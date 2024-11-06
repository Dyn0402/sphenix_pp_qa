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

    # plot_spin_patterns(spin_db_df)
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


def plot_spin_patterns(spin_db_df):
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

    # Print the spin patterns and counts
    print('Blue Fill Patterns:')
    for pattern, count in blue_fill_pattern_counts.items():
        pattern = ast.literal_eval(pattern)
        print(f'{count}: {pattern}')
        ones = pattern.count(1) + pattern.count(-1)
        tens = pattern.count(10)
        zeros = pattern.count(0)
        total = len(pattern)
        other = total - ones - tens - zeros
        print(f'Ones: {ones}, Tens: {tens}, Zeros: {zeros}, Total: {total}, Other: {other}\n')

    print('\nYellow Fill Patterns:')
    for pattern, count in yellow_fill_pattern_counts.items():
        pattern = ast.literal_eval(pattern)
        print(f'{count}: {pattern}')
        ones = pattern.count(1) + pattern.count(-1)
        tens = pattern.count(10)
        zeros = pattern.count(0)
        total = len(pattern)
        other = total - ones - tens - zeros
        print(f'Ones: {ones}, Tens: {tens}, Zeros: {zeros}, Total: {total}, Other: {other}\n')

    # Label each fill pattern by its number of ones. If there are multiple patterns with the same number of ones, append
    # an arbitrary number to the end of the label to differentiate them (111:1, 111:2, ...). Make it a separate object
    # so that the original fill patterns are still accessible.
    blue_labels = [ast.literal_eval(x).count(1) + ast.literal_eval(x).count(-1) if -999 not in ast.literal_eval(x)
                   else -999 for x in blue_fill_pattern_counts.index]
    yellow_labels = [ast.literal_eval(x).count(1) + ast.literal_eval(x).count(-1) if -999 not in ast.literal_eval(x)
                     else -999 for x in yellow_fill_pattern_counts.index]


    # Plot histograms as bar graphs
    fig, ax = plt.subplots(2, 1, figsize=(12, 6), sharex='all')
    ax[0].bar(range(len(blue_fill_pattern_counts.index)), blue_fill_pattern_counts.values, color='blue',
              label='Blue Spin Patterns')
    ax[0].set_ylabel('Number of Runs')
    ax[1].bar(range(len(yellow_fill_pattern_counts.index)), yellow_fill_pattern_counts.values, color='orange',
              label='Yellow Spin Patterns')
    ax[1].set_xlabel('Spin Pattern')
    ax[1].set_ylabel('Number of Runs')

    # Print the labels on the bars
    for i, label in enumerate(blue_labels):
        ax[0].text(i, blue_fill_pattern_counts.values[i], f'{label}', ha='center', va='bottom')

    for i, label in enumerate(yellow_labels):
        ax[1].text(i, yellow_fill_pattern_counts.values[i], f'{label}', ha='center', va='bottom')

    # Set xticks to each integer value
    ax[0].set_xticks(range(len(blue_fill_pattern_counts.index)))
    ax[1].set_xticks(range(len(yellow_fill_pattern_counts.index)))

    ax[0].set_ylim(0, np.max(blue_fill_pattern_counts.values) * 1.1)
    ax[1].set_ylim(0, np.max(yellow_fill_pattern_counts.values) * 1.1)

    ax[0].legend()
    ax[1].legend()

    fig.tight_layout()
    fig.subplots_adjust(hspace=0.0)

    # Make a two-dimensional histogram of the number of runs for each blue and yellow fill pattern
    two_dim_hist = np.zeros((len(blue_fill_pattern_counts.index), len(yellow_fill_pattern_counts.index)))
    for i, blue_pattern in enumerate(blue_fill_pattern_counts.index):
        for j, yellow_pattern in enumerate(yellow_fill_pattern_counts.index):
            two_dim_hist[i, j] = len(spin_db_df[(spin_db_df['spinpatternblue'] == blue_pattern) &
                                                 (spin_db_df['spinpatternyellow'] == yellow_pattern)])

    # Replace empty cells in `two_dim_hist` with NaN
    two_dim_hist = np.array(two_dim_hist, dtype=float)  # Ensure it's a float array to support NaNs
    two_dim_hist[two_dim_hist == 0] = np.nan  # Replace 0s or any placeholder with NaN

    # Create 1D histograms from the sum of the rows and columns of the 2D histogram
    blue_fill_pattern_hist = np.nansum(two_dim_hist, axis=1)
    yellow_fill_pattern_hist = np.nansum(two_dim_hist, axis=0)

    # Create figure and set up GridSpec layout
    fig = plt.figure(figsize=(12, 8))
    gs = GridSpec(4, 2, figure=fig, height_ratios=[1, 4, 0.5, 0.25], width_ratios=[4, 1])

    # Plot the 2D histogram in the center area
    ax_main = fig.add_subplot(gs[1, 0], zorder=1)
    cmap = plt.cm.jet
    cmap.set_bad(color='white')  # Set NaN values to white
    im = ax_main.imshow(two_dim_hist, cmap=cmap, aspect='auto')

    # Set axis labels only on the main histogram
    ax_main.set_xlabel('Yellow Fill Pattern')
    ax_main.set_ylabel('Blue Fill Pattern')

    # Plot 1D histogram for the x-axis (top histogram) with aligned axes
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main, zorder=0)
    ax_top.bar(range(len(yellow_fill_pattern_hist)), yellow_fill_pattern_hist, color='orange')
    ax_top.set_yticks([])  # Remove y-tick labels on the top histogram
    ax_top.set_xticks([])  # Remove x-tick labels on the top histogram

    # Plot 1D histogram for the y-axis (right histogram) with aligned axes
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main, zorder=0)
    ax_right.barh(range(len(blue_fill_pattern_hist)), blue_fill_pattern_hist, color='blue')
    ax_right.set_yticks([])  # Remove y-tick labels on the right histogram
    ax_right.set_xticks([])  # Remove x-tick labels on the right histogram

    # Colorbar as its own subplot below the main plot
    cbar_ax = fig.add_subplot(gs[3, 0:1])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label('Counts')  # Label for color bar

    # Set x and y ticks with labels
    blue_2d_labels = [f'{label}' for label in blue_labels]
    yellow_2d_labels = [f'{label}' for label in yellow_labels]
    ax_main.set_xticks(range(len(yellow_fill_pattern_hist)))
    ax_main.set_xticklabels(yellow_2d_labels)
    ax_main.set_yticks(range(len(blue_fill_pattern_hist)))
    ax_main.set_yticklabels(blue_2d_labels)

    # Display the plot
    plt.tight_layout()
    fig.subplots_adjust(hspace=0.0, wspace=0.0)
    plt.show()



if __name__ == '__main__':
    main()
