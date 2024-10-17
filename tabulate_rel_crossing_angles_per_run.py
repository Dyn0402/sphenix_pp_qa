#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 17 10:36 2024
Created in PyCharm
Created as sphenix_pp_qa/tabulate_rel_crossing_angles_per_run

@author: Dylan Neff, dn277127
"""


import os
import numpy as np
from scipy.optimize import curve_fit as cf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import pytz
import gzip


def main():
    bpm_dir = '/local/home/dn277127/Bureau/pp_crossing_angles/bpm_measurements/'
    crossing_angle(bpm_dir)
    print('donzo')


def crossing_angle(bpm_dir):
    for file_name in os.listdir(bpm_dir):
        print(file_name)
        data = read_crossing_angle(f'{bpm_dir}{file_name}')
        plot_crossing_angle(data)
        plt.show()


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


def plot_crossing_angle(data):
    plt.figure(figsize=(12, 6))

    plt.plot(list(data['time']), list(data['bh8_crossing_angle']), label='Blue', color='blue')
    plt.plot(list(data['time']), list(data['yh8_crossing_angle']), label='Yellow', color='orange')
    plt.plot(list(data['time']), list(data['gh8_crossing_angle']), label='Blue - Yellow', color='green')
    plt.axhline(0, color='gray', linestyle='-', alpha=0.7)

    plt.xlabel('Time')
    plt.ylabel('Angle (mrad)')
    plt.title('Crossing Angles vs Time')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()


if __name__ == '__main__':
    main()
