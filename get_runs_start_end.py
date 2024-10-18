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


def main():
    """
    Pulls run information from the sPHENIX run database and writes it to a CSV file.
    Must be connected to campus network proxy to access the database.
    :return:
    """
    # Define the rl1 and rl2 variables
    rl1 = 40000  # Start run number
    rl2 = ''  # End run number. Leave empty to get all runs from rl1 to the latest run

    # Construct the URL with the parameters
    base_url = "http://www.sphenix-intra.bnl.gov:7815/cgi-bin/run_info.py"
    params = {
        "time_range": 0,
        "type": "any",
        "duration": "any",
        "magnet": "any",
        "rl1": rl1,
        "rl2": rl2
    }

    # Send a GET request to the URL
    response = requests.get(base_url, params=params)

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

        # Write the DataFrame to a CSV file
        df.to_csv('run_info.csv', index=False)

        # Display the DataFrame
        print(df)
    else:
        print(f"Error: Unable to retrieve data (status code: {response.status_code})")
    print('donzo')


if __name__ == '__main__':
    main()
