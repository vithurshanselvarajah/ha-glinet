# Branch Protection

> **This file documents the intended branch-protection rules.**
> The rules themselves live in GitHub under
> **Settings → Rules → Rulesets** (or **Settings → Branches** for the
> legacy branch-protection rules). They are **not** part of the
> repository contents and must be configured by a maintainer.
>
> This file exists so that the ruleset is reproducible and the
> rationale for each rule is preserved.

---

## Overview

| Branch        | Role                            | Direct pushes | PRs allowed from              |
| ------------- | ------------------------------- | ------------- | ----------------------------- |
| `main`        | Release branch                  | ❌ No          | `development` only (releases) |
| `development` | Integration branch (default)    | ❌ No          | forks, same-repo feature branches |

---

## `main` — Release branch

Configure under **Settings → Rules → Rulesets → New ruleset → Branch**:

- **Target:** branch pattern `main`
- **Enforcement:** Active

Recommended rules:

- [x] **Require a pull request before merging**
  - Required approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - Required check: `test` (from `.github/workflows/ci.yml`)
  - [x] Require branches to be up to date before merging
- [x] **Require linear history** (no merge commits; squash-merge only)
- [x] **Do not allow force pushes**
- [x] **Do not allow deletions**
- [x] **Block creation of matching branches** (no one should create a `main` branch on a fork that pretends to be upstream)
- [x] **Restrict who can push to matching branches** — add `@vithurshanselvarajah` (and any other maintainers)
- [x] **Allow GitHub Actions to bypass** — leave this **off** for `main` (we want humans to approve every release)

### Dependabot on `main`

The release branch should not receive Dependabot PRs.
[`dependabot.yml`](.github/dependabot.yml) targets `development` only,
so this is already handled — but worth re-checking after Dependabot
configuration changes.

---

## `development` — Integration branch

Configure under **Settings → Rules → Rulesets → New ruleset → Branch**:

- **Target:** branch pattern `development`
- **Enforcement:** Active

Recommended rules:

- [x] **Require a pull request before merging**
  - Required approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
- [x] **Require status checks to pass before merging**
  - Required check: `test` (from `.github/workflows/ci.yml`)
  - [x] Require branches to be up to date before merging
- [x] **Require linear history** (squash-merge only)
- [ ] **Allow force pushes** — *optional*. Many projects allow this on
  `development` to make rebasing painless. Leave it **off** if you
  prefer a clean audit trail.
- [x] **Do not allow deletions**
- [x] **Allow GitHub Actions to bypass** — turn this **on** so that
  Dependabot PRs can be auto-merged by the
  [`dependabot-auto-merge`](.github/workflows/) workflow if you have
  one, and so the wiki-sync and stale workflows can push to the branch
  if needed.

---

## Collaborator access

Configure under **Settings → Collaborators and teams**:

- Only `@vithurshanselvarajah` (and any other trusted maintainers)
  should have **Write**, **Maintain**, or **Admin** access.
- Everyone else must fork the repository and submit a PR from a fork.
  GitHub enforces this automatically once write access is removed.
- When inviting a new maintainer, prefer the **Maintain** role over
  **Admin** so they cannot accidentally delete the repository.

---

## PR targeting rules (enforced by `.github/workflows/pr-target-check.yml`)

The `pr-target-check` workflow posts a warning comment and applies the
`wrong-target` label to any PR opened against `main`, **except** for
PRs whose head branch is `development` (those are valid release PRs).

This is a soft enforcement — it does not auto-close PRs. The
maintainer can decide whether to redirect or reject.

---

## Why a two-branch model?

- `development` is where day-to-day work happens. It can move fast,
  receive Dependabot updates, and accept PRs from anyone.
- `main` is sacred. It only moves when a release is cut, and every
  change to `main` is reviewed, CI-green, and intentionally
  documented.
- This separation lets the
  [release workflow](.github/workflows/release.yml) keep its simple
  `on: push: branches: [main]` trigger without needing per-PR
  approval logic.

---

## Checklist for applying these rules

When you set this up for the first time, do the following in order:

1. [ ] Create a new ruleset for `development` first (so PRs targeting
       `main` can be filtered by the bot even before `main` is
       protected).
2. [ ] Create a ruleset for `main`.
3. [ ] Confirm that the `test` job from `ci.yml` exists in the
       repository (it does — check the Actions tab after the first
       run).
4. [ ] Add `@vithurshanselvarajah` to the `CODEOWNERS` file and merge
       that change into `development` first.
5. [ ] Under **Settings → Collaborators and teams**, audit current
       collaborators and remove any that should not have write
       access.
6. [ ] Add a personal access token or use the GitHub UI to verify that
       outside contributors cannot push directly to `main` or
       `development` (they should not be able to — they fork instead).
7. [ ] Open a test PR from a fork to `main` to confirm the
       `pr-target-check` workflow comments and labels it correctly.
       Then close the test PR.
