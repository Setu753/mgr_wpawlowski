import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

plt.style.use("seaborn-v0_8")
plt.rcParams.update({
    "font.size": 11,
    "figure.figsize": (7, 4.5),
    "axes.grid": True,
})

ALGO_LABELS = {
    "ip":       "IP Routing",
    "cspf":     "CSPF",
    "weighted": "Weighted Greedy",
}
ALGO_COLORS = {
    "ip":       "#d55e00",
    "cspf":     "#0072b2",
    "weighted": "#009e73",
}
ALGO_MARKERS = {
    "ip":       "o",
    "cspf":     "s",
    "weighted": "^",
}

REJECTION_COLORS = {
    "bandwidth": "#d55e00",
    "delay":     "#0072b2",
}
REJECTION_LABELS = {
    "bandwidth": "Brak przepustowości",
    "delay":     "Przekroczenie opóźnienia",
}


def find_latest_run():
    base = "plots"
    if not os.path.exists(base):
        print("Brak folderu plots/")
        raise SystemExit(1)
    runs = sorted([d for d in os.listdir(base) if d.startswith("run_")], reverse=True)
    if not runs:
        raise SystemExit("Brak folderów run_*")
    return os.path.join(base, runs[0])


run_dir = find_latest_run()
csv_path = os.path.join(run_dir, "results_details.csv")
output_dir = os.path.join(run_dir, "plots_final")
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)

agg = df.groupby("n_flows").agg(
    **{f"{a}_{m}_{s}": (f"{a}_{m}", stat)
       for a in ["ip", "cspf", "weighted"]
       for m in ["acceptance", "avg_delay", "max_util", "avg_util", "blocking",
                 "reject_bandwidth_ratio", "reject_delay_ratio", "reject_no_path_ratio"]
       for s, stat in [("mean", "mean"), ("std", "std")]}
).reset_index()

x = agg["n_flows"].values
xticks = sorted(df["n_flows"].unique())


# Współczynnik akceptacji 
fig, ax = plt.subplots()
for algo in ["ip", "cspf", "weighted"]:
    ax.errorbar(
        x, agg[f"{algo}_acceptance_mean"],
        yerr=agg[f"{algo}_acceptance_std"],
        marker=ALGO_MARKERS[algo], capsize=4,
        label=ALGO_LABELS[algo], color=ALGO_COLORS[algo],
    )
ax.set_xlabel("Liczba przepływów")
ax.set_ylabel("Współczynnik akceptacji")
ax.set_title("Współczynnik akceptacji w funkcji liczby przepływów")
ax.set_xticks(xticks)
ax.legend(title="Algorytm")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "acceptance.png"), dpi=300)
plt.close(fig)
print("Zapisano: acceptance.png")


# Maksymalne wykorzystanie łącza 
fig, ax = plt.subplots()
for algo in ["ip", "cspf", "weighted"]:
    ax.errorbar(
        x, agg[f"{algo}_max_util_mean"],
        yerr=agg[f"{algo}_max_util_std"],
        marker=ALGO_MARKERS[algo], capsize=4,
        label=ALGO_LABELS[algo], color=ALGO_COLORS[algo],
    )
ax.set_xlabel("Liczba przepływów")
ax.set_ylabel("Maks. wykorzystanie łącza")
ax.set_title("Maksymalne wykorzystanie łącza (wąskie gardło)")
ax.set_xticks(xticks)
ax.legend(title="Algorytm")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "max_util.png"), dpi=300)
plt.close(fig)
print("Zapisano: max_util.png")


# Średnie opóźnienie end-to-end 
fig, ax = plt.subplots()
for algo in ["ip", "cspf", "weighted"]:
    ax.errorbar(
        x, agg[f"{algo}_avg_delay_mean"],
        yerr=agg[f"{algo}_avg_delay_std"],
        marker=ALGO_MARKERS[algo], capsize=4,
        label=ALGO_LABELS[algo], color=ALGO_COLORS[algo],
    )
ax.set_xlabel("Liczba przepływów")
ax.set_ylabel("Średnie opóźnienie end-to-end [ms]")
ax.set_title("Średnie opóźnienie end-to-end zaakceptowanych przepływów")
ax.set_xticks(xticks)
ax.legend(title="Algorytm")
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "delay.png"), dpi=300)
plt.close(fig)
print("Zapisano: delay.png")


# Struktura odrzuceń

fig, axes = plt.subplots(1, 3, figsize=(14, 5), sharey=False)
algo_titles = ["IP Routing", "CSPF", "Weighted Greedy"]

for ax, algo, title in zip(axes, ["ip", "cspf", "weighted"], algo_titles):
    n_flows_labels = agg["n_flows"].astype(str).tolist()
    bottom = [0.0] * len(agg)

    for metric_suffix in ["bandwidth", "delay"]:
        col = f"{algo}_reject_{metric_suffix}_ratio_mean"
        values = agg[col].tolist()
        bars = ax.bar(
            n_flows_labels,
            values,
            bottom=bottom,
            label=REJECTION_LABELS[metric_suffix],
            color=REJECTION_COLORS[metric_suffix],
            width=0.5,
        )
        for bar, v, b in zip(bars, values, bottom):
            if v > 0.0005:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    b + v + 0.0005,
                    f"{v:.3f}",
                    ha="center", va="bottom", fontsize=9,
                )
        bottom = [bv + vv for bv, vv in zip(bottom, values)]

    ax.set_title(title)
    ax.set_xlabel("Liczba przepływów")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))

axes[0].set_ylabel("Odsetek odrzuconych przepływów")

handles = [
    plt.Rectangle((0, 0), 1, 1, color=REJECTION_COLORS["bandwidth"],
                   label=REJECTION_LABELS["bandwidth"]),
    plt.Rectangle((0, 0), 1, 1, color=REJECTION_COLORS["delay"],
                   label=REJECTION_LABELS["delay"]),
]
fig.legend(handles=handles, title="Przyczyna odrzucenia",
           loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02),
           frameon=True, fontsize=10)
fig.suptitle("Struktura przyczyn odrzuceń według algorytmu", fontsize=13, y=1.02)
fig.tight_layout(rect=[0, 0.12, 1, 1])
fig.savefig(os.path.join(output_dir, "rejection_structure.png"),
            dpi=300, bbox_inches="tight")
plt.close(fig)
print("Zapisano: rejection_structure.png")

# Boxplot akceptacji
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)
for ax, algo, title in zip(axes, ["ip", "cspf", "weighted"], algo_titles):
    data_by_load = [
        df[df["n_flows"] == n][f"{algo}_acceptance"].values
        for n in xticks
    ]
    bp = ax.boxplot(data_by_load, tick_labels=[str(n) for n in xticks],
                    patch_artist=True, medianprops={"color": "black"})
    for patch in bp["boxes"]:
        patch.set_facecolor(ALGO_COLORS[algo])
        patch.set_alpha(0.6)
    ax.set_title(title)
    ax.set_xlabel("Liczba przepływów")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))

axes[0].set_ylabel("Współczynnik akceptacji")
fig.suptitle("Rozkład współczynnika akceptacji (10 prób)", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "boxplot.png"), dpi=300)
plt.close(fig)
print("Zapisano: boxplot.png")

print(f"\nWszystkie wykresy zapisane w: {output_dir}")