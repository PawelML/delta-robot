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
