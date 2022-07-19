if __name__ == "__main__":
    import os
    import shutil
    from boinc_result_to_tex import generate_tex
    from render_preview import render_preview, execute_silently

    for f in os.listdir("boinc_results"):
        if not f.startswith("RNM") or os.path.splitext(f)[1] != "":
            continue
        print("Generating TeX for " + f)
        try:
            generate_tex(os.path.join("boinc_results", f))
        except:
            print("Failed!")
            continue
        print("Rendering PNG for " + f)
        render_preview("result.tex")
        shutil.move("preview.png", os.path.join("boinc_results", f + ".png"))
