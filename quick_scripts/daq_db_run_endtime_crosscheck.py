#!/usr/bin/env python3
# -- coding: utf-8 --
"""
Created on May 02 1:58 PM 2025
Created in PyCharm
Created as sphenix_pp_qa/daq_db_run_endtime_crosscheck.py

@author: Dylan Neff, dylan
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2


def main():
    # get_db_csv()
    # get_full_dbs_csv()
    # analyze_short_csv()
    analyze_full_db_csvs()
    # analyze_run_db_csv()
    print('donzo')


def analyze_run_db_csv():
    run_csv_path = "/home/dylan/Desktop/pp_qa/run.csv"
    df = pd.read_csv(run_csv_path)
    print(df)
    print(df.columns)

    # Get rows where ertimestamp is null
    df_null_endtimes = df[df['ertimestamp'].isnull()]
    print(df_null_endtimes)

    # Make histogram of entries per runtype
    runtype_counts = df['runtype'].value_counts()
    plt.figure(figsize=(10, 6))
    plt.bar(runtype_counts.index, runtype_counts.values, color='blue', alpha=0.7)
    plt.title('Histogram of Run Types')
    plt.xlabel('Run Type')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    # plt.yscale('log')
    plt.tight_layout()

    # Make histogram of entries vs runnumber (binned)
    plt.figure(figsize=(10, 6))
    binning = np.linspace(0, 60000, 100)

    # Group run numbers by runtype
    runtype_groups = df.groupby('runtype')['runnumber'].apply(list)

    # Prepare data for stacked histogram
    data = [runtype_groups[r] for r in runtype_groups.index]
    labels = runtype_groups.index

    plt.hist(data, bins=binning, stacked=True, label=labels, alpha=0.7)
    plt.title('Stacked Histogram of Run Numbers by Runtype')
    plt.xlabel('Run Number')
    plt.ylabel('Frequency')
    plt.legend(title='Runtype')
    plt.tight_layout()

    plt.show()


def analyze_full_db_csvs():
    # base_path = "/home/dylan/Desktop/pp_qa/"
    base_path = "/local/home/dn277127/Bureau/pp_qa/"
    run_csv_path = f"{base_path}run.csv"
    filelist_csv_path = f"{base_path}filelist.csv"
    run_df = pd.read_csv(run_csv_path)
    filelist_df = pd.read_csv(filelist_csv_path)

    # Ensure datetime types
    run_df['ertimestamp'] = pd.to_datetime(run_df['ertimestamp'])
    filelist_df['mtime'] = pd.to_datetime(filelist_df['mtime'])

    # Get max mtime for each runnumber
    max_mtime_df = filelist_df.groupby('runnumber')['mtime'].max().reset_index()
    max_mtime_df.rename(columns={'mtime': 'max_mtime'}, inplace=True)

    # Get GL1_ mtime (use max in case there are multiple GL1_ files per run)
    gl1_df = filelist_df[filelist_df['filename'].str.contains('GL1_', na=False)]
    gl1_mtime_df = gl1_df.groupby('runnumber')['mtime'].max().reset_index()
    gl1_mtime_df.rename(columns={'mtime': 'gl1_mtime'}, inplace=True)

    # Merge with run_df
    merged_df = run_df.merge(max_mtime_df, on='runnumber', how='left')
    merged_df = merged_df.merge(gl1_mtime_df, on='runnumber', how='left')

    # Choose gl1_mtime when available, else fallback to max_mtime
    merged_df['preferred_mtime'] = merged_df['gl1_mtime'].combine_first(merged_df['max_mtime'])

    # # Merge with run_df
    # merged_df = pd.merge(run_df, max_mtime_df, on='runnumber', how='left')

    # Compute difference in seconds
    merged_df['time_diff'] = (merged_df['max_mtime'] - merged_df['ertimestamp']).dt.total_seconds()
    time_diffs = merged_df[(merged_df['runnumber'] > 40000) & (merged_df['runnumber'] < 52000)]['time_diff'].dropna()

    merged_df['time_diff_gl1'] = (merged_df['preferred_mtime'] - merged_df['ertimestamp']).dt.total_seconds()
    time_diffs_gl1 = merged_df[(merged_df['runnumber'] > 40000) & (merged_df['runnumber'] < 52000)]['time_diff_gl1'].dropna()

    # Plot histogram
    plt.figure(figsize=(10, 6))
    binning = np.arange(-20.5, 50.5, 1)
    plt.hist(time_diffs, bins=binning, color='blue', alpha=0.7, label='max_mtime')
    plt.hist(time_diffs_gl1, bins=binning, color='red', alpha=0.7, label='gl1_mtime')
    # Count overflow and underflow and make annotation
    underflow_count_maxmtime = np.sum(time_diffs < binning[0])
    overflow_count_maxmtime = np.sum(time_diffs > binning[-1])
    underflow_count_gl1 = np.sum(time_diffs_gl1 < binning[0])
    overflow_count_gl1 = np.sum(time_diffs_gl1 > binning[-1])
    plt.annotate(f'Max mtime:\nUnderflow: {underflow_count_maxmtime}\nOverflow: {overflow_count_maxmtime}', xy=(0.8, 0.95), va='top',
                    xycoords='axes fraction', fontsize=12, bbox=dict(boxstyle='round', fc='white', ec='black', lw=1))
    plt.annotate(f'Max gl1:\nUnderflow: {underflow_count_gl1}\nOverflow: {overflow_count_gl1}', xy=(0.6, 0.95), va='top',
                 xycoords='axes fraction', fontsize=12, bbox=dict(boxstyle='round', fc='white', ec='black', lw=1))
    plt.title('Histogram of Time Difference between Latest Filelist mtimes and Run End Times')
    plt.xlabel('ertimestamp - latest_mtime (seconds)')
    plt.ylabel('Runs')
    plt.legend()
    plt.yscale('log')
    plt.tight_layout()
    plt.show()


def analyze_short_csv():
    output_csv_path = "/home/dylan/Desktop/pp_qa/run_vs_filelist_times.csv"
    df = pd.read_csv(output_csv_path)
    print(df)

    # Parse datetime strings (no unit needed)
    df['ertimestamp'] = pd.to_datetime(df['ertimestamp'])
    df['latest_mtime'] = pd.to_datetime(df['latest_mtime'])

    # Compute time difference in seconds
    df['time_diff'] = (df['latest_mtime'] - df['ertimestamp']).dt.total_seconds()

    time_diffs = df[(df['runnumber'] > 40000) & (df['runnumber'] < 52000)]['time_diff'].dropna()

    # Plot histogram
    plt.figure(figsize=(10, 6))
    binning = np.linspace(-20, 360, 201)
    plt.hist(time_diffs, bins=binning, color='blue', alpha=0.7)
    # Count overflow and underflow and make annotation
    underflow_count = np.sum(time_diffs < binning[0])
    overflow_count = np.sum(time_diffs > binning[-1])
    plt.annotate(f'Underflow: {underflow_count}\nOverflow: {overflow_count}', xy=(0.8, 0.95), va='top',
                 xycoords='axes fraction', fontsize=12, bbox=dict(boxstyle='round', fc='white', ec='black', lw=1))
    plt.title('Histogram of Time Difference between Latest Filelist mtimes and Run End Times')
    plt.xlabel('latest_mtime - ertimestamp (seconds)')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.show()


def get_db_csv():
    # Database connection parameters
    host = "sphnxdaqdbreplica1.sdcc.bnl.gov"
    database = "daq"
    user = "phnxrc"
    password = ""  # Prompt securely or fill in if safe

    output_csv_path = "run_vs_filelist_times.csv"

    query = """
            SELECT r.runnumber, \
                   r.ertimestamp, \
                   f.latest_mtime
            FROM run r
                     LEFT JOIN (SELECT runnumber, MAX(mtime) AS latest_mtime \
                                FROM filelist \
                                GROUP BY runnumber) f ON r.runnumber = f.runnumber
            WHERE r.runnumber > 21920
            ORDER BY r.runnumber; \
            """

    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password  # You can prompt using getpass.getpass()
        )

        df = pd.read_sql_query(query, connection)
        df.to_csv(output_csv_path, index=False)
        print(f"Exported to {output_csv_path}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


def get_full_dbs_csv():
    # Database connection parameters
    host = "sphnxdaqdbreplica1.sdcc.bnl.gov"
    database = "daq"
    user = "phnxrc"
    password = ""  # Leave empty or prompt securely if needed

    # Output CSV paths
    filelist_csv_path = "filelist.csv"
    run_csv_path = "run.csv"

    def export_table_to_csv(connection, table_name, output_csv_path):
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql_query(query, connection)
        df.to_csv(output_csv_path, index=False)
        print(f"Exported {table_name} to {output_csv_path}")

    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password  # You can use getpass.getpass() if you want to prompt
        )

        # Export tables to CSV
        export_table_to_csv(connection, "filelist", filelist_csv_path)
        export_table_to_csv(connection, "run", run_csv_path)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()


def export_table_to_csv(connection, table_name, output_csv_path):
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, connection)
    df.to_csv(output_csv_path, index=False)
    print(f"Exported {table_name} to {output_csv_path}")


if __name__ == '__main__':
    main()
