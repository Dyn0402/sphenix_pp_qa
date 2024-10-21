#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 17 10:36 2024
Created in PyCharm
Created as sphenix_pp_qa/tabulate_rel_crossing_angles_per_run

@author: Dylan Neff, dn277127
"""


import os
import pandas as pd
from datetime import datetime
import pytz


def main():
    bpm_dir = 'bpm_measurements/'
    run_info_path = 'run_info.csv'
    check_bmp_files(bpm_dir)
    check_run_info_file(run_info_path)
    get_run_crossing_stats(bpm_dir, run_info_path)
    print('donzo')


def check_bmp_files(bpm_dir):
    """
    Check bmp_dir for files and pull from indico if files don't exist.
    :param bpm_dir:
    :return:
    """
    # Check to make sure bmp_dir exists
    if not os.path.exists(bpm_dir):
        print(f'{bpm_dir} does not exist.')
        raise FileNotFoundError

    expected_months = ['May', 'June', 'July', 'August', 'September']
    month_missing = False
    for month in expected_months:
        if not os.path.exists(f'{bpm_dir}BPM_{month}.dat'):
            month_missing = True
            break

    if month_missing:
        print('Missing files, pulling from indico.')
        pull_bpm_files(bpm_dir)


def pull_bpm_files(bpm_dir):
    """
    Download bpm files from indico to bpm_dir.
    :param bpm_dir:
    :return:
    """
    pass


def check_run_info_file(run_info_path):
    """
    Check to make sure run_info_path exists. If not, raise error and tell user to download.
    :param run_info_path:
    :return:
    """
    if not os.path.exists(run_info_path):
        print(f'{run_info_path} does not exist.')
        print('Run get_runs_start_end.py to download run info. You must be on the campus network for this and have '
              'beautifulsoup4 installed. To install beautifulsoup4 run "pip install beautifulsoup4".')
        raise FileNotFoundError


def get_run_crossing_stats(bpm_dir, run_info_path):
    """
    Get crossing angle statistics for each run in run_info.
    :param bpm_dir:
    :param run_info_path:
    :return:
    """
    run_info_df = get_run_info(run_info_path)

    # Load all crossing angle data and sort by time
    data = pd.DataFrame()
    for file_name in os.listdir(bpm_dir):
        data = data.append(read_crossing_angle(f'{bpm_dir}{file_name}'))
    data = data.sort_values('time')

    # Iterate through runs and get crossing angle stats
    runs_beam_stats_df = []
    calc_start_time = datetime.now()
    for index, row in run_info_df.iterrows():
        if index % 1000 == 0 and index > 0:  # Print progress and estimated time remaining
            time_remaining = (datetime.now() - calc_start_time) / index * (len(run_info_df) - index)
            est_end_time = datetime.now() + time_remaining
            est_end_time_str = est_end_time.strftime('%H:%M:%S')
            print(f'{index}/{len(run_info_df)}, {row["Runnumber"]} --> {est_end_time_str}')

        run_data = data[(data['time'] >= row['Start']) & (data['time'] <= row['End'])]

        run_beams_stats = {
            'run': row['Runnumber'],
            'start': row['Start'],
            'end': row['End'],
            'mid': row['Start'] + (row['End'] - row['Start']) / 2,
            'duration': (row['End'] - row['Start']).total_seconds(),
            'run_type': row['Type'],
            'num_events': row['Events']
        }

        run_beams_stats.update(get_run_stats(run_data))

        runs_beam_stats_df.append(run_beams_stats)

    runs_beam_stats_df = pd.DataFrame(runs_beam_stats_df)

    # Save the run stats to a csv file
    runs_beam_stats_df.to_csv('run_crossing_stats.csv', index=False)


def get_run_stats(run_data):
    """
    Get crossing angle statistics for a run.
    Get mean, std, min, max, and median for each crossing angle
    :param run_data:
    :return:
    """
    stats = {
        'blue_mean': run_data['bh8_crossing_angle'].mean(),
        'blue_std': run_data['bh8_crossing_angle'].std(),
        'blue_min': run_data['bh8_crossing_angle'].min(),
        'blue_max': run_data['bh8_crossing_angle'].max(),
        'blue_median': run_data['bh8_crossing_angle'].median(),
        'yellow_mean': run_data['yh8_crossing_angle'].mean(),
        'yellow_std': run_data['yh8_crossing_angle'].std(),
        'yellow_min': run_data['yh8_crossing_angle'].min(),
        'yellow_max': run_data['yh8_crossing_angle'].max(),
        'yellow_median': run_data['yh8_crossing_angle'].median(),
        'relative_mean': run_data['gh8_crossing_angle'].mean(),
        'relative_std': run_data['gh8_crossing_angle'].std(),
        'relative_min': run_data['gh8_crossing_angle'].min(),
        'relative_max': run_data['gh8_crossing_angle'].max(),
        'relative_median': run_data['gh8_crossing_angle'].median()
    }

    return stats


def read_crossing_angle(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Skip the header lines
    data_lines = lines[3:]

    # Lists to store the parsed data
    time_data = []
    bh8_crossing_angle = []
    yh8_crossing_angle = []
    gh8_crossing_angle = []

    # Parse each line
    line_i = 0
    for line in data_lines:
        line_i += 1
        columns = line.strip().split('\t')
        if len(columns) != 4:
            continue

        # print(time_data)

        try:
            time_data.append(datetime.strptime(columns[0].strip(), "%m/%d/%Y %H:%M:%S"))
        except ValueError:
            print(f'Error parsing time at line {line_i}:')
            print(line)
            continue
        bh8_crossing_angle.append(float(columns[1]))
        yh8_crossing_angle.append(float(columns[2]))
        gh8_crossing_angle.append(float(columns[3]))

    df = pd.DataFrame({
        'time': time_data,
        'bh8_crossing_angle': bh8_crossing_angle,
        'yh8_crossing_angle': yh8_crossing_angle,
        'gh8_crossing_angle': gh8_crossing_angle
    })

    # Set the time column to be in New York time
    bnl_tz = pytz.timezone('America/New_York')
    df['time'] = df['time'].dt.tz_localize(bnl_tz)

    # Return the data as a pandas DataFrame
    return df


def get_run_info(run_info_path):
    run_info_df = pd.read_csv(run_info_path)
    run_info_df['Start'] = pd.to_datetime(run_info_df['Start'])
    run_info_df['End'] = pd.to_datetime(run_info_df['End'])

    return run_info_df


if __name__ == '__main__':
    main()
