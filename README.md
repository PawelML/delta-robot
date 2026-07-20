# Delta robot

Warsztatowy demonstrator robota delta do pick-and-place nad taśmą. Projekt jest
rozwijany od zweryfikowanego modelu cyfrowego, przez test pojedynczego napędu,
do fizycznego robota i trackingu ruchomej taśmy.

Aktualny etap: **cyfrowe P0 zakończone; P1 przygotowane do budowy jednej osi,
ale jeszcze bez fizycznego zaliczenia**.

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
- `docs/specs/p1-single-drive.md` — kandydat jednego napędu i test P1.
- `docs/specs/p1-transmission-selection.md` — dokładny dobór przekładni 18/90.
- `docs/specs/p1-single-axis-bench-lld.md` — stanowisko jednej osi w ForgeCAD.
- `docs/specs/p1-bench-software.md` — komendy, telemetria i automatyczny gate.
- `docs/specs/p1-test-instrumentation.md` — aparatura i niezależny tor pomiarowy.
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
uv run python scripts/select_p1_transmission.py
uv run python scripts/run_p1_bench_simulation.py
forgecad run cad/2026/07/20/p1-single-axis-bench/main.forge.js
```

Powstają raporty walidacyjne oraz `workspace.json`, `pose.json`,
`conveyor_coverage.json` i `trajectory_25_305_25.json`. Wizualizacja używa
wybranej w P0 geometrii DIY:
promień bazy 180 mm, promień platformy 65 mm, ramię górne 280 mm i dolne
450 mm. Geometria przechodzi próbkowany walec Ø400×150 mm, a cały prostokąt
305×200 mm taśmy ma 17,64 mm analitycznego zapasu promieniowego i przechodzi
10 416-punktową kontrolę na pełnej wysokości 150 mm. Wynik pozostaje cyfrowy do
czasu sprawdzenia dynamiki, kolizji i sprzętu.

Pierwszy raport P1 odrzuca wcześniejszy dobór steppera 2,0–2,2 Nm i sprawdza
jedno zintegrowane serwo 400 W z redukcją 5:1. Jest to kandydat wyłącznie do
testu stołowego; szczegóły i blokery zakupowe są zapisane w
`docs/specs/p1-single-drive.md` oraz `BOM_delta.md`.

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
