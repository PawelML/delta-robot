"""Generate the deterministic simplified P1 dynamic sizing report."""

import json
from pathlib import Path

from delta_model.dynamic_sizing import dynamic_sizing_document


def main() -> None:
    """Write the dynamic report and fail if time-step convergence is inadequate."""

    document = dynamic_sizing_document()
    output = Path(__file__).resolve().parents[1] / "artifacts/dynamic_sizing.json"
    output.write_text(
        json.dumps(document, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(output)
    if document["status"] != "provisional_pass":
        raise SystemExit("dynamic sizing did not pass its sampling-convergence gate")


if __name__ == "__main__":
    main()
