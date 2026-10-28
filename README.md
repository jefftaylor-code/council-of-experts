# Council of experts

A local multi-agent debate with an auditor that checks the summary.

One AI answer hides the trade-offs. Ask several personas instead and you get a different problem: the summary at the end tends to claim agreement that the debate never reached. This project runs a small "council" of five expert personas on a local model, has a Chair write the verdict, and then checks that verdict with plain deterministic rules.

Everything runs on a laptop through [Ollama](https://ollama.com). No cloud API, no API key and no cost per run.

## How it works

1. **Round 1, initial positions.** Five personas (Engineer, Eccentric Futurist, Survivalist, Philosopher, Ruthless Minimalist) each answer the question alone, in a fixed structure.
2. **Round 2, evidence-locked challenge.** Each persona reads the Round 1 transcript and must quote another member word for word (5 to 25 words, no ellipses) before objecting to or praising them. No quote means no claim.
3. **Round 3, the Chair.** A neutral Chair writes the verdict: strongest arguments, real consensus, disagreements, claims that need outside checking, and a synthesis. It has strict rules: consensus needs named supporters, and inferred support doesn't count.
4. **Audit.** `auditor.py` checks the Chair's text without a model:
   - each consensus row's label matches its count of named members (UNANIMOUS = 5, MAJORITY = 3 or 4, MINORITY CONVERGENCE = 2)
   - no inferred-support wording ("implied", "consistent with") inside REAL CONSENSUS
   - the verification section doesn't rule on truth ("proven", "impossible")
   - absolute phrases such as "all members agree" are flagged for a human

The auditor checks the Chair's bookkeeping. It does not decide whether any argument is true.

## Example run

`examples/` holds one full run (Round 1, Round 2 and the Chair's verdict) for a playful question about designing a personal compound. In that run the Chair's consensus table holds up: every MAJORITY row names three supporters.

That example also caught a bug in the auditor itself. The first version searched the whole label cell for "UNANIMOUS", so a row labelled "MAJORITY ... Not unanimous" was reported as a false UNANIMOUS violation. The auditor now reads only the label the Chair actually assigned, and `tests/test_auditor.py` covers that case. Auditors need tests too.

## Run it

```bash
ollama pull qwen3:4b-instruct
python council_v0.py
```

This uses only the Python standard library. It writes `round1_latest.txt`, `round2_latest.txt` and `chair_latest.txt`, then prints the audit result.

To run the tests:

```bash
pip install pytest
python -m pytest
```

To ask your own question, edit `QUESTION` in `council_v0.py`. To change the council, edit `EXPERTS` and `MEMBER_NAMES` in `auditor.py`.

## Files

| File | What it does |
| --- | --- |
| `council_v0.py` | Runs the three rounds against a local Ollama model, saves the transcripts and audits the verdict |
| `auditor.py` | Deterministic checks on the Chair's verdict |
| `tests/test_auditor.py` | Tests for the auditor, including the saved example |
| `examples/` | One saved run |
