import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

def generate_report_assets(df, out_dir: Path):
    out_dir.mkdir(exist_ok=True, parents=True)

    plots = []
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols[:4]:
        safe = str(col).replace(" ", "_")
        file_path = out_dir / f"{safe}_hist.png"

        fig, ax = plt.subplots(figsize=(6, 3))
        df[col].dropna().hist(ax=ax, bins=20)
        ax.set_title(f"Distribution of {col}")

        fig.savefig(file_path)
        plt.close(fig)

        plots.append(file_path)

    return plots
