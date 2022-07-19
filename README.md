## LaTeX to PNG

Using the method `render_preview` from `render_preview.py` you can transform a LaTeX document (stored in a file) into a PNG image. To increase the resolution you can increase the `density` parameter.

## BOINC result to LaTeX

You can simply run `boinc_result_to_tex.py` with a given BOINC result file as a parameter, e.g. `python3 boinc_result_to_tex.py RNM_general_001574`

## Get Latest BOINC results

You can run the `get_boinc_results.py` to update your local `boinc_results` folder with the current results available on the server. Then, you may run `generate_boinc_result_previews.py` in order to create preview PNGs for the BOINC results you have, using the BOINC result to LaTeX and LaTeX to PNG transformations.

## Twitter Bot

In order to operate the twitter bot, you must keep the `queue` folder non-empty. Every day at 8AM GHAT (GitHub Actions Time ;p) the alphabetically first file in the `queue` folder is turned into a tweet and moved to the `posted` folder.
