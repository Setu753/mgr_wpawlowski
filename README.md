# Protokoły wyznaczania ścieżek MPLS z gwarancją QoS

## Opis projektu

Projekt stanowi środowisko symulacyjne przygotowane na potrzeby pracy magisterskiej poświęconej analizie metod wyznaczania ścieżek w sieciach MPLS z uwzględnieniem wymagań jakości usług (QoS).

Głównym celem projektu jest porównanie skuteczności wybranych algorytmów routingu w warunkach narastającego obciążenia sieci. Analiza koncentruje się na wpływie mechanizmu wyznaczania trasy na:

* współczynnik akceptacji przepływów
* poziom blokady ruchu
* wykorzystanie zasobów sieciowych
* opóźnienia transmisji

W badaniu uwzględniono trzy podejścia:

* `IP routing` - klasyczne wyznaczanie najkrótszej ścieżki według opóźnienia
* `CSPF (Constraint Shortest Path First)` - wyznaczanie ścieżki z uwzględnieniem ograniczeń przepustowości oraz dopuszczalnego opóźnienia
* `Weighted Greedy` - routing z dynamiczną funkcją kosztu zależną od opóźnienia i aktualnego obciążenia łączy

---

## Model symulacyjny

### Model sieci

Sieć reprezentowana jest w postaci nieskierowanego grafu `NetworkX`. W takim modelu:

* wierzchołki odpowiadają routerom
* krawędzie odpowiadają łączom transmisyjnym
* każde łącze opisane jest przez zestaw parametrów:
  * `bandwidth` - dostępna przepustowość
  * `delay` - opóźnienie transmisji na łączu
  * `load` - aktualnie zarezerwowane pasmo

Topologia jest generowana losowo z wymuszeniem spójności grafu, tak aby każda para węzłów mogła potencjalnie zostać połączona ścieżką routingu.

### Model ruchu

Ruch modelowany jest jako zbiór niezależnych przepływów opisanych czteroelementową krotką:

`(src, dst, bandwidth, max_delay)`

gdzie:

* `src` oznacza węzeł źródłowy
* `dst` oznacza węzeł docelowy
* `bandwidth` określa wymaganą przepustowość
* `max_delay` oznacza maksymalne dopuszczalne opóźnienie

Przepływy są generowane losowo dla każdej próby eksperymentalnej.

---

## Charakterystyka algorytmów

### IP Routing

Algorytm bazowy wykorzystuje metodę Dijkstry z wagą równą opóźnieniu łącza. Podejście to nie uwzględnia obciążenia sieci ani dostępnego pasma na etapie wyznaczania ścieżki, dlatego pełni funkcję punktu odniesienia dla metod świadomych ograniczeń QoS.

### CSPF

Algorytm `CSPF` usuwa z grafu łącza niespełniające wymagań przepustowości danego przepływu, a następnie wyznacza najkrótszą ścieżkę według opóźnienia. Po wyznaczeniu trasy wykonywana jest dodatkowa weryfikacja ograniczenia `max_delay`.

### Weighted Greedy

Algorytm `Weighted` wykorzystuje dynamiczną funkcję kosztu:

`weight = delay * (1 + beta * utilization)`

gdzie:

* `utilization = load / bandwidth`
* `beta` jest współczynnikiem określającym wpływ obciążenia na koszt ścieżki

Tak zdefiniowana funkcja preferuje ścieżki omijające silnie obciążone łącza, co sprzyja bardziej równomiernemu rozkładowi ruchu w sieci.

---

## Metodologia eksperymentu

Eksperyment został zaprojektowany w taki sposób, aby zapewnić porównywalność wyników między analizowanymi algorytmami.

Najważniejsze założenia metodologiczne są następujące:

* jedno uruchomienie `python main.py` generuje jedną topologię bazową
* ta sama topologia jest wykorzystywana dla całej serii testów w danym uruchomieniu
* ponowne uruchomienie programu skutkuje wygenerowaniem nowej topologii
* w obrębie pojedynczej próby wszystkie algorytmy analizują dokładnie ten sam zestaw przepływów
* stan sieci dla każdego algorytmu jest izolowany przy użyciu `deepcopy`
* dla każdego poziomu obciążenia wykonywana jest seria prób Monte Carlo

Badane poziomy obciążenia obejmują:

* `30` przepływów
* `60` przepływów
* `90` przepływów

Seed wygenerowanej topologii zapisywany jest w pliku:

`plots/run_<timestamp>/run_metadata.json`

Takie podejście pozwala zachować spójność warunków porównawczych w ramach jednej serii eksperymentów, a jednocześnie umożliwia analizę innych topologii przy kolejnym uruchomieniu programu.

---

## Metryki oceny

W projekcie analizowane są następujące miary jakości działania algorytmów:

* `Acceptance ratio` - odsetek zaakceptowanych przepływów
* `Blocking probability` - prawdopodobieństwo odrzucenia przepływu
* `Average delay` - średnie opóźnienie zaakceptowanych przepływów
* `Average link utilization` - średni poziom wykorzystania łączy
* `Maximum link utilization` - maksymalne wykorzystanie łącza, interpretowane jako wskaźnik występowania wąskiego gardła

Dodatkowo rejestrowane są przyczyny odrzuceń:

* `bandwidth` - brak wystarczającej przepustowości
* `delay` - przekroczenie dopuszczalnego opóźnienia
* `no_path` - brak dostępnej ścieżki

Rozróżnienie przyczyn odrzucenia pozwala analizować nie tylko skalę zjawiska blokady, ale również jego dominujący mechanizm.

---

## Generowane wyniki

Po uruchomieniu eksperymentu tworzony jest katalog:

`plots/run_<timestamp>/`

W katalogu tym zapisywane są między innymi:

* `results_details.csv` - szczegółowe wyniki dla poszczególnych prób
* `results_summary.csv` - zagregowane wartości średnie
* `run_metadata.json` - konfiguracja uruchomienia i seed topologii
* `logs/` - logi przebiegu eksperymentu
* `plots/` - wizualizacje topologii i heatmapy obciążenia

Po uruchomieniu skryptu `python generate_plots.py` tworzony jest katalog:

`plots/run_<timestamp>/plots_final/`

zawierający:

* wykresy porównawcze najważniejszych metryk
* wykres struktury odrzuceń `rejection_structure.png`
* plik `aggregated_results.csv`

---

## Wymagania

**Sprzętowe:** standardowy laptop lub komputer, brak wymagań GPU

**Programowe:**
* Python 3.14.2
* Biblioteki: `networkx`, `pandas`, `matplotlib`, `numpy` (zob. `requirements.txt`)

---

## Instalacja i konfiguracja

```bash
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

---

## Uruchomienie

### Uruchomienie eksperymentu

```bash
python main.py
```

**Orientacyjny czas działania: ~49 sekund** na standardowym laptopie.

### Generowanie wykresów i agregacji

```bash
python generate_plots.py
```

---

## Oczekiwany wynik

Projekt uruchomił się poprawnie, jeśli po `python main.py` katalog `plots/run_<timestamp>/` zawiera pliki `results_details.csv` i `run_metadata.json`, a konsola wypisuje podsumowania dla 30 / 60 / 90 przepływów.

W repozytorium zapisano przykładowe wyniki eksperymentu w katalogu `plots/run_1775554883/`. Aby wygenerować wykresy na podstawie tych danych bez uruchamiania eksperymentu:

```bash
python generate_plots.py
```

---

## Struktura projektu

```text
mpls_qos/
├── README.md
├── LICENSE
├── requirements.txt
├── main.py
├── network.py
├── routing.py
├── generate_plots.py
├── demo/
├── plots/
│   └── run_1775554883/        # przykładowe wyniki eksperymentu
└── docs/
    ├── architecture.md
    ├── development.md
    └── (prezentacje i poster)
```

---

## Testy

Projekt nie zawiera testów automatycznych. Weryfikację poprawności działania można przeprowadzić przez:

* porównanie wygenerowanych metryk z zapisanymi wynikami w `plots/run_1775554883/results_summary.csv`

---

## Dokumentacja

* [`docs/architecture.md`](docs/architecture.md) - architektura rozwiązania, komponenty, przepływ danych
* [`docs/development.md`](docs/development.md) - dokumentacja konserwacyjna, rozwijanie projektu
* [`docs/`](docs/) - prezentacje etapów prac magisterskich i poster

---

## Ograniczenia

* Topologia generowana jest losowo — każde uruchomienie daje inne wyniki liczbowe
* Projekt symuluje środowisko sieciowe, nie obsługuje rzeczywistego ruchu sieciowego
* Brak testów automatycznych
* Czas obliczeń ~49 s przy domyślnych parametrach (15 węzłów, 3 poziomy obciążenia, 10 prób)

---

## Główne obserwacje

Dotychczasowe wyniki wskazują na kilka powtarzających się tendencji:

* algorytmy `CSPF` i `Weighted Greedy` zwykle osiągają wyższy współczynnik akceptacji niż routing IP
* algorytm `Weighted Greedy` często skuteczniej ogranicza maksymalne wykorzystanie łączy
* routing IP może osiągać niższe opóźnienia, jednak kosztem większej podatności na przeciążenia
* wraz ze wzrostem obciążenia rośnie znaczenie mechanizmów uwzględniających ograniczenia QoS oraz stan zasobów sieci

---

## Technologie

* Python 3.14.2
* NetworkX
* Pandas
* Matplotlib
* NumPy

---

## Autor

Wojciech Pawłowski — praca magisterska, Uniwersytet im. Adama Mickiewicza w Poznaniu

## Licencja

MIT License — szczegóły w pliku [LICENSE](LICENSE)
