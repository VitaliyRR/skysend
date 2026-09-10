# Merge these locations into the canonical HTTPS server block after setting:
# root /srv/skysend/current;

include /etc/nginx/snippets/skysend-legacy-locations.inc;

error_page 404 /404.html;
error_page 410 /410.html;

location = /404.html {
    internal;
}

location = /410.html {
    internal;
}

location = /_redirects {
    return 404;
}

location / {
    try_files $uri $uri/ =404;
}

location ~* \.(?:css|js)$ {
    try_files $uri =404;
    expires -1;
}

location ~* \.(?:woff2|svg|png|jpe?g)$ {
    try_files $uri =404;
    expires 7d;
}

location = /data/providers.json {
    try_files $uri =404;
    expires 1h;
}

add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
