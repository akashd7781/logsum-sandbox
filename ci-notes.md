# CI Notes

## Workflow

File: `.github/workflows/ci.yml`  
Trigger: `push` and `pull_request` on all branches.  
Runner: `ubuntu-latest`, Python 3.11.  
Steps: install `ruff` + `pytest` → `ruff check .` → `pytest -v`.

## Result

Pending — link will be updated once the PR CI run completes.
