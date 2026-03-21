import pandas as pd
import matplotlib.pyplot as plt
import os
import time


plt.rcParams.update({
    "font.size": 11,
    "figure.figsize": (7, 4.5),
    "axes.grid": True
})


output_dir = os.path.join("plots", f"run_{int(time.time())}")
os.makedirs(output_dir, exist_ok=True)


df_runs = pd.read_csv("runs_details.csv")

print("\n=== PODGLĄD DANYCH (runs) ===")
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
})


agg.columns = ["_".join(col) for col in agg.columns]
agg = agg.reset_index()

print("\n=== AGREGACJA (mean + std) ===")
print(agg.round(3))



# 1. ACCEPTANCE — ERROR BARS

plt.figure()

plt.errorbar(agg["n_flows"], agg["ip_acceptance_mean"],
             yerr=agg["ip_acceptance_std"], marker="o", capsize=4, label="IP")

plt.errorbar(agg["n_flows"], agg["cspf_acceptance_mean"],
             yerr=agg["cspf_acceptance_std"], marker="s", capsize=4, label="CSPF")

plt.errorbar(agg["n_flows"], agg["weighted_acceptance_mean"],
             yerr=agg["weighted_acceptance_std"], marker="^", capsize=4, label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Współczynnik akceptacji")
plt.title("Akceptacja (średnia ± odchylenie standardowe)")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "acceptance_errorbars.png"), dpi=300)
plt.show()



#  2. MAX UTIL — ERROR BARS

plt.figure()

plt.errorbar(agg["n_flows"], agg["ip_max_util_mean"],
             yerr=agg["ip_max_util_std"], marker="o", capsize=4, label="IP")

plt.errorbar(agg["n_flows"], agg["cspf_max_util_mean"],
             yerr=agg["cspf_max_util_std"], marker="s", capsize=4, label="CSPF")

plt.errorbar(agg["n_flows"], agg["weighted_max_util_mean"],
             yerr=agg["weighted_max_util_std"], marker="^", capsize=4, label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Maksymalne wykorzystanie łącza")
plt.title("Maksymalne wykorzystanie (średnia ± odchylenie)")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "max_util_errorbars.png"), dpi=300)
plt.show()



#  3. DELAY — ERROR BARS

plt.figure()

plt.errorbar(agg["n_flows"], agg["ip_avg_delay_mean"],
             yerr=agg["ip_avg_delay_std"], marker="o", capsize=4, label="IP")

plt.errorbar(agg["n_flows"], agg["cspf_avg_delay_mean"],
             yerr=agg["cspf_avg_delay_std"], marker="s", capsize=4, label="CSPF")

plt.errorbar(agg["n_flows"], agg["weighted_avg_delay_mean"],
             yerr=agg["weighted_avg_delay_std"], marker="^", capsize=4, label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Średnie opóźnienie")
plt.title("Opóźnienie (średnia ± odchylenie)")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "delay_errorbars.png"), dpi=300)
plt.show()



# 📦 4. BOXPLOT — ACCEPTANCE (rozkład)

plt.figure()

data_ip = [group["ip_acceptance"].values for _, group in grouped]
data_cspf = [group["cspf_acceptance"].values for _, group in grouped]
data_weighted = [group["weighted_acceptance"].values for _, group in grouped]

positions = list(agg["n_flows"])
offset = 2

plt.boxplot(data_ip, positions=[p - offset for p in positions], widths=3)
plt.boxplot(data_cspf, positions=positions, widths=3)
plt.boxplot(data_weighted, positions=[p + offset for p in positions], widths=3)

plt.xlabel("Liczba przepływów")
plt.ylabel("Współczynnik akceptacji")
plt.title("Rozkład akceptacji (boxplot)")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "acceptance_boxplot.png"), dpi=300)
plt.show()