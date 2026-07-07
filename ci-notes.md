# CI Notes

## Workflow

File: `.github/workflows/ci.yml`  
Trigger: `push` and `pull_request` on all branches.  
Runner: `ubuntu-latest`, Python 3.11.  
Steps: install `ruff` + `pytest` → `ruff check .` → `pytest -v`.

## First run — RED

**Failure:** `ruff check .` exited 1.  
**Error:** `F401 [*] 'io' imported but unused → test/test_logsum.py:2`  
**Diagnosis:** Test file bug — `import io` was present in `test/test_logsum.py` but never used. Not a code bug, not a workflow bug.  
**Fix:** Removed `import io` from `test/test_logsum.py` (commit `faee777`).  
**Verdict:** Correct fix — deleted the dead import, did not touch any test logic.

## Second run — expected GREEN

Fix pushed to branch `add-ci-workflow`. CI re-triggered on PR:  
https://github.com/akashd7781/logsum-sandbox/pull/1  
(update URL if PR number differs)
