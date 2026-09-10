# SkySend public site

The production bundle is generated from the approved content files in `data/`.
There are no runtime dependencies and no application backend.

```bash
python site/build.py
python tools/validate_site.py
python -m http.server 4173 --directory dist
```

The build creates 41 canonical routes and 43 HTML files including the 404 and
410 documents. It publishes 71 download records, the local provider catalogue,
the sitemap, 153 legacy redirects, and 13 gone routes. Only the curated
production assets are copied into `dist/`.

`/software/` is not a public canonical page. The header exposes seven software
detail routes in a dropdown, and legacy general software URLs redirect to
`/software/terminal/`. Product pages include their relevant verified or clearly
labelled archival documentation; ALLVEND and FINGER retain their expanded
source-based content.

External registration and account URLs are disabled by default because their
TLS/DNS checks failed during the source audit. See `deploy/README.md` for the
release gate and Nginx rollout notes.
