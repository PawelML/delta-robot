"""Costed, provisional BOM for the complete budget demonstrator."""

import math
from dataclasses import asdict, dataclass
from typing import Literal

from delta_model.design_profiles import BUDGET_DEMONSTRATOR_PROFILE

BudgetCategory = Literal[
    "drives_and_power",
    "transmissions",
    "robot_mechanics",
    "frame",
    "control",
    "electrical",
    "vacuum",
    "vision",
    "conveyor_feedback",
    "integration",
    "logistics",
]
EvidenceState = Literal["dated_catalogue_price", "capped_allowance"]
Gate = Literal["P1_buy_once", "P1_one_axis_then_P2_balance", "P2", "P3", "P4"]


@dataclass(frozen=True, slots=True)
class BudgetBomLine:
    """One required, positively costed demonstrator line."""

    item_id: str
    category: BudgetCategory
    description: str
    quantity: float
    unit_price_pln_gross: float
    evidence_state: EvidenceState
    gate: Gate
    source_url: str | None
    acceptance_or_measurement: str

    def __post_init__(self) -> None:
        if not self.item_id or not self.description or not self.acceptance_or_measurement:
            raise ValueError("BOM text fields must not be empty")
        if not math.isfinite(self.quantity) or self.quantity <= 0.0:
            raise ValueError("BOM quantity must be finite and positive")
        if (
            not math.isfinite(self.unit_price_pln_gross)
            or self.unit_price_pln_gross <= 0.0
        ):
            raise ValueError("BOM unit price must be finite and positive")
        if self.evidence_state == "dated_catalogue_price" and self.source_url is None:
            raise ValueError("catalogue-priced lines require a source URL")

    @property
    def subtotal_pln_gross(self) -> float:
        return round(self.quantity * self.unit_price_pln_gross, 2)


LINES: tuple[BudgetBomLine, ...] = (
    BudgetBomLine(
        "drive_kit_3axis",
        "drives_and_power",
        "StepperOnline 3-CLYS30-V20: 3 motors, 3 drivers, 48 V / 500 W supply and cables",
        1,
        740.84,
        "dated_catalogue_price",
        "P1_buy_once",
        "https://www.stepperonline.pl/zestaw-cnc-z-silnikiem-krokowym-z-zamknieta-petla-ys-series-3-osie-v2-0-3-00nm-424-83oz-in-silnik-nema-23-z-przewodami-2-0m-i-zasilaczem-3-clys30-v20",
        "Confirm German-warehouse landed price, exact motor/driver/supply revisions "
        "and return terms before payment.",
    ),
    BudgetBomLine(
        "pulley_20t_finished",
        "transmissions",
        "HTD 20-5M-15 small pulley, finished 8 mm bore and secure retention",
        3,
        40.00,
        "capped_allowance",
        "P1_one_axis_then_P2_balance",
        "https://www.ebmia.pl/kola-do-pasow-htd-5m/832-kolo-zebate-htd-20-5m-15-do-pasa-szerokosci-15mm.html",
        "Buy/machine one first; verify bore, runout and retention on the delivered 8 mm jackshaft.",
    ),
    BudgetBomLine(
        "pulley_60t",
        "transmissions",
        "HTD 60-5M-15 aluminium large pulley",
        3,
        57.49,
        "dated_catalogue_price",
        "P1_one_axis_then_P2_balance",
        "https://www.ebmia.pl/kola-do-pasow-htd-5m/655-kolo-zebate-htd-60-5m-15-do-pasa-szerokosci-15mm.html",
        "Buy one first and measure hub, pilot bore, runout and tooth face.",
    ),
    BudgetBomLine(
        "pulley_60t_machining",
        "transmissions",
        "Finish bore, keyway/retention and runout check for each 60T pulley",
        3,
        50.00,
        "capped_allowance",
        "P1_one_axis_then_P2_balance",
        None,
        "Obtain local machining quote after measuring one delivered pulley and chosen shaft/hub.",
    ),
    BudgetBomLine(
        "belt_450_5m_15",
        "transmissions",
        "Optibelt 450-5M-15, 90-tooth belt; three installed plus one spare",
        4,
        49.45,
        "dated_catalogue_price",
        "P1_one_axis_then_P2_balance",
        "https://www.ebmia.pl/pasy-zebate-htd-5m/1350-pas-zebaty-450-5m-15-z90.html",
        "Check exact pitch/width marking; use one belt for P1 wear and tension evidence.",
    ),
    BudgetBomLine(
        "coupling_bkl3_8_8",
        "transmissions",
        "R+W BKL/3/8/8 zero-backlash bellows coupling",
        3,
        130.38,
        "dated_catalogue_price",
        "P1_one_axis_then_P2_balance",
        "https://www.ebmia.pl/sprzegla-mieszkowe-bkl/91682-sprzeglo-bezluzowe-bkl-3-8-8.html",
        "Verify both 8 mm clamp bores, 3 Nm rating and delivered clamp-screw instructions.",
    ),
    BudgetBomLine(
        "bearing_608_2rs",
        "transmissions",
        "SKF 608-2RS/2RSH-envelope sealed input bearings",
        6,
        6.62,
        "dated_catalogue_price",
        "P1_one_axis_then_P2_balance",
        "https://www.hurtowniatechpol.pl/product/Lozysko-608-2RS-SKF-IND-8x22x7-s20832",
        "Use one matched bearing series and close housing/shaft fits from its current SKF data.",
    ),
    BudgetBomLine(
        "input_support_fabrication",
        "transmissions",
        "Three C45 8 mm jackshafts, input carriers, bearing retainers and fasteners",
        3,
        60.00,
        "capped_allowance",
        "P1_one_axis_then_P2_balance",
        None,
        "Fabricate one after delivered-part measurement; weigh, check runout and "
        "inspect adjustment rigidity.",
    ),
    BudgetBomLine(
        "output_supports",
        "transmissions",
        "Three provisional 12 mm output shafts, two bearings/axis, hubs and retention",
        3,
        110.00,
        "capped_allowance",
        "P1_one_axis_then_P2_balance",
        None,
        "Freeze actual bearing series, fits, keyways and arm-hub retention only after "
        "P1 component measurement.",
    ),
    BudgetBomLine(
        "delta_links_platform",
        "robot_mechanics",
        "Upper arms, six 450 mm lower rods, twelve joints, spacers and moving platform",
        1,
        600.00,
        "capped_allowance",
        "P2",
        None,
        "Select parts within the accepted mass model; weigh every completed assembly "
        "and rerun dynamics if exceeded.",
    ),
    BudgetBomLine(
        "frame_and_guards",
        "frame",
        "Aluminium profiles/plates, brackets, fasteners and simple workshop guarding",
        1,
        650.00,
        "capped_allowance",
        "P2",
        None,
        "Freeze only after full three-axis collision/stiffness CAD; guarding is "
        "workshop containment, not a safety claim.",
    ),
    BudgetBomLine(
        "motion_control",
        "control",
        "Local MCU motion control, differential/isolated interfaces and homing I/O",
        1,
        200.00,
        "capped_allowance",
        "P2",
        None,
        "Choose after the exact CL57Y-V20 command/feedback interface is verified on "
        "P1; reuse existing PC for supervision.",
    ),
    BudgetBomLine(
        "electrical_panel",
        "electrical",
        "Enclosure, DC/AC-rated cutoff, emergency-stop loop, fusing, DIN hardware, PE and wiring",
        1,
        300.00,
        "capped_allowance",
        "P1_buy_once",
        None,
        "Confirm ratings against the delivered 48 V supply and driver manual; measure "
        "bus voltage during deceleration.",
    ),
    BudgetBomLine(
        "vacuum_system",
        "vacuum",
        "Budget vacuum source/ejector, valve, cup, tubing and vacuum confirmation",
        1,
        250.00,
        "capped_allowance",
        "P3",
        None,
        "Size from the real test part and demonstrate retention/release before conveyor operation.",
    ),
    BudgetBomLine(
        "camera_lighting",
        "vision",
        "USB/global-shutter candidate camera, lens, mount and controlled lighting",
        1,
        250.00,
        "capped_allowance",
        "P4",
        None,
        "Select from field of view, exposure and calibration tests; the allowance is "
        "not a frozen model.",
    ),
    BudgetBomLine(
        "conveyor_feedback",
        "conveyor_feedback",
        "Conveyor encoder/sensor, wheel/coupling and interface",
        1,
        150.00,
        "capped_allowance",
        "P4",
        None,
        "Derive resolution and update rate from the later tracking-error budget.",
    ),
    BudgetBomLine(
        "integration_consumables",
        "integration",
        "Connectors, extra cable, drag management, printed prototypes and workshop consumables",
        1,
        250.00,
        "capped_allowance",
        "P2",
        None,
        "Track actual spend; do not consume contingency invisibly.",
    ),
    BudgetBomLine(
        "poland_shipping",
        "logistics",
        "Combined delivery allowance to Poland",
        1,
        200.00,
        "capped_allowance",
        "P1_buy_once",
        None,
        "Recheck baskets and consolidate orders; VAT is already included in catalogue prices.",
    ),
)

CONTINGENCY_PLN_GROSS = 650.00
REQUIRED_CATEGORIES: tuple[BudgetCategory, ...] = (
    "drives_and_power",
    "transmissions",
    "robot_mechanics",
    "frame",
    "control",
    "electrical",
    "vacuum",
    "vision",
    "conveyor_feedback",
    "integration",
    "logistics",
)


def budget_bom_document() -> dict[str, object]:
    """Build a deterministic full-demonstrator cost envelope."""

    category_subtotals = {
        category: round(
            sum(line.subtotal_pln_gross for line in LINES if line.category == category),
            2,
        )
        for category in REQUIRED_CATEGORIES
    }
    base_total = round(sum(category_subtotals.values()), 2)
    total = round(base_total + CONTINGENCY_PLN_GROSS, 2)
    within_cap = (
        BUDGET_DEMONSTRATOR_PROFILE.total_budget_min_pln_gross
        <= total
        <= BUDGET_DEMONSTRATOR_PROFILE.total_budget_max_pln_gross
    )
    return {
        "schema": "delta-robot-budget-bom/v1",
        "status": "provisional_cost_envelope_not_purchase_authorization",
        "price_snapshot_date": "2026-07-22",
        "delivery_country": BUDGET_DEMONSTRATOR_PROFILE.delivery_country,
        "currency": "PLN_gross",
        "lines": [
            {**asdict(line), "subtotal_pln_gross": line.subtotal_pln_gross}
            for line in LINES
        ],
        "category_subtotals_pln_gross": category_subtotals,
        "base_total_pln_gross": base_total,
        "contingency_pln_gross": CONTINGENCY_PLN_GROSS,
        "total_with_contingency_pln_gross": total,
        "budget_bounds_pln_gross": {
            "minimum": BUDGET_DEMONSTRATOR_PROFILE.total_budget_min_pln_gross,
            "maximum": BUDGET_DEMONSTRATOR_PROFILE.total_budget_max_pln_gross,
        },
        "within_budget_cap": within_cap,
        "purchase_sequence": [
            "buy the three-axis kit once only after exact revision and landed-price confirmation",
            "buy/fabricate only one axis of transmission hardware for physical P1",
            "measure delivered parts and freeze fits, retention and masses",
            "run P1 before buying/fabricating the balance of the other two axes",
            "release P2/P3/P4 allowances only at their accepted gates",
        ],
        "reused_or_borrowed_not_costed": [
            "existing PC for supervision, development and logging",
            "existing workshop tools and 3D printer",
            "borrowed/rented calibrated tachometry, temperature and belt-force measurement for P1",
            "existing conveyor if available; this BOM covers feedback integration, "
            "not a new conveyor",
        ],
        "excluded": [
            "industrial Leadshine/Gates reference hardware",
            "ownership of TC-08, US Digital E6, Mark-10 gauge or Mesa 7I96S",
            "production safety certification, production guarding and CE conformity work",
            "labour, workshop rent and replacement of an existing conveyor/PC",
        ],
        "cost_risks": [
            "allowances for frame, joints and machining require quotations and may "
            "consume contingency",
            "catalogue stock and Polish/German-warehouse shipping can change after the snapshot",
            "a failed physical P1 may require a different ratio, driver supply or drive kit",
        ],
    }
