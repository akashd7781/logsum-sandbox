# Context Load Check

The loaded rule file is **CLAUDE.md**.

## Project context

The repository is **logsum-sandbox**, intended for experimenting with Python-based log summarisation while keeping implementations simple and incremental.

## Conventions

* Source code belongs in `src/`
* Tests belong in `tests/`
* Synthetic datasets belong in `data/`

## Utilities to prefer

Prefer Python 3.11 standard library before external packages, use `ruff` for linting, and `pytest` for testing.

## Escalation gates

* Stop before introducing new dependencies.
* Use synthetic data only.
* Do not overwrite `spec.md` after sign-off without asking.
* Ask before introducing architectural or framework changes.

**Source:** `CLAUDE.md`
