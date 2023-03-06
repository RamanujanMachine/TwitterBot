"""
This script unifies results gotten from https://rnma.xyz/boinc/result/
to a single file, and maintaines a readable form of them as a .md file
"""

from datetime import datetime
from get_boinc_results import get_webpage
import json
import os
import shutil
import smtplib
from boinc_result_to_tex import generate_tex_from_data
from render_preview import render_preview


# if __name__ == "__main__":
with open("all_boinc_results.json", "r") as result_file:
    # line format: [[an coeffs], [bn coeffs], limit, [filename]]
    previous_data = json.load(result_file)
loaded_filenames = set([i[-2] for i in previous_data])

current_data = {}
for table_row in get_webpage("https://rnma.xyz/boinc/result").split("</tr>")[3:-2]:
    table_cells = table_row.split("</td>")
    date = table_cells[2].split(">")[1].strip()
    name = table_cells[1].split(">")[-2].split("<")[0]
    current_data[name] = date

new_results = {}
for result_fn_on_server in current_data:
    try:
        if result_fn_on_server in loaded_filenames:
            # skip known results
            continue
        result_data = get_webpage("https://rnma.xyz/boinc/result/" + result_fn_on_server)
        result_data = json.loads(result_data)[0]
        tex = generate_tex_from_data(result_fn_on_server, result_data)[0]
        tex = tex.split('$')[1]
        tex = '\n$$' + tex + '$$\n'
        new_results[result_fn_on_server] = {
            'res_data': result_data,
            'tex': tex
        }
        
    except Exception as e:
        print('Error when processing result. Result details:')
        print(result)
        print(f'Error received:\n{e}')

import ipdb
ipdb.set_trace()
if len(new_results) == 0:
    print('No new results')
    exit()

added_tex = f'\n\n#{datetime.now().strftime("%d/%m/%y")}\n'
for res in new_results:
    added_tex += f'##{res}\n{new_results[res]["tex"]}'
    previous_data.append([
        new_results[res]['res_data'][0],
        new_results[res]['res_data'][1],
        new_results[res]['res_data'][2],
        res
        ])

with open("all_boinc_results.json", "w") as result_file:
    json.dump(previous_data, result_file)

with open("all_results.md", "a") as results_md:
    results_md.write(added_tex)
    