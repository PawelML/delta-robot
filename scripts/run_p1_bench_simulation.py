"""Run the deterministic no-hardware P1 command/log/evaluation path."""

import json
from pathlib import Path

from delta_model.p1_bench.artifacts import simulation_artifacts


def main() -> None:
    csv_content, report = simulation_artifacts()
    artifact_dir = Path(__file__).resolve().parents[1] / "artifacts"
    csv_path = artifact_dir / "p1_bench_simulation.csv"
    json_path = artifact_dir / "p1_bench_simulation.json"
    csv_path.write_text(csv_content, encoding="utf-8")
    json_path.write_text(
        json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()
