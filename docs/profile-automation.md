# Profile graphics: automatic updates

Status: published to `pengusto/pengusto` on 23 October 2026. The first manually dispatched [hosted workflow run](https://github.com/pengusto/pengusto/actions/runs/39986202267) succeeded. Existing commit history is preserved.

## Intended behavior

The workflow checks public data once a day at 05:23 UTC and can also be started manually. It targets only `pengusto/pengusto`, checks out the default branch, generates matching dark/light desktop/mobile scans and cities, and commits only these files if their content changes:

- `assets/city.svg`, `assets/city-light.svg`
- `assets/city-mobile.svg`, `assets/city-light-mobile.svg`
- `assets/scan.svg`, `assets/scan-light.svg`
- `assets/scan-mobile.svg`, `assets/scan-light-mobile.svg`
- `assets/project-{name}.svg`, `assets/project-{name}-light.svg` for each of the four selected projects
- `github-data.json`

The update script itself never commits or pushes. The GitHub Actions workflow handles the publishing step. Bot commits use `github-actions[bot]` rather than a personal name. There is no push trigger or force-push step.

The banner, profile introduction and Kaplum demo remain static assets. The four selected public repository cards now refresh with the calendar and scan. GitHub caches README images; an updated commit may not appear immediately. The numbers are periodically refreshed data, not a live feed on every profile view.

## Sources and permissions

Public GitHub contribution calendar HTML provides actual day counts and activity levels. The public users API provides repository/follower counts; the selected public repository and languages endpoints provide descriptions, topics, star counts, last push dates and language-byte shares, and the avatar is fetched from the public GitHub avatar endpoint. No personal access token or new secret is required. The workflow passes its built-in GitHub token to avoid shared runner rate limits; the fetcher attaches it only to api.github.com requests. Public repository ownership, visibility and metric types are validated before generating output. Repository count includes public forks, as in the previous design.

On GitHub, the automatic repository-scoped `GITHUB_TOKEN` needs `contents: write` only for the update job's final commit/push. Branch protection or repository Actions policy may prevent that step; no bypass is prepared. Official checkout/setup-python actions are pinned to inspected v6 commit IDs. The renderer uses Python 3.12 and Pillow 12.3.0.

## Local verification

From the repository root, with Pillow installed:

```sh
python -m unittest discover -s tests -p test_profile_update.py
python scripts/update_profile.py --output . --dry-run
python scripts/update_profile.py --output .
```

Run the commands above from the repository root.

The updater fetches and validates all inputs, renders to a temporary directory, and checks the SVGs before replacing generated output. Fetch, invalid calendar markup or invalid avatar errors leave the previous images in place. Temporary render directories are automatically removed. The calendar parser fails visibly if GitHub changes its HTML rather than replacing data with invented zeros. All-zero activity calendars are valid.

Identical inputs preserve the prior retrieval timestamp and produce no file changes, so a repeat run does not create an empty update commit. Actual changes to data, avatar, renderer or calendar date window regenerate the output. Rolling date windows can legitimately produce daily changes even when no new contributions were made.

## Activation and operation

The profile and workflow were published with explicit approval. Manual dispatch verified hosted execution. The published profile was checked in dark and light mode at 390 px and 1440 px: all 35 README images loaded, the matching theme and mobile sources were selected, and there was no horizontal overflow. Opening a local preview does not publish changes.

GitHub schedules can be delayed or dropped under load, and scheduled workflows in a public repository can be disabled after 60 days without repository activity. Manual dispatch remains the recovery route once enabled.

References: [GitHub schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [checkout bot commits](https://github.com/actions/checkout#push-a-commit-using-the-built-in-token).

## Verified locally on 23 October 2026

Six regression tests passed. A live public-data dry run succeeded; the local preview was refreshed, and a second live dry run reported no changes. Workflow YAML parsed successfully and action references are pinned. The integrated banner, scan and city passed browser checks at 320, 390, 600 and 768 px with all 24 images loaded. Hosted execution and repository write permission were subsequently verified by the successful workflow run linked above.

## Light/dark variants

The same validated data input generates all twelve generated SVGs in one staged build. Light mode uses explicit pale surfaces, dark purple text and shaded purple buildings; no inversion or CSS filter. The palette is maintained in scripts/profile_theme.py and included in the no-change fingerprint. Regression tests compare text/data across the themes and fail on unmapped colours. The banner, intro and small link labels also have paired theme assets; these static assets are not regenerated by the data updater. The explicit iris-indigo palettes are in profile_theme.py and are not browser visited-link colours or CSS filters.

The README uses GitHub-supported picture/source theme queries and width queries for mobile compositions where they improve readability. Two image sizes are not a general requirement. The local Dark and Light review pages force only the preview's source selection; auto.html retains the unmodified GitHub-rendered theme queries and follows the browser preference. No preview scripts or page stylesheet are embedded in the README.

## Landmarks and contribution evidence — 24 October 2026

The repository cards are original SVGs inspired by the Landmarks visual reference, not a copied GitSkins asset. The four repositories are an explicit public-only allowlist in scripts/profile_projects.py. Each card is a separate linked image, naturally wrapping into one column on narrow screens. Project-only data changes do not rewrite unchanged calendar or scan images, and calendar-only changes do not rewrite unchanged project cards. All outputs are validated and staged before replacement.

The city footer identifies @pengusto and the actual calendar date range in both sizes and themes. Inline SVG link labels use GitHub-retained align="absmiddle" so they sit on the same line as ordinary text. Separate inline middle-dot separators were removed; native list bullets remain intentional.

A search for `is:merged author:pengusto` is not sufficient evidence of every accepted contribution. Wallos #1260 and #1263 are closed/unmerged individually, but the upstream maintainer explicitly confirmed both were incorporated into merged batch #1267. docs/merged-contributions.json retains the individual status, confirmation links and the merged batch commit separately. The README therefore calls this section Upstream and does not incorrectly label the individual Wallos PRs as merged. Future contribution refreshes must check maintainer-confirmed batch or cherry-pick integration alongside direct merge state; do not count a closed PR as accepted without such evidence.


## Compact, clickable cards

Each landmark now has its own 420px SVG in dark and light palettes, wrapped in a real README repository link. GitHub applies its native image max-width; inline cards wrap into one column on narrow screens without custom CSS. Do not put separate repository links inside a combined SVG image: those regions cannot be independently clicked when the SVG is embedded as an image.

The updater generates eight project card files, eight city/scan files and the JSON manifest. Only the changed repository card pair is rewritten when its metadata changes. Language percentages and the ambiguous “code share” label were removed; cards show the leading language, public stars and push date. No project-completion percentage is implied. Static workbench/upstream cards retain scope labels and the README keeps attribution and merge evidence in expandable sections.

Regenerate static cards with `python scripts/render_static_cards.py`. Further workbench projects are collapsed by default so the profile stays short; every card remains a separate repository link when expanded.

City labels follow the compact reference hierarchy: CONTRIBUTION CITY, abbreviated total, “contributions in the last year”, active days and busiest day. Visible date ranges are omitted; full dates and exact counts remain in the public JSON snapshot and per-day SVG titles. The @pengusto footer is retained in all theme/viewport variants.


## Worldfolio and README Stats — 24 October 2026

Worldfolio is hosted separately at <https://pengusto.github.io/worldfolio/> from the root of `pengusto/worldfolio` on `main`. The profile links an actual runtime recording to that site. The GIF, reduced-motion poster and saved colourful GitSkins terminal SVGs are static assets; the workflow does not regenerate them. The original purple compositions and project/contribution evidence remain intact.

The original [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats) now recommends its maintained successor and [Stats Action](https://github.com/stats-organization/github-readme-stats-action). The same daily/manual workflow now uses that Action, pinned to v2.1.0 commit `2c498845f71017821efaad14293ebc736156ef21`, with `@stats-organization/github-readme-stats-core` fixed to `2.2.1`. This is the documented successor renderer, rather than an unchanged copy of the retired original.

Four local files are generated: `assets/readme-stats/stats.svg`, `stats-light.svg`, `top-langs.svg`, and `top-langs-light.svg`. Dark/light sources match GitHub's theme selection. Public data uses the built-in repository token; no personal token, private-repository access or visitor-time rendering server is required. Top languages represents the public repository language breakdown, not a measure of proficiency. Core dependencies are installed on the runner by the Action, never in this repository.

`fail_on_error: true` stops a failed API lookup before the commit step, retaining the last successful cards instead of publishing an error image. All four cards and the existing widgets publish together through the existing concurrency group. The 15-minute timeout includes installing the third-party renderer. There is still no push trigger and no force push; a conflicting external edit can fail the run safely, and the workflow can then be retried.

The coloured terminal option is a saved export, with its GitSkins branding retained. Its numbers are a snapshot from 24 October 2026; only the separate native widgets and README Stats cards refresh automatically. Source/hash records are in `docs/showcase-assets.json`.

Lesson retained: a local preview/draft must not replace a newer live profile wholesale. Fetch the current profile first, then add the requested section while preserving its existing content and automation.


### First hosted verification

[Run 40047160177](https://github.com/pengusto/pengusto/actions/runs/40047160177) succeeded on 24 October 2026 in 49 seconds, including all twelve existing regression tests, the native data refresh, all four Stats Action renders and the bot commit. The public README integration was then published separately so its image paths already existed.

The live GitHub profile was checked at 1440×960 in dark mode and 390×844 in light mode with reduced motion. All 31 README images loaded with expandable project/terminal sections open; theme-specific cards selected the expected local SVGs. The Worldfolio image links to the verified Pages address, and reduced motion selects its static poster. Neither viewport had page overflow. Worldfolio itself passed desktop driving, six project destinations, Enter-to-repository interaction, mobile touch start and the Details panel. The production world made no external resource requests and had no missing files or page errors. Physical Safari/iOS acceptance remains untested.

## Reviewed composition and weekly refresh — 24 October 2026

The reviewed profile composition now lives in `profile/`, with generated public assets saved in the repository. The root README is exported from that composition after validating its asset references. The existing source files, Worldfolio assets and public Stats Action are retained. Worldfolio is linked in Let's Connect; public GitHub Stats are available in an expandable section.

The existing single refresh workflow now runs weekly on Sunday at 08:00 Europe/Berlin rather than daily, with automatic daylight saving time adjustment. Its original concurrency group and pinned Stats Action remain in place. It adds the staged GitSkins/City refresh, both regression suites and root README export; changed generated output is committed and pushed using the built-in token. See [the current runbook](../profile/README-automation.md). The earlier daily wording above records the previous setup.

The first complete weekly-pipeline verification succeeded in [run 40056426560](https://github.com/pengusto/pengusto/actions/runs/40056426560), including its bot push (`251d3ab`). The public composition and native mobile City were verified in the browser; all 25 tests passed in the hosted workflow.
