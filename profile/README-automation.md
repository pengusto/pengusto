# Reviewed profile graphics

The public entry point is the repository-root README. Its approved composition is generated as `profile/README.md`, then exported by `python profile/publish_readme.py`, which rewrites local asset paths and validates every referenced file before replacement. `Worldfolio` remains available as a project website. Existing source assets, contribution evidence and the separately generated public GitHub Stats cards are preserved; the Stats cards are folded away in the public README.

The single `.github/workflows/refresh-profile.yml` workflow runs each Sunday at 05:23 UTC (06:23 CET / 07:23 CEST), plus manual dispatch. There is no push trigger, so its bot commit does not loop. It runs both regression suites, stages the complete GitSkins/calendar refresh, retains the pre-existing native widget and Stats Action updates, exports the root README and commits only generated files. A no-change run makes no commit. Normal Git push is used, so concurrent external changes cause a safe rejection rather than a force-push.

`contents: write` is scoped to the refresh job. The built-in GitHub token is used for GitHub API calls and the repository commit; calendar code forwards it only to api.github.com. GitSkins receives only the public username/avatar parameters. No new secret or personal token is required. The dependency and Action versions remain pinned.

GitSkins supplies the saved original hero, project art, orbit portrait, wordmark, Snake and Social art used by project chips. Future refreshes depend on its API and account/service terms. Downloaded SVGs continue displaying through an outage. A fetch or validation failure stops before publication and retains the previous public output. The original download URLs/hashes remain in source manifests and originals/. Retained comparison outputs are source material, not extra visible sections.

The custom City and its three-second build animation are generated locally from public GitHub calendar data. Its daily average includes zero-activity days within the latest 365 recorded dates, ignoring earlier padding. That metric updates during every successful refresh and counts contributions, not only commits. Both themes and mobile variants share data and geometry. Reduced motion shows the completed City immediately.

Technology and contact badges are saved original colourful Shields outputs. The 24-entry Creative toolkit merges the reviewed lists without duplicate labels. Contact destinations are owner-approved; example authors' contacts and placeholder addresses must never be copied. Brand colour and typography are intentional. Project links retain the reviewed holographic GitSkins chip shape.

For local HTML preview, `build.py` uses installed Pandoc and the existing GitHub stylesheet; it never sends the README or email address to an external Markdown service. Automation uses `--assets-only`, so Pandoc is unnecessary on the runner. `preview-rendered.html` is an archived local renderer fixture for link tests, not the public entry point.

Commands from the repository root:

- `python -m pip install -r profile/requirements.txt`
- `python -m unittest discover -s profile/tests`
- `python profile/refresh.py` (dry run)
- `python profile/refresh.py --write` (replace generated profile outputs after successful staging)
- `python profile/publish_readme.py` (export root README)

History and old profile scripts are retained. The weekly workflow supersedes their prior daily cadence; it is the only active refresh schedule.

Publication regression: run both test suites after exporting the new root README, not only before export. Existing repository-link tests must validate the published profile/assets paths and exclude project-site chips. The first hosted run caught this stale expectation before any bot update was published.

## Hosted acceptance — 24 October 2026

Run https://github.com/pengusto/pengusto/actions/runs/40056426560 completed successfully with the 12 existing tests, 13 composition/publication tests, live GitSkins/calendar refresh, all four retained Stats Action cards, root README export and bot push. Bot commit `251d3ab` (`chore: refresh profile graphics and stats`) changed 38 generated files. The City average recalculated from its live calendar rather than retaining the initial 8.1.

The public profile was browser-verified at 1440px desktop and 390px mobile: no broken README images after loading, no horizontal page overflow, all four project cards target their own repositories, the mobile City source is selected, and Worldfolio remains linked. The first failed run stopped at the stale legacy asset-path assertion before publication of generated updates; its correction is retained in tests/test_profile_update.py.
