# Test Failure Analysis

## Isolation method

Both failures were diagnosed by:
1. Running `pytest -v` to identify the two failing tests.
2. Reading `spec.md`, `src/logsum.py`, and `test/test_logsum.py` side-by-side.
3. Tracing the code path for each failing input to understand exactly what the
   implementation does versus what the test asserts.

---

## Failure 1 — `test_missing_required_field_value`

**What the test does:**  
Passes a row with an empty `level` field and asserts `returncode != 0`.

**What the code does:**  
`normalise_level("")` returns `"UNKNOWN"` (silent fallback). The file is
processed successfully and the tool exits with code 0.

**What the spec says:**  
> CSV header (required): `timestamp`, `level`, `service`, `message`

The spec mandates that the required *columns* be present (enforced via the
header check), but it says nothing about empty field *values* being an error.
The normalisation rules describe how to handle values (`level` → uppercase,
`service` → lowercase) but do not state that a blank value must be rejected.

**Verdict: Spec ambiguity**  
The spec is silent on whether an empty required field value is an error or
should be normalised to a sentinel like `UNKNOWN`. The test assumes the former;
the code implements the latter. Neither is demonstrably wrong given the spec.

**Recommended action:** Clarify in the spec whether blank required field values
are a validation error (exit non-zero) or a normalisation case (substitute
sentinel). Do not change code or test until the spec owner decides.

---

## Failure 2 — `test_malformed_timestamps[2026-07-07 14:30:00]`

**What the test does:**  
Passes the timestamp `"2026-07-07 14:30:00"` (space separator, no `Z`) and
asserts `returncode != 0`. The test comment reads: "Missing 'T' and 'Z'".

**What the code does:**  
`datetime.fromisoformat("2026-07-07 14:30:00")` succeeds. Python 3.11 expanded
`datetime.fromisoformat` to accept the space character as a valid ISO 8601
date-time separator (per ISO 8601:2004 §4.3.2, the space is a permitted
alternative to `T`). The row is processed normally and the tool exits with 0.

**What the spec says:**  
> Timestamps must be valid ISO 8601 values (for example: `2026-07-07T14:30:00Z`).

The spec provides one illustrative example but does not restrict timestamps to
only that exact format. `"2026-07-07 14:30:00"` is a valid ISO 8601 local
datetime; the code correctly accepts it.

**Verdict: Test bug**  
The test misreads the spec. It incorrectly classifies a valid ISO 8601 datetime
(space separator, naive/local time) as malformed. The implementation behaviour
is correct given both the spec wording and ISO 8601.

**Recommended fix:** Remove `"2026-07-07 14:30:00"` from the
`@pytest.mark.parametrize` list, or restrict the spec to require UTC (`Z`)
timestamps only — in which case the code also needs a format check, and the
change should be spec-driven.
