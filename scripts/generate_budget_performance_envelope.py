"""Generate the deterministic budget-drive performance envelope."""

import json
from pathlib import Path

from delta_model.budget_sizing import budget_performance_envelope_document


def main() -> None:
    """Write proxy-only budget performance evidence."""

    document = budget_performance_envelope_document()
    output = Path(__file__).resolve().parents[1] / "artifacts/budget_performance_envelope.json"
    output.write_text(
        json.dumps(document, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
