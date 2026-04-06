# Protokoły wyznaczania ścieżek MPLS z gwarancją QoS

## TL;DR

Symulator MPLS Traffic Engineering porównujący algorytmy routingu
(IP, CSPF, Weighted) pod kątem QoS.

Wynik: algorytmy uwzględniające ograniczenia i obciążenie osiągają
wyższy współczynnik akceptacji oraz lepsze rozłożenie ruchu w sieci.

---

## Cel

Celem projektu jest analiza wpływu różnych algorytmów routingu na:

* współczynnik akceptacji przepływów (acceptance ratio),
* obciążenie sieci,
* efektywność wykorzystania zasobów,
* opóźnienia transmisji.

Porównywane podejścia:

* **IP routing** – najkrótsza ścieżka według opóźnienia (baseline),
* **CSPF (Constraint Shortest Path First)** – uwzględnia ograniczenia pasma i opóźnienia,
* **Weighted Delay-First TE** – dynamiczna funkcja kosztu zależna od obciążenia łącza.

---

## Model

### Sieć

* losowa topologia (`NetworkX`),
* atrybuty łączy: `bandwidth`, `delay`, `load`,
* rezerwacja pasma na ścieżce,
* wymuszenie spójności grafu.

### Ruch

* przepływy: `(src, dst, bandwidth, max_delay)`,
* kontrolowana losowość (seed),
* różne poziomy obciążenia.

---

## Algorytmy

### IP Routing

* Dijkstra po `delay`,
* brak uwzględnienia obciążenia.

### CSPF

* filtracja krawędzi niespełniających ograniczeń pasma,
* Dijkstra po `delay`,
* walidacja ograniczenia `max_delay`.

### Weighted Routing

Dynamiczna funkcja kosztu:
weight = delay * (1 + beta * utilization)

gdzie:

* utilization = load / bandwidth
* beta – parametr wpływu obciążenia

Cechy:

* omija przeciążone łącza,
* lepiej rozkłada ruch.

---

## Metodologia eksperymentu

* jedna topologia na uruchomienie,
* te same przepływy dla wszystkich algorytmów,
* izolacja stanu (`deepcopy`),
* wielokrotne próby (Monte Carlo),
* poziomy obciążenia: 30 / 60 / 90 przepływów.

---

## Metryki

* **Acceptance ratio** – odsetek zaakceptowanych przepływów,
* **Average delay** – średnie opóźnienie,
* **Link utilization**:

  * średnie,
  * maksymalne (bottleneck),
* **Rejected flows** – liczba odrzuconych przepływów.

---

## Przykładowe wyniki

| Flows | IP   | CSPF | Weighted |
| ----- | ---- | ---- | -------- |
| 30    | 1.00 | 0.98 | 0.98     |
| 60    | 0.95 | 0.96 | 0.95     |
| 90    | 0.90 | 0.96 | 0.95     |

---

## Wizualizacja

Projekt generuje:

* topologie sieci,
* heatmapy obciążenia,
* wykresy (średnie, boxplot, porównania).

Wyniki zapisywane są w katalogu:
plots/run_<timestamp>/

---

## Reproducibility

Eksperymenty są powtarzalne dzięki użyciu seedów.

Każde uruchomienie:

* generuje jedną topologię bazową,
* wykonuje wiele prób,
* zapisuje wyniki w katalogu run_<timestamp>.

---

## Struktura projektu
```
mpls_qos/
├── main.py
├── network.py
├── routing.py
├── plot_results.py
├── plot_results_scientific.py
├── plots/        # wyniki eksperymentów (generowane)
├── logs/         # logi (generowane)
├── tests/
└── docs/
```
---

## Uruchomienie

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python main.py
python plot_results.py
python plot_results_scientific.py

---

## Wnioski

* CSPF i Weighted osiągają wyższy acceptance niż IP,
* Weighted lepiej rozkłada obciążenie sieci,
* IP minimalizuje opóźnienie kosztem przeciążeń,
* występuje kompromis QoS vs efektywność.

---

## Future Work

* dynamiczny ruch w czasie,
* RSVP-TE / Segment Routing,
* analiza stabilności algorytmów,
* inne modele topologii.

---

## Technologie

* Python 3
* NetworkX
* Pandas
* Matplotlib

---

## Autor

Projekt realizowany w ramach pracy magisterskiej – MPLS QoS / Traffic Engineering.
