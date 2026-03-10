
Projekt pracy magisterskiej:  
**Protokoły wyznaczania ścieżek MPLS z gwarancją QoS w sieciach komputerowych.**

---

## Cel projektu

Celem pracy jest porównanie algorytmów wyznaczania ścieżek w sieciach MPLS z uwzględnieniem wymagań QoS (Quality of Service), w szczególności:

- klasycznego routingu IP (baseline),
- CSPF (Constraint Shortest Path First),
- autorskiego algorytmu Weighted Delay-First Traffic Engineering.


---

## Zaimplementowano

### Model sieci
- generowanie losowej topologii (NetworkX)
- atrybuty łączy: przepustowość, opóźnienie, obciążenie
- mechanizm rezerwacji przepustowości

### Model ruchu
- generowanie strumieni (flow)
- wymagania: bandwidth, max_delay

### Algorytmy routingu
- IP routing (najkrótsza ścieżka wg delay)
- CSPF (constraint bandwidth + delay)
- Weighted Delay-First TE:
  - dynamiczna waga:  
    `weight = delay × (1 + β · utilization)`
  - Dijkstra z dynamicznymi wagami

### Metodologia eksperymentalna
- identyczna topologia i zestaw flow dla wszystkich algorytmów
- deep copy grafu (izolacja load)
- wielokrotne powtórzenia (Monte Carlo)
- analiza skalowalności: 30 / 60 / 90 flow

### Metryki
- acceptance ratio
- średni delay zaakceptowanych ścieżek
- średnie utilization łączy
- odchylenie standardowe wyników

---

## Aktualny etap
  
Trwa analiza parametryczna (wpływ β) oraz dalsza walidacja eksperymentalna.

---

## Uruchomienie

```bash
pip install -r requirements.txt
python main.py

