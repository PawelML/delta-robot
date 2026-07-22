"""Generate deterministic evidence for the two named hardware profiles."""

import json
from pathlib import Path

from delta_model.design_profiles import design_profiles_document


def main() -> None:
    """Write the profile registry without running an incomplete budget sizing."""

    output = Path(__file__).resolve().parents[1] / "artifacts/design_profiles.json"
    output.write_text(
        json.dumps(
            design_profiles_document(), allow_nan=False, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    print(output)


if __name__ == "__main__":
    main()
