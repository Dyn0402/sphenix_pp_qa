#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on October 18 1:54 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/get_runs_start_end.py

@author: Dylan Neff, Dylan
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import pytz


def main():
    """
    Pulls run information from the sPHENIX run database and writes it to a CSV file.
    Must be connected to campus network proxy to access the database --> ssh sph-tunnel to 3128 batch3.phy.bnl.gov:3128
    :return:
    """
    # Define the rl1 and rl2 variables
    rl1 = 40000  # Start run number
    rl2 = ''  # End run number. Leave empty to get all runs from rl1 to the latest run

    # Timezone for New York
    ny_tz = pytz.timezone('America/New_York')

    # Construct the URL with the parameters
    base_url = "http://www.sphenix-intra.bnl.gov:7815/cgi-bin/run_info.py"
    proxies = {
        "http": "http://localhost:3128",
        "https": "http://localhost:3128"
    }

    params = {
        "time_range": 0,
        "type": "any",
        "duration": "any",
        "magnet": "any",
        "rl1": rl1,
        "rl2": rl2
    }
    # Send a GET request to the URL
    response = requests.get(base_url, params=params, proxies=proxies)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the table
        table = soup.find('table', {'border': '1'})

        # Extract the headers
        headers = [header.text for header in table.find_all('th')]

        # Extract the rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip the header row
            cells = [cell.text for cell in row.find_all('td')]
            rows.append(cells)

        # Create a pandas DataFrame
        df = pd.DataFrame(rows, columns=headers)

        # Drop the 'Trigger' and 'Zero Suppressed' columns
        df = df.drop(columns=['Trigger', 'Zero Suppressed'])

        # Function to convert valid datetime strings to timezone-aware, or return NaT for invalid entries
        def convert_to_timezone_aware(time_str):
            try:
                # Try to parse the datetime and localize it to New York timezone
                return ny_tz.localize(pd.to_datetime(time_str))
            except ValueError:
                # If parsing fails, return NaT (Not a Time)
                return pd.NaT

        # Apply the conversion function to 'Start' and 'End' columns
        df['Start'] = df['Start'].apply(convert_to_timezone_aware)
        df['End'] = df['End'].apply(convert_to_timezone_aware)

        # Write the DataFrame to a CSV file
        df.to_csv('run_info.csv', index=False)

        # Display the DataFrame
        print(df)
    else:
        print(f"Error: Unable to retrieve data (status code: {response.status_code})")
    print('donzo')


if __name__ == '__main__':
    main()
