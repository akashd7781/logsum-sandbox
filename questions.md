# Questions

Files read: [src/logsum.py](src/logsum.py), [spec.md](spec.md), [.github/workflows/ci.yml](.github/workflows/ci.yml), [tests/test_logsum.py](tests/test_logsum.py), [pyproject.toml](pyproject.toml).

## Where is the grouping rule?
The grouping logic is in [src/logsum.py](src/logsum.py#L53-L57): each row is normalized, then stored under the `(level, service)` tuple key in `groups[(level, service)]`. The spec defines the exact key at [spec.md](spec.md#L43): `(level, service)`.

## How is missing level handled?
A blank `level` value is normalized to `UNKNOWN`, and a blank `service` value is normalized to `unknown` in [src/logsum.py](src/logsum.py#L11-L18). The spec matches that behavior in [spec.md](spec.md#L38-L40), where empty `level` and `service` values are documented as missing and mapped to `UNKNOWN`/`unknown`.

## How do I run tests and CI locally?
The CI workflow runs on `ubuntu-latest` with Python 3.11 in [\.github/workflows/ci.yml](.github/workflows/ci.yml#L9-L17). It installs `ruff` and `pytest`, then runs `ruff check .` and `pytest -v` in [\.github/workflows/ci.yml](.github/workflows/ci.yml#L19-L26). To mimic CI locally, run the same commands in your shell.

## Could not verify
I could not verify a separate local CI wrapper or task file in the files I read; the CI definition I could confirm is the GitHub Actions workflow in [\.github/workflows/ci.yml](.github/workflows/ci.yml#L1-L26).

## Verification
- [src/logsum.py](src/logsum.py#L53-L57): Correct — this is where `level` and `service` are normalized and the `(level, service)` group key is used.
- [spec.md](spec.md#L42-L43): Wrong rule — these lines only show the section heading and lead-in, not the actual grouping key.
- [src/logsum.py](src/logsum.py#L11-L18): Correct — these lines normalize blank `level` and `service` values.
- [spec.md](spec.md#L38-L40): Correct — these lines document the empty-field edge cases.
- [\.github/workflows/ci.yml](.github/workflows/ci.yml#L9-L17): Correct — these lines set the runner and Python 3.11 version.
- [\.github/workflows/ci.yml](.github/workflows/ci.yml#L19-L26): Correct — these lines install dependencies and run lint/test.
- [\.github/workflows/ci.yml](.github/workflows/ci.yml#L1-L26): Correct — this is the full CI workflow file.
