import json
import urllib.request
import urllib.error
import re

from auditor import audit_chair

MODEL = "qwen3:4b-instruct"

QUESTION = """
If Jeff could build his ideal personal compound with a generous budget
and few practical constraints, what should it contain and why?

Possible areas include energy, workshop/lab, computing, communications,
food/water resilience, gym, entertainment, vehicles, automation,
observatory/weather systems, guest facilities, security, gardens,
and anything else you think belongs there.
"""

EXPERTS = {
    "Engineer": """
You are the Engineer.

You care about feasibility, physical systems, interfaces, reliability,
maintenance, performance, and failure modes.

You dislike magical thinking and vague technology claims.
You ask: How would this actually work? What breaks? What depends on what?

Do not imitate the other experts.
""",

    "Eccentric Futurist": """
You are the Eccentric Futurist.

You care about ambitious possibilities, emerging technology,
experimentation, unusual combinations, and things that would make
the compound feel twenty years ahead of its time.

You are allowed to propose wild ideas, but explain why they might
actually be interesting rather than merely flashy.

You dislike timid incrementalism.
""",

    "Survivalist": """
You are the Survivalist.

You care about resilience, independence, redundancy, repairability,
stored resources, communications, energy, water, food, and graceful
degradation when external systems fail.

Assume electricity, internet, supply chains, public utilities, or
institutions may occasionally become unavailable.

You dislike hidden dependencies.
""",

    "Philosopher": """
You are the Philosopher.

You care about how Jeff would actually live there, what the compound
encourages him to become, human relationships, meaning, beauty,
solitude, community, and second-order effects.

Question assumptions that everyone else treats as obvious.

You dislike optimizing measurable systems while accidentally creating
a terrible life.
""",

    "Ruthless Minimalist": """
You are the Ruthless Minimalist.

You believe complexity has a carrying cost.

Your job is to identify what Jeff would genuinely use and eliminate
expensive, fragile, redundant, theatrical, or maintenance-heavy ideas.

You strongly prefer elegant systems that accomplish several purposes
at once.

You are explicitly permitted to tell the other imaginary experts
that their ideas are ridiculous.
"""
}


def ask_ollama(system_prompt, user_prompt):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "options": {
    	    "temperature": 0.8,
    	    "num_ctx": 16384
        }
    }

    request = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
       with urllib.request.urlopen(request) as response:
         result = json.loads(response.read().decode("utf-8"))

       return result["message"]["content"]

    except urllib.error.HTTPError as e:
      print("\nOLLAMA ERROR:")
      print(e.read().decode("utf-8"))
      raise



def main():
    print("\n" + "=" * 70)
    print("COUNCIL OF EXPERTS — ROUND 1")
    print("=" * 70)

    round1 = {}

    for name, persona in EXPERTS.items():

        prompt = f"""
    Here is tonight's playground question:

    {QUESTION}

    Give your INITIAL POSITION before hearing from the other Council members.

    Use this structure:

    POSITION:
    One clear statement of your overall design philosophy.

    MUST-HAVES:
    Choose 4-7 things the compound absolutely should contain.
    Explain each briefly.

    ONE INDULGENCE:
    Something unnecessary but glorious that you personally insist upon.

    WARNING:
    One mistake Jeff should avoid.

    Keep the whole response under roughly 450 words.
    Stay strongly in character.
    """

        print(f"\n\n{'-' * 70}")
        print(f"{name.upper()}")
        print("-" * 70)

        answer = ask_ollama(persona, prompt)
        round1[name] = answer

        print(answer)


    print("\n\n" + "=" * 70)
    print("ROUND 1 COMPLETE")
    print("=" * 70)

    # ============================================================
    # ROUND 2 — EVIDENCE-LOCKED CROSS-EXAMINATION
    # ============================================================

    transcript = "\n\n".join(
        f"### {name}\n{answer}"
        for name, answer in round1.items()
    )

    print("\n\n" + "=" * 70)
    print("COUNCIL OF EXPERTS — ROUND 2: EVIDENCE-LOCKED CHALLENGE")
    print("=" * 70)

    round2 = {}

    for name, persona in EXPERTS.items():

        prompt = f"""
    The Council has now heard everyone's initial position.

    ORIGINAL QUESTION:
    {QUESTION}

    ROUND 1 TRANSCRIPT:
    {transcript}

    You are {name}.

    GROUNDING RULE:
    You may discuss ONLY ideas that actually appear in the ROUND 1 TRANSCRIPT.

    When criticizing or praising another member:

    1. Name that member.
    2. Copy ONE CONTIGUOUS exact quotation of 5-25 words from that
       member's Round 1 response.
    3. Do not use ellipses (...) inside the quotation.
    4. Do not paraphrase inside quotation marks.
    5. If you cannot find a supporting quotation, do not make the claim.

    Do NOT simply repeat your original answer.

    Use exactly this structure:

    STRONGEST OBJECTION:

    MEMBER:
    Name one other Council member.

    EXACT CLAIM:
    Copy one contiguous 5-25 word quotation from that member.

    OBJECTION:
    Explain why that exact claim is wrong, incomplete, unrealistic,
    or rests on a questionable assumption.


    BEST IDEA I DIDN'T HAVE:

    MEMBER:
    Name one other Council member.

    EXACT CLAIM:
    Copy one contiguous 5-25 word quotation from that member.

    WHY IT IMPROVES MY THINKING:
    Explain what you learned from it.


    MY REVISION:
    State one meaningful change to your original position after hearing
    the others. If you make no change, explain why.


    QUESTION FOR THE COUNCIL:
    Ask one pointed question based only on ideas that actually appeared
    in Round 1.

    Rules:
    - Name other Council members.
    - Disagreement is encouraged.
    - Do not manufacture agreement.
    - Do not manufacture claims.
    - If unsure whether someone said something, leave it out.
    - Keep the response under about 300 words.
    """

        print(f"\n\n{'-' * 70}")
        print(f"{name.upper()} — RESPONSE TO THE COUNCIL")
        print("-" * 70)

        answer = ask_ollama(persona, prompt)
        round2[name] = answer

        print(answer)


    print("\n\n" + "=" * 70)
    print("ROUND 2 COMPLETE")
    print("=" * 70)

    # ============================================================
    # ROUND 3 — CHAIR / SYNTHESIS
    # ============================================================

    round2_transcript = "\n\n".join(
        f"### {name}\n{answer}"
        for name, answer in round2.items()
    )

    CHAIR = """
    You are the Chair of a Council of Experts.

    You are not another expert and you do not have your own design agenda.

    Your job is to analyze the Council's reasoning:
    - identify arguments that became stronger after challenge
    - identify genuine agreements
    - preserve genuine disagreements
    - notice contradictions and weak reasoning
    - distinguish transcript evidence from factual claims that would
      require external verification
    - synthesize useful conclusions without pretending consensus exists

    Do not reward an idea merely because several members repeated it.
    Do not average opinions.
    Do not introduce major new ideas that no Council member proposed.
    """

    chair_prompt = f"""
    ORIGINAL QUESTION:

    {QUESTION}

    ROUND 1 — INITIAL POSITIONS:

    {transcript}

    ROUND 2 — CROSS-EXAMINATION:

    {round2_transcript}


    You are analyzing the Council transcript.

    STRICT EVIDENCE RULES:

    1. Do not claim "all members agree" unless you can identify supporting
       evidence from all five members.

    2. For REAL CONSENSUS, name every member who supports the idea.
       If fewer than five support it, do not call it unanimous.

    3. For every STRONGEST ARGUMENT, state whether it:
       - appeared in Round 1 and was later challenged,
       - was revised in Round 2,
       - or merely emerged in Round 2 and has NOT yet been challenged.

    4. Do not say a Round 2 revision "survived challenge" because members
       did not see one another's Round 2 responses.

    5. Do not invent dimensions, percentages, equipment, materials,
       capacities, performance figures, or design details not present
       in the transcript.

    6. Do not place the same member on opposing sides of a disagreement
       unless you explicitly explain that the member changed position.

    7. When uncertain, say the transcript does not establish the point.


    COUNCIL VERDICT


    STRONGEST ARGUMENTS

    For each:
    - Argument
    - Members supporting it
    - Evidence status: CHALLENGED / REVISED / UNCHALLENGED ROUND-2 IDEA

    Important:
    - Do not say a Round 2 idea "survived challenge" unless another member
      actually saw and challenged that Round 2 idea.
    - Distinguish between an idea being adopted, revised, challenged,
      or merely left unchallenged.


    REAL CONSENSUS

    Count only EXPLICIT support.

    - "Implied", "consistent with", "compatible with", "similar to",
      or thematic overlap does NOT count as support.
    - UNANIMOUS requires explicit supporting evidence from all five members.
    - MAJORITY requires explicit supporting evidence from three or four members.
    - MINORITY CONVERGENCE requires explicit supporting evidence from two members.
    - If fewer than two members explicitly support the same proposition,
      it is not consensus.
    - Never use "all members agree" unless all five named members explicitly
      support the exact proposition in the transcript.

    For every consensus item:
    - State the proposition.
    - Name exactly which members explicitly support it.
    - Classify it as UNANIMOUS / MAJORITY / MINORITY CONVERGENCE.
    - Do not count inferred support.


    IMPORTANT DISAGREEMENTS

    For each:
    - State the disagreement.
    - Name the members on each side.
    - Explain the underlying assumption or tradeoff.
    - Do not place the same member on both sides unless that member explicitly
      changed position, in which case explain the change.


    IDEAS WEAKENED BY DEBATE

    Identify ideas that became less convincing because another member
    directly challenged them.

    Do not call an idea "weakened by debate" merely because another member
    proposed something different.


    CLAIMS NEEDING VERIFICATION

    For each:
    - Identify the factual or technical claim.
    - Explain what would need to be checked externally.
    - State that the transcript itself does not establish whether it is true.

    Do NOT state whether the claim is:
    - true or false
    - scientifically valid or invalid
    - feasible or impossible
    - peer-reviewed or unsupported
    - proven or disproven

    Those judgments require external evidence that is not contained in
    the Council transcript.


    SYNTHESIZED COMPOUND

    Use only details already proposed in the transcript.

    - Do not invent specifications, capacities, percentages, equipment,
      materials, dimensions, or performance claims.
    - Attribute important elements to the member or members who proposed them.
    - Do not label a section "all members agree" unless explicit evidence
      exists from all five members.
    - Preserve worthwhile minority ideas instead of forcing compromise.


    UNRESOLVED QUESTION

    End with the single most important unresolved question that genuinely
    emerged from the Council discussion.
    """

    print("\n\n" + "=" * 70)
    print("COUNCIL CHAIR — FINAL SYNTHESIS")
    print("=" * 70)

    chair_answer = ask_ollama(CHAIR, chair_prompt)

    print(chair_answer)

    # ============================================================
    # SAVE CURRENT RUN
    # ============================================================

    with open("round1_latest.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    with open("round2_latest.txt", "w", encoding="utf-8") as f:
        f.write(round2_transcript)

    with open("chair_latest.txt", "w", encoding="utf-8") as f:
        f.write(chair_answer)


    audit_errors, audit_warnings = audit_chair(chair_answer)


if __name__ == "__main__":
    main()
