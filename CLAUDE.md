# CLAUDE.md

## Project context

* Project: logsum-sandbox
* Purpose: experiment with Python log summarisation.
* Keep the implementation simple, incremental, and easy to review.

## Conventions

* Source code lives in `src/`
* Tests live in `tests/`
* Synthetic datasets live in `data/`

## Utilities to prefer

* Python 3.11 standard library first
* Use `ruff` for linting
* Use `pytest` for testing

## Escalation gates

* Stop before adding new dependencies.
* Use synthetic data only.
* Never overwrite `spec.md` after sign-off without asking first.
* Ask before introducing architectural or framework changes.
