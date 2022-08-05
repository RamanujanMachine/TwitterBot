if __name__ == "__main__":
    import os
    import shutil
    from boinc_result_to_tex import generate_tex
    from render_preview import render_preview

    for f in os.listdir("boinc_results"):
        if not f.startswith("RNM") or os.path.splitext(f)[1] != "":
            continue
        if "zeta4" in f:
            continue
        # print("Generating TeX for " + f)
        try:
            with open("result.tex", "w") as result_file:
                result_file.write(generate_tex(os.path.join("boinc_results", f)))
        except:
            print("Failed! " + f)
            continue
        # print("Rendering PNG for " + f)
        render_preview("result.tex")
        shutil.move("preview.png", os.path.join("boinc_results", f + ".png"))
