#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on December 13 2:06 PM 2024
Created in PyCharm
Created as sphenix_pp_qa/get_detailed_cni_polarizations.py

@author: Dylan Neff, Dylan
"""

from bs4 import BeautifulSoup
import pandas as pd

from get_cni_polarizations import fetch_html


def main():
    url = 'https://www.cnipol.bnl.gov/rundb/'

    run_csv_options = {'rp': '24'}
    db_file_name = 'cni_measurement_list.csv'
    read_db_from_web = True

    measurement_page_options = {'runid': None}

    proxy = {
        "http": "http://localhost:3128",
        "https": "http://localhost:3128"
    }

    if read_db_from_web:
        get_run_csv(url, run_csv_options, proxy, db_file_name)

    rundb = pd.read_csv(db_file_name)
    print(rundb)

    new_df = []
    for run_name in rundb['run_name']:
        print(run_name)
        measurement_page_options['runid'] = run_name
        measurements = get_measurement_page(url, measurement_page_options, proxy)
        new_df.append({'run_name': run_name, 'polarimeter': measurements[3], 'total_str': measurements[2],
                       'bunch_fill_pattern': measurements[0], 'bunch_spin_pattern': measurements[1]})

    new_df = pd.DataFrame(new_df)

    # merge new_df with rundb on run_name
    rundb = pd.merge(rundb, new_df, on='run_name', how='left')
    print(rundb)

    rundb.to_csv('cni_measurements.csv', index=False)

    print('donzo')


def get_measurement_page(url, options, proxy):
    res_text = fetch_html(url, proxy=proxy, params=options)
    bunch_fill_pattern, bunch_spin_pattern, total_str, polarimeter = scrape_bunch_patterns(res_text)
    return bunch_fill_pattern, bunch_spin_pattern, total_str, polarimeter


def get_run_csv(base_url, options, proxy, file_name):
    url = base_url + 'export.php'
    res_text = fetch_html(url, proxy=proxy, params=options)
    with open(file_name, 'w') as file:
        file.write(res_text)


def scrape_bunch_patterns(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Get polarimeter
    polarimeter = None
    pol_section = soup.find('b', text='Polarimeter:')
    if pol_section:
        polarimeter = pol_section.find_next('span').text.strip()

    # Find the relevant section using the Bunch fill pattern label
    fill_spin_pattern_section = soup.find('b', text='Bunch fill pattern:')
    bunch_fill_pattern, bunch_spin_pattern, total_str = None, None, None

    if fill_spin_pattern_section:
        fill_spin_pattern_text = fill_spin_pattern_section.find_next('td', class_='align_cm').text.strip()
        fill_spin_pattern_text = fill_spin_pattern_text.split('\n')
        bunch_fill_pattern = fill_spin_pattern_text[0].strip()
        total_str = fill_spin_pattern_text[2].replace('Bunch spin pattern: Total −/0/+:', '').strip()
        bunch_spin_pattern = fill_spin_pattern_text[-1].strip()

    return bunch_fill_pattern, bunch_spin_pattern, total_str, polarimeter


if __name__ == '__main__':
    main()
