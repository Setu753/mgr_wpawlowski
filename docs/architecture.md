# Architektura rozwiązania

## Cel i zakres

Projekt implementuje środowisko symulacyjne do porównania algorytmów routingu w sieciach MPLS
z gwarancjami QoS. System nie jest aplikacją produkcyjną — jest narzędziem badawczym
generującym dane eksperymentalne i wizualizacje.

---

## Główne komponenty

```
┌─────────────────────────────────────────────────────┐
│                     main.py                         │
│         Orkiestracja eksperymentu Monte Carlo        │
│  generowanie przepływów · izolacja stanu · zapis CSV │
└────────────┬────────────────────────┬───────────────┘
             │                        │
    ┌────────▼────────┐     ┌─────────▼──────────┐
    │   network.py    │     │    routing.py       │
    │  Network: graf  │     │  IPRouting          │
    │  Flow: krotka   │     │  CSPF               │
    │  rezerwacja BW  │     │  WeightedGreedy     │
    └─────────────────┘     └────────────────────┘
             │
    ┌────────▼──────────────────┐
    │   generate_plots  │
    │   Agregacja · wykresy     │
    │   PNG · CSV                │
    └───────────────────────────┘
```

### `network.py` — model sieci

- **`Network`** — opakowanie wokół grafu NetworkX (`nx.Graph`).
  Odpowiada za: generowanie losowej topologii (`generate_random`),
  rezerwację pasma na ścieżce (`reserve_bandwidth`),
  zapis wizualizacji topologii.
- **`Flow`** — krotka `(src, dst, bandwidth, max_delay, priority)`.
  Reprezentuje pojedyncze żądanie zestawienia połączenia.

### `routing.py` — algorytmy routingu

- **`IPRouting`** — Dijkstra po wadze `delay`, bez uwzględnienia obciążenia.
  Punkt odniesienia (baseline).
- **`CSPF`** — filtruje krawędzie niespełniające `bandwidth - load >= flow.bandwidth`,
  następnie Dijkstra po `delay`, na końcu weryfikuje `max_delay`.
- **`WeightedGreedy`** — jak CSPF, ale waga krawędzi to
  `delay * (1 + β * utilization)` gdzie `utilization = load / bandwidth`.
  Parametr `β = 3.0` (domyślnie) kontroluje wpływ obciążenia na koszt.

### `main.py` — eksperyment

- Generuje jedną topologię bazową na uruchomienie (seed losowany z `SystemRandom`)
- Dla każdego poziomu obciążenia (30 / 60 / 90 przepływów) i każdej próby (10):
  - klonuje graf bazowy przez `copy.deepcopy` — każdy algorytm operuje na izolowanej kopii
  - generuje ten sam zestaw przepływów (deterministyczny seed per próba)
  - zbiera metryki i zapisuje do CSV
- Seed topologii zapisywany w `run_metadata.json`

### `generate_plots.py` — wizualizacja

Odczytuje `results_details.csv` z ostatniego katalogu `run_*`,
agreguje wyniki i generuje 5 wykresów PNG oraz raport tekstowy.

---

## Przepływ danych

```
main.py
  │
  ├─ Network.generate_random()  →  graf NetworkX (węzły, krawędzie z BW/delay/load)
  │
  ├─ generate_flows()           →  lista obiektów Flow
  │
  ├─ deepcopy(base_graph) × 3   →  izolowane kopie dla IP / CSPF / Weighted
  │
  ├─ router.compute_path(flow)  →  ścieżka lub None + powód odrzucenia
  │
  ├─ Network.reserve_bandwidth()→  aktualizacja pola `load` na krawędziach
  │
  └─ results[]                  →  results_details.csv
                                    results_summary.csv
                                    run_metadata.json
                                    logs/log_*.txt
                                    plots/topo_*

generate_plots.py
  │
  ├─ results_details.csv        →  agregacja pandas (groupby n_flows)
  │
  └─ plots_final/               →  acceptance.png, max_util.png, delay.png,
                                    rejection_structure.png, boxplot.png,
                                    aggregated_results.csv
```

---

## Technologie

| Technologia | Wersja | Zastosowanie |
|-------------|--------|--------------|
| Python | 3.14.2 | język implementacji |
| NetworkX | ≥3.0 | reprezentacja grafu, algorytm Dijkstry |
| Pandas | ≥2.0 | agregacja wyników, zapis CSV |
| Matplotlib | ≥3.7 | wykresy, animacje, heatmapy |
| NumPy | ≥1.24 | interpolacja punktów animacji |

---

## Środowisko uruchomieniowe

Projekt działa lokalnie na dowolnym systemie z Pythonem 3.14.2.
Nie wymaga bazy danych, serwera, GPU ani połączenia z siecią zewnętrzną.
Wszystkie wyniki zapisywane są lokalnie w katalogu `plots/`.

---

## Odstępstwa od pierwotnych założeń

Demonstracja (`demo/demo.py`) została zrealizowana jako osobny skrypt animacyjny
na uproszczonej topologii 8-węzłowej (IP vs MPLS-TE), niezależny od głównego eksperymentu.
W pierwotnych założeniach demo nie było wyodrębnione jako osobny moduł.
