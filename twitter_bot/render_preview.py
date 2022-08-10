"""Renders a LaTeX document or equation to a high-quality .png image"""
from subprocess import DEVNULL, CalledProcessError, check_call
from PIL import Image
from typing import Union, List


def execute_silently(command: str, ignore_codes: List[int] = []) -> int:
    try:
        check_call(command.split(" "), stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL)
    except CalledProcessError as e:
        if e.returncode in ignore_codes:
            return

        import os

        os.system(command)  # Run again, this time showing output

        raise e


def render_preview(
    filename: str,
    margins=2,
    density=2000,
    scale=1,
    transparent=True,
    max_aspect_ratio: Union[float, None] = None,
    pdf_filename="preview",
    cropped_pdf_filename="preview.pdf",
    preview_filename="preview.png",
) -> None:
    execute_silently(f"pdflatex -jobname={pdf_filename} {filename}")
    execute_silently(
        f"pdfcrop --margins {margins} {pdf_filename} {cropped_pdf_filename}"
    )
    transparency_option = "" if transparent else "-alpha off"
    execute_silently(
        f"convert {transparency_option} -density {density} {cropped_pdf_filename} -scale {scale * 100}% {preview_filename}",
        ignore_codes=[1],
    )

    if max_aspect_ratio:
        height = None
        width = None
        with Image.open(preview_filename) as preview_image:
            height = preview_image.height
            width = preview_image.width
        if width / height > max_aspect_ratio:
            execute_silently(
                f"convert {preview_filename} -background white -thumbnail {width}x{int(width / max_aspect_ratio)}> -gravity center -extent {width}x{int(width / max_aspect_ratio)} {preview_filename}",
                ignore_codes=[1],
            )


def render_equation(equation: str, **kwargs) -> None:
    with open("tmp.tex", "w") as tex_file:
        tex_file.write(
            r"""\documentclass[preview,border=2pt]{standalone}
\usepackage{amsmath}
\begin{document}
\begin{equation*}
"""
        )
        tex_file.write(equation)
        tex_file.write(
            r"""
\end{equation*}
\end{document}"""
        )
    render_preview("tmp.tex", **kwargs)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--transparent", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    render_preview(args.file, transparent=args.transparent)
