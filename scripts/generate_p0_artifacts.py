"""Generate deterministic P0 JSON inputs for the Three.js visualizer."""

from pathlib import Path

from delta_model.reference_artifacts import generate_reference_artifacts


def main() -> None:
    """Write reference workspace and pose artifacts below the repository root."""

    output_directory = Path(__file__).resolve().parents[1] / "artifacts"
    generated_paths = generate_reference_artifacts(output_directory)
    for path in generated_paths:
        print(path)


if __name__ == "__main__":
    main()
