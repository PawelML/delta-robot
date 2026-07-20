# Robot delta DIY — wstępny HLD i plan POC

**Status:** draft 0.1 do przeglądu
**Charakter projektu:** warsztatowy demonstrator R&D, nie maszyna produkcyjna
**Źródło wymagań zakupowych:** po walidacji modelu; obecny `BOM_delta.md` jest listą hipotez, nie zamrożonym BOM-em

Zasady realizacji projektu są opisane w `docs/development-process.md`, a instrukcje obowiązujące narzędzia kodujące w `AGENTS.md`.

## 1. Problem

Celem jest zaprojektowanie i zbudowanie własnego robota delta do pick-and-place nad taśmą. Projekt ma najpierw udowodnić poprawność geometrii, kinematyki i doboru napędu w symulacji, a następnie przejść przez kontrolowane etapy uruchomienia sprzętu.

Demonstrator ma docelowo łączyć:

- mechanikę robota delta,
- model kinematyczny i uproszczony model dynamiczny,
- wizualizację 3D ułatwiającą zrozumienie ruchu,
- sterowanie trzema napędami,
- efektor podciśnieniowy,
- kamerę i enkoder taśmy,
- pomiary powtarzalności, czasu cyklu i skuteczności chwytu.

Projekt ma być dowodem kompetencji inżynierskich, dlatego każda ważna deklaracja ma wynikać z kodu, obliczeń lub powtarzalnego pomiaru.

## 2. Zakres i założenia początkowe

Założenia są punktem startowym do weryfikacji, a nie gwarantowanymi parametrami gotowego urządzenia.

| Parametr | Założenie początkowe | Uzasadnienie |
|---|---:|---|
| Użyteczny workspace | Ø350–400 mm × 150 mm | Rozmiar odpowiedni dla demonstratora nad istniejącą taśmą |
| Nominalny detal | do 0,30 kg | Realistyczny pierwszy cel dla szybkiego POC |
| Maksymalny testowany detal | 0,50 kg | Górne założenie z pierwotnego BOM-u; wymaga potwierdzenia obliczeniami |
| Minimalny cel czasu cyklu P4 | 1,0 pick/s | Pierwszy mierzalny cel dla trackingu ruchomej taśmy |
| Cel rozwojowy | 1,5 pick/s | Wartość osiągana dopiero po stabilnym P4 |
| Cel eksperymentalny | 2,0–2,5 pick/s | Stretch goal, nie kryterium powodzenia pierwszej wersji |
| Efektor | podciśnieniowy z wakuostatem | Pozwala potwierdzać chwyt niezależnie od samej komendy |
| Środowisko | prywatny warsztat | Brak przeznaczenia do eksploatacji produkcyjnej |

Poza zakresem pierwszej wersji znajdują się:

- certyfikacja i pełna architektura bezpieczeństwa maszyny produkcyjnej,
- czwarta oś obrotowa efektora,
- sterowanie siłą i backdrivability,
- deklarowanie zgodności z pełną procedurą ISO 9283,
- wdrożenie u klienta przed zakończeniem P4.

Warsztatowe minimum pozostaje obowiązkowe: fizyczne odcięcie zasilania napędów, ograniczone prędkości podczas uruchamiania oraz brak osób w przestrzeni ruchu robota.

## 3. Podejście

Projekt będzie rozwijany od modelu do sprzętu. Geometria i napęd nie zostaną zamrożone na podstawie samego katalogu lub wizualizacji.

```text
Wymagania i HLD
       │
       v
Model matematyczny w Pythonie ──> testy automatyczne
       │
       ├──> workspace / osobliwości / trajektorie
       ├──> prędkości / przyspieszenia / momenty
       └──> artefakty JSON
                    │
                    v
            Wizualizator Three.js
                    │
                    v
       Specyfikacja jednego napędu
                    │
                    v
          Test napędu na stole
                    │
                    v
             Zamrożenie BOM v1
                    │
                    v
        Budowa P2 → P3 → P4
```

Model Python jest źródłem prawdy dla obliczeń. Three.js służy do wizualizacji wyników i interaktywnego poznawania mechanizmu. Na początku komunikacja między nimi odbywa się przez pliki JSON; ROS2 i pełniejsza symulacja mogą zostać dodane po ustabilizowaniu geometrii.

## 4. Architektura repozytorium

Planowana struktura:

```text
delta-robot/
├── BOM_delta.md
├── poc_plan.md
├── delta_model/
│   ├── geometry.py
│   ├── inverse_kinematics.py
│   ├── forward_kinematics.py
│   ├── workspace.py
│   ├── trajectory.py
│   └── motor_sizing.py
├── tests/
├── visualizer/
│   ├── src/
│   │   ├── app.js
│   │   ├── delta_geometry.js
│   │   └── ui.html
│   ├── build.sh
│   └── index.html
└── artifacts/
    ├── workspace.json
    ├── trajectories.json
    └── motor_requirements.json
```

Wizualizator wykorzysta sprawdzone wzorce z `/home/pawelo/CODE/digital-twin/station_configurator`: scenę Three.js, kamerę orbitalną, panel parametrów, `localStorage`, animację cyklu, statystyki i ostrzeżenia. Nie zostaną przeniesione modele optyczne, geometria szafy ani uproszczony model czasu tamtego stanowiska.

## 5. Kluczowe interfejsy

| Interfejs | Kontrakt |
|---|---|
| Parametry geometrii → kinematyka | Promienie podstawy i efektora, długości ramion, orientacje osi oraz limity kątowe w spójnych jednostkach |
| IK | Pozycja efektora XYZ → trzy kąty silników albo jawny wynik `unreachable` |
| FK | Trzy kąty silników → pozycja efektora XYZ albo jawna informacja o braku poprawnego rozwiązania |
| Model → wizualizator | Wersjonowany JSON zawierający geometrię, pozy przegubów, trajektorię i metryki |
| Trajektoria → sizing napędu | Pozycja, prędkość i przyspieszenie w funkcji czasu oraz założone masy |
| Sizing → BOM | Wymagany moment szczytowy i RMS, prędkość, przełożenie, napięcie oraz zapas |
| Napęd → późniejsze sterowanie | Komenda pozycji/prędkości, sygnał błędu drivera i dostępny odczyt enkodera |

## 6. Słownik

| Termin | Znaczenie |
|---|---|
| FK | Kinematyka prosta: wyznaczenie XYZ efektora z kątów silników |
| IK | Kinematyka odwrotna: wyznaczenie kątów silników dla zadanego XYZ |
| Workspace | Zbiór pozycji osiągalnych bez przekroczenia ograniczeń mechanicznych |
| Użyteczny workspace | Część workspace'u z zachowanym zapasem od limitów i osobliwości |
| Osobliwość | Konfiguracja, w której mały ruch efektora może wymagać bardzo dużego ruchu przegubów lub robot traci kontrolę nad kierunkiem ruchu |
| Cykl 25-305-25 | Porównywalny cykl pick-and-place: ruch pionowy 25 mm, poziomy 305 mm i pionowy 25 mm |
| Moment szczytowy | Najwyższy chwilowy moment wymagany podczas trajektorii |
| Moment RMS | Zastępczy moment cieplny używany do oceny obciążenia napędu w całym cyklu |
| Gate | Mierzalny warunek, który trzeba spełnić przed przejściem dalej |

## 7. Etapy P0–P4 i kryteria

### P0 — zweryfikowany model cyfrowy

Zakres:

- parametryczny model geometrii delty,
- IK i FK w Pythonie,
- generowanie workspace'u,
- interaktywny wizualizator Three.js,
- animacja prostych trajektorii i cyklu 25-305-25,
- jawne oznaczanie punktów nieosiągalnych i pozycji bliskich limitom.

Gate P0:

- test `IK → FK` ma błąd numeryczny poniżej 0,01 mm dla minimum 10 000 poprawnych losowych punktów,
- rozwiązania naruszające limity kątowe są odrzucane,
- wizualizator pokazuje wszystkie trzy górne ramiona, sześć dolnych prętów i platformę bez rozłączania geometrii,
- zmiana wymiarów przebudowuje workspace,
- cykl 25-305-25 jest osiągalny w wybranym użytecznym obszarze albo model jawnie pokazuje, dlaczego nie jest,
- parametry modelu i wyniki można wyeksportować do JSON.

### P1 — model dynamiczny i jeden napęd na stole

Zakres:

- uproszczony model mas, prędkości, przyspieszeń i momentów,
- oszacowanie momentu szczytowego i RMS dla cyklu,
- wybór jednego kandydata silnik + driver + przełożenie,
- fizyczny test jednego napędu z docelowym kołem, paskiem i napięciem zasilania.

Gate P1:

- model podaje wymagany moment i prędkość dla całej trajektorii, nie tylko dla statycznej pozycji,
- wybrany napęd ma co najmniej 30% obliczeniowego zapasu momentu w planowanym punkcie pracy,
- napęd wykonuje minimum 1 000 cykli nawrotu bez alarmu drivera i bez narastającego błędu pozycji,
- zmierzona powtarzalność wyjścia przekładni jest raportowana w stopniach,
- temperatura silnika i drivera stabilizuje się w granicach dopuszczonych przez ich dokumentację,
- po teście można podjąć świadomą decyzję: zachować, zmienić przełożenie albo odrzucić napęd.

### P2 — złożony robot bez procesu pick-and-place

Zakres:

- rama, trzy napędy, ramiona i platforma,
- bazowanie,
- kontrolowane ruchy XYZ,
- porównanie modelu cyfrowego z rzeczywistym ruchem,
- pierwsza kalibracja geometryczna.

Gate P2:

- robot wykonuje minimum 1 000 powtarzalnych cykli bez kolizji i utraty synchronizacji,
- osiąga wcześniej zdefiniowany użyteczny workspace,
- wraca do punktu testowego z powtarzalnością nie gorszą niż 1,0 mm w początkowej metodzie pomiarowej,
- rzeczywiste limity ruchu i offsety są zapisane w konfiguracji, a nie korygowane ręcznie podczas każdego startu,
- różnice między modelem i sprzętem są opisane oraz prowadzą do aktualizacji parametrów modelu.

### P3 — statyczne pick-and-place

Zakres:

- efektor podciśnieniowy,
- wakuostat potwierdzający chwyt,
- pobieranie ze stałych pozycji bez ruchu taśmy,
- logowanie sukcesów i przyczyn niepowodzeń.

Gate P3:

- minimum 500 automatycznych prób z detalem nominalnym 0,30 kg,
- co najmniej 98% poprawnych cykli w ustalonych warunkach testu,
- brak zaliczenia chwytu, gdy wakuostat nie potwierdzi podciśnienia,
- nieudany chwyt kończy się kontrolowanym powrotem lub ponowną próbą,
- raport zawiera czas cyklu, rozrzut pozycji oraz kategorie błędów.

Test 0,50 kg jest rozszerzeniem P3 i nie blokuje przejścia do P4, jeśli model napędu lub mechaniki wykaże, że takie obciążenie jest nieuzasadnione.

### P4 — tracking ruchomej taśmy

Zakres:

- odczyt enkodera taśmy,
- detekcja i lokalizacja detalu,
- predykcja jego pozycji w chwili chwytu,
- wykonanie picku bez zatrzymywania taśmy,
- rejestrowanie opóźnień i skuteczności.

Gate P4:

- minimum 500 automatycznych prób przy ustalonej prędkości taśmy,
- co najmniej 90% poprawnych picków przy 100 mm/s,
- utrzymany średni throughput minimum 1,0 pick/s w serii testowej,
- raportowane opóźnienia perception → decyzja → komenda ruchu,
- wykres prędkość taśmy kontra skuteczność,
- każda nieudana próba otrzymuje kategorię: percepcja, tracking, trajektoria, chwyt lub odłożenie.

Po osiągnięciu gate P4 cele rozwojowe wynoszą ≥95% skuteczności, 1,5 pick/s oraz test długotrwały obejmujący co najmniej 10 000 cykli.

## 8. Model kinematyczny i dynamiczny

### Model kinematyczny musi dostarczyć

- FK i IK,
- kontrolę limitów kątowych,
- pozycje wszystkich przegubów do wizualizacji,
- wykrywanie konfiguracji niemożliwych geometrycznie,
- generowanie użytecznego workspace'u,
- miarę zbliżania się do osobliwości,
- przebiegi kątów, prędkości i przyspieszeń dla trajektorii.

### Pierwszy model dynamiczny może upraszczać

- ramiona jako bryły sztywne o skupionej lub równomiernej masie,
- dolne pręty jako lekkie elementy o znanej masie,
- detal i efektor jako masę skupioną,
- tarcie i sprężystość jako zapas projektowy zamiast dokładnego modelu.

Model nie może pomijać bezwładności ruchomych ramion ani opierać doboru silnika wyłącznie na statycznym udźwigu.

## 9. Specyfikacja jednego napędu

Specyfikacja zostanie zaktualizowana po P0 i pierwszym przebiegu modelu dynamicznego. Musi zawierać:

- wymagany zakres kąta osi,
- maksymalną prędkość i przyspieszenie osi,
- moment szczytowy,
- moment RMS,
- przełożenie i wynikową prędkość wyjścia,
- wymaganą rozdzielczość pozycjonowania,
- dopuszczalny luz i podatność przekładni,
- napięcie oraz szacowaną moc zasilania,
- sposób wykrycia błędu pozycji,
- kryteria temperaturowe testu stołowego.

Zakup trzech kompletów napędów nastąpi dopiero po zaliczeniu P1. Wcześniej kupowany jest najwyżej jeden reprezentatywny komplet do testów.

## 10. Alternatywy sterowania

| Opcja | Opis | Trade-off |
|---|---|---|
| Klipper/Moonraker | Szybkie uruchomienie STEP/DIR i ruchu mechaniki | Najkrótsza droga do ruchu, ale słabsza kontrola nad stosem robotycznym i eksperymentalne wsparcie `rotary_delta` |
| ROS2 + MCU | ROS2 na komputerze, deterministyczne generowanie ruchu i I/O na mikrokontrolerze | Największa wartość edukacyjna i rekrutacyjna, lecz większy zakres implementacji |
| PLC/motion controller | Przemysłowy kontroler ruchu | Najbliżej wdrożenia przemysłowego, ale zbyt kosztowne i ciężkie dla pierwszego POC |

Preferowana ścieżka do dalszego zatwierdzenia: ROS2 + MCU. Klipper pozostaje możliwym narzędziem do szybkiej walidacji mechaniki, nie jest jeszcze decyzją architektoniczną.

## 11. Przejście przez projekt krok po kroku

1. Użytkownik zmienia geometrię w wizualizatorze i obserwuje ramiona oraz workspace.
2. Python waliduje tę samą konfigurację na dużej liczbie punktów.
3. Użytkownik wybiera trajektorię testową i widzi kąty oraz limity osi.
4. Model dynamiczny wylicza wymagania napędu.
5. Powstaje specyfikacja jednego napędu, a następnie test stołowy.
6. Wyniki testu aktualizują model i dopiero wtedy zamrażają BOM v1.
7. Robot jest składany i uruchamiany na ograniczonych prędkościach.
8. Kalibracja wiąże model cyfrowy z rzeczywistą geometrią.
9. Dodawany jest chwyt statyczny i pomiar skuteczności.
10. Na końcu dochodzą kamera, enkoder i tracking taśmy.

## 12. Konkretne ryzyka do rozstrzygnięcia

1. Zakładany workspace Ø400 × 150 mm może wymagać konfiguracji zbyt bliskich osobliwościom; P0 musi pokazać użyteczny, nie tylko geometrycznie osiągalny zakres.
2. Redukcja 5:1 może ograniczyć maksymalną prędkość osi poniżej potrzeb cyklu 25-305-25; rozstrzyga to model i P1.
3. Pasek GT2 oraz drukowane koło 100T mogą ugiąć się na tyle, że powtarzalność wyjścia przekroczy 0,1°; P1 musi to zmierzyć na rzeczywistym zestawie.
4. Enkoder w closed-loop stepperze może być dostępny tylko dla drivera, więc system nadrzędny nie będzie znał rzeczywistej pozycji osi; trzeba sprawdzić interfejs konkretnego drivera przed zakupem.
5. Kamera 2D nie wystarczy sama do wiarygodnego pomiaru przestrzennej powtarzalności XYZ; metoda metrologiczna zostanie osobno zaprojektowana przed P2.
6. Cel 2,0–2,5 pick/s może przekraczać możliwości pierwszej mechaniki i efektora; pozostaje celem eksperymentalnym, nie warunkiem powodzenia.
7. Model Three.js może rozjechać się z modelem Python, jeśli oba będą niezależnie liczyć kinematykę; format JSON i testy zgodności mają temu zapobiec.
8. Mechanizm delta jest zamkniętym łańcuchem kinematycznym, więc późniejszy model URDF/Gazebo może wymagać uproszczeń albo dedykowanego rozwiązania.

## 13. Decyzje do zatwierdzenia po przeglądzie

| # | Decyzja | Uzasadnienie |
|---|---|---|
| 1 | P0 zaczyna się od modelu Python i wizualizatora Three.js | Ułatwia zrozumienie mechanizmu i waliduje geometrię przed zakupami |
| 2 | Python jest źródłem prawdy, a wizualizator konsumuje eksportowane dane | Zapobiega powstaniu dwóch rozbieżnych implementacji kinematyki |
| 3 | Wewnątrz modelu obowiązują SI, baza w `Z=0`, workspace w `Z<0` oraz jawna gałąź knee-out | Zapewnia spójność kodu, testów, wizualizacji i zewnętrznych przykładów referencyjnych |
| 4 | Pełny zakup trzech napędów nastąpi dopiero po P1 | Ogranicza koszt błędnego doboru napędu lub przełożenia |

Kolejne decyzje będą dopisywane po P0, modelu dynamicznym i teście P1.

## 14. Bramka rozpoczęcia kodowania

Kodowanie P0 może rozpocząć się po krótkim przeglądzie tego dokumentu. Przed rozpoczęciem trzeba zatwierdzić jedynie:

1. że pierwszym celem jest model Python + wizualizator Three.js,
2. że parametry tabeli w sekcji 2 są założeniami startowymi,
3. że zakup pełnego zestawu napędów czeka na wynik P1.

Nie trzeba przed P0 wybierać konkretnego silnika, sterownika ROS2, mikrokontrolera ani finalnej konstrukcji ramy.
