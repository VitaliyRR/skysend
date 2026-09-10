# SkySend public site

The production bundle is generated from the approved content files in `data/`.
There are no runtime dependencies and no application backend.

```bash
python site/build.py
python tools/validate_site.py
python -m http.server 4173 --directory dist
```

The build creates 41 canonical routes and 45 HTML files including the 404, 410,
and two redirect-only index documents. It publishes 71 download records, the local provider catalogue,
the sitemap, 153 legacy redirects, and 13 gone routes. Only the curated
production assets are copied into `dist/`.

`site/partner_art.py` contains the six geometric SVG navigation pictograms for
the home partner tiles. Their glass surfaces and responsive layout are defined
in `site/static/styles.css`; labels and destinations remain in `data/navigation.json`.

`/software/` and `/partners/` are not public canonical pages. The header exposes
their detail routes in dropdowns, while the index URLs use static fallback
redirects for hosts that ignore `_redirects`. Product pages include their relevant verified or clearly
labelled archival documentation; ALLVEND and FINGER retain their expanded
source-based content.

External registration and account URLs are disabled by default because their
TLS/DNS checks failed during the source audit. See `deploy/README.md` for the
release gate and Nginx rollout notes.
