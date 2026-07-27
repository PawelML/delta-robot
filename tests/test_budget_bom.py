import json
from pathlib import Path

from delta_model.budget_bom import (
    LINES,
    REQUIRED_CATEGORIES,
    budget_bom_document,
)


def test_every_required_category_has_a_positive_cost() -> None:
    document = budget_bom_document()
    subtotals = document["category_subtotals_pln_gross"]
    assert isinstance(subtotals, dict)
    assert set(subtotals) == set(REQUIRED_CATEGORIES)
    assert all(value > 0.0 for value in subtotals.values())


def test_complete_cost_with_contingency_is_inside_hld_cap() -> None:
    document = budget_bom_document()
    assert document["within_budget_cap"] is True
    total = document["total_with_contingency_pln_gross"]
    assert isinstance(total, float)
    assert 5000.0 <= total <= 6000.0


def test_all_required_lines_are_positively_costed_and_traceable() -> None:
    assert LINES
    assert all(line.subtotal_pln_gross > 0.0 for line in LINES)
    assert all(
        line.source_url is not None
        for line in LINES
        if line.evidence_state == "dated_catalogue_price"
    )


def test_owned_camera_is_not_costed_and_external_printing_is_budgeted() -> None:
    item_ids = {line.item_id for line in LINES}
    assert "camera_lighting" not in item_ids
    assert "outsourced_3d_printing" in item_ids
    printing = next(line for line in LINES if line.item_id == "outsourced_3d_printing")
    assert printing.subtotal_pln_gross == 250.0


def test_budget_bom_is_finite_deterministic_and_matches_artifact() -> None:
    document = budget_bom_document()
    encoded = json.dumps(document, allow_nan=False, sort_keys=True)
    committed = json.loads(
        (Path(__file__).parents[1] / "artifacts/budget_bom.json").read_text()
    )
    assert json.loads(encoded) == committed
