"""Deterministic checks on the Council Chair's verdict."""


MEMBER_NAMES = ["Engineer", "Eccentric Futurist", "Survivalist", "Philosopher", "Ruthless Minimalist"]

CLASSIFICATIONS = ("MINORITY CONVERGENCE", "UNANIMOUS", "MAJORITY")


def leading_classification(cell):
    """
    Return the label the Chair actually assigned: the first classification
    word in the cell. Later explanation such as "Not unanimous" is ignored.
    """
    text = cell.upper().replace("*", "")
    found = [(text.find(label), label) for label in CLASSIFICATIONS if label in text]
    return min(found)[1] if found else ""


def get_section(text, start_heading, end_heading=None):
    """
    Extract a section of the Chair report between two headings.
    """
    start = text.upper().find(start_heading.upper())

    if start == -1:
        return ""

    if end_heading is None:
        return text[start:]

    end = text.upper().find(end_heading.upper(), start + len(start_heading))

    if end == -1:
        return text[start:]

    return text[start:end]


def named_members(text):
    """
    Return Council member names explicitly present in a piece of text.
    """
    return [name for name in MEMBER_NAMES if name.lower() in text.lower()]


def audit_chair(chair_text):
    errors = []
    warnings = []

    consensus = get_section(
        chair_text,
        "REAL CONSENSUS",
        "IMPORTANT DISAGREEMENTS"
    )

    # --------------------------------------------------------
    # Rule 1 — implied support is forbidden in consensus
    # --------------------------------------------------------

    banned_consensus_words = [
        "implied",
        "implicitly",
        "consistent with",
        "compatible with",
        "thematic overlap"
    ]

    for phrase in banned_consensus_words:
        if phrase.lower() in consensus.lower():
            errors.append(
                f'Consensus section uses forbidden inferred-support language: "{phrase}"'
            )

    # --------------------------------------------------------
    # Rule 2 — audit consensus table rows
    # --------------------------------------------------------

    for line in consensus.splitlines():

        stripped = line.strip()

        if not stripped.startswith("|"):
            continue

        if "proposition" in stripped.lower():
            continue

        if set(stripped.replace("|", "").strip()) <= {"-", ":"}:
            continue

        cells = [
            cell.strip()
            for cell in stripped.strip("|").split("|")
        ]

        if len(cells) < 3:
            continue

        proposition = cells[0]
        supporters_text = cells[1]
        classification = leading_classification(cells[2])

        supporters = named_members(supporters_text)
        count = len(supporters)

        if classification == "UNANIMOUS" and count != 5:
            errors.append(
                f'UNANIMOUS violation: "{proposition}" '
                f'has {count} explicitly named supporter(s): {supporters}'
            )

        elif classification == "MAJORITY" and count not in (3, 4):
            errors.append(
                f'MAJORITY violation: "{proposition}" '
                f'has {count} explicitly named supporter(s): {supporters}'
            )

        elif classification == "MINORITY CONVERGENCE" and count != 2:
            errors.append(
                f'MINORITY CONVERGENCE violation: "{proposition}" '
                f'has {count} explicitly named supporter(s): {supporters}'
            )

    # --------------------------------------------------------
    # Rule 3 — high-risk consensus language anywhere
    # --------------------------------------------------------

    risky_phrases = [
        "all members agree",
        "all members support",
        "everyone agrees",
        "everyone supports",
        "no member endorses",
        "no member agrees"
    ]

    for phrase in risky_phrases:
        if phrase.lower() in chair_text.lower():
            warnings.append(
                f'Check absolute claim manually: "{phrase}"'
            )

    # --------------------------------------------------------
    # Rule 4 — verification section must not decide truth
    # --------------------------------------------------------

    verification = get_section(
        chair_text,
        "CLAIMS NEEDING VERIFICATION",
        "SYNTHESIZED COMPOUND"
    )

    forbidden_verification_phrases = [
        "scientifically invalid",
        "scientifically valid",
        "impossible",
        "proven",
        "disproven",
        "no empirical evidence exists",
        "no peer-reviewed evidence exists"
    ]

    for phrase in forbidden_verification_phrases:
        if phrase.lower() in verification.lower():
            errors.append(
                f'Verification section makes an external truth judgment: "{phrase}"'
            )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    print("\n\n" + "=" * 70)
    print("COUNCIL AUDITOR — V0.4")
    print("=" * 70)

    if errors:
        print("\nAUDIT RESULT: FAIL")
        print("\nHard violations:")

        for number, error in enumerate(errors, 1):
            print(f"{number}. {error}")
    else:
        print("\nAUDIT RESULT: PASS")
        print("\nNo deterministic rule violations detected.")

    if warnings:
        print("\nWarnings requiring human review:")

        for number, warning in enumerate(warnings, 1):
            print(f"{number}. {warning}")

    print("\nAudit scope:")
    print("- Checks consensus arithmetic and classification")
    print("- Rejects inferred support inside REAL CONSENSUS")
    print("- Checks verification section for prohibited truth judgments")
    print("- Flags risky absolute claims for human review")
    print("- Does NOT determine whether the underlying arguments are factually true")

    return errors, warnings
