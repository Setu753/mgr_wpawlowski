import pandas as pd
import matplotlib.pyplot as plt
import os

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
        exit()

    runs = [d for d in os.listdir(base) if d.startswith("run_")]

    if not runs:
        print("Brak folderów run_*")
        exit()

    runs.sort(reverse=True)
    return os.path.join(base, runs[0])


# === ŚCIEŻKI ===
run_dir = find_latest_run()

# 🔴 FIX: poprawna nazwa pliku
csv_path = os.path.join(run_dir, "results_details.csv")

output_dir = os.path.join(run_dir, "plots_final")

if not os.path.exists(csv_path):
    print("Brak pliku:", csv_path)
    exit()

os.makedirs(output_dir, exist_ok=True)

# === DANE ===
df_runs = pd.read_csv(csv_path)

print("\n=== PODGLĄD DANYCH ===")
print(df_runs.head())

# === AGREGACJA ===
grouped = df_runs.groupby("n_flows")

agg = grouped.agg({
    # acceptance
    "ip_acceptance": ["mean", "std"],
    "cspf_acceptance": ["mean", "std"],
    "weighted_acceptance": ["mean", "std"],

    # delay
    "ip_avg_delay": ["mean", "std"],
    "cspf_avg_delay": ["mean", "std"],
    "weighted_avg_delay": ["mean", "std"],

    # utilization
    "ip_max_util": ["mean", "std"],
    "cspf_max_util": ["mean", "std"],
    "weighted_max_util": ["mean", "std"],

    "ip_avg_util": ["mean", "std"],
    "cspf_avg_util": ["mean", "std"],
    "weighted_avg_util": ["mean", "std"],

    # blocking
    "ip_blocking": ["mean", "std"],
    "cspf_blocking": ["mean", "std"],
    "weighted_blocking": ["mean", "std"],
})

agg.columns = ["_".join(col) for col in agg.columns]
agg = agg.reset_index()

print("\n=== AGREGACJA ===")
print(agg.round(3))

agg.to_csv(os.path.join(output_dir, "aggregated_results.csv"), index=False)


# ===============================
# 1. ACCEPTANCE
# ===============================
plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.errorbar(
        agg["n_flows"],
        agg[f"{algo}_acceptance_mean"],
        yerr=agg[f"{algo}_acceptance_std"],
        marker="o",
        capsize=4,
        label=algo.upper()
    )

plt.xlabel("Liczba przepływów")
plt.ylabel("Współczynnik akceptacji")
plt.title("Akceptacja (średnia ± odchylenie standardowe)")
plt.legend(title="Algorytm")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "acceptance.png"), dpi=300)
plt.close()


# ===============================
# 2. MAX UTILIZATION
# ===============================
plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.errorbar(
        agg["n_flows"],
        agg[f"{algo}_max_util_mean"],
        yerr=agg[f"{algo}_max_util_std"],
        marker="o",
        capsize=4,
        label=algo.upper()
    )

plt.xlabel("Liczba przepływów")
plt.ylabel("Max wykorzystanie łącza")
plt.title("Bottleneck links")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "max_util.png"), dpi=300)
plt.close()


# ===============================
# 3. DELAY
# ===============================
plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.errorbar(
        agg["n_flows"],
        agg[f"{algo}_avg_delay_mean"],
        yerr=agg[f"{algo}_avg_delay_std"],
        marker="o",
        capsize=4,
        label=algo.upper()
    )

plt.xlabel("Liczba przepływów")
plt.ylabel("Średnie opóźnienie")
plt.title("Opóźnienie end-to-end")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "delay.png"), dpi=300)
plt.close()


# ===============================
# 4. BLOCKING PROBABILITY
# ===============================
plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.errorbar(
        agg["n_flows"],
        agg[f"{algo}_blocking_mean"],
        yerr=agg[f"{algo}_blocking_std"],
        marker="o",
        capsize=4,
        label=algo.upper()
    )

plt.xlabel("Liczba przepływów")
plt.ylabel("Blocking probability")
plt.title("Prawdopodobieństwo blokady")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "blocking.png"), dpi=300)
plt.close()


# ===============================
# 5. AVG UTILIZATION
# ===============================
plt.figure()

for algo in ["ip", "cspf", "weighted"]:
    plt.plot(
        agg["n_flows"],
        agg[f"{algo}_avg_util_mean"],
        marker="o",
        label=algo.upper()
    )

plt.xlabel("Liczba przepływów")
plt.ylabel("Średnie wykorzystanie")
plt.title("Obciążenie sieci")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "avg_util.png"), dpi=300)
plt.close()


# ===============================
# 6. BOXPLOT (FIX)
# ===============================
plt.figure()

df_runs.boxplot(
    column=["ip_acceptance", "cspf_acceptance", "weighted_acceptance"],
    by="n_flows"
)

plt.suptitle("")
plt.title("Rozkład akceptacji")
plt.xlabel("Liczba przepływów")
plt.ylabel("Acceptance")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "boxplot.png"), dpi=300)
plt.close()


print("\nWykresy zapisane w:", output_dir)