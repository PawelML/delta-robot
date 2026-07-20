import json
from pathlib import Path
from typing import cast

import pytest

from delta_model.dynamic_sizing import dynamic_sizing_document


def test_dynamic_sizing_report_matches_committed_artifact() -> None:
    document = dynamic_sizing_document()
    artifact_path = Path(__file__).resolve().parents[1] / "artifacts/dynamic_sizing.json"
    committed = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert json.loads(json.dumps(document)) == committed
    assert document["schema"] == "delta-robot-p1-dynamic-sizing/v1"
    assert document["status"] == "provisional_pass"
    convergence = cast(dict[str, object], document["convergence"])
    assert convergence["passes_one_percent"] is True
    assessment = cast(dict[str, object], document["candidate_assessment"])
    assert assessment["passes"] is True
    axes = cast(list[dict[str, float]], assessment["axes"])
    assert max(axis["required_peak_torque_nm"] for axis in axes) == pytest.approx(
        2.401083715716091
    )
