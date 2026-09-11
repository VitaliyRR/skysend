# SkySend public site

The production bundle is generated from the approved content files in `data/`.
There are no runtime dependencies and no application backend.

```bash
python site/build.py
python tools/validate_site.py
python -m http.server 4173 --directory dist
```

The build creates 40 canonical routes and 46 HTML files including the 404, 410,
and four redirect-only documents. It publishes 72 download records, the local provider catalogue,
the sitemap, 157 legacy redirects, and 13 gone routes. Only the curated
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

`site/partner_scenes.py` renders subject illustrations in 27 partner sections. Partner pages omit local links and jump navigation; representative contact fields are plain text in the final section. `/software/rma/` combines Windows, Linux and Android with nine downloads and redirects from both previous detail URLs.
