# Delta robot

Warsztatowy demonstrator robota delta do pick-and-place nad taśmą. Projekt jest
rozwijany od zweryfikowanego modelu cyfrowego, przez test pojedynczego napędu,
do fizycznego robota i trackingu ruchomej taśmy.

Aktualny etap: **cyfrowe P0 oraz mechaniczne/kosztowe domknięcie budżetowego P1
zakończone; następny jest zakup i fizyczny test jednej osi**. Obwiednia całego
demonstratora wynosi 5 821,97 PLN brutto z rezerwą, nadal bez fizycznego
zaliczenia. Dotychczasowy
Leadshine/Gates pozostaje uruchamialnym profilem referencyjnym, a nie aktywnym
planem zakupowym.

## Dokumentacja

- `poc_plan.md` — HLD, zakres oraz bramki P0–P4.
- `docs/development-process.md` — proces spec-driven i zasady walidacji.
- `docs/specs/p0-kinematics.md` — kontrakt pierwszego modelu kinematycznego.
- `docs/specs/p0-workspace-export.md` — klasyfikacja workspace'u i kontrakt JSON.
- `docs/specs/p0-differential-kinematics.md` — Jacobian i metryki osobliwości.
- `docs/specs/p0-diy-geometry-selection.md` — porównanie geometrii DIY.
- `docs/specs/p0-conveyor-footprint.md` — pokrycie obszaru taśmy 305×200 mm.
- `docs/specs/p0-trajectory-25-305-25.md` — jednosekundowy profil ruchu.
- `docs/specs/p1-dynamics-and-drive-sizing.md` — pierwszy model momentów.
- `docs/specs/p1-design-profiles.md` — wspólny model oraz profile przemysłowy i budżetowy.
- `docs/specs/p1-budget-transmission-and-envelope.md` — porównanie budżetowych
  przełożeń i obwiednia udźwig/czas cyklu.
- `docs/specs/p1-budget-mechanical-and-cost-closure.md` — naciąg pasa, podparty
  wał, łożyska, sprzęgło, CAD i kontrakt kosztowy.
- `BOM_budget_delta.md` — aktywna, prowizoryczna lista budżetowa 5 821,97 PLN.
- `docs/specs/p1-single-drive.md` — kandydat jednego napędu i test P1.
- `docs/specs/p1-transmission-selection.md` — dokładny dobór przekładni 18/90.
- `docs/specs/p1-single-axis-bench-lld.md` — stanowisko jednej osi w ForgeCAD.
- `docs/specs/p1-bench-software.md` — komendy, telemetria i automatyczny gate.
- `docs/specs/p1-test-instrumentation.md` — aparatura i niezależny tor pomiarowy.
- `docs/p1-bench-fabrication-package.md` — wymiary, datums i blokery wydania
  rysunków stanowiska.
- `docs/p1-budget-bench-fabrication-package.md` — odpowiednik dla budżetowego
  stanowiska 20/60.
- `docs/p1-procurement-checklist.md` — kolejność ofert, zakupu jednej osi,
  pomiarów, obróbki i fizycznego gate'u P1.
- `docs/p1-supplier-research-poland-2026-07-20.md` — datowana migawka cen,
  dostępności, blokery oraz gotowe zapytania ofertowe dla dostawy do Polski.
- `AGENTS.md` — instrukcje obowiązujące narzędzia kodujące.

## Środowisko developerskie

Wymagane są Python 3.12 i `uv`.

```bash
uv sync --dev
uv run ruff check .
uv run mypy delta_model tests
uv run pytest
```

Model zawiera zweryfikowane IK, FK, kinematykę różniczkową, próbkowanie
workspace'u oraz profil 25-305-25. Artefakty można odtworzyć poleceniami:

```bash
uv run python scripts/validate_differential_kinematics.py
uv run python scripts/compare_diy_geometries.py
uv run python scripts/generate_conveyor_coverage.py
uv run python scripts/generate_p0_artifacts.py
uv run python scripts/generate_dynamic_sizing.py
uv run python scripts/generate_design_profiles.py
uv run python scripts/generate_budget_performance_envelope.py
uv run python scripts/generate_budget_mechanical_closure.py
uv run python scripts/generate_budget_bom.py
uv run python scripts/select_p1_transmission.py
uv run python scripts/run_p1_bench_simulation.py
forgecad run cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js
```

Powstają raporty walidacyjne oraz `workspace.json`, `pose.json`,
`conveyor_coverage.json` i `trajectory_25_305_25.json`. Wizualizacja używa
wybranej w P0 geometrii DIY:
promień bazy 180 mm, promień platformy 65 mm, ramię górne 280 mm i dolne
450 mm. Geometria przechodzi próbkowany walec Ø400×150 mm, a cały prostokąt
305×200 mm taśmy ma 17,64 mm analitycznego zapasu promieniowego i przechodzi
10 416-punktową kontrolę na pełnej wysokości 150 mm. Wynik pozostaje cyfrowy do
czasu sprawdzenia dynamiki, kolizji i sprzętu.

`artifacts/design_profiles.json` rozdziela dwa warianty bez kopiowania modelu.
`industrial_reference` zachowuje obliczenia Leadshine/Gates dla 0,50 kg / 1 Hz.
Aktywny `budget_demonstrator` rejestruje zestaw StepperOnline `3-CLYS30-V20`.
`artifacts/budget_performance_envelope.json` porównuje HTD 5M 3:1, 4:1 i 5:1
i wybiera do fizycznego P1 katalogowy wariant 20/60, 15 mm, 450 mm. Model nie
odrzuca go dla 0,50 kg / 1,50 s ani 0,30 kg / 1,25 s, ale odrzuca 0,50 kg /
1,00 s. `artifacts/budget_mechanical_closure.json` odrzuca koło bezpośrednio na
silniku i sprawdza osobno podparty wał Ø8 mm, dwa 608 oraz sprzęgło BKL3.
Krzywa momentu dotyczy dokładnego silnika, lecz innego drivera i 36 V, więc ma
status `proxy_only`: wynik nie jest dowodem przejścia P1 ani zgodą na zakup.

## Budżetowe stanowisko CAD P1

Model aktywnej osi 20/60 znajduje się w
`cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js`. Ma regulację pasa
-15…+3 mm, ruch wyjścia -45…+80° i osobno podparty wał wejściowy. Gotowe pliki:

- `artifacts/cad/p1-budget-single-axis-bench-hero.png`;
- `artifacts/cad/p1-budget-single-axis-bench-report.pdf`;
- `artifacts/cad/p1-budget-single-axis-bench.step`.

Dokładny sweep zgłasza 0 kolizji w sześciu pozach, a testy integralności
przechodzą dla -45°, 0° i +80°. Pasowania, rowki/retencja i otwory konkretnej
serii pozostają do zamknięcia po pomiarze dostarczonych części.

## Referencyjne stanowisko przemysłowe CAD P1

Ten model dotyczy profilu przemysłowego Leadshine/Gates. Nie jest modelem
wykonawczym aktywnej osi budżetowej. Ma parametry kąta `-45…+80°` i regulacji
pasa `-21…+4 mm`.
Najprościej obejrzeć gotowe wyjścia w
`artifacts/cad/p1-single-axis-bench-report.pdf` oraz
`artifacts/cad/p1-single-axis-bench.step`. Źródło można też renderować lokalnie:

```bash
forgecad render 3d cad/2026/07/20/p1-single-axis-bench/main.forge.js \
  --view hero --output /tmp/p1-bench.png
```

Pakiet przechodzi kontrolę złożeń i kolizji w pozycjach -45°, 0° i +80°.
Pozostaje kandydatem wykonawczym: pasowania łożysk, śruby pierścieni
ustalających, otwory kołnierza serwa, szczegóły rowków wpustowych i mocowanie
konkretnej wersji E6 trzeba zamknąć na podstawie dostarczonych części przed
zleceniem obróbki „dokładnie według modelu”.

## Wizualizator Three.js

```bash
cd visualizer
npm install
npm test
npm run dev
```

Vite wyświetli lokalny adres, domyślnie `http://127.0.0.1:5173`. Wizualizator:

- pokazuje trzy ramiona górne, sześć dolnych prętów i platformę,
- rozdziela punkty użyteczne, słabe przy osobliwościach, limitowane i
  nieosiągalne,
- animuje autorytatywny cykl 25-305-25 oraz pokazuje kąty, prędkości i
  przyspieszenia osi,
- pozwala obracać, przesuwać i przybliżać scenę,
- sprawdza wersje schematów, jednostki, liczności i zgodność trzech artefaktów,
- nie implementuje ponownie kinematyki ani metryk w JavaScript.

Build produkcyjny wraz z aktualnymi plikami JSON powstaje przez:

```bash
cd visualizer
npm run build
```
