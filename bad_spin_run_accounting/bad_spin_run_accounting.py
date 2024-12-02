#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on November 28 12:14 2024
Created in PyCharm
Created as sphenix_pp_qa/bad_spin_run_accounting

@author: Dylan Neff, dn277127
"""

import ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def main():
    spin_db_csv = '../spin_db.csv'
    run_info_csv = '../pp_crossing_angles/run_info.csv'
    blue_spin_patterns_path = '../spin_patterns/blue_spin_patterns.txt'
    yellow_spin_patterns_path = '../spin_patterns/yellow_spin_patterns.txt'

    spin_db_df = pd.read_csv(spin_db_csv)
    run_info_df = pd.read_csv(run_info_csv)

    # Merge run_info into spin_db_df on spin_db runnumber and run_info Runnumber
    spin_db_df = pd.merge(spin_db_df, run_info_df, left_on='runnumber', right_on='Runnumber', how='left')

    blue_spin_patterns, yellow_spin_patterns = read_spin_patterns(blue_spin_patterns_path, yellow_spin_patterns_path)

    # plot_bad_runs(spin_db_df, blue_spin_patterns, yellow_spin_patterns)
    spin_db_df = check_polarizations(spin_db_df)
    count_events(spin_db_df)
    plt.show()

    print('donzo')


def plot_bad_runs(spin_db_df, blue_spin_patterns, yellow_spin_patterns):
    """
    Various plots for bad runs
    :param spin_db_df:
    :return:
    """
    bad_runs = spin_db_df[spin_db_df['badrunqa'] == 1]
    print(f'Bad runs: {len(bad_runs)}')
    print(bad_runs)

    bad_physics_runs = bad_runs[bad_runs['Type'] == 'physics']
    print(f'Bad physics runs: {len(bad_physics_runs)}')
    print(bad_physics_runs)

    # Convert Start to datetime and plot Events vs Start
    bad_physics_runs.loc[:, 'Start'] = pd.to_datetime(bad_physics_runs['Start'])
    bad_physics_runs.loc[:, 'duration'] = (
            pd.to_datetime(bad_physics_runs['End']) - pd.to_datetime(bad_physics_runs['Start'])
    ).dt.total_seconds()

    # plot_event_num_hist(bad_physics_runs, 'Bad Physics Runs No Event or Duration Cuts')
    # plot_duration_hist(bad_physics_runs, 'Bad Physics Runs No Event or Duration Cuts')
    #
    # bad_physics_runs = bad_physics_runs[bad_physics_runs['duration'] > 5 * 60]
    #
    # plot_event_num_hist(bad_physics_runs, 'Bad Physics Runs Duration > 2 min')
    #
    # bad_physics_runs = bad_physics_runs[bad_physics_runs['Events'] > 100]
    # print(f'Bad physics runs with more than 100 events: {len(bad_physics_runs)}')
    # print(bad_physics_runs)

    print(f'Polar blue: {bad_physics_runs["polarblue"]}')

    plot_events_vs_time(bad_physics_runs)
    plot_duration_vs_time(bad_physics_runs)

    # Check if any of the bad runs have spin patterns that are not in the good 4 spin patterns
    bad_blue_spin_patterns = bad_physics_runs['spinpatternblue']
    bad_yellow_spin_patterns = bad_physics_runs['spinpatternyellow']

    print(f'Bad blue spin patterns: {bad_blue_spin_patterns}')
    print(f'Bad yellow spin patterns: {bad_yellow_spin_patterns}')

    good_spin_patterns = []
    for i in range(len(bad_blue_spin_patterns)):
        good_spin_pattern = True
        if bad_blue_spin_patterns.iloc[i] not in blue_spin_patterns:
            print(f'Bad blue spin pattern: {bad_blue_spin_patterns.iloc[i]}')
            good_spin_pattern = False
        if bad_yellow_spin_patterns.iloc[i] not in yellow_spin_patterns:
            print(f'Bad yellow spin pattern: {bad_yellow_spin_patterns.iloc[i]}')
            good_spin_pattern = False
        good_spin_patterns.append(good_spin_pattern)

    bad_physics_runs['good_spin_pattern'] = good_spin_patterns

    print(f'Total bad runs: {len(bad_physics_runs)}')
    print(f'Bad runs with good spin patterns: {len(bad_physics_runs[bad_physics_runs["good_spin_pattern"]])}')
    print(f'Bad runs with bad spin patterns: {len(bad_physics_runs[~bad_physics_runs["good_spin_pattern"]])}')

    characterize_spin_patterns(bad_physics_runs)


def count_events(df):
    """
    Count the number of events in each run as cuts are made
    :param df:
    :return:
    """
    event_dict = {}

    event_dict.update({'original': np.sum(df['Events'])})
    print(f'Original events: {event_dict["original"]}')

    df_phys = df[df['Type'] == 'physics']
    event_dict.update({'physics': np.sum(df_phys['Events'])})
    print(f'Physics events: {event_dict["physics"]}')

    df_spin_phys = df_phys[df_phys['runnumber'] >= 45235]
    event_dict.update({'spin_phys': np.sum(df_spin_phys['Events'])})
    print(f'Spin physics events: {event_dict["spin_phys"]}')

    spin_pattern_df = characterize_spin_patterns(df_spin_phys)
    event_dict.update({'111x111': np.sum(df_spin_phys[(df_spin_phys['blue_bunch_num'] == 111) & (df_spin_phys['yellow_bunch_num'] == 111)]['Events'])})

    event_dict.update({'111x111 good pol': np.sum(df_spin_phys[(df_spin_phys['blue_bunch_num'] == 111) & (df_spin_phys['yellow_bunch_num'] == 111) & (df_spin_phys['bad_blue_pol'] == 0) & (df_spin_phys['bad_yellow_pol'] == 0)]['Events'])})

    event_dict.update({'badrunqa=0': np.sum(df_spin_phys[df_spin_phys['badrunqa'] == 0]['Events'])})
    print(f'Badrunqa=0 events: {event_dict["badrunqa=0"]}')

    plot_event_count_dict(event_dict)

    spin_pattern_dict = {}
    # Sum the number of events for each unique combined_fill_pattern_label and add to the spin_pattern_dict
    for pattern in spin_pattern_df['combined_fill_pattern_label2'].unique():
        spin_pattern_dict.update({pattern: np.sum(spin_pattern_df[spin_pattern_df['combined_fill_pattern_label2'] == pattern]['Events'])})

    plot_event_count_dict(spin_pattern_dict, fontsize=10, title='All Physics+Spin Spin Patterns')

    good_event_spin_pattern_dict = {}
    df_goodqa = spin_pattern_df[spin_pattern_df['badrunqa'] == 0]

    # Sum the number of events for each unique combined_fill_pattern_label and add to the good_event_spin_pattern_dict
    for pattern in df_goodqa['combined_fill_pattern_label2'].unique():
        good_event_spin_pattern_dict.update({pattern: np.sum(df_goodqa[df_goodqa['combined_fill_pattern_label2'] == pattern]['Events'])})

    print(f'Badrunqa=0 events: {np.sum(df_goodqa["Events"])}')
    print(f'Sum of good_event_spin_pattern_dict events: {np.sum(list(good_event_spin_pattern_dict.values()))}')

    plot_event_count_dict(good_event_spin_pattern_dict, fontsize=12, title='Badrunqa=0 Spin Patterns')

    bad_run_spin_pattern_dict = {}
    df_badqa = spin_pattern_df[spin_pattern_df['badrunqa'] == 1]
    # bad_run_spin_pattern_dict.update({'badrunqa=1': np.sum(df_badqa['Events'])})

    # Sum the number of events for each unique combined_fill_pattern_label and add to the bad_run_spin_pattern_dict
    for pattern in df_badqa['combined_fill_pattern_label2'].unique():
        bad_run_spin_pattern_dict.update({pattern: np.sum(df_badqa[df_badqa['combined_fill_pattern_label2'] == pattern]['Events'])})

    print(f'Badrunqa=1 events: {np.sum(df_badqa["Events"])}')
    print(f'Sum of bad_run_spin_pattern_dict events: {np.sum(list(bad_run_spin_pattern_dict.values()))}')

    plot_event_count_dict(bad_run_spin_pattern_dict, fontsize=12, title='Badrunqa=1 Spin Patterns')

    bad_run_non_111_dict = {}
    df_badqa_non_111 = df_badqa[(df_badqa['blue_bunch_num'] != 111) | (df_badqa['yellow_bunch_num'] != 111)]

    # Sum the number of events for each unique combined_fill_pattern_label and add to the bad_run_non_111_dict
    for pattern in df_badqa_non_111['combined_fill_pattern_label2'].unique():
        bad_run_non_111_dict.update({pattern: np.sum(df_badqa_non_111[df_badqa_non_111['combined_fill_pattern_label2'] == pattern]['Events'])})

    print(f'Badrunqa=1 non-111 events: {np.sum(df_badqa_non_111["Events"])}')

    plot_event_count_dict(bad_run_non_111_dict, fontsize=12, title='Badrunqa=1 Non-111x111 Spin Patterns')

    df_badqa_111 = df_badqa[(df_badqa['blue_bunch_num'] == 111) & (df_badqa['yellow_bunch_num'] == 111)]

    bad_run_all_dict = {
        'badrunqa=1': np.sum(df_badqa['Events']),
        'non-111x111': np.sum(df_badqa_non_111['Events']),
        '111x111': np.sum(df_badqa_111['Events']),
        'Good Polarizations': np.sum(df_badqa[(df_badqa['bad_blue_pol'] == 0) & (df_badqa['bad_yellow_pol'] == 0)]['Events']),
        'Bad Polarizations': np.sum(df_badqa[(df_badqa['bad_blue_pol'] == 1) | (df_badqa['bad_yellow_pol'] == 1)]['Events'])
    }
    plot_event_count_dict(bad_run_all_dict, fontsize=12, title='Badrunqa=1 All Spin Patterns')



def plot_event_count_dict(event_dict, fontsize=14, title=None):
    """
    Plot the event count dictionary as a horizontal bar chart
    :param event_dict:
    :param fontsize:
    :param title:
    :return:
    """
    # Plot these event counts as a horizontal bar chart
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    event_dict = dict(sorted(event_dict.items(), key=lambda item: item[1]))  # Sort the dictionary so original at top
    ax.barh(list(event_dict.keys()), list(event_dict.values()))
    max_val = max(event_dict.values())
    for i, v in enumerate(event_dict.values()):  # Write the number of events on the bars in green
        if v > 0.2 * max_val:
            ax.text(v, i, f'{int(v):.2e}  ', color='white', va='center', ha='right', fontweight='bold',
                    fontsize=fontsize)
        else:
            ax.text(v, i, f'  {int(v):.2e}', color='black', va='center', ha='left', fontweight='bold',
                    fontsize=fontsize)
    if title:
        ax.set_title(title)
    ax.set_xlabel('Number of Events')
    fig.tight_layout()


def read_spin_patterns(blue_spin_patterns_path, yellow_spin_patterns_path):
    with open(blue_spin_patterns_path, 'r') as file:
        blue_spin_patterns = file.readlines()
    with open(yellow_spin_patterns_path, 'r') as file:
        yellow_spin_patterns = file.readlines()
    blue_spin_patterns = [ast.literal_eval(pattern) for pattern in blue_spin_patterns]
    yellow_spin_patterns = [ast.literal_eval(pattern) for pattern in yellow_spin_patterns]
    return blue_spin_patterns, yellow_spin_patterns


def characterize_spin_patterns(spin_db_df):
    """
    Characterize spin patterns
    :param spin_db_df:
    :return:
    """
    # Get distinct blue and yellow spin patterns
    blue_fill_patterns = spin_db_df['spinpatternblue'].unique()
    yellow_fill_patterns = spin_db_df['spinpatternyellow'].unique()

    print(f'Blue fill patterns: {len(blue_fill_patterns)}')
    print(f'Yellow fill patterns: {len(yellow_fill_patterns)}')

    # For each blue and yellow distinct fill patterns, assign an index and make a histogram showing how many runs for
    # each spin pattern

    # Count the number of runs for each fill pattern
    blue_fill_pattern_counts = spin_db_df['spinpatternblue'].value_counts()
    yellow_fill_pattern_counts = spin_db_df['spinpatternyellow'].value_counts()

    # Print the spin patterns and counts
    print('Blue Fill Patterns:')
    for pattern, count in blue_fill_pattern_counts.items():
        pattern = ast.literal_eval(pattern)
        print(f'{count}: {pattern}')
        ones = pattern.count(1) + pattern.count(-1)
        tens = pattern.count(10)
        zeros = pattern.count(0)
        total = len(pattern)
        other = total - ones - tens - zeros
        print(f'Ones: {ones}, Tens: {tens}, Zeros: {zeros}, Total: {total}, Other: {other}\n')

    print('\nYellow Fill Patterns:')
    for pattern, count in yellow_fill_pattern_counts.items():
        pattern = ast.literal_eval(pattern)
        print(f'{count}: {pattern}')
        ones = pattern.count(1) + pattern.count(-1)
        tens = pattern.count(10)
        zeros = pattern.count(0)
        total = len(pattern)
        other = total - ones - tens - zeros
        print(f'Ones: {ones}, Tens: {tens}, Zeros: {zeros}, Total: {total}, Other: {other}\n')

    # Label each fill pattern by its number of ones. If there are multiple patterns with the same number of ones, append
    # an arbitrary number to the end of the label to differentiate them (111:1, 111:2, ...). Make it a separate object
    # so that the original fill patterns are still accessible.
    blue_bunch_num = [ast.literal_eval(x).count(1) + ast.literal_eval(x).count(-1) if -999 not in ast.literal_eval(x)
                   else -999 for x in blue_fill_pattern_counts.index]
    yellow_bunch_num = [ast.literal_eval(x).count(1) + ast.literal_eval(x).count(-1) if -999 not in ast.literal_eval(x)
                     else -999 for x in yellow_fill_pattern_counts.index]

    # To each blue and yellow label, append the first 4 elements of the fill pattern index to differentiate between
    # patterns with the same number of ones
    blue_labels = [
        f'{label} [{",".join([str(x) for x in ast.literal_eval(blue_fill_pattern_counts.index[i])][:4])}]' if label != -999 else 'No Data'
        for i, label in enumerate(blue_bunch_num)]
    yellow_labels = [
        f'{label} [{",".join([str(x) for x in ast.literal_eval(yellow_fill_pattern_counts.index[i])][:4])}]' if label != -999 else 'No Data'
        for i, label in enumerate(yellow_bunch_num)]

    # Sum the total events in the dataframe for each unique fill pattern
    blue_fill_pattern_events, yellow_fill_pattern_events = [], []
    for pattern in blue_fill_patterns:
        blue_fill_pattern_events.append(int(np.sum(spin_db_df[spin_db_df['spinpatternblue'] == str(pattern)]['Events'])))
    for pattern in yellow_fill_patterns:
        yellow_fill_pattern_events.append(int(np.sum(spin_db_df[spin_db_df['spinpatternyellow'] == str(pattern)]['Events'])))

    # Sort the labels and events together by the number of events
    blue_bunch_num, blue_labels, blue_fill_patterns, blue_fill_pattern_events = zip(*sorted(zip(blue_bunch_num, blue_labels, blue_fill_patterns, blue_fill_pattern_events), key=lambda x: x[3], reverse=True))
    yellow_bunch_num, yellow_labels, yellow_fill_patterns, yellow_fill_pattern_events = zip(*sorted(zip(yellow_bunch_num, yellow_labels, yellow_fill_patterns, yellow_fill_pattern_events), key=lambda x: x[3], reverse=True))

    # Print the labels and events for each fill pattern
    print('Blue Fill Patterns:')
    for i in range(len(blue_fill_patterns)):
        print(f'{blue_bunch_num[i]}: {blue_fill_pattern_events[i]}')
    print('\nYellow Fill Patterns:')
    for i in range(len(yellow_fill_patterns)):
        print(f'{yellow_bunch_num[i]}: {yellow_fill_pattern_events[i]}')

    # Make a second set of labels which is the bunch number followed by a letter. Iterate the letter only for labels
    # with the same bunch number
    blue_labels2, yellow_labels2 = [], []
    for i in range(len(blue_bunch_num)):
        if i == 0 or blue_bunch_num[i] != blue_bunch_num[i - 1]:
            letter = 'A'
        else:
            letter = chr(ord(letter) + 1)
        blue_labels2.append(f'{blue_bunch_num[i]}{letter}')
    for i in range(len(yellow_bunch_num)):
        if i == 0 or yellow_bunch_num[i] != yellow_bunch_num[i - 1]:
            letter = 'A'
        else:
            letter = chr(ord(letter) + 1)
        yellow_labels2.append(f'{yellow_bunch_num[i]}{letter}')

    # Print the labels and events for each fill pattern
    print('Blue Fill Patterns:')
    for i in range(len(blue_fill_patterns)):
        print(f'{blue_labels2[i]}: {blue_fill_pattern_events[i]}')
    print('\nYellow Fill Patterns:')
    for i in range(len(yellow_fill_patterns)):
        print(f'{yellow_labels2[i]}: {yellow_fill_pattern_events[i]}')

    # In the original dataframe add three columns for the blue and yellow fill pattern labels and a combined label
    # spin_db_df['blue_fill_pattern_label'] = [blue_labels[blue_fill_patterns.index(x)] for x in spin_db_df['spinpatternblue']]
    # spin_db_df['yellow_fill_pattern_label'] = [yellow_labels[yellow_fill_patterns.index(x)] for x in spin_db_df['spinpatternyellow']]
    # spin_db_df['combined_fill_pattern_label'] = [f'{spin_db_df["blue_fill_pattern_label"].iloc[i]} - {spin_db_df["yellow_fill_pattern_label"].iloc[i]}' for i in range(len(spin_db_df))]
    # Create a dictionary for quick lookup of the label based on the pattern
    blue_label_dict = dict(zip(blue_fill_patterns, blue_labels))
    yellow_label_dict = dict(zip(yellow_fill_patterns, yellow_labels))

    # In the original dataframe, map the labels using these dictionaries
    spin_db_df.loc[:, 'blue_fill_pattern_label'] = spin_db_df['spinpatternblue'].map(blue_label_dict)
    spin_db_df.loc[:, 'yellow_fill_pattern_label'] = spin_db_df['spinpatternyellow'].map(yellow_label_dict)
    spin_db_df.loc[:, 'combined_fill_pattern_label'] = [
        f'{spin_db_df["blue_fill_pattern_label"].iloc[i]} | {spin_db_df["yellow_fill_pattern_label"].iloc[i]}' for i in
        range(len(spin_db_df))]

    # Add the labels2 along with combined label2
    blue_label_dict2 = dict(zip(blue_fill_patterns, blue_labels2))
    yellow_label_dict2 = dict(zip(yellow_fill_patterns, yellow_labels2))

    spin_db_df.loc[:, 'blue_fill_pattern_label2'] = spin_db_df['spinpatternblue'].map(blue_label_dict2)
    spin_db_df.loc[:, 'yellow_fill_pattern_label2'] = spin_db_df['spinpatternyellow'].map(yellow_label_dict2)
    spin_db_df.loc[:, 'combined_fill_pattern_label2'] = [
        f'{spin_db_df["blue_fill_pattern_label2"].iloc[i]} | {spin_db_df["yellow_fill_pattern_label2"].iloc[i]}' for i in
        range(len(spin_db_df))]

    # Add bunch number column
    spin_db_df.loc[:, 'blue_bunch_num'] = spin_db_df['spinpatternblue'].map(dict(zip(blue_fill_patterns, blue_bunch_num)))
    spin_db_df.loc[:, 'yellow_bunch_num'] = spin_db_df['spinpatternyellow'].map(dict(zip(yellow_fill_patterns, yellow_bunch_num)))

    return spin_db_df


def check_polarizations(df):
    """
    Check the polarizations and ensure all are within reasonable bounds.
    polarblue and polaryellow are lists formatted as strings. Convert to floats and check for any values outside of
    reasonable bounds.
    :param df:
    :return:
    """
    # Convert polarizations to floats
    df.loc[:, 'polarblue'] = df['polarblue'].apply(lambda x: ast.literal_eval(x))
    df.loc[:, 'polaryellow'] = df['polaryellow'].apply(lambda x: ast.literal_eval(x))

    df_phys = df[df['Type'] == 'physics']
    df_spin_phys = df_phys[df_phys['runnumber'] >= 45235]

    # Flatten the lists of polarizations and histogram them for blue and yellow separately
    # blue_polarizations = [x for sublist in df_spin_phys['polarblue'] for x in sublist]
    # yellow_polarizations = [x for sublist in df_spin_phys['polaryellow'] for x in sublist]

    # fig_blue_pol, ax_blue_pol = plt.subplots(1, 1, figsize=(12, 6))
    # fig_yellow_pol, ax_yellow_pol = plt.subplots(1, 1, figsize=(12, 6))
    # ax_blue_pol.hist(blue_polarizations, bins=50)
    # ax_yellow_pol.hist(yellow_polarizations, bins=50)
    # ax_blue_pol.set_title('Blue Polarizations')
    # ax_yellow_pol.set_title('Yellow Polarizations')
    # ax_blue_pol.set_xlabel('Polarization')
    # ax_yellow_pol.set_xlabel('Polarization')
    # fig_blue_pol.tight_layout()
    # fig_yellow_pol.tight_layout()

    # Find runs with any polarization less than 0 or greater than 100
    bad_blue_pol = df_spin_phys[df_spin_phys['polarblue'].apply(lambda x: any([pol < 0 or pol > 100 for pol in x]))]
    bad_yellow_pol = df_spin_phys[df_spin_phys['polaryellow'].apply(lambda x: any([pol < 0 or pol > 100 for pol in x]))]

    # Print the bad runs
    print('Bad Blue Polarizations:')
    print(bad_blue_pol[['runnumber', 'polarblue']])

    print('Bad Yellow Polarizations:')
    print(bad_yellow_pol[['runnumber', 'polaryellow']])

    # Find runs with any polarization less than 0 or greater than 100 in all runs
    bad_blue_pol = df_spin_phys[df['polarblue'].apply(lambda x: any([pol < 0 or pol > 100 for pol in x]))]
    bad_yellow_pol = df_spin_phys[df['polaryellow'].apply(lambda x: any([pol < 0 or pol > 100 for pol in x]))]

    # Make a new column for bad blue and bad yellow polarizations in df
    df.loc[:, 'bad_blue_pol'] = 0
    df.loc[:, 'bad_yellow_pol'] = 0
    df.loc[df['runnumber'].isin(bad_blue_pol['runnumber']), 'bad_blue_pol'] = 1
    df.loc[df['runnumber'].isin(bad_yellow_pol['runnumber']), 'bad_yellow_pol'] = 1

    return df


def plot_events_vs_time(df):
    """
    Plot events vs time
    :param df:
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.plot(df['Start'], df['Events'], 'o')
    ax.set_ylabel('Number of Events in Run (Nominal)')
    ax.xaxis.set_major_formatter(DateFormatter('%b %-d'))
    ax.grid(True)
    ax.set_ylim(bottom=0)
    fig.tight_layout()


def plot_duration_vs_time(df):
    """
    Plot duration vs time
    :param df:
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.plot(df['Start'], df['duration'] / 60, 'o')
    ax.set_ylabel('Run Duration [min]')
    ax.xaxis.set_major_formatter(DateFormatter('%b %-d'))
    ax.grid(True)
    ax.set_ylim(bottom=0)
    fig.tight_layout()


def plot_event_num_hist(df, title=None):
    """
    Plot a histogram of the number of events in each run
    :param df:
    :param title:
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(df['Events'], bins=50)
    ax.set_xlabel('Number of Events')
    ax.set_ylabel('Number of Runs')
    if title:
        ax.set_title(title)
    fig.tight_layout()


def plot_duration_hist(df, title=None):
    """
    Plot a histogram of the duration of each run
    :param df:
    :param title:
    :return:
    """
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.hist(df['duration'] / 60, bins=50)
    ax.set_xlabel('Run Duration [min]')
    ax.set_ylabel('Number of Runs')
    if title:
        ax.set_title(title)
    fig.tight_layout()


if __name__ == '__main__':
    main()
