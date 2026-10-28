from pathlib import Path

from auditor import audit_chair, leading_classification

EXAMPLE = Path(__file__).parent.parent / "examples" / "chair.txt"


def consensus(rows):
    table = "\n".join(f"| {p} | {s} | {c} |" for p, s, c in rows)
    return f"REAL CONSENSUS\n| Proposition | Supporters | Classification |\n|---|---|---|\n{table}\nIMPORTANT DISAGREEMENTS\n"


def test_leading_label_wins_over_explanation():
    assert leading_classification("**MAJORITY** (3/5) - Not unanimous") == "MAJORITY"
    assert leading_classification("MINORITY CONVERGENCE (2/5)") == "MINORITY CONVERGENCE"
    assert leading_classification("no label") == ""


def test_majority_with_three_named_members_passes():
    errors, _ = audit_chair(consensus([("Off-grid", "Engineer, Survivalist, Philosopher", "**MAJORITY** (3/5). Not unanimous.")]))
    assert errors == []


def test_unanimous_with_three_members_fails():
    errors, _ = audit_chair(consensus([("Off-grid", "Engineer, Survivalist, Philosopher", "UNANIMOUS")]))
    assert len(errors) == 1 and "UNANIMOUS violation" in errors[0]


def test_inferred_support_is_rejected():
    errors, _ = audit_chair(consensus([("Gym", "Engineer, Survivalist (implied)", "MINORITY CONVERGENCE")]))
    assert any("inferred-support" in e for e in errors)


def test_truth_judgment_in_verification_section_fails():
    text = "CLAIMS NEEDING VERIFICATION\nFusion at home is impossible.\nSYNTHESIZED COMPOUND\n"
    errors, _ = audit_chair(text)
    assert any("truth judgment" in e for e in errors)


def test_saved_example_passes_hard_rules():
    errors, warnings = audit_chair(EXAMPLE.read_text(encoding="utf-8"))
    assert errors == []
    assert warnings  # the Chair's "all members agree is not established" note is flagged for a human
