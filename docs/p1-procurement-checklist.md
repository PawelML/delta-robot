# P1 — checklista zakupowa i gotowość do budowy

**Status:** wstrzymana — referencja profilu `industrial_reference`

**Data:** 2026-07-20

**Zakres:** jedna reprezentatywna oś stanowiska P1

Nie używać tej checklisty do zakupów aktywnego `budget_demonstrator`. Wróci do
użycia tylko po świadomej decyzji o budowie profilu przemysłowego. Budżetowa
checklista powstanie po wyborze przekładni i zamknięciu pełnego BOM-u <=6 000 PLN.

## Zasady użycia

Ta checklista ustala kolejność i wymagane dowody. Nie jest drugim BOM-em.
Parametry i ilości pochodzą wyłącznie z `BOM_delta.md`, kontrakt napędu z
`docs/specs/p1-single-drive.md`, a blokery obróbki z
`docs/p1-bench-fabrication-package.md`.

- Nie zaznaczaj pola na podstawie ustnej obietnicy, jeśli wymagane jest
  potwierdzenie pisemne, rysunek lub pomiar.
- Każdy zamiennik zmieniający napięcie, moment, przełożenie, bezwładność,
  interfejs lub wymiary wymaga ponownej oceny przed zakupem.
- Nie kupuj trzech napędów. Ta lista dotyczy najwyżej jednego zestawu P1.
- Ceny, dostępność, wersję i warunki zwrotu sprawdza się ponownie w dniu zakupu.

## 0. Przygotowanie cyfrowe — zakończone

- [x] Geometria i obszar taśmy przeszły P0.
- [x] Model dynamiczny wskazał wymagany moment, RMS i prędkość.
- [x] Wybrano kandydackie serwo 400 W i Gates 5MGT 18/90.
- [x] Powstał kandydacki CAD, STEP, raport oraz symulator stanowiska.
- [ ] Fizyczne P1 zaliczone — pozostaje niezaznaczone do zakończenia testu.

## 1. Zapytania ofertowe — bez składania zamówienia

### Napęd i przekładnia

- [ ] Oferta na dokładny Leadshine `iSV2-RS6040V48G`: rewizja, hamulec,
  dokumentacja, gwarancja, termin, cena dostarczona i prawo zwrotu.
- [ ] Potwierdzone kody, gotowe otwory i dostępność Gates P18, P90, tulei 1610
  20 mm oraz pasa 600-5MGT-15.
- [ ] Wybrany jeden producent/typ łożysk R6-2RS i 6204-2RS wraz z aktualnymi
  rysunkami i zaleceniami pasowań.
- [ ] Oferta na sprzęgło 14.000/9.525 mm z wymiarami, momentem, dopuszczalną
  niewspółosiowością i sposobem zacisku; zweryfikowano prześwit CAD dla
  rzeczywistej średnicy sprzęgła.

### Zasilanie, regeneracja i odcięcie DC

- [ ] Dostawca napędu pisemnie potwierdził zgodność konkretnego zasilacza
  48 V / co najmniej 600 W z iSV2-RS6040V48G.
- [ ] Pisemnie potwierdzono sposób obsługi regeneracji i rezystor startowy
  10 Ω / co najmniej 100 W; wyjaśniono dopuszczalne napięcie zwrotne zasilacza.
- [ ] Wyceniono DC-rated rozłącznik/stycznik co najmniej 60 VDC / 30 A,
  normalnie zamknięty grzybek, zabezpieczenie gałęzi, przewody i obudowane
  zaciski rezystora.
- [ ] Wątpliwości dotyczące przerwania DC, zabezpieczeń i przekrojów zostały
  sprawdzone z osobą kompetentną w instalacjach elektrycznych.

### Sterowanie i aparatura

- [ ] Potwierdzono dostępność oryginalnej, identyfikowalnej Mesa 7I96S lub
  wstrzymano zakup; zamiennik nie jest wybierany bez osobnej oceny interfejsów.
- [ ] Wybrano stabilizowany zasilacz 5,0 V / co najmniej 1 A dla Mesa i E6,
  a budżet prądowy oraz spadek napięcia mieszczą się w zakresie 4,75–5,25 V.
- [ ] Uzyskano wspólną wycenę dokładnej konfiguracji US Digital E6, przewodu,
  pokrywy/bazy i narzędzia centrującego.
- [ ] Uzyskano wycenę Pico TC-08 PP222 z właściwymi sondami powierzchniowymi
  typu K dla serwa, łożyska i rezystora oraz kanałem otoczenia.
- [ ] Uzyskano wycenę Mark-10 M3-5 z certyfikatem kalibracji albo zamiennika
  spełniającego wymagania z `docs/specs/p1-test-instrumentation.md`.
- [ ] Potwierdzono Waveshare USB TO RS485 (C), okablowanie CN5 oraz właściwy
  przewód konfiguracyjny Leadshine.

## 2. Bramka złożenia zamówienia jednej osi

Wolno zamawiać dopiero, gdy wszystkie warunki są spełnione:

- [ ] Nie ma nierozstrzygniętego zamiennika wpływającego na obliczenia lub CAD.
- [ ] Zasilacz i regeneracja mają pisemne potwierdzenie kompatybilności.
- [ ] Dostępne są rysunki dokładnych zamawianych rewizji i konfiguracji.
- [ ] Znane są łączne koszty dostawy, podatków, gwarancji i zwrotu.
- [ ] Zamówienie obejmuje najwyżej jeden napęd i jedną przekładnię P1.
- [ ] Użytkownik świadomie zatwierdził koszt całego etapu P1 przed płatnością.

## 3. Odbiór i pomiar części katalogowych

- [ ] Zapisano producenta, pełny kod, rewizję i numer seryjny serwa/aparatury.
- [ ] Sprawdzono dostawę względem zamówienia i dokumentacji przed upływem
  terminu zwrotu.
- [ ] Zmierzono kołnierz i wał serwa, wyjścia przewodów oraz dostęp montażowy.
- [ ] Zmierzono łożyska, koła, tuleję, pas, sprzęgło i wały w miejscach
  istotnych dla pasowań oraz stosu osiowego.
- [ ] Zmierzono E6, wyjście kabla, narzędzie centrujące i otwory mocujące.
- [ ] Wyniki zapisano w pakiecie wykonawczym wraz z przyrządem i niepewnością
  wystarczającą do danego pasowania.

## 4. Zwolnienie elementów do obróbki

- [ ] Obliczono pasowania dokładnych R6 i 6204 dla wybranych materiałów.
- [ ] Zdefiniowano barki, dystanse/pierścienie, retencję osiową i dostęp
  montażowy wałów.
- [ ] Zamknięto standard, głębokość i długość rowków wpustowych oraz wpływ na
  wytrzymałość wału.
- [ ] Dodano śruby pierścieni ustalających, gwinty i minimalną długość
  wkręcenia.
- [ ] Zamknięto otwory serwa, sprzęgła oraz dokładnej konfiguracji E6.
- [ ] Zregenerowano ForgeCAD, STEP, raport i BOM bez nieudokumentowanej zmiany
  geometrii przekładni.
- [ ] Pakiet został sprawdzony jako „wykonać według rysunku”; wcześniejszy STEP
  pozostaje wyłącznie kandydatem do wyceny.

## 5. Montaż elektryczny i mechaniczny

- [ ] Podstawa i nośnik są płaskie, a osie wałów równoległe w wymaganej
  tolerancji; koła mają ustawione współpłaszczyznowe płaszczyzny środkowe.
- [ ] Pasek założono przy pozycji rozluźnionej i napięto metodą Gates z zapisaną
  długością wolnego odcinka, ugięciem i siłą.
- [ ] Rezystor ma osłonięte zaciski, wentylowane mocowanie i aktywny pomiar
  temperatury.
- [ ] Rozłącznik DC, grzybek, bezpiecznik i przewody zostały sprawdzone bez
  zasilania, a następnie przy ograniczonym prądzie.
- [ ] Przy wyłączonym zasilaniu ręcznie sprawdzono `-45°`, `0°`, `+80°` bez
  kolizji i zakleszczeń.

## 6. Fizyczny gate P1

- [ ] Potwierdzono Pulse+Direction, Modbus, E6 i wszystkie kanały temperatury.
- [ ] Wykonano stopniowanie 25%, 50% i 100% prędkości/przyspieszenia.
- [ ] Zakończono co najmniej 1 000 nawrotów bez alarmu i narastającego błędu.
- [ ] Zapisano temperatury, napięcie szyny, alarmy, błąd pozycji i zewnętrznie
  zmierzony ruch wyjścia.
- [ ] Automatyczny raport P1 ma źródło `hardware` i wszystkie wymagane metadane.
- [ ] Podjęto decyzję: zachować 400 W/5:1, zmienić przełożenie, przejść na
  750 W albo odrzucić rozwiązanie.
- [ ] Dopiero po pozytywnej decyzji zamrożono BOM v1 i dopuszczono zakup dwóch
  kolejnych napędów.

## Rejestr dowodów

| Dowód | Plik / numer oferty / data |
|---|---|
| Rozeznanie dostawców (nie oferta) | `docs/p1-supplier-research-poland-2026-07-20.md` |
| Oferta napędu i przekładni | |
| Potwierdzenie zasilania i regeneracji | |
| Oferta Mesa i interfejsów | |
| Oferta E6 + TC-08 + Mark-10 | |
| Pomiary części dostarczonych | |
| Wydany pakiet wykonawczy | |
| Raport fizycznego P1 | |
