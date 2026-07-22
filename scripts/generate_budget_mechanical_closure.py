"""Generate deterministic mechanical closure evidence for the budget drive."""

import json
from pathlib import Path

from delta_model.budget_mechanics import budget_mechanical_closure_document


def main() -> None:
    """Write the mechanical-closure artifact."""

    output = Path(__file__).resolve().parents[1] / "artifacts/budget_mechanical_closure.json"
    output.write_text(
        json.dumps(
            budget_mechanical_closure_document(),
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
