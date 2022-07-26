"""A short script to notify the Ramanujan Machine team about new results from BOINC"""

from get_boinc_results import get_available_results, get_webpage


if __name__ == "__main__":
    import json
    import os
    import shutil
    from boinc_result_to_tex import generate_tex
    from render_preview import render_preview

    previous_data = {}
    with open("notified_results.json", "r") as notified_results_file:
        previous_data = json.load(notified_results_file)

    current_data = {}
    for table_row in get_webpage("https://rnma.xyz/boinc/result").split("</tr>")[3:-2]:
        table_cells = table_row.split("</td>")
        date = table_cells[2].split(">")[1].strip()
        name = table_cells[1].split(">")[-2].split("<")[0]
        current_data[name] = date

    preview_images = []
    for result in current_data:
        if result not in previous_data or current_data[result] != previous_data[result]:
            result_filename = os.path.join("boinc_results", result)
            with open(result_filename, "w") as result_file:
                result_file.write(
                    get_webpage("https://rnma.xyz/boinc/result/" + result)
                )
            with open("result.tex", "w") as result_file:
                result_file.write(generate_tex(result_filename)[0])
            render_preview("result.tex")
            preview_filename = os.path.join("boinc_results", result + ".png")
            shutil.move("preview.png", preview_filename)
            preview_images.append(preview_filename)

    print(preview_images)
    with open("notified_results.json", "w") as notified_results_file:
        json.dump(current_data, notified_results_file)
