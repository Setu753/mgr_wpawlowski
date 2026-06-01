# Dokumentacja konserwacyjna

## Struktura kodu

```
main.py                    # punkt wejścia, logika eksperymentu
network.py                 # model danych: sieć i przepływy
routing.py                 # algorytmy routingu
generate_plots.py          # wykresy finalne i agregacja wyników
demo/demo.py               # animacja demonstracyjna (materiał pomocniczy)
```

Projekt jest celowo płaski — brak pakietów, brak klas abstrakcyjnych ponad to co konieczne. Każdy plik ma jedno, wyraźne zadanie.

---

## Dodawanie nowego algorytmu routingu

1. Otwórz `routing.py`
2. Dodaj nową klasę wzorowaną na `CSPF` lub `WeightedGreedy`:

```python
class MojAlgorytm:
    def __init__(self, graph):
        self.graph = graph

    def compute_path(self, flow):
        path, _ = self.compute_path_with_reason(flow)
        return path

    def compute_path_with_reason(self, flow):
        # zwraca (path, reason)
        # reason: "accepted" / "bandwidth" / "delay" / "no_path"
        ...
```

3. W `main.py` w funkcji `run_experiment` dodaj analogiczny blok dla nowego algorytmu (skopiuj blok CSPF i podmień nazwę klasy oraz prefix `"cspf_"` na własny)
4. W `generate_plots.py` dodaj nowy algorytm do słowników `ALGO_LABELS`, `ALGO_COLORS`, `ALGO_MARKERS`

---

## Zmiana parametrów eksperymentu

Wszystkie kluczowe parametry są w `main.py` w funkcji `run_scaling_experiments()`:

```python
n_nodes = 15               # liczba węzłów w topologii
flow_levels = [30, 60, 90] # poziomy obciążenia
runs_per_level = 10        # liczba prób Monte Carlo na poziom
```

Parametr `β` algorytmu Weighted Greedy ustawiany jest w wywołaniu `run_experiment(..., beta=3.0)`.

---

## Reprodukcja konkretnej topologii

Seed topologii zapisywany jest w `plots/run_<timestamp>/run_metadata.json`. Aby odtworzyć eksperyment z tą samą topologią, ustaw w `run_scaling_experiments()`:

```python
topology_seed = <wartość z run_metadata.json>
topology_rng = random.Random(topology_seed)
```

---

## Generowanie wykresów bez ponownego eksperymentu

```bash
python generate_plots.py
```

Skrypt automatycznie wybiera ostatni katalog `run_*` z `plots/`. Aby wskazać konkretny katalog, zmodyfikuj funkcję `find_latest_run()` w pliku lub tymczasowo ustaw zmienną `run_dir` bezpośrednio.

---

## Zależności

Wszystkie zależności w `requirements.txt`. Instalacja:

```bash
pip install -r requirements.txt
```

Projekt nie wymaga żadnych zależności systemowych poza Pythonem 3.14.2.
