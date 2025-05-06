#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 06 14:42 2025
Created in PyCharm
Created as sphenix_pp_qa/fill_missing_run_ends_daq_db

@author: Dylan Neff, dn277127
"""

import psycopg2


def main():
    first_run = 40000
    last_run = 53000
    runtype = 'physics'
    max_duration = 60 * 60 * 3  # in seconds
    update_database = False  # WARNING: If True, this will update the database! Otherwise, just print proposed changes.

    # Database connection parameters
    # host = "localhost"
    host = "sphnxdaqdbreplica1.sdcc.bnl.gov"
    database = "daq"
    user = "phnxrc"
    password = ""  # fill in your actual password if needed

    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        connection.autocommit = False
        cursor = connection.cursor()

        # Get runnumbers in range with missing ertimestamp
        cursor.execute("""
            SELECT runnumber FROM run 
            WHERE ertimestamp IS NULL 
              AND runnumber BETWEEN %s AND %s
              AND runtype = %s;
        """, (first_run, last_run, runtype))
        runs_to_update = cursor.fetchall()

        for (runnumber,) in runs_to_update:
            # Try to get mtime of 'GL1_' file
            cursor.execute("""
                SELECT mtime FROM filelist
                WHERE runnumber = %s AND filename LIKE '%%GL1_%%'
                ORDER BY mtime DESC LIMIT 1;
            """, (runnumber,))
            result = cursor.fetchone()

            fallback = False
            if result and result[0]:
                chosen_mtime = result[0]
            else:
                # Fallback: latest mtime
                fallback = True
                cursor.execute("""
                    SELECT mtime FROM filelist
                    WHERE runnumber = %s
                        AND mtime IS NOT NULL
                    ORDER BY mtime DESC LIMIT 1;
                """, (runnumber,))
                result = cursor.fetchone()
                chosen_mtime = result[0] if result else None

            if not chosen_mtime:
                print(f"No mtime found for run {runnumber}, skipping.")
                continue

            # Get brtimestamp
            cursor.execute("""
                SELECT brtimestamp FROM run WHERE runnumber = %s;
            """, (runnumber,))
            result = cursor.fetchone()

            if not result or result[0] is None:
                print(f"No brtimestamp for run {runnumber}, skipping.")
                continue

            brtimestamp = result[0]
            duration = (chosen_mtime - brtimestamp).total_seconds()

            if duration > max_duration:
                print(f"Run {runnumber} duration {duration:.0f}s exceeds max {max_duration}s, skipping.")
                continue

            # Update ertimestamp
            if update_database:
                cursor.execute("""
                    UPDATE run SET ertimestamp = %s WHERE runnumber = %s;
                """, (chosen_mtime, runnumber))
            fallback_str = " no GL1, " if fallback else " "
            duration_str = format_duration(duration)
            update_str = 'Updated ' if update_database else 'Proposed update --> '
            print(f"{update_str}run {runnumber} with{fallback_str}ertimestamp {chosen_mtime} (duration {duration_str})")

        connection.commit()
        print("Valid ertimestamps updated successfully.")

    except Exception as e:
        print(f"Error: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            cursor.close()
            connection.close()
        print('Done.')


def format_duration(seconds):
    seconds = int(seconds)
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")

    return ' '.join(parts)


if __name__ == '__main__':
    main()
