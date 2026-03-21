# Protokoły wyznaczania ścieżek MPLS z gwarancją QoS

Projekt do pracy magisterskiej: porównanie algorytmów wyznaczania ścieżek w sieciach MPLS/TE z uwzględnieniem ograniczeń QoS.

---

##  Cel

Celem projektu jest porównanie trzech podejść routingowych:

* **IP routing** – najkrótsza ścieżka według opóźnienia (baseline),
* **CSPF (Constraint Shortest Path First)** – uwzględnia ograniczenia pasma i opóźnienia,
* **Weighted Delay-First TE** – dynamiczna funkcja kosztu zależna od obciążenia łącza.

---

##  Co jest zaimplementowane

###  Model sieci

* losowa topologia (`NetworkX`),
* atrybuty łączy: `bandwidth`, `delay`, `load`,
* rezerwacja pasma na całej ścieżce,
* opcjonalne wymuszenie spójności topologii bazowej.

###  Model ruchu

* generowanie przepływów (`src`, `dst`, `bandwidth`, `max_delay`),
* kontrolowana losowość (seed),
* symulacja różnych poziomów obciążenia.

###  Algorytmy

* `IPRouting` – Dijkstra po `delay`,
* `CSPF` – filtr pasma + Dijkstra po `delay` + walidacja `max_delay`,
* `WeightedGreedy` – filtr pasma + Dijkstra po:

  ```
  weight = delay * (1 + beta * utilization)
  ```

  * walidacja `max_delay`.

---

##  Metodologia eksperymentu

* ta sama topologia i ten sam zestaw flow dla wszystkich algorytmów,
* izolacja stanu poprzez `deepcopy`,
* wielokrotne uruchomienia (Monte Carlo),
* poziomy obciążenia: `30 / 60 / 90` flow,
* agregacja wyników:

  * średnia (mean),
  * odchylenie standardowe (std).

---

##  Metryki

* **Acceptance ratio** – odsetek zaakceptowanych przepływów,
* **Average delay** – średnie opóźnienie zaakceptowanych flow,
* **Link utilization**:

  * średnie wykorzystanie,
  * maksymalne wykorzystanie (bottleneck).

---

##  Wizualizacja wyników

Projekt umożliwia generowanie:

* wykresów średnich wartości,
* wykresów z odchyleniem standardowym (error bars),
* wykresów pudełkowych (boxplot).

Wyniki zapisywane są w katalogu:

```
plots/run_<timestamp>/
```

---

## ▶ Szybki start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py
python plot_results.py
python plot_results_scientific.py
```

---

##  Struktura projektu

```
mpls_qos/
├── main.py
├── network.py
├── routing.py
├── plot_results.py
├── plot_results_scientific.py
├── results_summary.csv
├── runs_details.csv
├── plots/
├── tests/
└── docs/
```

---

##  Wnioski (skrót)

* CSPF i Weighted osiągają wyższy współczynnik akceptacji niż IP,
* Weighted lepiej rozkłada obciążenie (mniej przeciążeń),
* IP zapewnia niższe opóźnienia kosztem efektywności,
* występuje kompromis: **QoS vs wydajność sieci**.

---

##  Technologie

* Python 3
* NetworkX
* Pandas
* Matplotlib

---

##  Autor

Projekt realizowany w ramach pracy magisterskiej – MPLS QoS / Traffic Engineering.
