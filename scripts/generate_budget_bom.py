"""Generate the active budget-demonstrator BOM and cost envelope."""

import json
from pathlib import Path

from delta_model.budget_bom import budget_bom_document


def main() -> None:
    """Write the budget BOM artifact."""

    output = Path(__file__).resolve().parents[1] / "artifacts/budget_bom.json"
    output.write_text(
        json.dumps(budget_bom_document(), allow_nan=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
