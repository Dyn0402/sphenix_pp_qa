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

    hjet_root_csv = 'hjet_gpfs_pol_info.csv'
    hjet_wiki_csv = 'hjet_wiki_pol_info.csv'

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)
    hjet_wiki_df = pd.read_csv(hjet_wiki_csv)
    hjet_root_df = pd.read_csv(hjet_root_csv)

    compare_hjet_wiki_and_root(hjet_wiki_df, hjet_root_df)
    input()

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')
    spin_db_df = add_polarized_bunch_num_cols(spin_db_df, hjet_wiki_df)

    cni_measurements_df = pd.read_csv(cni_measurements_csv)
    cni_measurements_df = add_cni_df_columns(cni_measurements_df)

    blue_spin_patterns, yellow_spin_patterns = read_spin_patterns(blue_spin_patterns_path, yellow_spin_patterns_path)
    check_cni_patterns_vs_known(cni_measurements_df, blue_spin_patterns, yellow_spin_patterns)
    print()
    cross_check_spin_patterns(spin_db_df, cni_measurements_df, plot_fill_run_nums=True)
    plt.show()
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


def cross_check_spin_patterns(spin_db_df, cni_measurements_df, plot_fill_run_nums=False):
    """
    Cross-check spin patterns from spin_db with cni_measurements
    :param spin_db_df:
    :param cni_measurements_df:
    :param plot_fill_run_nums:
    :return:
    """
    # Get spin physics runs from spin_db
    spin_db_spin_physics_all = spin_db_df[(spin_db_df['Type'] == 'physics') & (spin_db_df['runnumber'] >= 45235)]
    spin_db_spin_physics = spin_db_spin_physics_all[(spin_db_spin_physics_all['polarized']) & (spin_db_spin_physics_all['bunches'] == 111)]

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
    print(f'{mismatched_runs} runs with {mismatched_events} events with mismatched spin patterns')
    print(f'{missing_runs} runs with {missing_events} events missing CNI measurements')
    print(f'{missing_runs + mismatched_runs} total bad runs with {missing_events + mismatched_events} events')
    # Sort missing_cni_fills by fill number
    missing_cni_fills = dict(sorted(missing_cni_fills.items()))
    print(f'\n\nMissing CNI fills ({len(missing_cni_fills)})')
    for fill, info in missing_cni_fills.items():
        print(f'\nFill {fill} with {info["events"]} events missing {info["runs"]} runs')
        print(f'Runs: {info["runns"]}')

    missing_cni_info_runs = [run for fill, info in missing_cni_fills.items() for run in info['runns']]

    bad_spindb_qa_runs = spin_db_spin_physics[spin_db_spin_physics['badrunqa'] != 0]['runnumber'].tolist()

    # Get missing_cni_info_runs or mismatched_spin_db_runs that are not in bad_spindb_qa_runs
    missing_cni_info_runs_good_spin_qa = [run for run in missing_cni_info_runs if run not in bad_spindb_qa_runs]
    mismatched_spin_db_runs_good_spin_qa = [run for run in mismatched_spin_db_runs if run not in bad_spindb_qa_runs]

    print(f'\nMissing CNI info runs with good spinDB QA flag ({len(missing_cni_info_runs_good_spin_qa)})')
    print(missing_cni_info_runs_good_spin_qa)
    print(spin_db_df[spin_db_df['runnumber'].isin(missing_cni_info_runs_good_spin_qa)]['fillnumber'])

    print(f'\nMismatched spin db runs with good spinDB QA flag ({len(mismatched_spin_db_runs_good_spin_qa)})')
    print(mismatched_spin_db_runs_good_spin_qa)
    print(spin_db_df[spin_db_df['runnumber'].isin(mismatched_spin_db_runs_good_spin_qa)]['fillnumber'])

    # Get bad_spindb_qa_runs that are not in missing_cni_info_runs or mismatched_spin_db_runs
    bad_spindb_qa_runs = [run for run in bad_spindb_qa_runs
                          if run not in missing_cni_info_runs and run not in mismatched_spin_db_runs]

    all_bad_runs = mismatched_spin_db_runs + missing_cni_info_runs + bad_spindb_qa_runs

    print(f'\nMismatched spin db runs ({len(mismatched_spin_db_runs)})')
    print(mismatched_spin_db_runs)

    # Get the date and time of each run. Plot the number of events on the y axis with good runs as green circle and bad as red x.
    good_runs = spin_db_spin_physics[~spin_db_spin_physics['runnumber'].isin(all_bad_runs)]
    missing_cni_runs = spin_db_spin_physics[spin_db_spin_physics['runnumber'].isin(missing_cni_info_runs)]
    mismatch_runs = spin_db_spin_physics[spin_db_spin_physics['runnumber'].isin(mismatched_spin_db_runs)]
    other_bad_spin_db_qa_runs = spin_db_spin_physics[spin_db_spin_physics['runnumber'].isin(bad_spindb_qa_runs)]
    unpolarized_runs = spin_db_spin_physics_all[~spin_db_spin_physics_all['polarized']]
    non_111x111_runs = spin_db_spin_physics_all[spin_db_spin_physics_all['bunches'] != 111]

    good_runs['Start'] = pd.to_datetime(good_runs['Start'])
    missing_cni_runs['Start'] = pd.to_datetime(missing_cni_runs['Start'])
    mismatch_runs['Start'] = pd.to_datetime(mismatch_runs['Start'])
    other_bad_spin_db_qa_runs['Start'] = pd.to_datetime(other_bad_spin_db_qa_runs['Start'])
    unpolarized_runs['Start'] = pd.to_datetime(unpolarized_runs['Start'])
    non_111x111_runs['Start'] = pd.to_datetime(non_111x111_runs['Start'])

    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.plot(good_runs['Start'], good_runs['Events'], 'go', alpha=0.5, label='Good Runs')
    ax.plot(unpolarized_runs['Start'], unpolarized_runs['Events'], 'bo', alpha=0.5, label='Unpolarized Runs')
    ax.plot(non_111x111_runs['Start'], non_111x111_runs['Events'], 'yo', alpha=0.5, label='Non 111x111 Bunch Runs')
    ax.plot(missing_cni_runs['Start'], missing_cni_runs['Events'], 'ro', markersize=9,
            label='Missing CNI Measurements')
    ax.plot(mismatch_runs['Start'], mismatch_runs['Events'], color='orange', marker='o', ls='none', markersize=9,
            label='Mismatched with CNI Spin Patterns')
    ax.plot(other_bad_spin_db_qa_runs['Start'], other_bad_spin_db_qa_runs['Events'], color='purple', marker='o',
            ls='none', markersize=9, label='Other Bad Spin DB QA')

    # Find the start and end runs for each fill. Draw vertical lines between fills and label with fill number.
    fill_numbers = spin_db_spin_physics_all['fillnumber'].unique()
    fill_start_end = {}
    for fill in fill_numbers:
        fill_runs = spin_db_spin_physics_all[spin_db_spin_physics_all['fillnumber'] == fill]
        run_min, run_max = fill_runs['runnumber'].min(), fill_runs['runnumber'].max()
        fill_start_end[fill] = (fill_runs['Start'].min(), fill_runs['Start'].max(), run_min, run_max)
    if plot_fill_run_nums:
        for fill, (start, end, run_min, run_max) in fill_start_end.items():
            start_timestamp, end_timestamp = pd.to_datetime(start), pd.to_datetime(end)
            mid_timestamp = start_timestamp + (end_timestamp - start_timestamp) / 2
            ax.axvspan(start_timestamp, end_timestamp, color='black', alpha=0.1)
            run_range = f'{run_min}-{run_max}' if run_min != run_max else f'{run_min}'
            ax.text(mid_timestamp, ax.get_ylim()[1], f'{fill} ({run_range}) ', rotation=90, va='top',
                    ha='center')

    ax.set_ylabel('Nominal Number of Events in Run')
    ax.legend()
    ax.set_ylim(bottom=0)
    fig.tight_layout()

    print(f'Total bad events: {mismatched_events + missing_events}')

    # Write in latex table format with Fill & Empty (for notes) & Runs & Events \\
    # print('\nLatex table format')
    # for fill, info in missing_cni_fills.items():
    #     print(f'{fill} & & {info["runs"]} & {info["events"]} \\\\')


def compare_hjet_wiki_and_root(hjet_wiki_df, hjet_root_df):
    """
    Compare H-jet information from the wiki and the root files
    :param hjet_wiki_df:
    :param hjet_root_df:
    :return:
    """
    print(f'H-jet wiki info: {len(hjet_wiki_df)}')
    print(f'H-jet root info: {len(hjet_root_df)}')
    print(f'Wiki columns: {hjet_wiki_df.columns}')
    print(f'Root columns: {hjet_root_df.columns}')

    # Find wiki rows with Fill entries which are not in root Fill entries
    wiki_fills = hjet_wiki_df['Fill'].tolist()
    root_fills = hjet_root_df['Fill'].tolist()
    missing_fills_root = [fill for fill in wiki_fills if fill not in root_fills]
    missing_fills_wiki = [fill for fill in root_fills if fill not in wiki_fills]
    # Make a dataframe of the missing fills
    missing_fills_wiki_df = hjet_wiki_df[hjet_wiki_df['Fill'].isin(missing_fills_root)]
    print('\nMissing fills in wiki:')
    print(missing_fills_wiki_df)
    missing_fills_root_df = hjet_root_df[hjet_root_df['Fill'].isin(missing_fills_wiki)]
    print('\nMissing fills in root:')
    print(missing_fills_root_df)

    print(f'\nMissing fills in root: {len(missing_fills_root)}')
    print(f'Missing fills in wiki: {len(missing_fills_wiki)}')

    # Get duplicate fills in both dataframes
    wiki_duplicate_fills = hjet_wiki_df[hjet_wiki_df['Fill'].duplicated()]['Fill'].tolist()
    wiki_duplicate_fills_df = hjet_wiki_df[hjet_wiki_df['Fill'].isin(wiki_duplicate_fills)]
    print(f'\nDuplicate fills in wiki: {len(wiki_duplicate_fills)}')
    print(wiki_duplicate_fills_df)

    root_duplicate_fills = hjet_root_df[hjet_root_df['Fill'].duplicated()]['Fill'].tolist()
    root_duplicate_fills_df = hjet_root_df[hjet_root_df['Fill'].isin(root_duplicate_fills)]
    print(f'\nDuplicate fills in root: {len(root_duplicate_fills)}')
    print(root_duplicate_fills_df)

    common_fills = [fill for fill in wiki_fills if fill in root_fills]

    # Get common fills and compare
    common_fills_wiki_df = hjet_wiki_df[hjet_wiki_df['Fill'].isin(common_fills)]
    common_fills_root_df = hjet_root_df[hjet_root_df['Fill'].isin(common_fills)]

    print(f'\nCommon fills: {len(common_fills_wiki_df)}, {len(common_fills_root_df)}')

    # For common fills, insert the 'Date' and 'Comments' columns from the wiki into the root dataframe
    hjet_root_df = hjet_root_df.merge(common_fills_wiki_df[['Fill', 'Date', 'Comments']], on='Fill', how='left')

    # The two dataframes will now have the same columns. Append any missing Fill entries from the wiki to the root dataframe
    hjet_combo_df = hjet_root_df.merge(missing_fills_wiki_df, how='outer')
    print(hjet_combo_df)


def add_polarized_bunch_num_cols(spin_db_df, hjet_wiki_df):
    """
    Add columns to spin_db_df for whether the beams were intended to be polarized and the number of intended bunches
    :param spin_db_df:
    :param hjet_wiki_df:
    :return:
    """
    # Get unpolarized fills from H-jet wiki
    unpolarized_rows = hjet_wiki_df[hjet_wiki_df['Comments'].str.contains('unpolarized', na=False)]
    unpolarized_fills = unpolarized_rows['Fill'].tolist()

    # Get non-111x111 bunch numbers from H-jet wiki
    non_111x111_rows = hjet_wiki_df[hjet_wiki_df['Comments'].str.contains(' bunches', na=False)]
    # Extract bunch numbers from comments as xx bunches
    non_111x111_fills = non_111x111_rows['Fill'].tolist()
    non_111x111_bunches = [int(row['Comments'].split(' ')[0]) for index, row in non_111x111_rows.iterrows()]

    # Add columns to spin_db_df for whether the beams were intended to be polarized and the number of intended bunches
    spin_db_df['polarized'] = spin_db_df['fillnumber'].apply(lambda x: x not in unpolarized_fills)

    # Add column for number of bunches (defualt to 111)
    spin_db_df['bunches'] = 111
    for fill, bunches in zip(non_111x111_fills, non_111x111_bunches):
        spin_db_df.loc[spin_db_df['fillnumber'] == fill, 'bunches'] = bunches

    return spin_db_df




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
