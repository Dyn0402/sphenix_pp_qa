#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on January 23 08:11 2025
Created in PyCharm
Created as sphenix_pp_qa/get_hjet_from_root_files

@author: Dylan Neff, dn277127
"""
import os

import pandas as pd
import uproot


def main():
    hjet_dir_path = '/gpfs02/eic/cnipol/jet_run24/results/'
    df_name = 'hjet_gpfs_pol_info.csv'
    df = []
    for dir_name in os.listdir(hjet_dir_path):
        if 'fill_' not in dir_name:
            continue
        fill = int(dir_name.split('_')[-1])
        root_path = f'{hjet_dir_path}fill_{fill}/DST_{fill}.root'
        print(f'Opening {root_path}')
        with uproot.open(root_path) as file:
            yellow_spin_pattern = file['h_polYellow'].to_numpy()[0].tolist()
            blue_spin_pattern = file['h_polBlue'].to_numpy()[0].tolist()
            results = file['h_results']
            res_vals, res_errs = results.values(), results.errors()
            yellow_an, blue_an = res_vals[6], res_vals[7]
            yellow_an_err, blue_an_err = res_errs[6], res_errs[7]
            yellow_pol, blue_pol = res_vals[8], res_vals[9]
            yellow_pol_err, blue_pol_err = res_errs[8], res_errs[9]
            df.append({'Fill': fill, 'Blue Spin Pattern': blue_spin_pattern, 'Yellow Spin Pattern': yellow_spin_pattern,
                       'Blue A_N': blue_an, 'Blue A_N Err': blue_an_err, 'Yellow A_N': yellow_an, 'Yellow A_N Err': yellow_an_err,
                       'Blue P_B': blue_pol, 'Blue P_B Err': blue_pol_err, 'Yellow P_B': yellow_pol, 'Yellow P_B Err': yellow_pol})

    df = pd.DataFrame(df)
    for col in df.columns:
        if ('Blue' in col or 'Yellow' in col or 'Fill' in col) and 'Pattern' not in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.to_csv(df_name, index=False)

    print('donzo')


if __name__ == '__main__':
    main()
