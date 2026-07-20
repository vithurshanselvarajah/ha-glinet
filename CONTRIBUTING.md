# Contributing to ha-glinet-router

Thanks for your interest in contributing! This document explains how the
project is organised, how to set up a development environment, and the
process for opening pull requests.

> **New here?** Skim [Branching & PRs](#branching--prs) first, then
> [Local Development](#local-development), then open your PR.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Branching & PRs](#branching--prs)
- [Reporting Bugs & Requesting Features](#reporting-bugs--requesting-features)
- [Local Development](#local-development)
- [Testing & Linting](#testing--linting)
- [Commit Messages](#commit-messages)
- [Release Process](#release-process)
- [Adding a New Sensor or Module](#adding-a-new-sensor-or-module)
- [Documentation](#documentation)
- [Dependency Policy](#dependency-policy)
- [Security](#security)

---

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/).
By participating, you agree to abide by its terms. Be respectful, assume
good intent, and focus on what is best for the community.

---

## Branching & PRs

The repository uses a two-branch model:

| Branch        | Purpose                                                                       | PRs accepted? |
| ------------- | ----------------------------------------------------------------------------- | ------------- |
| `main`        | Release branch. Always points at the latest released code.                   | **No** (except releases — see below) |
| `development` | Integration branch. All day-to-day work lands here. **No ruleset** — maintainers may push directly. | **Yes**       |

### Rules

1. **All pull requests must target `development`.** PRs opened against
   `main` are automatically flagged and labelled `wrong-target` by a
   bot. They will not be merged.
2. **Releases are the only exception.** A release is a pull request from
   `development` into `main`. Releases are managed by the maintainer(s)
   only and use the [Release PR template](.github/PULL_REQUEST_TEMPLATE/release.md).
3. **Outside contributors must fork.** No one outside the maintainer
   team has direct write access. Fork the repository, create a feature
   branch on your fork, and open a pull request back into
   `development`.
4. **Merge method.** `main` is configured to allow normal merge
   commits so the release history stays visible. `development` has
   no ruleset — maintainers may push directly there for hotfixes,
   rebases, or coordinating work.
5. **Approvals and CI apply to `main` only.** The `main` ruleset
   requires 1 approval from a code owner and a passing `test`
   check. `development` is unconstrained so day-to-day work and
   Dependabot updates don't get blocked.
6. **Self-merge is allowed for solo maintainers.** The
   `protect-main` ruleset intentionally leaves the
   *"Require approval of the most recent reviewable push"* rule
   off so the only maintainer can self-merge release PRs without
   needing a second approver. This rule will be re-enabled when a
   second trusted maintainer is added. See
   [`.github/BRANCH_PROTECTION.md`](.github/BRANCH_PROTECTION.md)
   for the rationale.

### Typical contribution flow

```text
   ┌──────────────┐
   │  Fork (you)  │   (outside contributors only)
   └──────┬───────┘
          │ git clone / git fork
          ▼
   ┌──────────────────────┐
   │ feature/your-change  │
   └──────┬───────────────┘
          │ git push
          ▼
   ┌───────────────────────────────┐
   │ PR: feature/your-change       │
   │   → vithurshanselvarajah/...  │
   │     development              │
   └──────┬────────────────────────┘
          │ review + CI
          ▼
   ┌───────────────────────────────┐
   │ squash-merge into development │
   └──────┬────────────────────────┘
          │ cut a release
          ▼
   ┌───────────────────────────────┐
   │ PR: development → main        │
   │   (Release template)          │
   └───────────────────────────────┘
```

### Pull request templates

A PR template picker is provided. Choose the one that best matches
your change:

| Template    | When to use                                            |
| ----------- | ------------------------------------------------------ |
| (default)   | General-purpose changes                                |
| `feature`   | New user-facing feature                                |
| `bugfix`    | Fixing a bug                                           |
| `docs`      | Documentation-only changes                             |
| `release`   | Cutting a release (maintainers only — `development` → `main`) |

---

## Reporting Bugs & Requesting Features

Please use the GitHub issue templates:

- [Bug report](.github/ISSUE_TEMPLATE/bug_report.yml)
- [Feature request](.github/ISSUE_TEMPLATE/feature_request.yml)

For general support or questions, use the
[Discord](https://discord.gg/Metvr5hC3m) — issues are for actionable
items only.

> When filing a bug, include your Home Assistant version, integration
> version, router model, and router firmware version. Diagnostic dumps
> are hugely helpful — see [Diagnostics](docs/hub.md) for instructions
> on how to generate one from within Home Assistant.

---

## Local Development

### 1. Fork and clone

```bash
git clone https://github.com/<your-username>/ha-glinet-router.git
cd ha-glinet-router
git remote add upstream https://github.com/vithurshanselvarajah/ha-glinet-router.git
```

### 2. Set up a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows PowerShell
python -m pip install --upgrade pip
python -m pip install -e ".[test]" ruff
```

### 3. Create a feature branch

Always branch off `development`:

```bash
git fetch upstream
git checkout -b feature/your-change upstream/development
```

### 4. Make your changes

See [Architecture](docs/architecture.md) and
[Developer Reference](docs/developer-reference.md) for an overview of
how the codebase is organised.

### 5. Run the checks

See the next section.

---

## Testing & Linting

Before opening a PR, run the full local check suite:

```bash
# Tests
python -m pytest -q

# Lint (with auto-fix where safe)
ruff check custom_components tests --fix

# Format
ruff format custom_components tests

# Sanity-check that everything compiles
python -m compileall -q custom_components tests
```

CI runs the same checks on every PR (see
[CI & Release Workflows](docs/ci-release.md)).

### Test guidelines

- **All new code must be covered by tests.** A PR that adds
  functionality but no tests will be asked to add them.
- Tests live in `tests/` and mirror the structure of
  `custom_components/glinet_router/`.
- Use `pytest` and `pytest-asyncio`. Network calls are mocked — no
  test should require a live router.
- Run `python -m pytest -q` before pushing. CI will reject a PR if
  the test suite fails.

---

## Commit Messages

This project does not enforce a strict commit message convention, but
the following guidelines help reviewers and `git log` readers:

- **Imperative mood** in the subject line
  ("Add battery sensor", not "Added battery sensor").
- **One logical change per commit** (squash-merge will collapse them
  into one anyway).
- **Reference the issue** in the footer when relevant
  (`Fixes #123`, `Refs #456`).

### ⚠️ Avoid `release:` in commit messages unless you mean it

The release workflow ([`.github/workflows/release.yml`](.github/workflows/release.yml))
is triggered by a push to `main` whose **head commit message contains
the literal string `release:`**. The same trigger works on
`workflow_dispatch` from `main`. Releases are maintainer-only.

**Never** put `release:` in a commit message on `development` or on a
feature branch. It will not trigger a release from those branches,
but it makes history confusing.

---

## Release Process

Releases are cut by the maintainer(s) and follow this flow:

1. Land the desired changes on `development`.
2. Bump the version in **both**:
   - `custom_components/glinet_router/manifest.json` → `version`
   - `pyproject.toml` → `project.version`
   The CI version check will fail if these two disagree.
3. Open a PR from `development` to `main` using the
   [Release PR template](.github/PULL_REQUEST_TEMPLATE/release.md).
4. After merge, push a follow-up commit to `main` with a message
   containing `release:` to trigger the release workflow, **or** run
   the `Release` workflow manually from the Actions tab
   (`workflow_dispatch` on `main`).
5. The release workflow runs CI, builds a HACS-friendly zip, generates
   release notes (via GitHub Models, with a fallback), and publishes a
   GitHub release tagged `v<manifest-version>`.

> Releases are **not** cut by Dependabot. Dependabot only updates
> `development`.

---

## Adding a New Sensor or Module

The high-level checklist is in
[Developer Reference → Adding a New Sensor](docs/developer-reference.md#adding-a-new-sensor).
The short version:

1. **API models:** add a field to `custom_components/glinet_router/api/models.py`
   if the raw API response needs a typed model.
2. **Hub models:** add a field to `custom_components/glinet_router/models.py`
   if the hub needs to expose a higher-level view.
3. **Hub:** update `custom_components/glinet_router/hub.py` to fetch,
   store, and expose the new data.
4. **Entity:** add the new entity under `custom_components/glinet_router/entities/`
   (in the right domain file, e.g. `sensor.py`, `switch.py`).
5. **Diagnostics:** update `custom_components/glinet_router/diagnostics.py`
   so the new field is included in the diagnostics export and any PII
   (SSIDs, MACs, IPs) is redacted.
6. **Tests:** add or update tests in `tests/` and run `pytest`.
7. **Docs:** add or update the relevant page under `docs/`.

---

## Documentation

User-facing documentation lives under `docs/` and is synced to the
GitHub wiki by the
[wiki-sync workflow](.github/workflows/wiki-sync.yml). Any change to a
file under `docs/` will be mirrored to the wiki on merge to
`development`.

When your change is user-facing, update the relevant page(s) under
`docs/` in the same PR. If you are introducing a new feature, add a
new page and link it from [docs/Home.md](docs/Home.md) and the
README's [Feature Matrix](README.md#features).

---

## Dependency Policy

- The integration must remain lightweight. It targets Home Assistant
  core, so heavy third-party dependencies are a tax on every user.
- The only hard runtime dependency is `aiohttp`, which is shipped with
  Home Assistant. Please justify any new dependency in the PR
  description.
- Dev / test dependencies (pytest, pytest-asyncio, ruff, etc.) are
  fine and live in `pyproject.toml` under `[project.optional-dependencies]`.

---

## Security

If you discover a security vulnerability, **do not** open a public
issue. Please follow the
[GitHub security advisory process](https://github.com/vithurshanselvarajah/ha-glinet-router/security/advisories/new)
or contact the maintainer via Discord. We will coordinate a fix and a
disclosure timeline.

---

## Related Pages

- [Architecture](docs/architecture.md) — How the integration is structured.
- [Developer Reference](docs/developer-reference.md) — Codebase overview and conventions.
- [CI and Release Workflows](docs/ci-release.md) — Automated testing and releases.
- [Router API Notes](docs/router-api.md) — Endpoint inventory and auth model.
- [Hub Reference](docs/hub.md) — The `GLinetHub` coordinator and polling loop.
