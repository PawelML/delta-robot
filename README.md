# Delta robot

Warsztatowy demonstrator robota delta do pick-and-place nad taśmą. Projekt jest
rozwijany od zweryfikowanego modelu cyfrowego, przez test pojedynczego napędu,
do fizycznego robota i trackingu ruchomej taśmy.

Aktualny etap: **P0 — model kinematyczny w Pythonie i wizualizator Three.js**.

## Dokumentacja

- `poc_plan.md` — HLD, zakres oraz bramki P0–P4.
- `docs/development-process.md` — proces spec-driven i zasady walidacji.
- `docs/specs/p0-kinematics.md` — kontrakt pierwszego modelu kinematycznego.
- `docs/specs/p0-workspace-export.md` — klasyfikacja workspace'u i kontrakt JSON.
- `AGENTS.md` — instrukcje obowiązujące narzędzia kodujące.

## Środowisko developerskie

Wymagane są Python 3.12 i `uv`.

```bash
uv sync --dev
uv run ruff check .
uv run mypy delta_model tests
uv run pytest
```

Model zawiera zweryfikowane IK i FK, próbkowanie workspace'u oraz działający
wizualizator Three.js. Referencyjne dane można odtworzyć poleceniem:

```bash
uv run python scripts/generate_p0_artifacts.py
```

Powstają `artifacts/workspace.json` i `artifacts/pose.json`. Korzystają z
wymiarów Williamsa i demonstracyjnych limitów osi `+/-45°`, żeby pokazać trzy
klasy punktów. Nie są geometrią ani limitami projektowanego robota DIY.

## Wizualizator Three.js

```bash
cd visualizer
npm install
npm test
npm run dev
```

Vite wyświetli lokalny adres, domyślnie `http://127.0.0.1:5173`. Wizualizator:

- pokazuje trzy ramiona górne, sześć dolnych prętów i platformę,
- koloruje punkty osiągalne, limitowane i nieosiągalne,
- pozwala obracać, przesuwać i przybliżać scenę,
- sprawdza wersje schematów, jednostki, liczności i zgodność obu artefaktów,
- nie implementuje ponownie IK ani FK w JavaScript.

Build produkcyjny wraz z aktualnymi plikami JSON powstaje przez:

```bash
cd visualizer
npm run build
```
