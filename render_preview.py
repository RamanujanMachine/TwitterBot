"""Renders a LaTeX document or equation to a high-quality .png image"""
import os


def render_preview(
    filename: str,
    margins=2,
    density=10000,
    scale=0.25,
    transparent=True,
    pdf_filename="preview",
    cropped_pdf_filename="preview.pdf",
    preview_filename="preview.png",
) -> None:
    os.system(f"pdflatex -jobname={pdf_filename} {filename}")
    os.system(f"pdfcrop --margins {margins} {pdf_filename} {cropped_pdf_filename}")
    transparency_option = "" if transparent else "-alpha off"
    os.system(
        f"magick convert {transparency_option} -density {density} {cropped_pdf_filename} -scale {scale * 100}% {preview_filename}"
    )


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()
    render_preview(args.filename)
