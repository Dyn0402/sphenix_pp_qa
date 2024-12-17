#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on December 13 4:46 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/spin_db_cni_crosscheck.py

@author: Dylan Neff, Dylan
"""

import ast
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from bad_spin_run_accounting import read_spin_patterns


def main():
    spin_db_csv = '../spin_db.csv'
    run_info_csv = '../pp_crossing_angles/run_info.csv'
    cni_measurements_csv = 'cni_measurements.csv'
    blue_spin_patterns_path = '../spin_patterns/blue_spin_patterns.txt'
    yellow_spin_patterns_path = '../spin_patterns/yellow_spin_patterns.txt'

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')

    cni_measurements_df = pd.read_csv(cni_measurements_csv)
    cni_measurements_df = add_cni_df_columns(cni_measurements_df)

    blue_spin_patterns, yellow_spin_patterns = read_spin_patterns(blue_spin_patterns_path, yellow_spin_patterns_path)
    check_cni_patterns_vs_known(cni_measurements_df, blue_spin_patterns, yellow_spin_patterns)

    cross_check_spin_patterns(spin_db_df, cni_measurements_df)
    print('donzo')


def check_cni_patterns_vs_known(cni_measurements_df, blue_spin_patterns, yellow_spin_patterns):
    """
    Check cni measurements against known spin patterns
    :param cni_measurements_df:
    :param blue_spin_patterns:
    :param yellow_spin_patterns:
    :return:
    """
    mismatched_111_patterns = 0
    for index, row in cni_measurements_df.iterrows():
        # bunch_fill_pattern = row['bunch_fill_pattern']
        bunch_spin_pattern = row['bunch_spin_pattern']
        # polarimeter = row['polarimeter']
        fill_number = row['fillnumber']
        total_str = row['total_str']
        if type(total_str) != str and np.isnan(total_str):
            total_ints = None
        else:
            total_ints = [int(i) for i in total_str.split('/')]
        beam = row['beam']
        if not bunch_spin_pattern:
            continue
        if total_ints is None or total_ints[1] != 9 or total_ints[0] + total_ints[2] != 111:
            continue
        if beam == 'blue':
            if bunch_spin_pattern not in blue_spin_patterns:
                mismatched_111_patterns += 1
                print(f'Blue spin pattern mismatch for fill {fill_number} with bunch spin pattern {total_str} {bunch_spin_pattern}')
        elif beam == 'yellow':
            if bunch_spin_pattern not in yellow_spin_patterns:
                mismatched_111_patterns += 1
                print(f'Yellow spin pattern mismatch for fill {fill_number} with bunch spin pattern {total_str} {bunch_spin_pattern}')

    if mismatched_111_patterns == 0:
        print('All 111 patterns match known spin patterns')
    else:
        print(f'{mismatched_111_patterns} 111 patterns do not match known spin patterns')


def cross_check_spin_patterns(spin_db_df, cni_measurements_df):
    """
    Cross-check spin patterns from spin_db with cni_measurements
    :param spin_db_df:
    :param cni_measurements_df:
    :return:
    """
    # Get spin physics runs from spin_db
    spin_db_spin_physics = spin_db_df[(spin_db_df['Type'] == 'physics') & (spin_db_df['runnumber'] >= 45235)]

    mismatched_runs, mismatched_events, missing_runs, missing_events = 0, 0, 0, 0
    missing_cni_fills, mismatched_spin_db_runs = {}, []
    for index, row in spin_db_spin_physics.iterrows():
        blue_spin_patterns, yellow_spin_patterns = get_fill_spin_patterns(cni_measurements_df, row['fillnumber'])
        if blue_spin_patterns is None or yellow_spin_patterns is None or len(blue_spin_patterns) == 0 or len(yellow_spin_patterns) == 0:
            print(f'No CNI measurement for fill {row["fillnumber"]} for run {row["runnumber"]} with {row["Events"]} events')
            # input('Enter to continue')
            missing_runs += 1
            missing_events += row['Events']
            if row['fillnumber'] not in missing_cni_fills:
                missing_cni_fills[row['fillnumber']] = {'events': row['Events'], 'runs': 1, 'runns': [row['runnumber']]}
            else:
                missing_cni_fills[row['fillnumber']]['events'] += row['Events']
                missing_cni_fills[row['fillnumber']]['runs'] += 1
                missing_cni_fills[row['fillnumber']]['runns'].append(row['runnumber'])
            continue
        if len(blue_spin_patterns) != 1:
            print(f'Fill {row["fillnumber"]} has {len(blue_spin_patterns)} blue spin patterns')
            print(blue_spin_patterns)
        if len(yellow_spin_patterns) != 1:
            print(f'Fill {row["fillnumber"]} has {len(yellow_spin_patterns)} yellow spin patterns')
            print(yellow_spin_patterns)
        blue_cni_fill_spin_pattern = list(blue_spin_patterns.keys())[0]
        yellow_cni_fill_spin_pattern = list(yellow_spin_patterns.keys())[0]
        spindb_blue_spin_pattern = ast.literal_eval(row['spinpatternblue'])
        spindb_yellow_spin_pattern = ast.literal_eval(row['spinpatternyellow'])
        mismatch = False
        if blue_cni_fill_spin_pattern != spindb_blue_spin_pattern:
            print(f'Blue spin pattern mismatch for fill {row["fillnumber"]}')
            print(f'CNI: {type(blue_cni_fill_spin_pattern)} {blue_cni_fill_spin_pattern}')
            print(f'SpinDB: {type(spindb_blue_spin_pattern)} {spindb_blue_spin_pattern}')
            mismatch = True
        if yellow_cni_fill_spin_pattern != spindb_yellow_spin_pattern:
            print(f'Yellow spin pattern mismatch for fill {row["fillnumber"]}')
            print(f'CNI: {yellow_cni_fill_spin_pattern}')
            print(f'SpinDB: {spindb_yellow_spin_pattern}')
            mismatch = True
        if mismatch:
            print(f'Mismatch for fill {row["fillnumber"]}')
            mismatched_runs += 1
            mismatched_events += row['Events']
            mismatched_spin_db_runs.append(row['runnumber'])
        # else:
        #     print(f'Run {row["runnumber"]} Fill {row["fillnumber"]} matches')

        # input('Enter to continue')
    print(f'{mismatched_runs} runs with {mismatched_events} events mismatched')
    print(f'{missing_runs} runs with {missing_events} events missing CNI measurements')
    # Sort missing_cni_fills by fill number
    missing_cni_fills = dict(sorted(missing_cni_fills.items()))
    print(f'Missing CNI fills ({len(missing_cni_fills)})')
    for fill, info in missing_cni_fills.items():
        print(f'\nFill {fill} with {info["events"]} events missing {info["runs"]} runs')
        print(f'Runs: {info["runns"]}')

    print(f'\nMismatched spin db runs ({len(mismatched_spin_db_runs)})')
    print(mismatched_spin_db_runs)

    all_bad_runs = mismatched_spin_db_runs + [run for fill, info in missing_cni_fills.items() for run in info['runns']]


    # Write in latex table format with Fill & Empty (for notes) & Runs & Events \\
    # print('\nLatex table format')
    # for fill, info in missing_cni_fills.items():
    #     print(f'{fill} & & {info["runs"]} & {info["events"]} \\\\')


def get_fill_spin_patterns(cni_measurements_df, fill_number):
    """
    Get spin patterns for a fill number
    :param cni_measurements_df:
    :param fill_number:
    :return:
    """
    cni_fill = cni_measurements_df[cni_measurements_df['fillnumber'] == fill_number]
    # Remove measurements where run name ends with alpha0 (I think energy calibration?)
    cni_fill = cni_fill[~cni_fill['run_name'].str.endswith('alpha0')]
    blue_spin_patterns, yellow_spin_patterns = None, None
    if len(cni_fill) == 0:
        print(f'No CNI measurement for fill {fill_number}')
    else:
        # Get unique spin patterns for blue and yellow beams and their counts
        blue_spin_patterns = cni_fill[cni_fill['beam'] == 'blue']['bunch_spin_pattern'].value_counts()
        yellow_spin_patterns = cni_fill[cni_fill['beam'] == 'yellow']['bunch_spin_pattern'].value_counts()

    # if fill_number == 35089:
    #     print('Fill 35089')
    #     print(cni_fill)
    #     print(blue_spin_patterns)
    #     print(yellow_spin_patterns)
    #     input('Enter to continue')
    return blue_spin_patterns, yellow_spin_patterns


def add_cni_df_columns(cni_measurements_df):
    """
    Add columns to cni_measurements for convenience
    :param cni_measurements_df:
    :return:
    """
    # Make new cni_measurements_df with fill number extracted
    cni_measurements_df['fillnumber'] = cni_measurements_df['run_name'].str.extract(r'(\d+)').astype(int)

    # Add column for spin pattern and fill pattern as integer lists
    cni_measurements_df['bunch_fill_pattern'] = cni_measurements_df['bunch_fill_pattern'].apply(lambda x: spin_fill_pattern_to_list(x))
    cni_measurements_df['bunch_spin_pattern'] = cni_measurements_df['bunch_spin_pattern'].apply(lambda x: spin_fill_pattern_to_list(x))

    cni_measurements_df['beam'] = cni_measurements_df['polarimeter'].apply(lambda x: get_beam_color(x))

    return cni_measurements_df


def get_beam_color(polarimeter):
    """
    Get beam color from polarimeter string
    :param polarimeter:
    :return:
    """
    if type(polarimeter) != str:
        if not np.isnan(polarimeter):
            print(f'Invalid polarimeter type: {type(polarimeter)}, {polarimeter}')
        return 'unknown'
    if 'B' in polarimeter:
        return 'blue'
    elif 'Y' in polarimeter:
        return 'yellow'
    else:
        return 'unknown'


def spin_fill_pattern_to_list(pattern):
    """
    Convert spin or fill pattern string to list of integers
    :param pattern: string of integers or +, - signs, no separators
    :return:
    """
    pattern_list = []
    if type(pattern) != str:
        if not np.isnan(pattern):
            print(f'Invalid pattern type: {type(pattern)}, {pattern}')
        return pattern_list
    for i in pattern:
        if i.isdigit():
            if i == '0':
                pattern_list.append(10)
            else:
                pattern_list.append(int(i))
        elif i == '+':
            pattern_list.append(1)
        elif i == '-':
            pattern_list.append(-1)
        elif i == '−':
            pattern_list.append(-1)
        else:
            print(f'Invalid spin char: {i}')
    return pattern_list


if __name__ == '__main__':
    main()
