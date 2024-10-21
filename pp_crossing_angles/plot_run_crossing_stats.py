#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 18 3:36 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/plot_run_crossing_stats.py

@author: Dylan Neff, Dylan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.pyplot import tight_layout
import matplotlib.dates as mdates


def main():
    run_crossing_csv = 'run_crossing_stats.csv'
    events_cut = 1e6 * 0
    duration_cut = 200 * 0

    run_crossing_df = pd.read_csv(run_crossing_csv)

    # Filter df to only include runs where run_type == 'physics' and
    plot_df = run_crossing_df[run_crossing_df['run_type'] == 'physics']

    plot_num_events_hist(plot_df, cut_val=events_cut)
    plot_run_duration_hist(plot_df, cut_val=duration_cut)

    plot_df = plot_df[(plot_df['num_events'] > events_cut) & (plot_df['duration'] > duration_cut)]
    plot_crossing_vs_time(plot_df)
    plt.show()
    print('donzo')


def plot_num_events_hist(run_crossing_df, cut_val=None):
    """
    Plot histogram of number of events in each run.
    :param run_crossing_df:
    :param cut_val:
    :return:
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    # ax.hist(run_crossing_df['num_events'], bins=np.arange(0, 1e6, 1e4))
    ax.hist(run_crossing_df['num_events'], bins=200)
    if cut_val:
        ax.axvline(cut_val, ls='--', color='red')
    ax.set_xlabel('Number of Events')
    ax.set_ylabel('Number of Runs')
    ax.set_title('Number of Events in Each Run')
    fig.tight_layout()


def plot_run_duration_hist(run_crossing_df, cut_val=None):
    """
    Plot histogram of run duration.
    :param run_crossing_df:
    :param cut_val:
    :return:
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(run_crossing_df['duration'], bins=200)
    if cut_val:
        ax.axvline(cut_val, ls='--', color='red')
    ax.set_xlabel('Run Duration (s)')
    ax.set_ylabel('Number of Runs')
    ax.set_title('Duration of Each Run')
    tight_layout()


def plot_crossing_vs_time(run_crossing_df):
    """
    Plot crossing angles vs time. Plot mid date on x axis and mean crossing angles on y axis with std as error bars.
    :param run_crossing_df:
    :return:
    """
    fig_all, ax_all = plt.subplots(figsize=(12, 6))
    run_crossing_df['mid'] = pd.to_datetime(run_crossing_df['mid'])
    # Ensure the 'mid' column in the DataFrame is timezone-naive
    run_crossing_df['mid'] = run_crossing_df['mid'].dt.tz_localize(None)

    ax_all.plot(run_crossing_df['mid'], run_crossing_df['blue_mean'], color='blue', alpha=0.4)
    ax_all.errorbar(run_crossing_df['mid'], run_crossing_df['blue_mean'], yerr=run_crossing_df['blue_std'],
                    color='blue', label='Blue', marker='.', markersize=3, ls='None')
    ax_all.plot(run_crossing_df['mid'], run_crossing_df['yellow_mean'], color='orange', alpha=0.4)
    ax_all.errorbar(run_crossing_df['mid'], run_crossing_df['yellow_mean'], yerr=run_crossing_df['yellow_std'],
                    color='orange', label='Yellow', marker='.', markersize=3, ls='None')
    ax_all.plot(run_crossing_df['mid'], run_crossing_df['relative_mean'], color='green', alpha=0.4)
    ax_all.errorbar(run_crossing_df['mid'], run_crossing_df['relative_mean'], yerr=run_crossing_df['relative_std'],
                    color='green', label='Relative', marker='.', markersize=3, ls='None')
    ax_all.axhline(0, ls='-', alpha=0.3, color='black')
    ax_all.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax_all.set_ylabel('Crossing Angle (mrad)')
    ax_all.legend()

    # Create the secondary x-axis for run numbers
    ax_run = ax_all.secondary_xaxis('top')  # Add a secondary x-axis at the top

    # Get the tick positions from the first x-axis (dates)
    xticks_dates = ax_all.get_xticks()

    # Convert x-ticks (float format) back to datetime for matching, making sure they're timezone-naive
    print(xticks_dates)
    xticks_dates_converted = pd.to_datetime(xticks_dates, unit='d', origin='unix').tz_localize(None)

    # Find the closest run number for each tick date
    closest_runs = []
    for tick_date in xticks_dates_converted:
        # Find the index of the closest date in the 'mid' column
        print(tick_date)
        closest_idx = (run_crossing_df['mid'] - tick_date).abs().idxmin()
        closest_runs.append(run_crossing_df.loc[closest_idx, 'run'])

    # Set the x-ticks and corresponding run numbers on the secondary x-axis
    ax_run.set_xticks(xticks_dates)
    ax_run.set_xticklabels(closest_runs)
    # ax_run.set_xlabel('Run Number')

    fig_all.tight_layout()

    fig_rel, ax_rel = plt.subplots(figsize=(12, 6))
    ax_rel.plot(run_crossing_df['mid'], run_crossing_df['relative_mean'], color='green', alpha=0.4)
    ax_rel.errorbar(run_crossing_df['mid'], run_crossing_df['relative_mean'], yerr=run_crossing_df['relative_std'],
                    color='green', label='Relative', marker='.', markersize=3, ls='None')
    # Plot the relative_min and relative_max as lighter error bars
    ax_rel.errorbar(run_crossing_df['mid'], run_crossing_df['relative_mean'],
                    yerr=[run_crossing_df['relative_mean'] - run_crossing_df['relative_min'],
                          run_crossing_df['relative_max'] - run_crossing_df['relative_mean']],
                    color='green', alpha=0.2, ls='None')
    ax_rel.axhline(0, ls='-', alpha=0.3, color='black')
    ax_rel.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax_rel.set_ylabel('Crossing Angle (mrad)')

    ax_rel_run = ax_rel.secondary_xaxis('top')  # Add a secondary x-axis at the top
    xticks_dates = ax_rel.get_xticks()

    xticks_dates_converted = pd.to_datetime(xticks_dates, unit='d', origin='unix').tz_localize(None)

    closest_runs = []
    for tick_date in xticks_dates_converted:
        closest_idx = (run_crossing_df['mid'] - tick_date).abs().idxmin()
        closest_runs.append(run_crossing_df.loc[closest_idx, 'run'])

    ax_rel_run.set_xticks(xticks_dates)
    ax_rel_run.set_xticklabels(closest_runs)
    # ax_rel_run.set_xlabel('Run Number')

    fig_rel.tight_layout()


if __name__ == '__main__':
    main()
