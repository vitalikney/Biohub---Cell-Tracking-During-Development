"""Build exp77-secft-n2.ipynb from cells/ (run from anywhere).

Same format as experiments/_lib/build_nb.py. Files named md_* become markdown cells. The worker file (w05_*) becomes a
`%%writefile /kaggle/working/exp77_worker.py` cell, so it stays a plain, testable .py file in the repo."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CELLS = [
    "md_00_intro.py",
    "c01_setup_v1.py",
    "c02_sanity_read_v1.py",
    "c03_splits_v1.py",
    "c04_exp77_inputs.py",
    "w05_exp77_worker.py",
    "c06_exp77_launch.py",
    "c07_exp77_sanity.py",
    "c08_exp77_export.py",
]
WRITEFILE = "%%writefile /kaggle/working/exp77_worker.py\n"


def build(out=HERE / "exp77-secft-n2.ipynb"):
    cells = []
    for name in CELLS:
        src = (HERE / "cells" / name).read_text(encoding="utf-8")
        if name.startswith("md_"):
            cells.append({"cell_type": "markdown", "metadata": {}, "source": src})
            continue
        if name.startswith("w05_"):
            src = WRITEFILE + src
        cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src})
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
          "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
    out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print("wrote", out, len(cells), "cells")


if __name__ == "__main__":
    build()
