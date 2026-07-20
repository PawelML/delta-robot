# BOM — Robot delta DIY (pick-and-place nad taśmą)

**Założenia projektowe:** przestrzeń robocza Ø350–400 mm × 150 mm wysokości, udźwig do 0,5 kg, cel 1,5–2,5 picków/s, efektor podciśnieniowy, integracja z istniejącą taśmą z enkoderem i kamerą Gemini 336.

---

## 1. Napędy (serce budżetu)

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Silnik krokowy closed-loop NEMA 23 + sterownik | 2,0–2,2 Nm, enkoder 1000 linii, komplet silnik+driver (np. zestawy typu 23E2/HSS57) | 3 | AliExpress (~180–220 zł/kpl) lub ebmia.pl / akcesoria-cnc.pl (~330–380 zł/kpl, szybciej + gwarancja PL) | 550–1100 zł |
| Redukcja pasowa 5:1 | Koło GT2 20T (alu) + koło 100T (druk 3D lub alu z Allegro), pasek GT2 zamknięty 6–9 mm | 3 kpl | Botland / Allegro / AliExpress | 100–180 zł |

**Uwagi:**
- Closed-loop jest nienegocjowalny — otwarty stepper przy dynamice delty zgubi kroki i nie będziesz wiedział kiedy. Enkoder w silniku = wykrywanie zgubienia pozycji.
- Redukcja pasowa zamiast planetarnej: zero luzu praktycznego przy napiętym pasku, koszt 5× niższy niż przekładnie planetarne (te mają zresztą 15–30 arcmin luzu w tanich wersjach — gorzej niż pasek).
- Zasilanie sterowników 36–48 V dla momentu przy prędkości.

## 2. Kinematyka (ramiona i przeguby)

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Rurka węglowa | Ø12×10 mm, dł. 400–450 mm (przedramiona) | 6 | Allegro (modelarstwo) / sklepy RC | 100–150 zł |
| Przeguby kulowe igus KBRM-10 / KGLM-10 | polimerowe, bezobsługowe, M10 lub gwint wewn. | 12 | igus.pl (próbki/sklep) / TME / Allegro | 150–250 zł |
| Ramiona górne (bicepsy) | druk 3D PETG/PC + wkładki alu LUB frezowane alu na zamówienie (Allegro) | 3 | druk własny / Allegro | 30–250 zł |
| Pręty gwintowane/łączniki, sprężyny ściągające przeguby | M10, stal | kpl | lokalnie / Castorama | 50 zł |

**Uwagi:**
- Przeguby magnetyczne z drukarek delta odpadają — przy ruchach bocznych z ładunkiem 0,3–0,5 kg i przyspieszeniach >3 g wypinają się. igus KBRM to standard w tanich deltach przemysłowych.
- Rozstaw przegubów w parze (równoległobok) trzymaj sztywno — dystanse alu, nie druk.

## 3. Rama i platforma

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Profil aluminiowy 3030 | konstrukcja nośna nad taśmą, ~3 mb + narożniki, śruby teowe | kpl | ebmia.pl / Motedis / Allegro | 250–350 zł |
| Płyta górna (mocowanie silników) | sklejka 15 mm frezowana lub alu 8 mm cięte wodą (Allegro: „cięcie aluminium na wymiar") | 1 | lokalny zakład / Allegro | 80–250 zł |
| Platforma robocza (traveling plate) | druk PETG-CF lub alu | 1 | druk własny | 20 zł |

## 4. Sterowanie

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Płyta sterująca | BTT SKR 3 / Octopus (wyjścia step/dir na zewnętrzne drivery) | 1 | Botland / AliExpress | 150–280 zł |
| Raspberry Pi 4 (4 GB) | host Klipper + API do twojego softu wizyjnego | 1 | Botland / używka | 180–280 zł |
| Czujniki bazowania | indukcyjne NPN M8 lub krańcówki optyczne | 3 | Botland / TME | 40–80 zł |
| E-stop grzybkowy + stycznik/przekaźnik na zasilanie silników | NC, rozłączanie mocy, nie tylko sygnału | 1 kpl | TME | 60–100 zł |

**Uwagi:**
- Klipper ma natywną kinematykę `rotary_delta` — dostajesz planowanie trajektorii, input shaping (tłumienie drgań = krótszy settling time!) i API (Moonraker) do sterowania z Pythona za darmo.
- Enkoder taśmy podłączasz do RPi/mikrokontrolera obok — tracking realizujesz w swojej warstwie (predykcja pozycji detalu w chwili picku), Klipper dostaje gotowe współrzędne. Na 1,5–2 picki/s to wystarczy; streaming trajektorii w czasie rzeczywistym to etap 2.

## 5. Efektor podciśnieniowy

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Pompa próżniowa membranowa 12/24 V | min. -60 kPa, praca ciągła | 1 | Botland / AliExpress | 60–120 zł |
| Elektrozawór 2/2 + zawór zwalniający | szybkie puszczanie detalu (wdmuch lub odpowietrzenie) | 1–2 | AliExpress / TME | 50–90 zł |
| Przyssawki silikonowe + przewód PU 4/6 mm | 2–3 rozmiary pod detale testowe | kpl | AliExpress | 30–50 zł |
| Wakuostat / czujnik podciśnienia analogowy | potwierdzenie chwytu (ważne do liczenia success rate!) | 1 | AliExpress / TME | 30–60 zł |

## 6. Zasilanie i okablowanie

| Pozycja | Specyfikacja | Ilość | Źródło | Cena szac. |
|---|---|---|---|---|
| Zasilacz Mean Well LRS-350-36 (lub 48 V zależnie od driverów) | 350 W | 1 | TME / Botland | 160–220 zł |
| Zasilacz pomocniczy 12/24 V | pompa, zawory, czujniki | 1 | TME | 50–80 zł |
| Przewody, złącza GX16, koryta, drobnica | — | kpl | TME / lokalnie | 100–150 zł |

---

## Podsumowanie kosztów

| Wariant | Koszt |
|---|---|
| **Budżetowy** (Ali, druk własny, sklejka) | **~2 200–2 800 zł** |
| **Solidny** (napędy z PL z gwarancją, alu cięte, igus) | **~3 500–4 400 zł** |
| Rezerwa na wpadki (spalony driver, nieudane wydruki, druga iteracja ramion) | +20–25% |

Obie ścieżki mieszczą się w 5 tys. zł. Czego tu **nie ma**: 4. oś (obrót detalu) — dokładaj dopiero, gdy demo tego wymaga (+150–250 zł, wał przez środek lub silnik na platformie); osłony/wygrodzenie do pokazów u klienta.

## Kolejność budowy (minimalizacja ryzyka)

1. **Jeden napęd na stole**: silnik + redukcja + driver + Klipper — zmierz powtarzalność kątową zanim zbudujesz resztę.
2. Rama + trzy napędy + ramiona → bazowanie, kinematyka, pierwsze ruchy XYZ na wolnych prędkościach.
3. Pomiar powtarzalności kamerą (fiducjał na platformie) → masz pierwszą liczbę do raportu zanim jeszcze jest efektor.
4. Efektor + podciśnienie → picki statyczne z tacki.
5. Integracja z enkoderem taśmy → tracking, krzywa prędkość taśmy vs. success rate.
