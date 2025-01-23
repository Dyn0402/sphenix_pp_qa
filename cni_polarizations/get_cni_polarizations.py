#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on November 18 13:38 2024
Created in PyCharm
Created as sphenix_pp_qa/get_spin_stuff

@author: Dylan Neff, dn277127
"""


import requests
import re
import pandas as pd



def main():
    # get_from_site_csv()
    get_from_site_user()
    print('donzo')


def get_from_site_csv():
    url = 'https://www.cnipol.bnl.gov/fills/s/?rp=24&fn=&ft=&be=&mode=11&sb=Select'
    reread = False  # If True, reread file even if it exists
    html_file_path = 'cnipol_fills.html'
    df_out_path = 'cnipol_fills.csv'

    # Check if HTML file exists and read it if it does
    try:
        with open(html_file_path, 'r') as f:
            html_content = f.read()
            print('HTML read from file')
    except FileNotFoundError:
        html_content = None
        print('HTML file not found')

    if not html_content or reread:
        # Need to set up a proxy to BNL internal. In a separate terminal run:
        # "ssh <usrname>@cssh.rhic.bnl.gov -L 3128:batch3.phy.bnl.gov:3128"
        proxy = {
            "http": "http://localhost:3128",
            "https": "http://localhost:3128"
        }

        # Fetch and print the HTML content
        html_content = fetch_html(url, proxy=proxy)
        save_html_to_file(html_content, html_file_path)

    # Parse the HTML table into a DataFrame
    start_flag = '<table class="simple cntr" cellspacing=0 align=center>'
    html_content = html_content[html_content.find(start_flag) + len(start_flag):]

    # Get string between <pre> and </pre> tags
    html_content = html_content[html_content.find('<pre>') + len('<pre>'):html_content.find('</pre>')]

    df = extract_data_to_dataframe(html_content)

    df = convert_df(df)

    df = calculate_average_polarizations(df)

    # Save the DataFrame to a CSV file
    df.to_csv(df_out_path, index=False)


def get_from_site_user():
    url = 'https://www.cnipol.bnl.gov/fills/?rp=24&fn=&ft=&be=&mode=1&sb=Select'
    reread = False  # If True, reread file even if it exists
    html_file_path = 'cnipol_fills_user.html'
    df_out_path = 'cnipol_fills_user.csv'

    # Check if HTML file exists and read it if it does
    try:
        with open(html_file_path, 'r') as f:
            html_content = f.read()
            print('HTML read from file')
    except FileNotFoundError:
        html_content = None
        print('HTML file not found')

    if not html_content or reread:
        # Need to set up a proxy to BNL internal. In a separate terminal run:
        # "ssh <usrname>@cssh.rhic.bnl.gov -L 3128:batch3.phy.bnl.gov:3128"
        proxy = {
            "http": "http://localhost:3128",
            "https": "http://localhost:3128"
        }

        # Fetch and print the HTML content
        html_content = fetch_html(url, proxy=proxy)
        save_html_to_file(html_content, html_file_path)

    df = extract_user_data_to_dataframe(html_content)

    df = convert_df_user(df)

    # Save the DataFrame to a CSV file
    df.to_csv(df_out_path, index=False)


def fetch_html(url, proxy=None, params=None, headers=None):
    """
    Fetch the HTML content of a given URL.

    Parameters:
    - url (str): The URL to fetch.
    - proxy (dict, optional): A dictionary of proxies, e.g., {"http": "http://localhost:3128", "https": "http://localhost:3128"}.

    Returns:
    - str: HTML content of the page.
    """
    try:
        # Optional proxy support
        response = requests.get(url, proxies=proxy, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_data_to_dataframe(input_string):
    # Split the input into lines and remove any leading/trailing whitespace
    lines = input_string.strip().split('\n')

    # Extract column headers
    pre_header_parts = re.split(r'\s{2,}', lines[0].strip())  # the first line contains the pre-headers
    header_parts = re.split(r'\s{2,}', lines[1].strip())  # the second line contains the headers
    len_diff = len(header_parts) - len(pre_header_parts)
    header_parts[-len(pre_header_parts):] = [f'{pre_header_parts[i]} {header_parts[i + len_diff]}' for i in range(len(pre_header_parts))]
    headers = header_parts

    # Initialize a list to hold the data
    data = []

    # Iterate over the lines with data
    for line in lines[3:]:  # Data starts at line 4 (index 3)
        # Split the line into columns, assuming consistent spacing
        columns = re.split(r'\s{3,}', line.strip())  # Split on 2 or more spaces

        # If there are no actual data columns, continue to the next line
        if len(columns) < len(headers):
            continue

        # Append the row data to the data list
        data.append(columns)

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=headers)

    return df


def extract_user_data_to_dataframe(input_string):
    """
    Extract the data from the input string and return a DataFrame.
    :param input_string:
    :return:
    """
    start_flag = '<table class="simple cntr" cellspacing=0 align=center>'
    end_flag = '<th colspan=10>&nbsp;<br>&nbsp;'

    # Find the start and end of the table
    start_idx = input_string.find(start_flag)
    end_idx = input_string.find(end_flag)

    # Extract the table content
    table_content = input_string[start_idx:end_idx]
    table_lines = table_content.split('\n')

    headers, data, data_line = [], [], []
    is_header = False
    is_data = False
    found_headers = False
    blue_slope_error_code, yellow_slope_error_code = False, False
    for line in table_lines:
        if '<th ' in line:
            is_data = False
            is_header = True
        elif '<tr class=my_tr_highlight>' in line:
            is_header = False
            is_data = True
            if not found_headers and len(headers) > 0:
                headers.append('Blue Slope Error')
                headers.append('Yellow Slope Error')
                found_headers = True
            if len(data_line) > 0:
                data_line.append(blue_slope_error_code)
                data_line.append(yellow_slope_error_code)
                data.append(data_line)
                data_line = []
                blue_slope_error_code, yellow_slope_error_code = False, False

        if is_header:
            if not found_headers:
                if '<th ' in line:
                    if 'colspan' in line:
                        continue
                    header = re.sub(r'<.*?>', '', line).strip()
                    if 'bluPol' in line:
                        header = 'Blue ' + header
                    elif 'yelPol' in line:
                        header = 'Yellow ' + header
                    headers.append(header)
                    if 'Blue' in header or 'Yellow' in header:
                        headers.append(header + ' Error')
        elif is_data:
            if '<td ' in line:
                line = re.sub(r'<!--.*?-->', '', line)  # Remove HTML comments
                split_line = line.split('<td ')[1:]
                split_line = [re.sub(r'<[^>]*>', '', '<td ' + item).strip() for item in split_line]
                if 'Pol' in line:
                    if len(split_line) != 1:
                        print(f'Error: Expected 1 data column, found {len(split_line)}')
                    if split_line[0] in ['', '&nbsp;']:
                        data_line.append(pd.NA)
                        data_line.append(pd.NA)
                    else:
                        val, err = split_line[0].split('&nbsp;&plusmn;&nbsp;')
                        data_line.append(val)
                        data_line.append(err)
                    if "<span class='feature'>" in line:
                        if 'bluPol' in line:
                            blue_slope_error_code = True
                        elif 'yelPol' in line:
                            yellow_slope_error_code = True
                        else:
                            print(f'Error: Unexpected error code line: {line}')
                else:
                    data_line.extend(split_line)

    df = pd.DataFrame(data, columns=headers)

    return df


def convert_df(df):
    """
    Convert the string values in the DataFrame to appropriate data types.
    Also split columns with errors (dP/dT and P_0) into value and error columns.
    :param df:
    :return:
    """
    # Convert columns to appropriate data types
    df['Fill'] = df['Fill'].astype(int)

    for col in ['Start T', 'Stop T']:
        # Convert to numeric (integer) type first to avoid the warning
        df[col] = pd.to_numeric(df[col], errors='coerce')  # This converts strings to integers, coercing errors to NaN
        df[col] = pd.to_datetime(df[col], unit='s')  # Now convert to datetime

    # Convert the rest of the columns to float
    for col in ['Yellow dP/dT', 'Yellow P_0', 'Blue dP/dT', 'Blue P_0']:
        # Split using r'\s*\+\-\s*' and expand into two columns
        split_df = df[col].str.split(r'\s*\+\-\s*', expand=True)

        # Check if split results in two columns; if not, fill with NaN
        if split_df.shape[1] == 2:
            # Assign the first and second parts to the respective columns
            df[col] = split_df[0].astype(float)  # First part (value)
            df[col + ' Error'] = split_df[1].astype(float)  # Second part (error)
        else:
            # Handle the case where there are no errors (e.g., just a single value)
            df[col] = split_df[0].astype(float)
            df[col + ' Error'] = pd.NA  # If there's no second part, assign NaN to the error column

    return df


def convert_df_user(df):
    """
    Convert the string values in the DataFrame to appropriate data types.
    :param df:
    :return:
    """
    df['Fill'] = df['Fill'].astype(int)
    df['Beam Energy, GeV'] = df['Beam Energy, GeV'].astype(float)
    df['Physics On'] = pd.to_datetime(df['Physics On'], format='%b %d, %Y %H:%M:%S %a', errors='coerce')
    df['Fill Length'] = df['Fill Length'].apply(time_to_seconds)

    # For any column starting with Blue or Yellow convert to float
    for col in df.columns:
        if col.startswith('Blue') or col.startswith('Yellow'):
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def time_to_seconds(time_str):
    # Regular expression to capture hours, minutes, and seconds
    time_parts = re.match(r'(\d+)h:(\d+)m:(\d+)s', time_str)

    if time_parts:
        hours = int(time_parts.group(1))
        minutes = int(time_parts.group(2))
        seconds = int(time_parts.group(3))

        # Convert to seconds
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return None  # Return None if the format doesn't match


def calculate_average_polarizations(df):
    """
    Calculate the average polarizations for each fill.
    :param df:
    :return:
    """
    # Calculate fill durations in seconds
    df['Duration'] = (df['Stop T'] - df['Start T']).dt.total_seconds()

    # Calculate end polarizations using slope in percent per hour
    df['Yellow P_f'] = (df['Yellow dP/dT'] / 100 * df['Duration'] / 3600 + 1) * df['Yellow P_0']
    df['Blue P_f'] = (df['Blue dP/dT'] / 100 * df['Duration'] / 3600 + 1) * df['Blue P_0']

    # Calculate average polarizations
    df['Yellow P_avg'] = (df['Yellow P_0'] + df['Yellow P_f']) / 2
    df['Blue P_avg'] = (df['Blue P_0'] + df['Blue P_f']) / 2

    return df


def save_html_to_file(html, file_path):
    """
    Save the HTML content to a file.
    :param html:
    :param file_path:
    :return:
    """
    with open(file_path, 'w') as f:
        f.write(html)


def read_html_from_file(file_path):
    """
    Read the HTML content from a file.
    :param file_path:
    :return:
    """
    with open(file_path, 'r') as f:
        return f.read()


if __name__ == '__main__':
    main()
