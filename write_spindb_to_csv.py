#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 31 6:28 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/write_spindb_to_csv.py

@author: Dylan Neff, Dylan
"""

import pandas as pd
import psycopg2


def main():
    # Configuration for PostgreSQL connection
    db_config = {
        "dbname": "spinDB",
        "user": "phnxrc",
    }

    # Specify the table name and output CSV file path
    table_name = "spin"
    output_csv_path = "spin_db.csv"

    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_config)

        # Load the table into a DataFrame
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql(query, conn)

        # Write DataFrame to a CSV file
        df.to_csv(output_csv_path, index=False)

        print(f"Data from {table_name} has been written to {output_csv_path}")

    except Exception as e:
        print("An error occurred:", e)

    finally:
        # Close the connection
        if conn:
            conn.close()
    print('donzo')


if __name__ == '__main__':
    main()
