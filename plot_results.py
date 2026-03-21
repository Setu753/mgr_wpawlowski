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

# WCZYTANIE DANYCH
df = pd.read_csv("results_summary.csv")

print("\n=== TABELA WYNIKÓW ===")
print(df.round(3))


# WYKRES 1: AKCEPTACJA
plt.figure()
plt.plot(df["n_flows"], df["ip_acceptance_mean"], marker="o", label="IP")
plt.plot(df["n_flows"], df["cspf_acceptance_mean"], marker="s", label="CSPF")
plt.plot(df["n_flows"], df["weighted_acceptance_mean"], marker="^", label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Współczynnik akceptacji")
plt.title("Współczynnik akceptacji w funkcji obciążenia")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "acceptance.png"), dpi=300)
plt.show()


# WYKRES 2: MAKSYMALNE WYKORZYSTANIE ŁĄCZA
plt.figure()
plt.plot(df["n_flows"], df["ip_max_util_mean"], marker="o", label="IP")
plt.plot(df["n_flows"], df["cspf_max_util_mean"], marker="s", label="CSPF")
plt.plot(df["n_flows"], df["weighted_max_util_mean"], marker="^", label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Maksymalne wykorzystanie łącza")
plt.title("Maksymalne wykorzystanie łącza w funkcji obciążenia")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "max_utilization.png"), dpi=300)
plt.show()


# WYKRES 3: OPÓŹNIENIE
plt.figure()
plt.plot(df["n_flows"], df["ip_delay_mean"], marker="o", label="IP")
plt.plot(df["n_flows"], df["cspf_delay_mean"], marker="s", label="CSPF")
plt.plot(df["n_flows"], df["weighted_delay_mean"], marker="^", label="Weighted")

plt.xlabel("Liczba przepływów")
plt.ylabel("Średnie opóźnienie")
plt.title("Średnie opóźnienie w funkcji obciążenia")
plt.legend(title="Algorytm")
plt.tight_layout()

plt.savefig(os.path.join(output_dir, "delay.png"), dpi=300)
plt.show()