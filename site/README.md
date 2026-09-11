# SkySend public site

The production bundle is generated from the approved content files in `data/`.
There are no runtime dependencies and no application backend.

```bash
python site/build.py
python tools/validate_site.py
python -m http.server 4173 --directory dist
```

The build creates 37 canonical routes and 46 HTML files including the 404, 410,
and seven redirect-only documents. It publishes 72 download records, the local provider catalogue,
the sitemap, 163 legacy redirects, and 13 gone routes. Only the curated
production assets are copied into `dist/`.

`site/partner_art.py` renders six navigation tiles with large subject images on opaque white surfaces. `site/partner_editorial.py` selects contextual editorial pictures for partner modules; exact prompts, sources and responsive exports are recorded in `data/editorial-artwork.json`. Source PNGs stay under `design/editorial-sources/` and are not published. Original product specification photos and brand marks are retained.

`/software/` and `/partners/` are not public canonical pages. The header exposes
their detail routes in dropdowns, while the index URLs use static fallback
redirects for hosts that ignore `_redirects`. Product pages include their relevant verified or clearly
labelled archival documentation; ALLVEND and FINGER retain their expanded
source-based content.

External registration and account URLs are disabled by default because their
TLS/DNS checks failed during the source audit. See `deploy/README.md` for the
release gate and Nginx rollout notes.

Unchanged workflows use `site/partner_diagrams.py` and four retained scenes use `site/partner_scenes.py`, on opaque surfaces; FINGER uses its real brand mark. Partner pages omit local links and jump navigation; representative contact fields are plain text in the final section. `/software/rma/` combines Windows, Linux and Android with nine downloads and redirects from both previous detail URLs.

All terminal information is on `/equipment/`; old model/category URLs redirect to section anchors. XML, POS and FINGER descriptions are consolidated, and support has one contact section. Lucide symbols and their license are under `assets/icons/process/`.
