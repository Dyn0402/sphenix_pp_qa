#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 18 3:36 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/plot_run_crossing_stats.py

@author: Dylan Neff, Dylan
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, ScalarFormatter
from datetime import datetime

from Measure import Measure
from tabulate_rel_crossing_angles_per_run import read_crossing_angle

def main():
    crossing_angle_period_boundaries = [
        datetime(2024, 6, 9),
        datetime(2024, 6, 10, 14),
        datetime(2024, 6, 13, 18),
        datetime(2024, 6, 20, 20),
        datetime(2024, 6, 24, 15),
        datetime(2024, 8, 13, 11, 40),
        datetime(2024, 10, 1, 8),
    ]

    # plot_from_run_crossing_csv(crossing_angle_period_boundaries)
    plot_from_spin_db_csv(crossing_angle_period_boundaries)

    print('donzo')


def plot_from_run_crossing_csv(crossing_angle_period_boundaries):
    """
    Plot from the raw run_crossing_stats.csv file.
    :return:
    """
    run_crossing_csv = 'run_crossing_stats.csv'
    events_cut = 1e6 * 0
    duration_cut = 200 * 0
    first_spin_run, last_spin_run = 45235, 53880

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


def plot_from_spin_db_csv(crossing_angle_period_boundaries):
    """
    Plot from the raw spin_db.csv file.
    :return:
    """
    spin_db_csv = '../spin_db.csv'
    run_info_csv = 'run_info.csv'
    out_dir = 'C:/Users/Dylan/Desktop/pp_crossing_angles/Analysis/Weird_Crossing_Runs/'
    plot_weird_runs = True

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')

    good_run_qa = spin_db_df[spin_db_df['badrunqa'] == 0]
    non_phys_runs = good_run_qa[good_run_qa['Type'] != 'physics']
    print(f'Non physics runs: {len(non_phys_runs)}')

    one_event_runs = good_run_qa[good_run_qa['Events'] <= 1]
    print(f'One event runs: {len(one_event_runs)}')
    print(one_event_runs)

    spin_db_df = spin_db_df[spin_db_df['Events'] > 1]  # Important!!!
    spin_db_df = spin_db_df[spin_db_df['badrunqa'] == 0]

    spin_db_df['mid'] = pd.to_datetime(spin_db_df['Start']) + (pd.to_datetime(spin_db_df['End']) - pd.to_datetime(spin_db_df['Start'])) / 2

    spin_db_df['relative_mean'] = spin_db_df['crossingangle']
    spin_db_df['relative_std'] = spin_db_df['crossanglestd']
    spin_db_df['relative_min'] = spin_db_df['crossanglemin']
    spin_db_df['relative_max'] = spin_db_df['crossanglemax']
    spin_db_df['run'] = spin_db_df['runnumber']

    # Check if vernier scan runs are in the data
    vernier_scan_runs = [48029, 51195]
    for run in vernier_scan_runs:
        print(f'Vernier scan run {run} in data: {run in spin_db_df["run"].values}')

    mid_blind = pd.to_datetime(spin_db_df['mid']).dt.tz_localize(None)

    # weird_runs = spin_db_df[(mid_blind > datetime(2024, 8, 11)) & (mid_blind < datetime(2024, 8, 13))]
    pd.set_option('display.max_columns', None)
    weird_runs = spin_db_df[spin_db_df['relative_std'] > 0.0025]
    print(weird_runs)
    # for row in weird_runs.iterrows():
    #     print(row)

    # Sort on run number
    spin_db_df = spin_db_df.sort_values('run')

    plot_crossing_vs_time(spin_db_df, crossing_angle_period_boundaries, ls='None')
    plot_rel_crossing_angle_std_hist(spin_db_df)

    if plot_weird_runs:
        plot_full_run_crossing_angles(weird_runs['runnumber'], spin_db_df, out_dir)

    plt.show()


def plot_full_run_crossing_angles(runs, spin_db_df, out_dir):
    bpm_dir = 'bpm_measurements/'
    # Load all crossing angle data and sort by time
    data = []
    for file_name in os.listdir(bpm_dir):
        data.append(read_crossing_angle(f'{bpm_dir}{file_name}'))
    data = pd.concat(data)
    data = data.sort_values('time')

    # Iterate through runs and plot crossing angles
    figs, stds = [], []
    for run in runs:
        start_time = spin_db_df[spin_db_df['runnumber'] == run]['Start'].values[0]
        end_time = spin_db_df[spin_db_df['runnumber'] == run]['End'].values[0]
        run_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]
        relative_crossing_angle = spin_db_df[spin_db_df['runnumber'] == run]['crossingangle'].values[0]
        relative_crossing_std = spin_db_df[spin_db_df['runnumber'] == run]['crossanglestd'].values[0]
        n_events = spin_db_df[spin_db_df['runnumber'] == run]['Events'].values[0]
        plot_raw_run_crossing_vs_time(run_data, run, relative_crossing_angle, relative_crossing_std, n_events)
        figs.append(plt.gcf())
        stds.append(relative_crossing_std)
        plt.savefig(f'{out_dir}run_{run}_crossing_angles.png')
        plt.savefig(f'{out_dir}run_{run}_crossing_angles.pdf')

    # Sort figs by std, greatest to least
    figs = [fig for _, fig in sorted(zip(stds, figs), reverse=True)]
    with PdfPages(f'{out_dir}all_weird_runs.pdf') as pdf:
        for fig in figs:
            pdf.savefig(fig)


def plot_rel_crossing_angle_std_hist(spin_db_df):
    """
    Plot histogram of relative crossing angle std.
    :param spin_db_df:
    :return:
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(spin_db_df['relative_std'], bins=100)
    ax.set_xlabel('Relative Crossing Angle Std (mrad)')
    ax.set_ylabel('Number of Runs')
    ax.set_title('Relative Crossing Angle Std')
    ax.set_yscale('log')
    fig.tight_layout()

    relative_std_filtered = spin_db_df[spin_db_df['relative_std'] < 0.1]
    fig_filtered, ax_filtered = plt.subplots(figsize=(8, 4))
    ax_filtered.hist(relative_std_filtered['relative_std'], bins=100)
    ax_filtered.set_xlabel('Relative Crossing Angle Std (mrad)')
    ax_filtered.set_ylabel('Number of Runs')
    ax_filtered.set_title('Relative Crossing Angle Std (<0.1 mrad)')
    ax_filtered.set_yscale('log')
    fig_filtered.tight_layout()

    relative_std_filtered_harder = spin_db_df[spin_db_df['relative_std'] < 0.01]
    fig_filtered_harder, ax_filtered_harder = plt.subplots(figsize=(8, 4))
    ax_filtered_harder.hist(relative_std_filtered_harder['relative_std'], bins=100)
    ax_filtered_harder.set_xlabel('Relative Crossing Angle Std (mrad)')
    ax_filtered_harder.set_ylabel('Number of Runs')
    ax_filtered_harder.set_title('Relative Crossing Angle Std (<0.01 mrad)')
    ax_filtered_harder.set_yscale('log')
    fig_filtered_harder.tight_layout()


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


def plot_crossing_vs_time(run_crossing_df, period_boundaries=None, ls='-'):
    """
    Plot crossing angles vs time. Plot mid date on x axis and mean crossing angles on y axis with std as error bars.
    :param run_crossing_df:
    :param period_boundaries:
    :param ls:
    :return:
    """
    run_crossing_df.loc[:, 'mid'] = pd.to_datetime(run_crossing_df['mid'])
    # Ensure the 'mid' column in the DataFrame is timezone-naive
    run_crossing_df['mid'] = run_crossing_df['mid'].dt.tz_localize(None)

    if 'blue_mean' in run_crossing_df.columns:
        fig_all, ax_all = plt.subplots(figsize=(12, 6))

        ax_all.plot(run_crossing_df['mid'], run_crossing_df['blue_mean'], color='blue', ls=ls, alpha=0.4)
        ax_all.errorbar(run_crossing_df['mid'], run_crossing_df['blue_mean'], yerr=run_crossing_df['blue_std'],
                        color='blue', label='Blue', marker='.', markersize=3, ls='None')
        ax_all.plot(run_crossing_df['mid'], run_crossing_df['yellow_mean'], color='orange', ls=ls, alpha=0.4)
        ax_all.errorbar(run_crossing_df['mid'], run_crossing_df['yellow_mean'], yerr=run_crossing_df['yellow_std'],
                        color='orange', label='Yellow', marker='.', markersize=3, ls='None')
        ax_all.plot(run_crossing_df['mid'], run_crossing_df['relative_mean'], color='green', ls=ls, alpha=0.4)
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
    ax_rel.plot(run_crossing_df['mid'], run_crossing_df['relative_mean'], color='green', ls=ls, alpha=0.4)
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


def plot_raw_run_crossing_vs_time(raw_run_df, run, relative_crossing_angle, relative_crossing_std, n_events):
    """
    Plot raw bpm crossing angle data vs time.
    :param raw_run_df:
    :param run:
    :param relative_crossing_angle:
    :param relative_crossing_std:
    :param n_events:
    :return:
    """

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(raw_run_df['time'], raw_run_df['bh8_crossing_angle'], color='blue', label='Blue')
    ax.plot(raw_run_df['time'], raw_run_df['yh8_crossing_angle'], color='orange', label='Yellow')
    ax.plot(raw_run_df['time'], raw_run_df['gh8_crossing_angle'], color='green', label='Relative')
    ax.axhline(0, ls='-', alpha=0.3, color='black')
    ax.set_ylabel('Crossing Angle (mrad)')
    ax.legend()
    run_str = f'Run: {run}\nRelative Crossing Angle: {Measure(relative_crossing_angle, relative_crossing_std)}\nEvents: {n_events}'
    ax.annotate(run_str, xy=(0.5, 0.99), xycoords='axes fraction', ha='center', va='top', fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
    fig.tight_layout()


if __name__ == '__main__':
    main()
