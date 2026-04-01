import pandas as pd
import matplotlib.pyplot as plt
import os


def find_latest_run():
    runs = [d for d in os.listdir() if d.startswith("run_")]
    runs.sort(reverse=True)
    return runs[0] if runs else None


run_dir = find_latest_run()

if not run_dir:
    print("Brak folderu run_*")
    exit()

csv_path = os.path.join(run_dir, "results.csv")
output_dir = os.path.join(run_dir, "plots_final")
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(csv_path)

print("\n=== DANE ===")
print(df.head())

# ===== WYKRES 1: ŚREDNIA AKCEPTACJA =====
grouped = df.groupby("n_flows").mean(numeric_only=True)

plt.figure()
plt.plot(grouped.index, grouped["ip_acceptance"], marker="o", label="IP")
plt.plot(grouped.index, grouped["cspf_acceptance"], marker="s", label="CSPF")
plt.plot(grouped.index, grouped["weighted_acceptance"], marker="^", label="Weighted")

plt.xlabel("Liczba flow")
plt.ylabel("Acceptance")
plt.title("Acceptance vs obciążenie")
plt.legend()
plt.grid()

plt.savefig(os.path.join(output_dir, "acceptance_vs_flows.png"))
plt.close()


# ===== WYKRES 2: PORÓWNANIE ALGORYTMÓW =====
plt.figure()

labels = ["IP", "CSPF", "Weighted"]
values = [
    grouped["ip_acceptance"].mean(),
    grouped["cspf_acceptance"].mean(),
    grouped["weighted_acceptance"].mean()
]

plt.bar(labels, values)

plt.title("Średnia skuteczność algorytmów")
plt.ylabel("Acceptance")

plt.savefig(os.path.join(output_dir, "algorithms_comparison.png"))
plt.close()


# ===== WYKRES 3: BOXPLOT =====
plt.figure()

df.boxplot(column=["ip_acceptance", "cspf_acceptance", "weighted_acceptance"])

plt.title("Rozkład wyników (boxplot)")
plt.ylabel("Acceptance")

plt.savefig(os.path.join(output_dir, "boxplot.png"))
plt.close()


print(f"\nWykresy zapisane w: {output_dir}")