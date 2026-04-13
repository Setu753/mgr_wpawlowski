import os

import matplotlib.pyplot as plt
import pandas as pd


plt.style.use("seaborn-v0_8")

plt.rcParams.update({
    "font.size": 11,
    "figure.figsize": (7, 4.5),
    "axes.grid": True
})


def find_latest_run():
    base = "plots"

    if not os.path.exists(base):
        print("Brak folderu plots/")
        raise SystemExit(1)

    runs = [d for d in os.listdir(base) if d.startswith("run_")]

    if not runs:
        print("Brak folderow run_*")
        raise SystemExit(1)

    runs.sort(reverse=True)
    return os.path.join(base, runs[0])


run_dir = find_latest_run()
csv_path = os.path.join(run_dir, "results_details.csv")
output_dir = os.path.join(run_dir, "plots_final")

if not os.path.exists(csv_path):
    print("Brak pliku:", csv_path)
    raise SystemExit(1)

os.makedirs(output_dir, exist_ok=True)

df_runs = pd.read_csv(csv_path)

print("\n=== PODGLAD DANYCH ===")
print(df_runs.head())

grouped = df_runs.groupby("n_flows")

agg = grouped.agg({
    "ip_acceptance": ["mean", "std"],
    "cspf_acceptance": ["mean", "std"],
    "weighted_acceptance": ["mean", "std"],
    "ip_avg_delay": ["mean", "std"],
    "cspf_avg_delay": ["mean", "std"],
    "weighted_avg_delay": ["mean", "std"],
    "ip_max_util": ["mean", "std"],
    "cspf_max_util": ["mean", "std"],
    "weighted_max_util": ["mean", "std"],
    "ip_avg_util": ["mean", "std"],
    "cspf_avg_util": ["mean", "std"],
    "weighted_avg_util": ["mean", "std"],
    "ip_blocking": ["mean", "std"],
    "cspf_blocking": ["mean", "std"],
    "weighted_blocking": ["mean", "std"],
    "ip_reject_bandwidth_ratio": ["mean", "std"],
    "ip_reject_delay_ratio": ["mean", "std"],
    "ip_reject_no_path_ratio": ["mean", "std"],
    "cspf_reject_bandwidth_ratio": ["mean", "std"],
    "cspf_reject_delay_ratio": ["mean", "std"],
    "cspf_reject_no_path_ratio": ["mean", "std"],
    "weighted_reject_bandwidth_ratio": ["mean", "std"],
    "weighted_reject_delay_ratio": ["mean", "std"],
    "weighted_reject_no_path_ratio": ["mean", "std"],
})

agg.columns = ["_".join(col) for col in agg.columns]
agg = agg.reset_index()

print("\n=== AGREGACJA ===")
print(agg.round(3))

agg.to_csv(os.path.join(output_dir, "aggregated_results.csv"), index=False)


def dominant_reason_for_row(row, algo):
    values = {
        "bandwidth": row[f"{algo}_reject_bandwidth_ratio_mean"],
        "delay": row[f"{algo}_reject_delay_ratio_mean"],
        "no_path": row[f"{algo}_reject_no_path_ratio_mean"],
    }
    dominant_reason = max(values, key=values.get)

    if values[dominant_reason] <= 0:
        return "none"

    return dominant_reason


def build_interpretation_lines():
    lines = [
        "Automatyczna interpretacja wynikow",
        ""
    ]

    for _, row in agg.iterrows():
        n_flows = int(row["n_flows"])
        best_algo = max(
            ["ip", "cspf", "weighted"],
            key=lambda algo: row[f"{algo}_acceptance_mean"]
        ).upper()

        lines.append(f"Obciazenie: {n_flows} przeplywow")
        lines.append(
            f"- Najwyzszy acceptance: {best_algo} "
            f"({max(row['ip_acceptance_mean'], row['cspf_acceptance_mean'], row['weighted_acceptance_mean']):.3f})"
        )
        lines.append(
            f"- IP: dominujacy powod odrzucen = {dominant_reason_for_row(row, 'ip')}"
        )
        lines.append(
            f"- CSPF: dominujacy powod odrzucen = {dominant_reason_for_row(row, 'cspf')}"
        )
        lines.append(
            f"- Weighted: dominujacy powod odrzucen = {dominant_reason_for_row(row, 'weighted')}"
        )

        if row["weighted_max_util_mean"] < row["ip_max_util_mean"]:
            lines.append("- Weighted lepiej ogranicza maksymalne wykorzystanie laczy niz IP")

        if row["cspf_acceptance_mean"] > row["ip_acceptance_mean"]:
            lines.append("- CSPF poprawia wspolczynnik akceptacji wzgledem IP")

        if row["weighted_acceptance_mean"] > row["ip_acceptance_mean"]:
            lines.append("- Weighted poprawia wspolczynnik akceptacji wzgledem IP")

        lines.append("")

    return lines


def plot_metric_with_errorbars(metric_name, ylabel, title, filename):
    plt.figure()

    for algo in ["ip", "cspf", "weighted"]:
        plt.errorbar(
            agg["n_flows"],
            agg[f"{algo}_{metric_name}_mean"],
            yerr=agg[f"{algo}_{metric_name}_std"],
            marker="o",
            capsize=4,
            label=algo.upper()
        )

    plt.xlabel("Liczba przeplywow")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(title="Algorytm")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=300)
    plt.close()


plot_metric_with_errorbars(
    "acceptance",
    "Wspolczynnik akceptacji",
    "Akceptacja (srednia +- odchylenie standardowe)",
    "acceptance.png"
)

plot_metric_with_errorbars(
    "max_util",
    "Maksymalne wykorzystanie lacza",
    "Bottleneck links",
    "max_util.png"
)

plot_metric_with_errorbars(
    "avg_delay",
    "Srednie opoznienie",
    "Opoznienie end-to-end",
    "delay.png"
)

plot_metric_with_errorbars(
    "blocking",
    "Blocking probability",
    "Prawdopodobienstwo blokady",
    "blocking.png"
)


plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.plot(
        agg["n_flows"],
        agg[f"{algo}_avg_util_mean"],
        marker="o",
        label=algo.upper()
    )

plt.xlabel("Liczba przeplywow")
plt.ylabel("Srednie wykorzystanie")
plt.title("Obciazenie sieci")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_util.png"), dpi=300)
plt.close()


plt.figure()

df_runs.boxplot(
    column=["ip_acceptance", "cspf_acceptance", "weighted_acceptance"],
    by="n_flows"
)

plt.suptitle("")
plt.title("Rozklad akceptacji")
plt.xlabel("Liczba przeplywow")
plt.ylabel("Acceptance")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "boxplot.png"), dpi=300)
plt.close()


fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
rejection_types = [
    ("reject_bandwidth_ratio", "Bandwidth", "#d55e00"),
    ("reject_delay_ratio", "Delay", "#0072b2"),
    ("reject_no_path_ratio", "No path", "#999999"),
]

for ax, algo in zip(axes, ["ip", "cspf", "weighted"]):
    bottom = pd.Series([0.0] * len(agg))

    for metric_suffix, label, color in rejection_types:
        values = agg[f"{algo}_{metric_suffix}_mean"]
        ax.bar(
            agg["n_flows"].astype(str),
            values,
            bottom=bottom,
            label=label,
            color=color
        )
        bottom = bottom + values

    ax.set_title(algo.upper())
    ax.set_xlabel("Liczba przeplywow")

axes[0].set_ylabel("Udzial odrzuconych przeplywow")
axes[0].legend(title="Powod")
fig.suptitle("Struktura odrzuconych przeplywow")
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "rejection_structure.png"), dpi=300)
plt.close(fig)


interpretation_lines = build_interpretation_lines()
interpretation_path = os.path.join(output_dir, "results_interpretation.txt")

with open(interpretation_path, "w", encoding="utf-8") as f:
    f.write("\n".join(interpretation_lines))

print("\n=== INTERPRETACJA ===")
for line in interpretation_lines:
    print(line)


print("\nWykresy zapisane w:", output_dir)
