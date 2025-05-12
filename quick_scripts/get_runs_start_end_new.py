#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 12 15:36 2025
Created in PyCharm
Created as sphenix_pp_qa/get_runs_start_end_new

@author: Dylan Neff, dn277127
"""

import psycopg2
import pandas as pd
from datetime import timedelta


def main():
    first_run = 40000
    last_run = 53000
    runtype = 'physics'
    max_duration = 60 * 60 * 3  # in seconds

    host = "sphnxdaqdbreplica1.sdcc.bnl.gov"
    database = "daq"
    user = "phnxrc"
    password = ""  # if needed

    rows = []

    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        connection.autocommit = False
        cursor = connection.cursor()

        # Get all runs in range (even those with ertimestamp set, we recalculate)
        cursor.execute("""
            SELECT runnumber, runtype, brtimestamp, eventsinrun 
            FROM run 
            WHERE runnumber BETWEEN %s AND %s AND marked_invalid != 1 AND runtype = %s;
        """, (first_run, last_run, runtype))
        run_list = cursor.fetchall()

        for runnumber, runtype, brtimestamp, eventsinrun in run_list:
            # Skip if brtimestamp is missing
            if brtimestamp is None:
                print(f"No brtimestamp for run {runnumber}, skipping.")
                continue

            # Try to get mtime of 'GL1_' file
            cursor.execute("""
                SELECT mtime FROM filelist
                WHERE runnumber = %s AND filename LIKE '%%GL1_%%'
                ORDER BY mtime DESC LIMIT 1;
            """, (runnumber,))
            result = cursor.fetchone()

            fallback = False
            if result and result[0]:
                endtime = result[0]
            else:
                fallback = True
                cursor.execute("""
                    SELECT mtime FROM filelist
                    WHERE runnumber = %s AND mtime IS NOT NULL
                    ORDER BY mtime DESC LIMIT 1;
                """, (runnumber,))
                result = cursor.fetchone()
                endtime = result[0] if result else None

            if not endtime:
                print(f"No mtime found for run {runnumber}, skipping.")
                continue

            # Skip very long runs
            duration_seconds = (endtime - brtimestamp).total_seconds()
            if duration_seconds > max_duration:
                print(f"Run {runnumber} duration {duration_seconds:.0f}s exceeds max {max_duration}s, skipping.")
                continue

            # Collect data
            run_length = str(endtime - brtimestamp)
            rows.append({
                'Runnumber': runnumber,
                'Type': runtype,
                'Start': brtimestamp,
                'End': endtime,
                'Run Length': run_length,
                'Events': eventsinrun
            })

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

    # Write to CSV
    df = pd.DataFrame(rows)
    df = df.sort_values(by='Runnumber')
    df.to_csv('corrected_run_data.csv', index=False)
    print("CSV written to 'corrected_run_data.csv'")


if __name__ == '__main__':
    main()

