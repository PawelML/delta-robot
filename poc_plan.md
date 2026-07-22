# Robot delta DIY — wstępny HLD i plan POC

**Status:** active HLD v0.4 — cyfrowe P0 zakończone, budżetowe P1 w przygotowaniu
**Charakter projektu:** warsztatowy demonstrator R&D, nie maszyna produkcyjna
**Źródło wymagań zakupowych:** `BOM_delta.md` jest kontrolowaną listą kandydatów P1, nie zamrożonym BOM-em trzech osi

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

Cały kupowany demonstrator ma zmieścić się w przedziale **5 000--6 000 PLN
brutto z dostawą do Polski**. Limit obejmuje mechanikę robota, trzy napędy,
zasilanie i sterowanie, warsztatowe odcięcie napędów, efektor podciśnieniowy
oraz budżetową kamerę i enkoder taśmy. Nie obejmuje posiadanego komputera,
taśmy, drukarki 3D, podstawowych narzędzi ani aparatury pożyczonej lub
wynajętej. W 6 000 PLN musi pozostać rezerwa na wysyłkę, drobne elementy i
nieprzewidziane poprawki; szczegółowy limit kategorii zamknie budżetowy BOM.

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

Wynik przemysłowego profilu referencyjnego P0/P1 z 2026-07-20 (nadal przed pomiarem sprzętu): geometria o promieniach
bazy/platformy 180/65 mm i ramionach 280/450 mm przechodzi próbkowany walec
Ø400×150 mm. Wewnątrz niego prostokątny obszar taśmy 305×200×150 mm zostawia
17,64 mm zapasu promieniowego; wszystkie 10 416 próbek przechodzą przyjęte
marginesy kinematyczne. Pierwszy model dynamiczny dla konserwatywnego detalu 0,50 kg
wskazuje 8,190 Nm peak i 3,507 Nm RMS na osi wyjściowej. Po doliczeniu wybranej
przekładni 18/90, pasa 600-5MGT-15, wałów, tulei, sprzęgła i wirnika wymaganie
silnika wynosi 2,576 Nm peak, 1,096 Nm RMS i 330,48 rpm. Reprezentatywnym
kandydatem do **jednego** testu referencyjnego P1 jest serwo 48 V / 400 W z tą
redukcją 5:1, zgodnie z `docs/specs/p1-single-drive.md`. Obliczenia pozostają
profilem `industrial_reference`, ale nie są aktywnym planem zakupowym przy
limicie 5--6 kPLN. Aktywnie rozwijany `budget_demonstrator` ma zachować tę samą
geometrię i znaleźć uczciwy kompromis udźwig/czas cyklu na podstawie krzywej
moment--prędkość oraz testu jednej osi.

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
       └──> wspólne artefakty JSON
                    │
                    v
            Wizualizator Three.js
                    │
                    v
        Jawny wybór profilu napędu
             │                 │
             v                 v
   industrial_reference   budget_demonstrator
             │                 │
             └────────┬────────┘
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

Model Python jest źródłem prawdy dla obliczeń. Three.js służy do wizualizacji
wyników i interaktywnego poznawania mechanizmu. Komunikacja odbywa się przez
wersjonowane pliki JSON. Ewentualne ROS2 lub pełniejsza symulacja wymagają
osobnej decyzji po fizycznym P1/P2; nie są domyślną kontynuacją P0.

## 4. Architektura repozytorium

Aktualna struktura odpowiedzialności:

```text
delta-robot/
├── BOM_delta.md
├── poc_plan.md
├── delta_model/
│   ├── geometria, IK, FK i kinematyka różniczkowa
│   ├── workspace, dobór geometrii i trajektoria
│   ├── dynamika, dobór napędu i przekładni
│   ├── profile napędu i ich jawne źródła danych
│   └── p1_bench/ — komendy, telemetria, Modbus i ocena gate'u
├── scripts/ — odtwarzalne generatory raportów i artefaktów
├── tests/ — niezależne przypadki, własności i regresje
├── visualizer/ — konsument JSON w Three.js
├── cad/ — parametryczny model stanowiska P1 w ForgeCAD
├── artifacts/ — wersjonowane wyniki JSON/CSV oraz CAD
└── docs/ — specyfikacje, decyzje i pakiet wykonawczy
```

Wizualizator wykorzystuje wzorce sceny i interakcji zaczerpnięte ze
`station_configurator`, ale nie przejmuje jego modeli optycznych ani modelu
czasu. Python pozostaje jedynym źródłem kinematyki; Three.js konsumuje
wersjonowane artefakty.

## 5. Kluczowe interfejsy

| Interfejs | Kontrakt |
|---|---|
| Parametry geometrii → kinematyka | Promienie podstawy i efektora, długości ramion, orientacje osi oraz limity kątowe w spójnych jednostkach |
| IK | Pozycja efektora XYZ → trzy kąty silników albo jawny wynik `unreachable` |
| FK | Trzy kąty silników → pozycja efektora XYZ albo jawna informacja o braku poprawnego rozwiązania |
| Model → wizualizator | Wersjonowany JSON zawierający geometrię, pozy przegubów, trajektorię i metryki |
| Trajektoria → sizing napędu | Pozycja, prędkość i przyspieszenie w funkcji czasu oraz założone masy |
| Sizing → BOM | Wymagany moment szczytowy i RMS, prędkość, przełożenie, napięcie oraz zapas |
| Profil → sizing | Jawny identyfikator, napęd, krzywa moment--prędkość, przekładnia i stan dowodów; brakujący parametr kończy obliczenie błędem |
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

## 9. Profile napędu i specyfikacja jednej osi

Projekt utrzymuje dwa profile opisane w
`docs/specs/p1-design-profiles.md` i
`docs/adr/0003-parallel-industrial-and-budget-profiles.md`:

- `industrial_reference` zachowuje Leadshine `iSV2-RS6040V48G`, Gates 5MGT
  18/90 i dotychczasowe wyniki 0,50 kg / 1 Hz jako policzony punkt odniesienia;
- `budget_demonstrator` zaczyna od zestawu StepperOnline `3-CLYS30-V20` z
  silnikami `23HS40-5004D-E1000`; przeszukanie proxy rekomenduje do dalszego
  domknięcia katalogową przekładnię HTD 5M 20/60 (3:1), 15 mm, pas 450 mm.

Profile współdzielą jeden model. Nie wolno kopiować wzorów ani utrzymywać
osobnych implementacji dynamiki. Budżetowa krzywa moment--prędkość jest obecnie
tylko proxy: dotyczy tego samego silnika, lecz innego drivera i 36 V, dlatego
może odrzucić zbyt wymagający punkt, ale nie może zatwierdzić zakupu.
Ten etap nie zmienia po cichu liczbowych gate'ów P3/P4. Jeżeli przeszukanie
budżetowego profilu wykaże, że nie mieszczą się w limicie 6 000 PLN, ich zmiana
wymaga osobnej jawnej aktualizacji HLD po przedstawieniu osiągalnych wariantów.

Przemysłowa specyfikacja została obliczona i zapisana w
`docs/specs/p1-single-drive.md`. Kandydatem do testu jednej osi jest Leadshine
`iSV2-RS6040V48G` z przekładnią Gates 5MGT 18/90. Kontrakt zawiera:

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

Wynik obliczeniowy nie zastępuje testu. Raport
`artifacts/budget_performance_envelope.json` nie odrzuca katalogowego wariantu
20/60 dla 0,50 kg / 1,50 s (wykorzystanie proxy 0,853 z zapasem 1,30), ale
odrzuca 0,50 kg / 1,25 s i 1,00 s. Dla nominalnych 0,30 kg najszybszym
nieodrzuconym punktem siatki jest 1,25 s. To rekomendacja do domknięcia
mechaniki i kosztu, nie zatwierdzenie napędu: trzeba jeszcze rozstrzygnąć
obciążenie promieniowe wału, przygotować BOM całego robota <=6 000 PLN, a
następnie sprawdzić jedną oś. Zakup trzech kompletów nastąpi dopiero po
zaliczeniu właściwego P1.

## 10. Alternatywy sterowania

| Opcja | Opis | Trade-off |
|---|---|---|
| Klipper/Moonraker | Szybkie uruchomienie STEP/DIR i ruchu mechaniki | Najkrótsza droga do ruchu, ale słabsza kontrola nad stosem robotycznym i eksperymentalne wsparcie `rotary_delta` |
| ROS2 + MCU | ROS2 na komputerze, deterministyczne generowanie ruchu i I/O na mikrokontrolerze | Największa wartość edukacyjna i rekrutacyjna, lecz większy zakres implementacji |
| PLC/motion controller | Przemysłowy kontroler ruchu | Najbliżej wdrożenia przemysłowego, ale zbyt kosztowne i ciężkie dla pierwszego POC |

Na P1 Mesa 7I96S + LinuxCNC jest kandydatem na aparaturę do generowania
Pulse+Direction i przechwycenia zewnętrznego enkodera, a nie wyborem kontrolera
docelowego robota. Decyzja między ROS2 + MCU, PLC/motion controllerem lub innym
stosem pozostaje odroczona do czasu pomiarów P1 i wymagań P2. P0/P1 nie
wprowadzają ROS2 ani Klippera.

## 11. Przejście przez projekt krok po kroku

1. **Zakończone:** P0 waliduje geometrię, workspace i trajektorię w Pythonie i
   pokazuje wyniki w Three.js.
2. **Zakończone cyfrowo:** model dynamiczny, dobór 5:1, kandydat serwa,
   symulator stanowiska oraz kandydacki CAD P1.
3. **Zakończone cyfrowo:** profile przemysłowy/budżetowy i budżetowa obwiednia
   udźwig/czas cyklu/przełożenie z krzywej proxy.
4. **Teraz:** domknięcie mechaniczne wariantu 20/60 oraz przygotowanie
   budżetowego BOM-u całego demonstratora z sumą <=6 000 PLN i rezerwą;
   dotychczasowa checklista przemysłowa pozostaje referencyjna.
5. Zakup wyłącznie elementów jednej budżetowej osi potrzebnych do P1 i zwymiarowania.
6. Pomiar dostarczonych części, zamknięcie pasowań/retencji i dopiero wtedy
   wydanie rysunków do obróbki.
7. Budowa i pomiar stanowiska; wyniki P1 aktualizują model i zamrażają BOM v1.
8. Budowa P2 na ograniczonych prędkościach i kalibracja rzeczywistej geometrii.
9. P3 dodaje chwyt statyczny, a P4 kamerę, enkoder i tracking taśmy.

## 12. Konkretne ryzyka do rozstrzygnięcia

Cyfrowe P0 rozstrzygnęło próbkowane pokrycie Ø400×150 mm, obszar taśmy
305×200 mm i obliczeniową prędkość redukcji 5:1. Aktywne ryzyka są następujące:

1. Rzeczywiste tarcie, podatność, niewspółosiowość i masa mogą przekroczyć
   uproszczenia modelu oraz 30% zapasu; rozstrzyga to dopiero fizyczne P1.
2. Gates 5MGT 18/90 może mieć większy luz i ugięcie pod zmianą kierunku niż
   zakłada model; zewnętrzny E6 musi zmierzyć wyjście za przekładnią.
3. Energia regeneracyjna podczas nawrotów może przeciążyć szynę DC, zasilacz lub
   rezystor 10 Ω; kompatybilność wymaga pisemnego potwierdzenia i pomiaru.
4. Mesa 7I96S i dokładne konfiguracje aparatury mogą być niedostępne albo mieć
   długi termin dostawy; brak identyfikowalnego egzemplarza wstrzymuje zakup.
5. Rysunki katalogowe nie zamykają pasowań, rowków wpustowych i mocowań;
   finalne rysunki powstają z wybranych i zmierzonych części.
6. Kamera 2D nie wystarczy sama do wiarygodnego pomiaru przestrzennej
   powtarzalności XYZ; metoda metrologiczna zostanie zaprojektowana przed P2.
7. Cel 2,0–2,5 pick/s może przekraczać możliwości pierwszej mechaniki i
   efektora; pozostaje celem eksperymentalnym.
8. Mechanizm delta jest zamkniętym łańcuchem, więc późniejszy model URDF/Gazebo
   może wymagać uproszczeń albo dedykowanego rozwiązania.
9. Opublikowana krzywa silnika `23HS40-5004D-E1000` używa CL57T-V41 przy 36 V,
   a nie zestawowego CL57Y-V20 przy 48 V; jest tylko proxy do czasu uzyskania
   zgodnej krzywej lub pomiaru P1.
10. Limit 6 000 PLN może wymusić mniejszy udźwig lub wolniejszy cykl; nie wolno
    utrzymywać celu 0,50 kg / 1 Hz przez ukryte zmniejszenie zapasu napędu.

## 13. Przyjęte decyzje

| # | Decyzja | Uzasadnienie |
|---|---|---|
| 1 | P0 zaczyna się od modelu Python i wizualizatora Three.js | Ułatwia zrozumienie mechanizmu i waliduje geometrię przed zakupami |
| 2 | Python jest źródłem prawdy, a wizualizator konsumuje eksportowane dane | Zapobiega powstaniu dwóch rozbieżnych implementacji kinematyki |
| 3 | Wewnątrz modelu obowiązują SI, baza w `Z=0`, workspace w `Z<0` oraz jawna gałąź knee-out | Zapewnia spójność kodu, testów, wizualizacji i zewnętrznych przykładów referencyjnych |
| 4 | Pełny zakup trzech napędów nastąpi dopiero po P1 | Ogranicza koszt błędnego doboru napędu lub przełożenia |
| 5 | P0 przyjmuje geometrię 180/65/280/450 mm do trajektorii i P1 | Jako jedyna z badanych przechodzi cały próbkowany walec Ø400×150 mm z wymaganym zapasem |
| 6 | Profil przemysłowy odrzuca wcześniejszy stepper 2,0–2,2 Nm i zachowuje serwo 400 W + 5:1 | Wynik dotyczy wymagającego przypadku 0,50 kg / 1 Hz; nie jest ogólnym odrzuceniem wolniejszego profilu budżetowego liczonego z krzywej momentu |
| 7 | Obszar aplikacyjny P0 obejmuje wycentrowany prostokąt 305×200 mm na pełnej wysokości 150 mm | Odpowiada długości profilu 25-305-25 i całej szerokości istniejącej taśmy; oddzielny raport sprawdza go bez utożsamiania prostokąta z całym walcem |
| 8 | Mesa 7I96S + LinuxCNC jest tylko kandydatem aparatury P1 | Nie zamraża kontrolera przyszłego robota przed pomiarami stanowiska |
| 9 | Finalne rysunki stanowiska powstają po wyborze i pomiarze części katalogowych | Zapobiega obróbce według nominalnych wymiarów, które nie zamykają pasowań i interfejsów dostarczonej wersji |
| 10 | Projekt utrzymuje `industrial_reference` i `budget_demonstrator` na jednym modelu | Zachowuje droższe obliczenia jako benchmark bez duplikowania matematyki |
| 11 | Aktywny demonstrator ma kosztować 5--6 kPLN brutto z dostawą do Polski | Przywraca wykonalny zakres DIY; osiągi zostaną wyznaczone, a nie założone |

Kolejne decyzje będą dopisywane po fizycznym teście P1.

## 14. Aktualna bramka: mechaniczne i kosztowe domknięcie budżetowego P1

P0 i przemysłowa programistyczna część P1 są gotowe i zachowane jako punkt
odniesienia. Przeszukanie przełożenia/udźwigu/cyklu jest zapisane w
`docs/specs/p1-budget-transmission-and-envelope.md`; rekomenduje HTD 5M 20/60
do dalszego domknięcia. Przed zakupem i obróbką wariantu budżetowego trzeba:

1. rozstrzygnąć wymagany naciąg pasa i limit 75 N na wale silnika, ewentualnie
   przywrócić podparty wał wejściowy;
2. sprawdzić wykonalność koła 60T, piasty, wału i zakresu ruchu w budżetowym CAD;
3. przygotować pełny BOM z rezerwą i sumą <=6 000 PLN;
4. uzyskać zgodną krzywą CL57Y-V20/48 V albo zaplanować pomiar jednej osi;
5. kupić najwyżej zestaw jednej osi i jej przekładnię;
6. zmierzyć dostarczone części i zaktualizować CAD przed obróbką.

Dotychczasowy BOM, STEP stanowiska Leadshine i checklista zakupowa pozostają
referencją profilu przemysłowego. Bez wykonania powyższych kroków nie wolno ich
używać jako aktywnego polecenia zakupu ani kupować trzech kompletów napędów.
