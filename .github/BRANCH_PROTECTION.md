# Branch Protection

> **This file documents the intended branch-protection rules.**
> The rules themselves live in GitHub under
> **Settings → Rules → Rulesets** (or **Settings → Branches** for the
> legacy branch-protection rules). They are **not** part of the
> repository contents and must be configured by a maintainer.
>
> This file exists so the ruleset is reproducible and the rationale
> for each rule is preserved.

---

## Overview

| Branch        | Role                            | Direct pushes | PRs allowed from              | Branch ruleset |
| ------------- | ------------------------------- | ------------- | ----------------------------- | -------------- |
| `main`        | Release branch                  | ❌ No          | `development` only (releases) | ✅ yes          |
| `development` | Integration branch (default)    | ✅ Yes (maintainers) | forks, same-repo feature branches | ❌ no (intentionally) |

> **`development` has no ruleset on purpose.** It's the working
> branch — Dependabot, wiki-sync, and direct pushes from maintainers
> are all allowed there so day-to-day work doesn't fight the
> rules. The `pr-target-check.yml` bot (below) still runs to
> prevent accidental PRs to `main`.

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
  - [ ] **Require approval of the most recent reviewable push** —
    leave **off** for solo-maintainer repos (it blocks self-approval;
    see the callout below).

> **Solo-maintainer note: leave the self-approval rule OFF.**
>
> The "Require approval of the most recent reviewable push" rule
> exists to prevent a multi-maintainer attack where one person
> approves a PR, another person pushes a malicious change, and
> the first person's stale approval still counts. In a single-
> maintainer project this rule is **purely destructive** — it
> blocks the only person who can approve from ever self-merging,
> so the merge button is permanently disabled. GitHub will show:
>
> > Cannot update this protected ref. New changes require
> > approval from someone other than the last pusher.
>
> When you add a second trusted maintainer with **Write** or
> **Maintain** access, re-enable this rule. Until then, leave it
> off.

- [x] **Require status checks to pass before merging**
  - Required check: **`test`** (from `.github/workflows/ci.yml`)
  - [x] Require branches to be up to date before merging
- [x] **Block force pushes**
- [x] **Restrict deletions**
- [x] **Restrict creations** — only `@vithurshanselvarajah` can
  create a `main` branch (prevents forks from creating a fake one)
- [x] **Restrict updates** — only `@vithurshanselvarajah` can push
  directly (everything else must go through a PR)

**Do NOT enable:**

- ~~Require linear history~~ — incompatible with merge commits. Drop it.
- ~~Allow GitHub Actions to bypass~~ — leave the Bypass list empty
  (or grant only yourself). The release workflow doesn't need bypass;
  it doesn't write to `main` itself.

### Merge method

**Settings → General → Pull Requests:**

- [x] **Allow merge commits** (you want a visible history)
- [x] Allow squash merging (optional — useful for one-off cleanups)
- [x] Allow rebase merging (optional)
- Default merge method: **Merge commit**

### Dependabot on `main`

The release branch should not receive Dependabot PRs.
[`dependabot.yml`](.github/dependabot.yml) targets `development` only,
so this is already handled.

---

## `development` — Integration branch

**No ruleset.** This is intentional.

- Maintainers (currently `@vithurshanselvarajah`) can push directly
  to `development` for hotfixes, rebases, or coordinating multi-PR
  work without needing a PR.
- Dependabot, the wiki-sync workflow, and the stale-bot all push to
  `development` without friction.
- The only protection on this branch is **social**: the
  [`pr-target-check.yml`](../workflows/pr-target-check.yml) bot
  (below) still runs against PRs that target `main` from anywhere
  other than `development`.

When you're ready to add a ruleset to `development`, see the
[archived template](#archived-development-ruleset-template) at the
bottom of this file.

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

The bot runs **regardless of branch protection** because it's a
workflow trigger, not a ruleset rule. This means it works even
before you set up the `main` ruleset, and it keeps working if you
ever decide to remove the ruleset.

---

## Why a two-branch model?

- `development` is where day-to-day work happens. It can move fast,
  receive Dependabot updates, and accept direct pushes from
  maintainers.
- `main` is sacred. It only moves when a release is cut, and every
  change to `main` is reviewed, CI-green, and intentionally
  documented.
- This separation lets the
  [release workflow](release.yml) keep its simple
  `on: push: branches: [main]` trigger without needing per-PR
  approval logic.

---

## Checklist for applying these rules

When you set this up for the first time, do the following in order:

1. [ ] Create a ruleset for `main` only.
2. [ ] Confirm the `test` job from `ci.yml` exists in the repository
       (check the Actions tab after the first run).
3. [ ] Add `@vithurshanselvarajah` to the [`CODEOWNERS`](CODEOWNERS)
       file (already done) and merge that change into `development`
       first.
4. [ ] Under **Settings → General → Pull Requests**, enable **Allow
       merge commits** and set the default to **Merge commit**.
5. [ ] Under **Settings → Collaborators and teams**, audit current
       collaborators and remove any that should not have write
       access.
6. [ ] Add a personal access token or use the GitHub UI to verify
       that outside contributors cannot push directly to `main`
       (they should not be able to — they fork instead).
7. [ ] Open a test PR from a fork to `main` to confirm the
       `pr-target-check` workflow comments and labels it correctly.
       Then close the test PR.
8. [ ] Open a release PR from `development` → `main` to confirm the
       bot skips it (head = `development` is the allowed exception).

---

## Archived: `development` ruleset template

If you ever decide to add a ruleset to `development`, here's the
template that was previously recommended. It mirrors `main` but
loosens the rules to allow Dependabot and bot bypass.

**Settings → Rules → Rulesets → New ruleset → Branch:**

- **Target:** branch pattern `development`
- **Enforcement:** Active

Recommended rules:

- [x] **Require a pull request before merging**
  - Required approvals: **1**
  - [x] Dismiss stale pull request approvals when new commits are pushed
  - [x] Require review from Code Owners
  - [ ] **Require approval of the most recent reviewable push** —
    leave **off** for solo-maintainer repos (see the callout in the
    `main` section above). Re-enable when a second maintainer is added.
- [x] **Require status checks to pass before merging**
  - Required check: **`test`**
  - [x] Require branches to be up to date before merging
- [x] **Block force pushes**
- [x] **Restrict deletions**
- Bypass list: **`@vithurshanselvarajah`** plus the **GitHub Actions**
  role (so Dependabot and the wiki-sync bot can push without
  tripping the rules).

> **Don't enable "Require linear history"** if you want to allow
> normal merge commits on `development`.
