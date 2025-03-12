#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on March 12 13:21 2025
Created in PyCharm
Created as sphenix_pp_qa/check_cw_runs

@author: Dylan Neff, dn277127
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from tabulate_rel_crossing_angles_per_run import read_crossing_angle, get_run_info, get_run_stats
from plot_full_bmp_and_check_run_time_sync import get_bpm_crossing_angles, plot_crossing_angles_vs_time


def main():
    spin_db_csv = '../spin_db.csv'
    run_info_csv = 'run_info.csv'
    out_dir = 'C:/Users/Dylan/Desktop/pp_crossing_angles/Analysis/Weird_Crossing_Runs/'
    plot_weird_runs = False

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')

    bpm_dir = 'bpm_measurements/'

    crossing_angles_df = get_bpm_crossing_angles(bpm_dir)

    print(spin_db_df)

    selected_runs_df = run_info_df[(run_info_df['Runnumber'] <= 54281) & (run_info_df['Runnumber'] >= 54275)]

    print(selected_runs_df)
    all_run_stats = []
    for index, row in selected_runs_df.iterrows():
        run_df = crossing_angles_df[(crossing_angles_df['time'] >= row['Start']) & (crossing_angles_df['time'] <= row['End'])]
        plot_crossing_angles_vs_time(run_df)
        run_stats = get_run_stats(run_df)
        all_run_stats.append(run_stats)
        plt.title(f'Run {row["Runnumber"]}')
        plt.subplots_adjust(top=0.96)
    all_run_stats_df = pd.DataFrame(all_run_stats)
    # Save to csv
    all_run_stats_df.to_csv('cw_runs_crossing_angles.csv', index=False)
    print(all_run_stats_df)
    plt.show()
    print('donzo')


if __name__ == '__main__':
    main()
