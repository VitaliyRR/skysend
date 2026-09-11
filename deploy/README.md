# SkySend deployment

`dist/` is the complete static release. Copy the contents of `dist/` directly
into an immutable release directory, so `index.html` sits at the release root.
Move the `current` symlink only after the files and Nginx configuration have
been checked:

```text
/srv/skysend/releases/<git-sha>/
/srv/skysend/current -> /srv/skysend/releases/<git-sha>/
```

Before switching the symlink, verify
`test -f /srv/skysend/releases/<git-sha>/index.html`.

## Canonical HTTPS host

Set `root /srv/skysend/current;` in the active `https://skysend.ru` server and
merge `skysend-server.inc` into it. The file contains `location /`, cache rules,
error pages, security headers and the generated legacy rules. Do not include it
unchanged in a virtual host that already declares the same locations.

Run `nginx -t` before moving `current` or reloading Nginx. Keep the previous
symlink target until the public smoke checks pass so rollback is one symlink
change and one reload.

## HTTP and www hosts

These hosts need the exact legacy rules before the broad canonical redirect.
A server-level `return 301` runs before location matching, so place the broad
redirect in `location /`:

```nginx
root /srv/skysend/current;
include /etc/nginx/snippets/skysend-legacy-locations.inc;

error_page 410 /410.html;

location = /410.html {
    internal;
}

location / {
    return 301 https://skysend.ru$request_uri;
}
```

Copy `deploy/legacy-locations.inc` to
`/etc/nginx/snippets/skysend-legacy-locations.inc`. The generated file contains
163 exact `301` rules and 13 exact `410` rules. Its targets are already absolute
canonical URLs. The public software navigation is a dropdown of seven detail
routes; `/software`, `/software/` and the old general `/program` addresses
redirect to `/software/terminal/` rather than serving a software index.

## Release checks

Run the build and acceptance check from the repository root:

```bash
python site/build.py
python tools/validate_site.py
```

The expected production manifest contains 37 canonical routes, 46 HTML files
(including seven redirect-only documents), 72 download records, 163 redirects
and 13 gone routes. Treat any different
count as a release failure until the content sources, migration map and generated
Nginx/static redirect files agree.

Then verify at least one canonical page, one old redirect, one removed promo URL,
the branded 404 page, `/data/providers.json`, CSS and an image. Expected statuses
are `200`, `301`, `410` and `404` respectively. Confirm that `/_redirects`
returns `404` on Nginx.

The optional Sites preview serves the branded 404 page, but its static redirect
format cannot emit HTTP 410. Production Nginx remains the authoritative host for
the 13 removed promo URLs.

## External account links

Registration and account endpoints failed TLS or DNS checks during the source
audit. The default build replaces them with sales and support contacts. Enable
the external endpoints only after a launch-time check succeeds:

```bash
SKYSEND_EXTERNAL_ACCOUNTS_VERIFIED=1 python site/build.py
SKYSEND_EXTERNAL_ACCOUNTS_VERIFIED=1 python tools/validate_site.py
```

Do not enable the flag when either endpoint redirects unexpectedly, presents an
invalid certificate or cannot complete its normal sign-in flow.
