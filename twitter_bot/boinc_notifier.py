"""A short script to notify the Ramanujan Machine team about new results from BOINC"""

from datetime import datetime
from get_boinc_results import get_webpage


if __name__ == "__main__":
    import json
    import os
    import shutil
    import smtplib
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
        try:
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
        except Exception as e:
            print('Error when processing result. Result details:')
            print(result)
            print(f'Error received:\n{e}')

    if len(preview_images) == 0:
        print("No new results to send!")
        exit(-1)
    with open("notified_results.json", "w") as notified_results_file:
        json.dump(current_data, notified_results_file)

    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg["Subject"] = f"Daily Update: {datetime.now().strftime('%d/%m/%y')}"
    msg["From"] = f"RM Notifier <{os.environ['MAIL_USERNAME']}>"
    msg["To"] = "ramanujanmachine@gmail.com"

    for file in preview_images:
        with open(file, "rb") as fp:
            img = MIMEImage(fp.read())
        img.add_header(
            "Content-Disposition", "attachment; filename= %s" % file.split("/")[-1]
        )
        msg.attach(img)

    try:
        s = smtplib.SMTP(os.environ["MAIL_SERVER"], 587)
    except Exception as e:
        s = smtplib.SMTP_SSL(os.environ["MAIL_SERVER"], 465)
    s.ehlo()
    s.starttls()
    s.login(os.environ["MAIL_USERNAME"], os.environ["MAIL_PASSWORD"])
    s.sendmail(
        os.environ["MAIL_USERNAME"], "ramanujanmachine@gmail.com", msg.as_string()
    )
    s.quit()
