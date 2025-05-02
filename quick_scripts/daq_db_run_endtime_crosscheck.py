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

    print('donzo')


if __name__ == '__main__':
    main()
