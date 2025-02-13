#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on February 10 11:18 AM 2025
Created in PyCharm
Created as sphenix_pp_qa/plot_full_bmp_and_check_run_time_sync.py

@author: Dylan Neff, Dylan
"""

import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd

from tabulate_rel_crossing_angles_per_run import read_crossing_angle, get_run_info


def main():
    bpm_dir = 'bpm_measurements/'
    run_info_path = 'run_info.csv'

    run_info_df = get_run_info(run_info_path)
    crossing_angles_df = get_bpm_crossing_angles(bpm_dir)
    # plot_crossing_angles_vs_time(crossing_angles_df)
    check_time_shift(crossing_angles_df, run_info_df)
    plt.show()

    print('donzo')


def check_time_shift(crossing_angles_df, run_info_df):
    """
    Shift crossing angle time data by a few hours in each direction and check run standard deviation to make sure
    no time shift.
    :param crossing_angles_df:
    :param run_info_df:
    :return:
    """
    time_shifts = np.arange(-8, 9)
    run_info_df['Mid'] = run_info_df['Start'] + (run_info_df['End'] - run_info_df['Start']) / 2
    run_info_df = run_info_df[run_info_df['Type'] == 'physics']
    run_info_df['duration'] = (run_info_df['End'] - run_info_df['Start']).dt.total_seconds()
    run_info_df = run_info_df[(run_info_df['Events'] > 10000) & (run_info_df['duration'] > 20 * 60)]
    run_info_df = run_info_df[(run_info_df['Mid'] >= crossing_angles_df['time'].min()) &
                              (run_info_df['Mid'] <= crossing_angles_df['time'].max())]
    vernier_scan_runs = [48029, 51195]
    run_info_df = run_info_df[~run_info_df['Runnumber'].isin(vernier_scan_runs)]

    shifted_xing_dfs = []
    for shift in time_shifts:
        shift_xing_df = crossing_angles_df.copy()
        shift_xing_df['time'] = shift_xing_df['time'] + pd.Timedelta(hours=shift)
        shifted_xing_dfs.append(shift_xing_df)

    data = []
    for index, row in run_info_df.iterrows():
        print(f'Run: {row["Runnumber"]}')
        for shift, shift_xing_df in zip(time_shifts, shifted_xing_dfs):
            run_angles = shift_xing_df[(shift_xing_df['time'] >= row['Start']) & (shift_xing_df['time'] <= row['End'])]
            if len(run_angles) == 0:
                continue
            rel_angle_std = run_angles['gh8_crossing_angle'].std()
            data.append({'Run': row['Runnumber'], 'Start': row['Start'], 'End': row['End'], 'Mid': row['Mid'],
                         'n_events': row['Events'], 'Shift': shift, 'Std': rel_angle_std})

    data = pd.DataFrame(data)

    # plot standard deviation vs mid time for each time shift (different colors)
    # fig, ax = plt.subplots(figsize=(12, 6))
    # for shift in time_shifts:
    #     shift_data = data[data['Shift'] == shift]
    #     ax.plot(shift_data['Mid'], shift_data['Std'], label=f'Shift: {shift} hours')
    # ax.set_ylabel('Relative Crossing Angle Standard Deviation (mrad)')
    # ax.legend()
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    # fig.tight_layout()

    # Plot average standard deviation vs time shift
    fig, ax = plt.subplots(figsize=(12, 4.5))
    avg_std = data.groupby('Shift').mean()
    ax.plot(avg_std.index, avg_std['Std'], marker='o')
    ax.set_ylabel('Average Relative Crossing Angle Standard Deviation (mrad)')
    ax.set_xlabel('Time Shift of Crossing Angle Data (hours)')
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
    fig.tight_layout()


def get_bpm_crossing_angles(bpm_dir):
    """
    Load all crossing angle data from bpm_dir and sort by time.
    :return:
    """
    # Load all crossing angle data and sort by time
    data = []
    for file_name in os.listdir(bpm_dir):
        data.append(read_crossing_angle(f'{bpm_dir}{file_name}'))
    data = pd.concat(data)
    data = data.sort_values('time')

    return data


def plot_crossing_angles_vs_time(crossing_angles_df):
    """
    NOT USEFUL. Too much fluctuation as beams turn off/on
    Plot blue, yellow and relative crossing angles vs time.
    :param crossing_angles_df:
    :return:
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(crossing_angles_df['time'], crossing_angles_df['bh8_crossing_angle'], label='Blue', color='blue')
    ax.plot(crossing_angles_df['time'], crossing_angles_df['yh8_crossing_angle'], label='Yellow', color='gold')
    ax.plot(crossing_angles_df['time'], crossing_angles_df['gh8_crossing_angle'], label='Relative', color='green')
    ax.axhline(0, ls='-', alpha=0.3, color='black')
    ax.set_ylabel('Crossing Angle (mrad)')
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    fig.tight_layout()


if __name__ == '__main__':
    main()
