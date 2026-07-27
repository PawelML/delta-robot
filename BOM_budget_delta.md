# BOM — budżetowy demonstrator delta

**Status:** aktywna prowizoryczna obwiednia kosztowa; nie jest zgodą na zakup  
**Migawka cen:** 2026-07-22  
**Aktualizacja zasobów:** 2026-07-27

**Dostawa:** Polska  
**Profil:** `budget_demonstrator`

Maszynowym źródłem sum i pozycji jest `artifacts/budget_bom.json`, generowany
przez `scripts/generate_budget_bom.py`. Ten dokument tłumaczy kolejność zakupów
i otwarte decyzje. Przemysłowy wariant Leadshine/Gates pozostaje osobno w
`BOM_delta.md` i nie wchodzi do poniższej sumy.

## Mapa plików — gdzie szukać szczegółów

Najpierw należy czytać dokument opisowy `.md`, a do pliku JSON zaglądać po
dokładne wartości, warianty i adresy źródeł. Pliki w `artifacts/` są generowanym
dowodem obliczeń i nie należy poprawiać ich ręcznie.

| Potrzebna informacja | Główne źródło | Co można tam znaleźć |
|---|---|---|
| Aktualna lista zakupów, ilości, ceny i linki do ofert | `artifacts/budget_bom.json` | Dokładne pozycje kosztowe, `source_url`, stan dowodu, bramkę zakupu, założenia i wyłączenia. Jest generowany przez `scripts/generate_budget_bom.py`. |
| Co wolno kupić teraz i w jakiej kolejności | `BOM_budget_delta.md`, szczególnie sekcje 2--4 | Czytelny skrót aktywnego BOM-u oraz ograniczenie mechaniki do jednej osi przed fizycznym P1. |
| Cel projektu, budżet, geometria, pole robocze i bramki P0--P4 | `poc_plan.md` | HLD całego demonstratora i nadrzędne wymagania, których BOM nie może samodzielnie zmieniać. |
| Dokładna tożsamość zestawu napędowego i różnice między profilami | `docs/specs/p1-design-profiles.md` oraz `artifacts/design_profiles.json` | Modele silników i sterowników, zasilanie, parametry obu profili oraz ograniczenia danych z opublikowanej charakterystyki silnika. |
| Dlaczego przyjęto HTD 5M 20/60, pas 450 mm i które cykle są obiecujące | `docs/specs/p1-budget-transmission-and-envelope.md` | Kryteria wyboru przełożenia i opis budżetowej obwiedni osiągów. |
| Pełne wyniki porównania obciążeń, czasów cyklu i wariantów transmisji | `artifacts/budget_performance_envelope.json` | Liczbowe wyniki całego przemiatania wariantów, także tych niewybranych. Jest generowany przez `scripts/generate_budget_performance_envelope.py`. |
| Siły w pasie, odrzucenie montażu 20T na silniku, wałek 8 mm, łożyska i sprzęgło | `docs/specs/p1-budget-mechanical-and-cost-closure.md` | Założenia i kryteria mechanicznego domknięcia jednej budżetowej osi. |
| Dokładne naprężenia, zapasy i obciążenia elementów transmisji | `artifacts/budget_mechanical_closure.json` | Wyniki liczbowe dla pasa, wału, łożysk i sprzęgła. Jest generowany przez `scripts/generate_budget_mechanical_closure.py`. |
| Co wykonać, jakie wymiary zmierzyć po dostawie i czego jeszcze nie zamrażać | `docs/p1-budget-bench-fabrication-package.md` | Pakiet wykonawczy stanowiska jednej osi, kontrolowane wymiary, otwarte pasowania i blokery zwolnienia części do obróbki. |
| Parametryczny model CAD stanowiska | `cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js` | Źródłowy model ForgeCAD; to tutaj zmienia się parametry modelu, a nie w plikach eksportowych. |
| Rysunki poglądowe i model do konsultacji z wykonawcą | `artifacts/cad/p1-budget-single-axis-bench-report.pdf`, `artifacts/cad/p1-budget-single-axis-bench.step` | PDF z widokami i wymiarami oraz STEP do wymiany. Są materiałem kandydackim; pasowania końcowe zależą od pomiaru dostarczonych części. |
| Zbliżenia pasa i wałka oraz wynik kontroli CAD | `artifacts/cad/p1-budget-single-axis-bench-belt.png`, `artifacts/cad/p1-budget-single-axis-bench-jackshaft.png`, `artifacts/cad/inspections/p1-budget-single-axis-bench/` | Szybka kontrola wizualna układu i zapis inspekcji kolizji oraz łączności części. |
| Zakres fizycznego testu P1 | `poc_plan.md` | Kryteria przejścia bramki. `docs/specs/p1-bench-software.md` opisuje istniejący symulator, logowanie i raportowanie, ale adapter sprzętowy jest obecnie przygotowany dla przemysłowego Leadshine, a nie potwierdzonego `CL57Y-V20`. |

Najkrótsza ścieżka przed wydaniem pieniędzy to:

1. sprawdzić dozwolony zakres P1 w sekcji 3 tego dokumentu;
2. otworzyć `artifacts/budget_bom.json` i potwierdzić dokładne modele, ilości,
   aktualne ceny oraz dostawę do Polski;
3. dla transmisji porównać pozycję z
   `docs/specs/p1-budget-mechanical-and-cost-closure.md`;
4. przed zleceniem obróbki użyć
   `docs/p1-budget-bench-fabrication-package.md`;
5. po dostawie zmierzyć rzeczywiste części i dopiero wtedy zamrozić pasowania
   oraz rysunki wykonawcze.

### Dokumenty nieaktywne dla budżetowych zakupów

`BOM_delta.md`, `docs/specs/p1-single-drive.md`,
`docs/p1-procurement-checklist.md`, `docs/p1-bench-fabrication-package.md` i
`docs/p1-supplier-research-poland-2026-07-20.md` dotyczą zachowanego profilu
`industrial_reference`. Nie należy na ich podstawie kupować części do aktywnego
demonstratora budżetowego. Służą jako punkt porównania i nie wchodzą do sumy
5 821,97 PLN.

Repozytorium nie ma jeszcze osobnej, aktywnej checklisty przedpłatowej dla
profilu `budget_demonstrator`, która w jednym miejscu zbiera potwierdzenia
dostawców i pomiary odbiorcze. Do czasu jej przygotowania obowiązują sekcja 3
tego dokumentu oraz blokery z
`docs/p1-budget-bench-fabrication-package.md`. Sam BOM nadal nie jest zgodą na
zakup.

## 1. Wynik kosztowy

| Kategoria | Brutto PLN |
|---|---:|
| Zestaw trzech napędów i zasilacz | 740,84 |
| Trzy przekładnie, podpory, wały i sprzęgła | 1 581,13 |
| Ramiona, pręty, przeguby i platforma | 600,00 |
| Rama i proste osłony warsztatowe | 650,00 |
| Sterowanie lokalne | 200,00 |
| Rozdzielnia, odcięcie, E-stop, zabezpieczenia i przewody | 300,00 |
| Podciśnienie | 250,00 |
| Zlecany druk 3D prototypów i adapterów | 250,00 |
| Sprzężenie z taśmy | 150,00 |
| Integracja i materiały | 250,00 |
| Dostawy do Polski | 200,00 |
| **Suma bazowa** | **5 171,97** |
| **Rezerwa jawna** | **650,00** |
| **Razem** | **5 821,97** |

Suma mieści się w przyjętym limicie 5--6 tys. PLN, ale część pozycji to limity
kosztowe wymagające ofert, a nie potwierdzone ceny. Rezerwy nie wolno wydawać
po cichu: przekroczenie pozycji ma być zapisane i odjęte od 650 PLN.

## 2. Pozycje katalogowe do potwierdzenia

| Pozycja | Ilość docelowa | Cena przyjęta | Co sprawdzić przed płatnością |
|---|---:|---:|---|
| StepperOnline `3-CLYS30-V20` | 1 zestaw | 740,84 PLN | Magazyn DE, koszt dostawy, dokładne rewizje 3 silników, 3 sterowników i zasilacza 48 V / 500 W, zwrot i gwarancja |
| Koło HTD `20-5M-15` | 3 | 40,00 PLN/szt. z wykończeniem | Najpierw jedna sztuka; otwór 8 mm, bicie i pewna retencja na osobnym wałku |
| Koło HTD `60-5M-15` | 3 | 57,49 + 50,00 PLN/szt. obróbki | Najpierw jedna sztuka; zmierzyć piastę, dobrać otwór/rowek lub zacisk i sprawdzić bicie |
| Pas `450-5M-15` | 3 + 1 zapas | 49,45 PLN/szt. | Oznaczenie podziałki, szerokość, metoda i pomiar napięcia montażowego |
| Sprzęgło R+W `BKL/3/8/8` | 3 | 130,38 PLN/szt. | Oba otwory 8 mm, 3 Nm, instrukcja momentu śrub zaciskowych |
| Łożysko SKF `608-2RS/2RSH` | 6 | 6,62 PLN/szt. | Jedna zgodna seria 8x22x7; pasowanie dopiero z aktualnej karty i pomiaru części |

Pełne adresy ofert i stany dowodowe są zapisane przy każdej pozycji w JSON.
Ceny i magazyn należy sprawdzić ponownie w dniu tworzenia koszyka.

Kamera i kontrolowane oświetlenie są już posiadane, więc nie występują jako
pozycja zakupowa. Zwolnione 250 PLN przechodzi na zewnętrzny druk FDM. Drukarka
3D nie jest wymagana ani ujęta w kosztach demonstratora.

## 3. Co wolno kupić na P1

Zestaw napędowy jest sprzedawany jako trzyosiowy, więc może zostać kupiony jako
jedna pozycja, jeśli potwierdzenie dostawy i rewizji nie ujawni problemu.
Mechanikę należy jednak uwolnić tylko dla **jednej osi**:

1. jedno koło 20T, jedno 60T, jeden pas i jedno sprzęgło;
2. dwa łożyska 608, jeden wałek wejściowy i jeden regulowany wspornik;
3. prowizoryczny wał wyjściowy, dwa wybrane łożyska wyjściowe i piasta ramienia;
4. płytę/bracket stanowiska oraz podstawową elektrykę odcięcia i pomiaru;
5. dopiero po dostawie: pomiary części, pasowania, retencja i rysunki do obróbki.

Nie należy jeszcze wykonywać dwóch pozostałych przekładni, pełnej ramy ani
kupować elementów P3/P4. Najpierw jedna oś ma przejść wymagania fizycznego P1.

## 4. Co trzeba wykonać, a nie kupić z katalogu

- wałek wejściowy C45 Ø8 mm z kołem między dwoma łożyskami oddalonymi o 50 mm;
- regulowany nośnik wejścia z zakresem -15 do +3 mm;
- obudowy i retencję łożysk na podstawie pomiaru dostarczonej serii;
- wał i piastę wyjściową po wyborze konkretnego łożyska 12x28x8;
- wspornik NEMA 23 według dostarczonego silnika;
- bezpieczne mechanicznie mocowanie ramienia i masy testowej;
- okablowanie, odcięcie oraz logowanie napięcia szyny, temperatury i błędu
  nadążania zgodnie z bramką P1.

Źródłem układu jest
`cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js`, a gotowe podglądy i
pakiet wymiarowy znajdują się w `artifacts/cad/`.

## 5. Założenia utrzymujące limit

W budżecie są ponownie użyte: komputer, narzędzia warsztatowe, kamera,
oświetlenie i istniejąca taśma. Projekt nie zakłada własnej drukarki 3D.
Prototypy, uchwyty, szablony, osłony i nisko obciążone adaptery mogą być
zamawiane partiami z PLA/PETG/ASA/PA w ramach limitu 250 PLN. Zwykły FDM nie
zastępuje metalowych podpór wałów, mocowań łożysk ani elementów przenoszących
moment bez osobnego obliczenia i walidacji.

Przemysłowa aparatura TC-08/E6/Mark-10/Mesa nie jest kupowana; potrzebne
wielkości na P1 trzeba zmierzyć pożyczoną/wynajętą aparaturą albo tańszym torem
z udokumentowaną kalibracją i rozdzielczością.

Największe ryzyka przekroczenia ceny to przeguby/pręty, rama i lokalna obróbka.
Niepowodzenie fizycznego P1 może też wymusić inne przełożenie lub napęd; dlatego
pozostałe dwie osie są zablokowane do wyniku testu.
