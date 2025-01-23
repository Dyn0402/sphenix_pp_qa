#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on January 23 04:58 2025
Created in PyCharm
Created as sphenix_pp_qa/get_hjet_from_wiki

@author: Dylan Neff, dn277127
"""

from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd

from get_cni_polarizations import fetch_html


def main():
    base_url = 'https://wiki.bnl.gov/rhicspin/Polarimetry/H-jet/'
    run_name = 'Run24pp'
    url = f'{base_url}{run_name}'
    df_file_name = f'hjet_wiki_pol_info.csv'
    download = True

    if download:
        hjet_df = scrape_hjet_info_from_wiki(url)
        hjet_df = split_val_err(hjet_df)
        # Save the H-jet information to a csv file
        hjet_df.to_csv(df_file_name, index=False)
    else:
        hjet_df = pd.read_csv(df_file_name)

    unpolarized_rows = hjet_df[hjet_df['Comments'].str.contains('unpolarized', na=False)]
    unpolarized_runs = unpolarized_rows['Fill'].tolist()
    print(unpolarized_runs)
    print(hjet_df[(~hjet_df['Comments'].str.contains('unpolarized', na=False) & (hjet_df['Comments'] != ''))])

    print('donzo')


def scrape_hjet_info_from_wiki(url):
    """
    Scrapes the H-jet information from the wiki page for the specified run.
    :param url:
    :return:
    """
    res_text = fetch_html(url)

    soup = BeautifulSoup(res_text, 'html.parser')

    table = soup.find('table')
    rows = table.find_all('tr')
    data = []
    for row in rows:
        cols = row.find_all(['td', 'th'])
        cols = [ele.text.strip() for ele in cols]
        data.append(cols)

    # Append Blue and Yellow to the beginning of data[1]
    an_pb = ['Blue ' + x for x in data[1][:2]] + ['Yellow ' + x for x in data[1][2:]]
    headers = data[0][:2] + an_pb + [data[0][-1]]
    data = data[2:]

    df = pd.DataFrame(data, columns=headers)

    return df


def split_val_err(hjet_df):
    """
    For columns in list, split the value and error into separate columns from plus minus separator.
    :param hjet_df:
    :return:
    """
    split_cols = ['Blue A_N', 'Blue P_B', 'Yellow A_N', 'Yellow P_B']
    for col in split_cols:
        hjet_df[col + ' Err'] = hjet_df[col].str.split('±').str[1].str.strip()
        hjet_df[col] = hjet_df[col].str.split('±').str[0].str.strip()

    return hjet_df


if __name__ == '__main__':
    main()
