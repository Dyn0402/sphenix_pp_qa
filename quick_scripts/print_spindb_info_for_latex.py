#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on February 13 13:51 2025
Created in PyCharm
Created as sphenix_pp_qa/print_spindb_info_for_latex

@author: Dylan Neff, dn277127
"""

import subprocess


def main():
    # Database connection details
    dbname = "spinDB"
    table_name = "spin"

    # SQL query to get column names and data types
    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position;
    """

    # Run the psql command using subprocess and capture the output
    command = f"psql -d {dbname} -c \"{query}\" -t -A"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Split the output into lines
    lines = result.stdout.strip().split("\n")

    # Start LaTeX table code
    latex_code = "\\begin{table}[ht]\n\\centering\n\\begin{tabular}{|l|l|}\n\\hline\n"
    latex_code += "Column Name & Data Type \\\\ \\hline\n"

    # Process each line of the result
    for line in lines:
        line = line.strip().split("|")
        if len(line) != 2:
            print(f"Skipping line: {line}")
            continue
        column_name, data_type = line  # Output columns are separated by '|'
        column_name = column_name.strip()
        data_type = data_type.strip()
        latex_code += f"{column_name} & {data_type} \\\\ \\hline\n"

    latex_code += "\\end{tabular}\n\\caption{Table structure of '" + table_name + "'}\n\\end{table}"

    # Print the LaTeX code
    print(latex_code)
    print('donzo')


if __name__ == '__main__':
    main()
