#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on November 20 12:24 2024
Created in PyCharm
Created as sphenix_pp_qa/plot_cnipol_qa

@author: Dylan Neff, dn277127
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd


def main():
    csv_file_path = 'cnipol_fills_user.csv'
    df = pd.read_csv(csv_file_path)
    print(df.head())
    print(df.columns)
    # Print the type of each column
    print(df.dtypes)

    # Convert Physics On to datetime
    df['Physics On'] = pd.to_datetime(df['Physics On'])
    print(df['Physics On'])

    # Select physics fills at 100 GeV
    df = df[(df['Type'] == 'phys') & (df['Beam Energy, GeV'] == 100)]

    # Plot polarization vs time
    plot_pol_vs_time(df)
    plot_fill_duration_hist(df)
    plt.show()
    print('donzo')


def plot_pol_vs_time(df):
    """
    Plot polarization of the blue and yellow beams vs time on the bottom x-axis and fill number on the top x-axis
    :param df:
    :return:
    """
    fig, ax1 = plt.subplots(figsize=(12, 5))

    # Plot blue beam polarization
    ax1.errorbar(df['Physics On'], df['Blue Avrg.'], yerr=df['Blue Avrg. Error'], fmt='o',
                 label='Blue Polarization', color='b', alpha=0.8)
    ax1.set_ylabel('Beam Polarization (%)')

    # Set datetime ticks and format
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())  # Automatically space major ticks
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %-d'))  # Format as month-day
    # ax1.tick_params(axis='x', rotation=45)

    # Plot yellow beam polarization
    ax1.errorbar(df['Physics On'], df['Yellow Avrg.'], yerr=df['Yellow Avrg. Error'], fmt='o',
                 label='Yellow Polarization', color='y', alpha=0.8)
    ax1.legend()

    # Add a secondary axis for Fill numbers
    ax2 = ax1.twiny()
    ax2.set_xlim(ax1.get_xlim())  # Ensure both axes share the same range

    ax1.axhline(50, color='gray', alpha=0.8, lw=0.5)

    # Reduce the number of fill ticks (e.g., every nth tick)
    num_ticks = 10  # Choose the number of ticks you want to display
    tick_indices = range(0, len(df['Physics On']), max(len(df['Physics On']) // num_ticks, 1))
    ax2.set_xticks([mdates.date2num(df['Physics On'].iloc[i]) for i in tick_indices])  # Match datetime positions
    ax2.set_xticklabels(df['Fill'].iloc[tick_indices])  # Replace the tick labels with Fill numbers
    ax2.set_xlabel('Fill Number')
    ax1.set_ylim(0, 100)
    ax1.grid()

    plt.tight_layout()


def plot_fill_duration_hist(df):
    """
    Plot a histogram of fill durations
    :param df:
    :return:
    """
    fig, ax = plt.subplots(figsize=(12, 5))
    fill_durations = df['Fill Length'] / 3600  # Convert seconds to hours
    ax.hist(fill_durations, bins=50, zorder=10)
    ax.set_xlabel('Fill Duration [hours]')
    ax.set_ylabel('Number of Fills')
    ax.grid()
    fig.tight_layout()


if __name__ == '__main__':
    main()
