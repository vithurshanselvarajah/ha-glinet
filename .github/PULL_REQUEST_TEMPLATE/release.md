---
name: Release
about: Cut a new release by merging `development` into `main` (maintainers only)
---

<!--
  ⚠️  MAINTAINERS ONLY — DO NOT USE FOR REGULAR CHANGES.

  This template is for the `development` → `main` release PR.
  The release is finalised by either:
    1. Merging this PR with a follow-up commit on `main` whose message
       contains the literal `release:` string, OR
    2. Running the "Release" workflow via workflow_dispatch on `main`
       AFTER this PR is merged.

  See .github/workflows/release.yml and docs/ci-release.md for details.
-->

## Release checklist

- [ ] All PRs intended for this release are merged into `development`
- [ ] `custom_components/glinet_router/manifest.json` `version` is bumped
- [ ] `pyproject.toml` `project.version` matches `manifest.json` (CI enforces this)
- [ ] CI on `development` is green
- [ ] No `release:` string in any commit message on this branch
      (it would only fire on `main`, but keep history clean)

## Version

<!-- The version being released, e.g. 1.7.0. -->

- From `manifest.json`:
- Will be tagged as: `v<version>`

## Release notes draft

<!-- Optional. A short summary of what is in this release. The
     release workflow will auto-generate notes from commits, but
     feel free to add a curated summary here. -->

### Highlights

-

### Breaking changes

- None.

### Fixes

-

### Thanks

- Thanks to all contributors who landed changes in this cycle.
