"""Figures for "Decided in the Bulk", in the site's house figure style.
Run: python figs.py   (needs matplotlib, numpy)
The plotting scripts and results live in the research bundle (code/noise-to-boundaries,
left unchanged so it still runs on its own). This file runs three of its plotting scripts on
the saved results, with the site's house figure style switched on, and copies the pictures here:
fig01 = plot_mnist.py, fig02 = plot_fine.py, fig03 = immse_compare.py."""
import os, runpy, shutil, sys, tempfile, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, str(next(p / "_figstyle" for p in pathlib.Path(__file__).resolve().parents if (p / "_figstyle").is_dir())))
import house; house.apply()

HERE = pathlib.Path(__file__).resolve().parent
BUNDLE = HERE / "code" / "noise-to-boundaries"
JOBS = [("plot_mnist.py", "mnist_beta.png", "fig01.png"),
        ("plot_fine.py", "mnist_fine.png", "fig02.png"),
        ("immse_compare.py", "immse_validation.png", "fig03.png")]

if __name__ == "__main__":
    for script, made, name in JOBS:
        with tempfile.TemporaryDirectory() as tmp:
            for f in (BUNDLE / "results").glob("*.json"):
                shutil.copy(f, tmp)
            cwd = os.getcwd(); os.chdir(tmp)
            try:
                runpy.run_path(str(BUNDLE / "src" / script), run_name="__main__")
            finally:
                os.chdir(cwd)
            shutil.copy(pathlib.Path(tmp) / made, HERE / "figures" / name)
            plt.close("all")
