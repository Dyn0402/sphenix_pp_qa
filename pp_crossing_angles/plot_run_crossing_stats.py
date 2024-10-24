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
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from datetime import datetime

def main():
    run_crossing_csv = 'run_crossing_stats.csv'
    events_cut = 1e6 * 0
    duration_cut = 200 * 0
    first_spin_run, last_spin_run = 45235, 53880
    crossing_angle_period_boundaries = [
        datetime(2024, 6, 9),
        datetime(2024, 6, 10, 14),
        datetime(2024, 6, 13, 18),
        datetime(2024, 6, 20, 20),
        datetime(2024, 6, 24, 15),
        datetime(2024, 8, 13, 11, 40),
        datetime(2024, 10, 1, 8),
    ]

    run_crossing_df = pd.read_csv(run_crossing_csv)
    run_crossing_df = run_crossing_df[(run_crossing_df['run'] >= first_spin_run) &
                                      (run_crossing_df['run'] <= last_spin_run)]

    # Filter df to only include runs where run_type == 'physics' and
    plot_df = run_crossing_df[run_crossing_df['run_type'] == 'physics']

    plot_num_events_hist(plot_df, cut_val=events_cut)
    plot_run_duration_hist(plot_df, cut_val=duration_cut)
    plot_run_duration_num_events_2d(plot_df)
    plt.show()

    plot_df = plot_df[(plot_df['num_events'] > events_cut) & (plot_df['duration'] > duration_cut)]
    plot_crossing_vs_time(plot_df, crossing_angle_period_boundaries)
    # plot_crossing_vs_time(plot_df)

    # Pair adjacent period boundaries
    # for i in range(len(crossing_angle_period_boundaries) - 1):
    #     df_period = plot_df[(plot_df['mid'] >= crossing_angle_period_boundaries[i]) &
    #                         (plot_df['mid'] < crossing_angle_period_boundaries[i + 1])]
    #     plot_crossing_vs_time(df_period)

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
    ax.hist(run_crossing_df['duration'] / 60, bins=200)
    if cut_val:
        ax.axvline(cut_val, ls='--', color='red')
    ax.set_xlabel('Run Duration (minutes)')
    ax.set_ylabel('Number of Runs')
    ax.set_title('Duration of Each Run')
    fig.tight_layout()


def plot_run_duration_num_events_2d(run_crossing_df):
    """
    Scatter plot of num events on y and run duration on x. In addition, plot a vertical event_number density histogram
    on the right and a horizontal run_duration density histogram on the top, weighted by the number of events, and
    normalized to show percentages.
    :param run_crossing_df:
    :return:
    """
    rate_lines_khz = [10, 5, 2]
    colors = ['red', 'orange', 'green']
    x_lims = [0, 79]

    # Total number of events for normalization
    total_events = run_crossing_df['num_events'].sum()

    # Create main plot with scatter
    fig, ax = plt.subplots(figsize=(8, 4))
    scatter = ax.scatter(run_crossing_df['duration'] / 60, run_crossing_df['num_events'], s=4, alpha=0.3)

    # Plot diagonal lines for constant rates
    for i, rate in enumerate(rate_lines_khz):
        ax.plot(x_lims, np.array(x_lims) * rate * 60 * 1e3, ls='--', c=colors[i], alpha=0.5, label=f'{rate} kHz',
                zorder=0)

    # Set scientific notation for y-axis with `4e5` style

    ax.set_xlabel('Run Duration (minutes)')
    ax.set_ylabel('Number of Events')
    ax.set_xlim(x_lims)
    ax.set_ylim(bottom=0)
    ax.legend()

    # Place title inside the plot area
    ax.text(0.45, 0.95, 'Number of Events vs Run Duration', horizontalalignment='center', verticalalignment='center',
            transform=ax.transAxes, fontsize=12)

    # Create inset axis for rotated histogram on the right (weighted by number of events and normalized to percentage)
    ax_hist_right = ax.inset_axes([1.01, 0.0, 0.2, 1.0])  # [left, bottom, width, height]
    num_event_binning = np.linspace(*ax.get_ylim(), 50)
    counts_right, bins_right, _ = ax_hist_right.hist(run_crossing_df['num_events'], bins=num_event_binning,
                                                     orientation='horizontal', color='black', alpha=0.8,
                                                     weights=run_crossing_df['num_events'], density=False)

    # Convert counts to percentages
    counts_right_percentage = counts_right / total_events * 100
    ax_hist_right.clear()  # Clear and replot with percentages
    ax_hist_right.barh(bins_right[:-1], counts_right_percentage, height=np.diff(bins_right), color='black', alpha=0.8)
    ax_hist_right.set_ylim(*ax.get_ylim())
    ax_hist_right.set_yticks([])
    # ax_hist_right.set_xlabel('%')

    # Create inset axis for horizontal histogram on the top (weighted by number of events and normalized to percentage)
    ax_hist_top = ax.inset_axes([0.0, 1.01, 1.0, 0.2])  # [left, bottom, width, height]
    duration_binning = np.linspace(*ax.get_xlim(), 50)
    counts_top, bins_top, _ = ax_hist_top.hist(run_crossing_df['duration'] / 60, bins=duration_binning,
                                               orientation='vertical', color='black', alpha=0.8,
                                               weights=run_crossing_df['num_events'], density=False)

    # Convert counts to percentages
    counts_top_percentage = counts_top / total_events * 100
    ax_hist_top.clear()  # Clear and replot with percentages
    ax_hist_top.bar(bins_top[:-1], counts_top_percentage, width=np.diff(bins_top), color='black', alpha=0.8)
    ax_hist_top.set_xlim(*ax.get_xlim())
    ax_hist_top.set_xticks([])
    # ax_hist_top.set_ylabel('%')

    # Function to format axis labels in scientific notation
    def sci_notation_formatter(x, pos):
        exp_format = f'{x:.0e}'  # Basic scientific notation
        exp_format = exp_format.replace('e+0', 'e').replace('e+', 'e').replace('e0', 'e')
        if x == 0:
            exp_format = '0'
        return exp_format

    # Function to format ticks as percentages
    def percent_formatter(x, pos):
        return f'{int(x)}%'  # Convert to percentage and add '%' symbol

    # Apply the percentage formatter to the right histogram y-axis and top histogram x-axis
    ax_hist_right.xaxis.set_major_formatter(FuncFormatter(percent_formatter))  # Right histogram
    ax_hist_top.yaxis.set_major_formatter(FuncFormatter(percent_formatter))  # Top histogram
    ax.yaxis.set_major_formatter(FuncFormatter(sci_notation_formatter))  # Y-axis of the main plot

    fig.tight_layout()
    plt.show()


def plot_crossing_vs_time(run_crossing_df, period_boundaries=None):
    """
    Plot crossing angles vs time. Plot mid date on x axis and mean crossing angles on y axis with std as error bars.
    :param run_crossing_df:
    :param period_boundaries:
    :return:
    """
    fig_all, ax_all = plt.subplots(figsize=(12, 6))
    run_crossing_df.loc[:, 'mid'] = pd.to_datetime(run_crossing_df['mid'])
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
    if period_boundaries:
        for boundary in period_boundaries:
            ax_rel.axvline(boundary, ls='--', color='red', alpha=0.5, zorder=0)
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
