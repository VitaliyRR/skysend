# SkySend public site

The production bundle is generated from the approved content files in `data/`.
There are no runtime dependencies and no application backend.

```bash
python site/build.py
python tools/validate_site.py
python -m http.server 4173 --directory dist
```

The build creates 42 canonical routes, the local provider catalogue, sitemap,
404 and 410 documents, and Nginx legacy rules. Only the curated production
assets are copied into `dist/`.

External registration and account URLs are disabled by default because their
TLS/DNS checks failed during the source audit. See `deploy/README.md` for the
release gate and Nginx rollout notes.
