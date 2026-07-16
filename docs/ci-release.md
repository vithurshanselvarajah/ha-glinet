# CI and Release Workflows (`.github/workflows/`)

The repository has several GitHub Actions workflows.

## Branching model

| Branch        | Role                                                  | Direct pushes | PRs accepted from                  | Ruleset |
| ------------- | ----------------------------------------------------- | ------------- | ---------------------------------- | ------- |
| `main`        | Release branch — always points at the latest release  | ❌ No          | `development` only (release PRs)   | ✅ yes   |
| `development` | Integration branch — where day-to-day work lands      | ✅ Yes (maintainers only) | forks, same-repo feature branches  | ❌ no    |

All day-to-day pull requests target `development`. The only PRs that
ever open against `main` are **release PRs** opened by a maintainer
from `development` into `main`. A bot
([`pr-target-check.yml`](../.github/workflows/pr-target-check.yml))
will comment and apply the `wrong-target` label on any other PR
opened against `main`.

`development` intentionally has no branch ruleset so that
Dependabot updates, the wiki-sync bot, and maintainer direct pushes
can all proceed without friction. See
[`.github/BRANCH_PROTECTION.md`](../.github/BRANCH_PROTECTION.md) for
the rationale and an archived template if you ever want to add one.

See [`CONTRIBUTING.md`](../CONTRIBUTING.md#branching--prs) for the
full contribution flow.

## CI

`.github/workflows/ci.yml` runs on pull requests and as a reusable workflow call.

It performs:

- JSON validation for `manifest.json` and `hacs.json`.
- Python compilation for `custom_components` and `tests`.
- Pytest.
- Ruff linting.
- Version consistency check between `custom_components/glinet_router/manifest.json` and `pyproject.toml`.

## Release

`.github/workflows/release.yml` runs only on `main` and publishes releases when a stable release is requested.

Release triggers:

- Stable release: push to `main` with `release:` anywhere in the head commit message.
- Manual run: trigger workflow dispatch on `main`.

The workflow reads the version from `custom_components/glinet_router/manifest.json`.

Stable releases create:

```text
v<manifest-version>
```

The release job runs CI first, builds a HACS-friendly zip containing `custom_components/glinet_router`, asks GitHub Models to generate release notes via `actions/ai-inference`, then publishes a GitHub release. If GitHub Models is not available, the workflow falls back to commit-based release notes.

## PR target check

`.github/workflows/pr-target-check.yml` is a soft-enforcement bot
that runs on every pull request whose base branch is `main`. It
posts a warning comment and applies the `wrong-target` and
`needs-triage` labels to any PR that is **not** a `development`
→ `main` release. It does **not** auto-close the PR — the
maintainer decides what to do with it.

## Related Pages

- [Developer Reference](https://github.com/vithurshanselvarajah/ha-glinet-router/wiki/developer-reference) — Contributing, tooling, and project structure.
- [`CONTRIBUTING.md`](https://github.com/vithurshanselvarajah/ha-glinet-router/blob/main/CONTRIBUTING.md) — Full contributor guide.
- [`BRANCH_PROTECTION.md`](https://github.com/vithurshanselvarajah/ha-glinet-router/blob/main/.github/BRANCH_PROTECTION.md) — Intended branch-protection ruleset.
