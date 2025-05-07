#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 07 16:01 2025
Created in PyCharm
Created as sphenix_pp_qa/check_spin_db_qalevel

@author: Dylan Neff, dn277127
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def main():
    # db_path = '../spin_db.csv'
    db_path = '/local/home/dn277127/Bureau/test/spin_db.csv'
    df = pd.read_csv(db_path)
    print(df)
    print(df.columns)
    print(df['qa_level'].value_counts())
    print(df[df['qa_level'] == 10])

    df_qa_old = df[df['qa_level'] == 65535]
    df_qa_new = df[df['qa_level'] == 0]
    df_qa_default = df[df['is_default']]

    qa_new_runs = df_qa_new['runnumber'].unique()
    qa_old_runs = df_qa_old['runnumber'].unique()

    # Get runs in new qa level but not in old
    new_not_old = set(qa_new_runs) - set(qa_old_runs)
    print(f'New QA level runs not in old: {new_not_old}')
    # Get runs in old qa level but not in new
    old_not_new = set(qa_old_runs) - set(qa_new_runs)
    print(f'Old QA level runs not in new: {old_not_new}')
    print(f'Number of new QA level runs: {len(new_not_old)}')
    print(f'Number of old QA level runs: {len(old_not_new)}')

    # Print runs default not in new qa level
    default_not_new = set(df_qa_default['runnumber']) - set(qa_new_runs)
    new_not_default = set(qa_new_runs) - set(df_qa_default['runnumber'])
    print(f'Default runs not in new QA level: {default_not_new}')
    print(f'New QA level runs not in default: {new_not_default}')
    print(f'Number of default runs not in new QA level: {len(default_not_new)}')
    print(f'Number of new QA level runs not in default: {len(new_not_default)}')

    # Print the old_not_new entries
    # for run in old_not_new:
    #     entries = df_qa_old[df_qa_old['runnumber'] == run]
    #     if len(entries) > 1:
    #         print(f'Run {run} has multiple entries:')
    #         print(entries)
    #         continue
    #     entry = entries.iloc[0]
    #     print(f'Run {run} --> badrunqa: {entry["badrunqa"]}, is_default: {entry["is_default"]}')
    #     if not entry['badrunqa']:
    #         print(f'Run {run} in old qa level but not in new:')
    #         print(df_qa_old[df_qa_old['runnumber'] == run])

    print('donzo')


if __name__ == '__main__':
    main()
