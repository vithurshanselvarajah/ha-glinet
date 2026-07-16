---
name: Documentation
about: Documentation-only change (wiki pages, README, inline docs, etc.)
---

<!--
  Documentation PRs target `development`, not `main`.
  Note: changes under `docs/` are auto-synced to the GitHub wiki
  via .github/workflows/wiki-sync.yml on merge to `development`.
-->

## What is being changed?

<!-- One paragraph: which page(s) and what is changing. -->

## Motivation

<!-- Why is this change needed? Link an issue if applicable. -->

- Fixes #
- Refs #

## Checklist

- [ ] Markdown lints clean (no broken links, consistent code-fence languages)
- [ ] Internal links use the `docs/<page>.md` style so they survive wiki sync
- [ ] If this introduces a new page, it is linked from `docs/Home.md` and the README
- [ ] No code changes — only docs (`.md`, `.rst`, or similar)
