# K 5.W.9 — By-hand vs by-agent comparison

## What both produced
Both the supervised chain and the agent replay converged on the same end state: the logsum feature matches the spec, the tests pass, the replay note is recorded, and the work is published on a branch. The final result keeps the CLI behavior stable, keeps the deterministic sort, preserves the grouping rules, and documents the change.

## Where the agent saved time
The agent compressed the whole replay into a few batched reads, edits, and validations instead of stepping file by file. It also handled the branch move and push directly, so the implementation, notes, and publication all happened in one pass.

## Where the agent went wrong or shorter
The agent went shorter on local validation than a fully supervised/manual chain would ideally do. `pytest -v` was run successfully, but `ruff check .` could not be reproduced locally because `ruff` was not installed in this environment. The agent also leaned on the existing CI workflow instead of explicitly editing it, which was correct for this repo but shorter than a full replay that might touch every surface.

## What the agent did better
It kept the edit set focused and avoided unnecessary churn. The code refactor was small and readable, the tests were trimmed to spec-driven assertions, and the provenance/refactor notes were updated to reflect the actual replay rather than a generic summary.

## What I learned about supervised vs async
Supervised work is better for catching mismatches early and forcing explicit checkpoints, especially around validation and provenance. Async agent work is faster at moving from context to changes, but it needs a tight verification loop so it does not stop at a plausible-looking answer.

## What I would do differently next time
I would ask for a stricter validation plan up front, including the exact commands I expect to run and what counts as acceptable fallback if a tool is missing. I would also separate "code replay" from "publication" more explicitly so branch creation and push happen only after the verification step is complete.