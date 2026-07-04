#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter


PAGE_ONE_REDACTIONS = [
    # Hide the Ph.D. Grant / ANID entry in Grants and Fellowships.
    # Coordinates are PDF points measured from the top-left of an A4 page.
    (36, 770, 560, 806),
]


def render_pdf(input_pdf: Path, output_prefix: Path, dpi: int) -> None:
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        bundled = Path(
            "/Users/ibrito/.cache/codex-runtimes/"
            "codex-primary-runtime/dependencies/bin/pdftoppm"
        )
        pdftoppm = str(bundled) if bundled.exists() else None

    if pdftoppm is None:
        raise RuntimeError("pdftoppm is required to create the public CV PDF")

    subprocess.run(
        [pdftoppm, "-r", str(dpi), "-png", str(input_pdf), str(output_prefix)],
        check=True,
    )


def blur_box(image: Image.Image, box_pts: tuple[int, int, int, int], dpi: int) -> None:
    scale = dpi / 72
    box = tuple(round(value * scale) for value in box_pts)
    cropped = image.crop(box)
    blurred = cropped.filter(ImageFilter.GaussianBlur(radius=18))
    image.paste(blurred, box)


def build_public_cv(input_pdf: Path, output_pdf: Path, dpi: int) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        prefix = tmpdir / "page"
        render_pdf(input_pdf, prefix, dpi)

        page_paths = sorted(tmpdir.glob("page-*.png"))
        if not page_paths:
            raise RuntimeError(f"No pages rendered from {input_pdf}")

        pages: list[Image.Image] = []
        for index, page_path in enumerate(page_paths):
            image = Image.open(page_path).convert("RGB")
            if index == 0:
                for box in PAGE_ONE_REDACTIONS:
                    blur_box(image, box, dpi)
            pages.append(image)

        output_pdf.parent.mkdir(parents=True, exist_ok=True)
        first_page, remaining_pages = pages[0], pages[1:]
        first_page.save(
            output_pdf,
            "PDF",
            resolution=dpi,
            save_all=True,
            append_images=remaining_pages,
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()

    build_public_cv(args.input_pdf, args.output_pdf, args.dpi)


if __name__ == "__main__":
    main()
