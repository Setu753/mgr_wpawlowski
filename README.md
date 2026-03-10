# Protokoły wyznaczania ścieżek MPLS z gwarancją QoS
 
Projekt do pracy magisterskiej: porównanie algorytmów wyznaczania ścieżek w sieciach MPLS/TE z uwzględnieniem ograniczeń QoS.
 
## Cel

Porównanie trzech podejść routingowych:
- **IP routing** (baseline: najkrótsza ścieżka po opóźnieniu),
- **CSPF** (constraint bandwidth + delay),
- **Weighted Delay-First TE** (dynamiczna waga zależna od obciążenia łącza).
 
## Co jest zaimplementowane
 
### Model sieci
- losowa topologia (`NetworkX`),
- atrybuty łączy: `bandwidth`, `delay`, `load`,
- rezerwacja pasma na całej ścieżce,
- opcjonalne wymuszenie spójności topologii bazowej.
 
### Model ruchu
- generowanie flow (`src`, `dst`, `bandwidth`, `max_delay`),
- deterministyczne seedy dla powtarzalności eksperymentów.
 
### Algorytmy
- `IPRouting`: Dijkstra po `delay`,
- `CSPF`: filtr pasma + Dijkstra po `delay` + walidacja `max_delay`,
- `WeightedGreedy`: filtr pasma + Dijkstra po `weight = delay * (1 + beta * utilization)` + walidacja `max_delay`.

### Metodologia
- ta sama topologia i ten sam zestaw flow dla wszystkich algorytmów,
- izolacja stanu przez `deepcopy`,
- wielokrotne uruchomienia (Monte Carlo),
- poziomy obciążenia domyślnie: `30 / 60 / 90` flow.

### Metryki
- acceptance ratio,
- średni delay zaakceptowanych flow,
- średnie utilization łączy.
 
---
 
## Szybki start
 
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py