"""Assemble a Kaggle notebook from python source files. Usage: build_nb.py out.ipynb cell1.py [cell2.py ...]
A file whose name starts with 'md_' is inserted as a markdown cell."""
import json, sys
out, files = sys.argv[1], sys.argv[2:]
cells = []
for f in files:
    src = open(f, encoding="utf-8").read()
    name = f.replace("\\", "/").split("/")[-1]
    if name.startswith("md_"):
        cells.append({"cell_type": "markdown", "metadata": {}, "source": src})
    else:
        cells.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": src})
nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
json.dump(nb, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("wrote", out, len(cells), "cells")
