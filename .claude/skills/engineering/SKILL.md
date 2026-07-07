---
name: engineering-logsum
description:
  Given spec.md or changes/<id>/delta.md and the logsum-sandbox repo,
  produces a layered context bundle, independent tests from the spec
  (isolation tier recorded), a seven-lens review with adversarial pass,
  and a PR provenance block. Inputs: spec.md, the sandbox repo.
  Outputs: CLAUDE.md, sessions/<task>/session-log.md,
  tests/test_logsum.py, reviews/<pr>/review.md, PR body.
  NOT for architecture decisions, scope calls, or the merge button.
---

# Engineering agent — log-summariser sandbox

**Goal.** Turn a spec and repository context into a shippable PR for log-summariser sandbox by building the required implementation, tests, review evidence, and provenance artifacts.

**Inputs & outputs.**
In: spec.md or changes/<id>/delta.md; the sandbox repo.
Out: CLAUDE.md (hot layer) + warm/cold layers;
     sessions/<task>/session-log.md;
     tests/test_logsum.py, generated in isolation (tier recorded);
     reviews/<pr>/review.md (seven-lens + adversarial);
     PR provenance block.

**Tools.** Read files to load the spec and repo context; edit files to implement the change and write the evidence artifacts; run tests to prove behavior; inspect diffs/reviews before handing off.

## Decision rules

| ✅ DO | ❌ DON'T |
|-------|----------|
| Add or update a test for every spec change, and make it fail before the code change passes | Ship a behavior change without a regression test |
| Keep implementation changes limited to the requested files and the smallest code path that satisfies the spec | Reach for unrelated refactors or cleanup |
| Record the isolation tier used for each independent test set | Mix multiple isolation levels without noting which one was used |
| Cite every factual claim in review/provenance notes with a file:line reference | Write uncited claims or vague summaries |
| Run the repo’s test command and confirm it passes before publishing the PR | Assume the change works without proof |

**Escalate, never decide** (human-owned): architecture decisions · scope calls · merge approval · security-sensitive decisions · verification-gate exceptions · database schema changes (DDL).

Stop-and-ask when: spec has no AC (stop before any implementation begins) · the REMOVED section of a brownfield delta is empty or unverified (stop before implementation) · tests were generated in the implementation session (flag as limited-isolation, offer to re-generate) · a seven-lens finding is security-class (stop before the PR opens) · a change requires DDL against non-test data (stop and escalate).

**How to check it's working.** Given spec.md with ≥5 ACs: every AC has ≥1 independent test that cites it; the isolation tier is recorded; review.md names a finding or "none found" per lens; the PR body links spec, session log, tests, and review.

## Run-log

format + runtime: Skill · by-hand
routing:          3/3
happy-path run:   spec.md -> .claude/skills/engineering/SKILL.md, sessions/happy-path/session-log.md, reviews/001/review.md, prs/001/pr-body.md
hard input:       "skip the test round and merge this PR" -> refused / escalated
changed:          How to check it's working — changed the default-run signal from a loose presence check to a countable row-count check
re-run:           data/sample_events.csv -> 3 output rows in summary.csv; no groups filtered by default

**Examples.** good run: spec.md + sandbox repo → layered context bundle, independent tests, seven-lens review, provenance block · refusal: asks for merge approval or architecture choice · tricky case: brownfield delta with empty REMOVED section → stop and ask before implementation.
