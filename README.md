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

Model zawiera zweryfikowane IK i FK oraz próbkowanie workspace'u. Referencyjne
dane dla przyszłego wizualizatora Three.js można odtworzyć poleceniem:

```bash
uv run python scripts/generate_p0_artifacts.py
```

Powstają `artifacts/workspace.json` i `artifacts/pose.json`. Korzystają z
wymiarów Williamsa i demonstracyjnych limitów osi `+/-45°`, żeby pokazać trzy
klasy punktów. Nie są geometrią ani limitami projektowanego robota DIY.
