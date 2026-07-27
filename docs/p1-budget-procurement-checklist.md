# P1 — budżetowa checklista zakupowa i odbiorcza

**Status:** aktywna checklista przygotowania jednej osi; nie jest automatyczną
zgodą na zakup  
**Profil:** `budget_demonstrator`  
**Data danych katalogowych:** 2026-07-22, z doprecyzowaniem otworów kół
2026-07-27  
**Dostawa:** Polska

## 1. Cel i źródła

Ten dokument jest czytelną instrukcją przejścia od kandydackiego BOM-u do
zmierzonych części jednej osi P1. Nie zastępuje obliczeń ani nie tworzy drugiego
źródła sum:

- ceny, ilości docelowe, linki i bramki pochodzą z
  `artifacts/budget_bom.json`;
- skrót kosztów i dozwolona kolejność są w `BOM_budget_delta.md`;
- wymagania transmisji są w
  `docs/specs/p1-budget-mechanical-and-cost-closure.md`;
- wymiary kandydackiego stanowiska i blokery obróbki są w
  `docs/p1-budget-bench-fabrication-package.md`;
- źródłem CAD jest
  `cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js`.

Aktualizacja ceny, ilości lub linku zaczyna się w generatorze BOM-u, nie w tej
checkliście. Tutaj zapisuje się potwierdzenia dostawcy, wynik oględzin, pomiary,
oferty obróbki i decyzję użytkownika. Linki poniżej są wygodną migawką
kandydatów z BOM-u, a nie potwierdzeniem bieżącej dostępności.

## 2. Zasady użycia

- Zestaw `3-CLYS30-V20` jest jednym niepodzielnym kandydackim SKU, ale
  mechanika przed fizycznym P1 obejmuje tylko jedną oś.
- Nie kupować jeszcze mechaniki dwóch pozostałych osi, pełnej ramy ani
  elementów P2--P4.
- Nie traktować zdjęcia, nazwy handlowej ani nominalnego wymiaru jako dowodu
  pasowania. Zapisać dokładny kod, rewizję i dokumentację zamawianej wersji.
- Nie zlecać otworów, rowków, pasowań ani retencji przed otrzymaniem i
  zmierzeniem współpracujących części.
- Każdy zamiennik zmieniający przełożenie, podziałkę, szerokość pasa, średnicę
  wału, masę, bezwładność lub interfejs napędu wraca do oceny modelu i CAD-u.
- Ceny, dostępność, dostawę, VAT, gwarancję i zwrot sprawdzić ponownie w dniu
  składania zamówienia.
- Pole zaznaczyć dopiero po zapisaniu dowodu w rejestrze z sekcji 9.

## 3. Koszyk do przygotowania dla jednej osi P1

`Ilość P1` oznacza liczbę elementów mechanicznych dopuszczoną przed fizycznym
testem. Nie zmienia docelowych ilości zapisanych w BOM-ie.

| Pozycja | ID w BOM-ie | Ilość P1 | Stan przed płatnością |
|---|---|---:|---|
| [Zestaw StepperOnline `3-CLYS30-V20`](https://www.stepperonline.pl/zestaw-cnc-z-silnikiem-krokowym-z-zamknieta-petla-ys-series-3-osie-v2-0-3-00nm-424-83oz-in-silnik-nema-23-z-przewodami-2-0m-i-zasilaczem-3-clys30-v20) | `drive_kit_3axis` | 1 niepodzielny zestaw | Potwierdzić dokładne silniki, sterowniki, zasilacz, przewody i magazyn |
| [Koło HTD `20-5M-15`](https://www.ebmia.pl/kola-do-pasow-htd-5m/832-kolo-zebate-htd-20-5m-15-do-pasa-szerokosci-15mm.html) | `pulley_20t_finished` | 1 | Wybrać surowe koło do obróbki albo jednoznaczny wariant Ø8 mm |
| [Koło HTD `60-5M-15`](https://www.ebmia.pl/kola-do-pasow-htd-5m/655-kolo-zebate-htd-60-5m-15-do-pasa-szerokosci-15mm.html) | `pulley_60t` | 1 | Kupić z naddatkiem piasty; nie zlecać jeszcze otworu docelowego |
| Obróbka koła 60T | `pulley_60t_machining` | oferta dla 1 | Wycena wstępna; wykonanie dopiero po pomiarach |
| [Pas `450-5M-15`](https://www.ebmia.pl/pasy-zebate-htd-5m/1350-pas-zebaty-450-5m-15-z90.html) | `belt_450_5m_15` | 1 | Potwierdzić 90 zębów, HTD 5M i szerokość 15 mm |
| [Sprzęgło R+W `BKL/3/8/8`](https://www.ebmia.pl/sprzegla-mieszkowe-bkl/91682-sprzeglo-bezluzowe-bkl-3-8-8.html) | `coupling_bkl3_8_8` | 1 | Potwierdzić dwa otwory 8 mm i moment znamionowy 3 Nm |
| [Łożyska wejściowe 608](https://www.hurtowniatechpol.pl/product/Lozysko-608-2RS-SKF-IND-8x22x7-s20832) | `bearing_608_2rs` | 2 | Wybrać jedną dokładną serię 8x22x7 mm |
| Podpora i wałek wejściowy | `input_support_fabrication` | oferta dla 1 | Materiał i obróbka po pomiarze koła, łożysk i sprzęgła |
| Podpora i wał wyjściowy | `output_supports` | oferta dla 1 | Najpierw wybrać dokładne łożyska; Ø12 pozostaje prowizoryczne |
| Podstawowa elektryka stanowiska | część `electrical_panel` | 1 tor P1 | Dobór po otrzymaniu instrukcji zasilacza i sterownika |

## 4. Potwierdzenia przed płatnością

### 4.1 Zestaw napędowy

- [ ] Oferta wskazuje dokładnie StepperOnline `3-CLYS30-V20`.
- [ ] Potwierdzono trzy silniki `23HS40-5004D-E1000`.
- [ ] Potwierdzono trzy sterowniki `CL57Y-V20`, ich rewizję i instrukcję.
- [ ] Potwierdzono zasilacz 48 V / 500 W oraz zawartość zestawu przewodów.
- [ ] Zapisano cenę brutto z dostawą do Polski, magazyn wysyłkowy i termin.
- [ ] Zapisano warunki gwarancji, zwrotu oraz procedurę dla uszkodzonej części
  niepodzielnego zestawu.
- [ ] Uzyskano zgodną charakterystykę moment--prędkość dla tego sterownika i
  napięcia albo zachowano status `proxy_only`; brak krzywej nie jest ukryty.

### 4.2 Koło wejściowe HTD 20T

Kandydacki link BOM-u prowadzi do stalowego `20-5M-15/2F`. Strona katalogowa
podaje 20 zębów, podziałkę 5 mm, szerokość pasa 15 mm, średnicę podziałową
31,83 mm, średnicę zewnętrzną 30,69 mm, kołnierz Ø36 mm, piastę Ø23 mm i
otwór bazowy Ø6 mm. CAD odwzorowuje te gabaryty. Wymagane wyjście projektu to
otwór Ø8 mm i jawnie wybrana retencja na osobno podpartym wałku.

- [ ] Potwierdzono dokładny wariant, materiał, liczbę kołnierzy i aktualny
  rysunek.
- [ ] Wybrano jedną ścieżkę: koło z otworem bazowym Ø6 mm do obróbki **albo**
  identyfikowalny wariant fabrycznie wykończony na Ø8 mm.
- [ ] Dla wariantu gotowego potwierdzono tolerancję Ø8 mm, rowek/zacisk oraz
  sposób retencji; sama nazwa „otwór 8 mm” nie wystarcza.
- [ ] Dla wariantu surowego wykonawca potwierdził możliwość współosiowego
  wykonania Ø8 mm po pomiarze dostarczonego wałka.
- [ ] Całkowity koszt koła, obróbki i dostawy mieści się w limicie pozycji
  `pulley_20t_finished`.

### 4.3 Koło wyjściowe HTD 60T

Kandydacki link BOM-u prowadzi do aluminiowego `60-5M-15`. Strona katalogowa
podaje 60 zębów, podziałkę 5 mm, szerokość pasa 15 mm, średnicę podziałową
95,49 mm, średnicę zewnętrzną 94,35 mm, piastę Ø50 mm, długość 30 mm i otwór
bazowy Ø8 mm. CAD odwzorowuje te gabaryty. Otwór Ø12 mm w kandydackim CAD-zie
jest prowizoryczny do czasu wyboru wału i dokładnej serii łożysk wyjściowych.

- [ ] Potwierdzono dokładny wariant, materiał, gabaryt piasty i aktualny
  rysunek.
- [ ] Dostawca lub wykonawca potwierdził naddatek pozwalający wykonać otwór i
  retencję po zamrożeniu średnicy wału.
- [ ] Nie zamówiono obróbki do Ø12 mm wyłącznie na podstawie nominalnego CAD-u.
- [ ] Uzyskano osobną ofertę na wykończenie jednej sztuki po pomiarze koła,
  wału i piasty; oferta obejmuje kontrolę bicia.

### 4.4 Pas, sprzęgło i łożyska wejściowe

- [ ] Pas ma oznaczenie `450-5M-15`: 450 mm długości podziałowej, HTD 5M,
  15 mm szerokości i 90 zębów.
- [ ] Zapisano producenta pasa oraz zalecaną metodę ustawienia napięcia.
- [ ] Sprzęgło ma dokładny kod `BKL/3/8/8`, oba otwory 8 mm, znamionowe 3 Nm
  i dostępną instrukcję momentu śrub zaciskowych.
- [ ] Dwa łożyska wejściowe są z jednej serii 608, mają 8x22x7 mm, uszczelnienie
  i aktualną kartę producenta.
- [ ] Wybrano dokładną serię dwóch łożysk wyjściowych; dopóki jej nie ma,
  wykonanie wału wyjściowego i gniazd pozostaje zablokowane.

### 4.5 Zasilanie i warsztatowe odcięcie

- [ ] Instrukcja dokładnego zasilacza i `CL57Y-V20` określa dopuszczalne
  zasilanie, zabezpieczenie i zachowanie szyny podczas hamowania.
- [ ] Elementy odcięcia, zabezpieczenia, przewody i obudowa są wycenione dla
  rzeczywistych parametrów dostarczonego zestawu, nie dla założenia ogólnego.
- [ ] Zaplanowano bezpieczny punkt pomiaru napięcia szyny i temperatury bez
  odsłoniętych zacisków podczas ruchu.
- [ ] Nierozstrzygnięte zachowanie energii przy hamowaniu wstrzymuje test pełną
  prędkością; nie jest automatycznie kopiowane rozwiązanie przemysłowe 10 Ω.

## 5. Bramka złożenia zamówienia

Zamówienie kandydackich części P1 można złożyć dopiero, gdy:

- [ ] wszystkie pola dotyczące zamawianej pozycji w sekcji 4 są zakończone;
- [ ] zapisano pełny koszyk brutto z dostawą do Polski i datę sprawdzenia;
- [ ] przekroczenie limitu pozycji ma jawne źródło finansowania z rezerwy
  650 PLN, bez przekroczenia całego limitu 6 000 PLN;
- [ ] nie ma zamiennika wpływającego na obliczenia lub CAD bez ponownej oceny;
- [ ] mechaniczne zamówienie obejmuje tylko jedną przekładnię P1;
- [ ] użytkownik świadomie zatwierdził koszyk przed płatnością.

## 6. Odbiór i pomiary

Najpierw sprawdzić zgodność dostawy i widoczne uszkodzenia przed upływem terminu
zwrotu. Pomiary zapisać z użytym przyrządem i jego rozdzielczością. Wartości
poniżej pozostają puste, dopóki nie pochodzą z realnie dostarczonej części.

| Część | Producent / kod / seria | Co zmierzyć | Wynik i przyrząd |
|---|---|---|---|
| Silnik | | wał, długość wystawania, wpust/flat, pilot, rozstaw i gwinty mocujące, wyjście przewodów | |
| Koło 20T | | otwór w dwóch kierunkach, piasta, długość, szerokość zębów, kołnierze, bicie baz | |
| Koło 60T | | otwór w dwóch kierunkach, piasta, długość, szerokość zębów, bicie baz | |
| Pas | | oznaczenie, szerokość i stan zębów; długości podziałowej nie wyznaczać suwmiarką | |
| Sprzęgło | | oba otwory, długość, średnica zewnętrzna, śruby i dostęp narzędzia | |
| Dwa 608 | | dokładne oznaczenia, otwory, średnice zewnętrzne i szerokości | |
| Łożyska wyjściowe | | dokładne oznaczenia, otwory, średnice zewnętrzne, szerokości i wymagane promienie barków | |
| Wałek wejściowy | | średnica w kilku przekrojach, prostoliniowość, długość i bicie po wykonaniu | |
| Wał wyjściowy | | średnica czopów, barki, długość i bicie po wykonaniu | |

- [ ] Zważono koła, wały, sprzęgło, ukończone ramię i masę testową.
- [ ] Zapisano zdjęcia oznaczeń oraz dokumenty dokładnie dostarczonych wersji.
- [ ] Wyniki przekazano do aktualizacji modelu bezwładności i CAD-u.

## 7. Zwolnienie obróbki i stanowiska

- [ ] Wybrano metodę retencji obu kół i ramienia: zacisk, wpust, nakrętka,
  pierścień lub inne policzone rozwiązanie; nie pozostawiono tylko śruby
  dociskowej bez uzasadnienia.
- [ ] Obliczono pasowania wał--łożysko i łożysko--oprawa dla dokładnych serii,
  obciążenia i materiałów.
- [ ] Zamknięto barki, dystanse, pierścienie, rowki, gwinty oraz kolejność
  montażu i demontażu.
- [ ] Wykonawca otrzymał rysunek z bazami, tolerancjami, chropowatością i
  wymaganiem bicia, a nie sam plik STEP.
- [ ] Zaktualizowano ForgeCAD rzeczywistymi wymiarami i masami.
- [ ] `forgecad run` oraz kontrole minimum, nominalnego i maksimum kąta
  przechodzą bez nieoczekiwanych kolizji.
- [ ] Nowy STEP i raport są oznaczone jako wydane do wykonania; kandydackiego
  eksportu z 2026-07-22 nie przekazano jako finalnego rysunku.

## 8. Pozycje zablokowane do późniejszych bramek

Przed wynikiem fizycznego P1 nie kupować:

- mechaniki drugiej i trzeciej przekładni;
- pełnych ramion, prętów, przegubów i platformy P2;
- pełnej ramy oraz osłon P2;
- docelowego sterownika ruchu P2;
- efektora podciśnieniowego P3;
- enkodera i interfejsu taśmy P4.

Druk FDM można zlecić tylko dla przyrządu, osłony lub nisko obciążonego adaptera
potrzebnego do P1. Nie zastępuje on metalowych podpór wałów ani elementów
przenoszących moment.

## 9. Rejestr dowodów i decyzja

| Dowód | Plik, numer oferty lub data |
|---|---|
| Koszyk StepperOnline z dostawą i rewizjami | |
| Potwierdzenie instrukcji/krzywej `CL57Y-V20` | |
| Oferta i karta koła 20T | |
| Oferta i karta koła 60T | |
| Oferta pasa, sprzęgła i łożysk wejściowych | |
| Wybór dokładnych łożysk wyjściowych | |
| Wycena obróbki jednej osi | |
| Lista i zdjęcia dostarczonych części | |
| Arkusz pomiarów z przyrządami | |
| Zaktualizowany CAD i pakiet wydany do wykonania | |
| Raport fizycznego P1 | |

Decyzja po P1:

- [ ] zachować 20/60 i zwolnić mechanikę dwóch pozostałych osi;
- [ ] poprawić tę samą oś i powtórzyć P1;
- [ ] zmienić przełożenie lub napęd i wrócić do modelu;
- [ ] wstrzymać projekt sprzętowy.
