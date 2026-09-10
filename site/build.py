#!/usr/bin/env python3
"""Build the SkySend public site from the approved content handoff.

The output is dependency-free static HTML. JavaScript only enhances navigation,
image viewing, motion, and the provider catalogue; core content stays readable
without it.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
SITE = ROOT / "site"
DIST = ROOT / "dist"
BASE_URL = "https://skysend.ru"
EXTERNAL_ACCOUNTS_VERIFIED = os.environ.get("SKYSEND_EXTERNAL_ACCOUNTS_VERIFIED") == "1"


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SITE_CONTENT = load_json("site-content.json")
SECONDARY_CONTENT = load_json("secondary-content.json")
UTILITY_CONTENT = load_json("utility-content.json")
EQUIPMENT = load_json("equipment-content.json")
DOWNLOADS = load_json("download-catalog.json")
PROVIDERS = load_json("providers-source.json")
NAVIGATION = load_json("navigation.json")
BINDINGS = load_json("section-assets.json")["bindings"]
PROVIDER_WALL = load_json("provider-wall-selection.json")
ASSET_MANIFEST = load_json("assets-manifest.json")
SORTED_PROVIDERS = sorted(PROVIDERS["providers"], key=lambda item: item["name"].casefold())

PAGES = [
    page
    for page in [
        *SITE_CONTENT["pages"],
        *SECONDARY_CONTENT["pages"],
        *UTILITY_CONTENT["pages"],
    ]
    if page["path"] != "/partners/"
]
PAGE_BY_PATH = {page["path"]: page for page in PAGES}
SOFTWARE_PAGES = [
    page for page in SITE_CONTENT["pages"] if page.get("template") == "software-detail"
]
DOWNLOAD_BY_GROUP = {
    group["id"]: [item for item in DOWNLOADS["items"] if item["group"] == group["id"]]
    for group in DOWNLOADS["groups"]
}
DOWNLOAD_BY_ID = {item["id"]: item for item in DOWNLOADS["items"]}
EXPLICIT_DOWNLOAD_ITEMS = {
    ("/software/terminal/", "flash"): ("terminal-a65a6fe49e", "terminal-2dd1aa405f"),
    ("/software/xml/", "protocol"): ("xml-f638411134",),
    ("/software/pos/", "start"): ("pos-9484f696f3",),
    ("/support/", "downloads"): (
        "rma-b6571ae893",
        "rma-5a93447b3a",
        "system-documents-d7aa6f83af",
    ),
    ("/connect/", "documents"): (
        "system-documents-9d640ab884",
        "system-documents-715b844cf0",
        "system-documents-44d1acf427",
    ),
    ("/system-rules/", "document"): ("system-documents-9d640ab884",),
}
ASSET_META = {
    item.get("path"): item
    for item in ASSET_MANIFEST["assets"]
    if item.get("path")
}
ORIGINAL_BY_NAME = {
    item.name.lower(): item for item in (ASSETS / "originals").glob("*") if item.is_file()
}


def e(value) -> str:
    return html.escape(str(value or ""), quote=True)


def clean_text(value: str) -> str:
    return " ".join(str(value or "").split())


def is_external(href: str) -> bool:
    return href.startswith(("http://", "https://"))


def link_attrs(href: str) -> str:
    if is_external(href):
        return ' target="_blank" rel="noopener noreferrer"'
    return ""


def resolved_action_items(items):
    accounts = {
        account.get("href"): account
        for key, account in NAVIGATION.get("external_accounts", {}).items()
        if key in {"registration", "login"} and isinstance(account, dict)
    }
    resolved = []
    seen_hrefs = set()
    for item in items:
        candidate = item
        account = accounts.get(item.get("href"))
        if account and not (EXTERNAL_ACCOUNTS_VERIFIED or account.get("launch_enabled")):
            candidate = account.get("fallback") or {"label": "Связаться со SkySend", "href": "/support/"}
        href = candidate.get("href", "#")
        if href in seen_hrefs:
            continue
        seen_hrefs.add(href)
        resolved.append(candidate)
    return resolved


def action_links(items, *, primary_first: bool = False, css: str = "actions") -> str:
    if not items:
        return ""
    links = []
    for index, item in enumerate(resolved_action_items(items)):
        href = item.get("href", "#")
        kind = "button button--primary" if primary_first and index == 0 else "text-link"
        links.append(
            f'<a class="{kind}" href="{e(href)}"{link_attrs(href)}>'
            f'{e(item.get("label"))}<span aria-hidden="true">&nbsp;↗</span></a>'
        )
    return f'<div class="{e(css)}">{"".join(links)}</div>'


def route_output(path: str) -> Path:
    if path == "/":
        return DIST / "index.html"
    return DIST / path.strip("/") / "index.html"


def asset_url(path: str) -> str:
    return "/" + quote(path.replace("\\", "/").lstrip("/"), safe="/")


def asset_dimensions(path: str) -> tuple[int | None, int | None]:
    meta = ASSET_META.get(path, {})
    return meta.get("width"), meta.get("height")


def image_tag(
    path: str,
    alt: str,
    *,
    css: str = "media-image",
    eager: bool = False,
) -> str:
    width, height = asset_dimensions(path)
    attrs = ""
    if width and height:
        attrs = f' width="{width}" height="{height}"'
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if eager else ""
    return (
        f'<img class="{e(css)}" src="{e(asset_url(path))}" alt="{e(alt)}"'
        f'{attrs} loading="{loading}" decoding="async"{priority}>'
    )


def figure_image(
    path: str,
    alt: str,
    *,
    caption: str | None = None,
    css: str = "media-object",
    lightbox: bool = False,
    eager: bool = False,
) -> str:
    image = image_tag(path, alt, css=css, eager=eager)
    if lightbox:
        image = (
            f'<a class="media-open" href="{e(asset_url(path))}" data-lightbox-src="{e(asset_url(path))}" '
            f'data-lightbox-alt="{e(alt)}" data-lightbox-caption="{e(caption or alt)}" '
            f'aria-label="Открыть изображение: {e(caption or alt)}">{image}</a>'
        )
    figcaption = f'<figcaption>{e(caption)}</figcaption>' if caption else ""
    return f'<figure class="media-figure">{image}{figcaption}</figure>'


def picture_figure(paths: list[str], alt: str, *, caption: str | None = None, lightbox=False) -> str:
    desktop = paths[0]
    mobile = paths[1] if len(paths) > 1 else None
    width, height = asset_dimensions(desktop)
    dimensions = f' width="{width}" height="{height}"' if width and height else ""
    source = f'<source media="(max-width: 47.99rem)" srcset="{e(asset_url(mobile))}">' if mobile else ""
    image = (
        f'<picture>{source}<img class="media-object media-object--diagram" src="{e(asset_url(desktop))}" '
        f'alt="{e(alt)}"{dimensions} loading="lazy" decoding="async"></picture>'
    )
    if lightbox:
        image = (
            f'<a class="media-open" href="{e(asset_url(desktop))}" data-lightbox-src="{e(asset_url(desktop))}" '
            f'data-lightbox-alt="{e(alt)}" data-lightbox-caption="{e(caption or alt)}" '
            f'aria-label="Открыть изображение: {e(caption or alt)}">{image}</a>'
        )
    figcaption = f'<figcaption>{e(caption)}</figcaption>' if caption else ""
    return f'<figure class="media-figure">{image}{figcaption}</figure>'


def provider_wall() -> str:
    items = []
    for index, item in enumerate(PROVIDER_WALL["items"], 1):
        items.append(
            f'<li class="provider-logo provider-logo--{(index % 5) + 1}">'
            f'{image_tag(item["path"], item["provider_name"], css="provider-logo__image")}'
            f'<span class="sr-only">{e(item["provider_category"])}</span></li>'
        )
    return (
        '<figure class="provider-wall"><ul class="provider-wall__grid" '
        f'aria-label="{e(BINDINGS["provider-logos"]["alt"])}">{"".join(items)}</ul></figure>'
    )


def feature_list(section) -> str:
    rows = []
    for field in section.get("visual_fields", []):
        value = field.get("value")
        value_html = f'<dd>{e(value)}</dd>' if value is not None else ""
        rows.append(f'<div><dt>{e(field.get("label"))}</dt>{value_html}</div>')
    return f'<dl class="feature-list">{"".join(rows)}</dl>'


def process_visual(section) -> str:
    nodes = section.get("visual_nodes", [])
    edges = section.get("visual_edges", [])
    outgoing = {}
    for edge in edges:
        outgoing.setdefault(edge.get("from"), []).append(edge)
    rows = []
    for node in nodes:
        connectors = "".join(
            f'<span class="process-edge">{e(edge.get("label"))}<span aria-hidden="true"> →</span></span>'
            for edge in outgoing.get(node.get("id"), [])
        )
        rows.append(f'<li class="process-node"><strong>{e(node.get("label"))}</strong>{connectors}</li>')
    return f'<ol class="process-list">{"".join(rows)}</ol>'


def contact_panel(section, page_path: str) -> str:
    contacts = NAVIGATION["contact_defaults"]
    if page_path == "/about/" and section.get("id") == "information":
        rows = []
        for item in section.get("links", []):
            rows.append(
                f'<a class="route-row" href="{e(item.get("href"))}">'
                f'<strong>{e(item.get("label"))}</strong><span aria-hidden="true">↗</span></a>'
            )
        return f'<nav class="route-list" aria-label="Информация о компании">{"".join(rows)}</nav>'

    section_links = resolved_action_items([*section.get("cta", []), *section.get("links", [])])
    support_links = [
        {"label": contacts["phone"], "href": contacts["phoneHref"]},
        {"label": contacts["supportEmail"], "href": f'mailto:{contacts["supportEmail"]}'},
        {"label": "@infsysgroup", "href": contacts["telegram"]},
    ]
    special_links = {
        ("/partners/representatives/", "publication-of-information"): [
            {"label": contacts["officePhone"], "href": "tel:+78612011221"},
            {"label": "Контакты центрального офиса", "href": "/contacts/"},
        ],
        ("/about/careers/", "resume"): [
            {"label": contacts["officePhone"], "href": "tel:+78612011221"},
        ],
        ("/equipment/", "contact"): [
            {"label": "sales@inf-sys.ru", "href": "mailto:sales@inf-sys.ru"},
            {"label": contacts["phone"], "href": contacts["phoneHref"]},
            {"label": "Все контакты", "href": "/contacts/"},
        ],
        ("/", "support"): [support_links[0], support_links[2]],
        ("/partners/gateways/", "round-the-clock-support"): support_links,
        ("/providers/", "support"): support_links,
        ("/connect/", "existing"): support_links,
    }
    special = special_links.get((page_path, section.get("id")))
    if special is not None:
        section_links = special
    else:
        section_links = [
            item for item in section_links
            if item.get("href", "").startswith(("tel:", "mailto:")) or "t.me/" in item.get("href", "")
        ]
    if section_links:
        rows = []
        for item in section_links:
            href = item.get("href", "")
            if href.startswith("tel:"):
                label = "Телефон"
            elif href.startswith("mailto:"):
                label = "Электронная почта"
            elif "t.me/" in href:
                label = "Telegram"
            elif is_external(href):
                label = "Внешний сервис"
            else:
                label = "Раздел сайта"
            rows.append(
                f'<a href="{e(href)}"{link_attrs(href)}><small>{e(label)}</small>'
                f'<strong>{e(item.get("label"))}</strong></a>'
            )
        return (
            '<address class="contact-panel"><span class="contact-panel__eyebrow">По этому вопросу</span>'
            f'{"".join(rows)}</address>'
        )
    return (
        '<address class="contact-panel">'
        '<span class="contact-panel__eyebrow">Связаться со SkySend</span>'
        f'<a href="{e(contacts["phoneHref"])}"><small>Общий телефон</small><strong>{e(contacts["phone"])}</strong></a>'
        f'<a href="mailto:{e(contacts["supportEmail"])}"><small>Поддержка</small><strong>{e(contacts["supportEmail"])}</strong></a>'
        f'<a href="{e(contacts["telegram"])}" target="_blank" rel="noopener noreferrer"><small>Telegram</small><strong>@infsysgroup</strong></a>'
        '</address>'
    )


def partner_routes() -> str:
    tiles = []
    for item in NAVIGATION["partners"]:
        tiles.append(
            f'<a class="partner-tile" href="{e(item["href"])}">'
            f'<strong>{e(item["label"])}</strong><span aria-hidden="true">↗</span></a>'
        )
    return f'<nav class="partner-grid" aria-label="Направления для партнёров">{"".join(tiles)}</nav>'


def download_is_linkable(item) -> bool:
    target = item.get("target_url") or ""
    blocked = {
        "unsupported_browser_scheme",
        "unavailable_checked",
        "missing_url",
        "head_network_error",
        "head_http_error",
    }
    return target.startswith(("https://", "http://")) and item.get("status") not in blocked


def download_rows(items, *, compact: bool = False) -> str:
    rows = []
    chosen = items[:3] if compact else items
    for item in chosen:
        fmt = (item.get("format_from_url") or item.get("link_kind") or "файл").upper()
        size = item.get("source_size_text")
        meta = " · ".join(value for value in [fmt, size] if value)
        if download_is_linkable(item):
            label = "Открыть" if item.get("link_kind") in {"store", "page"} else "Скачать"
            target = item.get("target_url")
            action = (
                f'<a class="download-row__action" href="{e(target)}" target="_blank" '
                f'rel="noopener noreferrer">{label}<span aria-hidden="true"> ↗</span></a>'
            )
            state = "Источник доступен на дату проверки" if item.get("status") == "reachable_head" else "Ссылка из материалов SkySend"
        else:
            fallback = item.get("fallback") or {}
            action = f'<a class="download-row__action" href="{e(fallback.get("href", "/support/"))}">Поддержка →</a>'
            state = fallback.get("text", "Доступность файла уточняйте в поддержке")
        rows.append(
            f'<li class="download-row"><span class="file-badge" aria-hidden="true">{e(fmt[:4])}</span>'
            '<span class="download-row__body">'
            f'<strong>{e(item.get("display_title"))}</strong><small>{e(meta)}</small><small>{e(state)}</small></span>{action}</li>'
        )
    if not rows:
        return '<p class="empty-state">Материалы не найдены. Обратитесь в поддержку.</p>'
    note = ""
    if compact and len(items) > len(chosen):
        note = '<a class="text-link" href="/downloads/">Все материалы <span aria-hidden="true">↗</span></a>'
    return f'<div class="download-list"><ul>{"".join(rows)}</ul>{note}</div>'


def section_downloads(section, page_path: str):
    if page_path == "/downloads/":
        return DOWNLOAD_BY_GROUP.get(section.get("id"), [])
    item_ids = EXPLICIT_DOWNLOAD_ITEMS.get((page_path, section.get("id")), ())
    if item_ids:
        return [DOWNLOAD_BY_ID[item_id] for item_id in item_ids]
    collection = section.get("collection") or {}
    if collection.get("itemId"):
        item = DOWNLOAD_BY_ID.get(collection["itemId"])
        return [item] if item else []
    return []


def software_catalog() -> str:
    cards = []
    for index, page in enumerate(SOFTWARE_PAGES):
        overview = page["sections"][0]
        text = overview.get("paragraphs", [""])[0]
        visual_id = (overview.get("media") or [""])[0]
        badge = {
            "terminal-screen": "Терминал",
            "rma-desktop": "Компьютер",
            "rma-android": "Android",
            "xml-flow": "Интеграция",
            "pos-product": "POS",
            "finger-product": "Смартфон",
            "terminal-product": "Самообслуживание",
        }.get(visual_id, "ПО")
        binding = BINDINGS.get(visual_id, {})
        media_paths = binding.get("paths") or []
        media = ""
        if media_paths:
            media = (
                '<span class="software-card__media">'
                f'{image_tag(media_paths[0], binding.get("alt", ""), css="software-card__image")}</span>'
            )
        cards.append(
            f'<a class="software-card software-card--{index + 1}" href="{e(page["path"])}">'
            f'<span class="software-card__index">{e(badge)}</span>'
            f'{media}<strong>{e(page["title"])}</strong><p>{e(text)}</p>'
            '<span class="software-card__arrow" aria-hidden="true">↗</span></a>'
        )
    return f'<div class="software-grid">{"".join(cards)}</div>'


def local_equipment_image(row) -> str | None:
    name = unquote(Path(urlparse(row.get("image_url", "")).path).name)
    name = re.sub(r"_200x(?=\.)", "", name, flags=re.I)
    item = ORIGINAL_BY_NAME.get(name.lower())
    return f"assets/originals/{item.name}" if item else None


def product_cards() -> str:
    cards = []
    image_map = {
        "fastpay-beauty-ii": "assets/originals/beautyII4.png",
        "fastpay-simple": "assets/originals/FastPay Simple.png",
    }
    for product in EQUIPMENT["products"]:
        image = image_tag(image_map[product["slug"]], product["title"], css="product-card__image")
        facts = " · ".join(value for label, value in product["facts"] if label in {"Высота", "Масса"})
        cards.append(
            f'<article class="product-card"><div class="product-card__visual">{image}</div>'
            f'<div class="product-card__copy"><small>Платёжный терминал</small><h3>{e(product["title"])}</h3>'
            f'<p>{e(product["lead"])}</p><p class="product-card__facts">{e(facts)}</p>'
            f'<a class="text-link" href="{e(product["path"])}">Характеристики <span aria-hidden="true">↗</span></a></div></article>'
        )
    return f'<div class="product-grid">{"".join(cards)}</div>'


def equipment_index(section_id: str) -> str:
    if section_id == "terminals":
        return product_cards()
    categories = []
    for category in EQUIPMENT["categories"]:
        if category["path"] == "/equipment/payment-terminals/":
            continue
        count = len(category.get("rows", []))
        descriptor = f"{count} поз." if count else "По запросу"
        categories.append(
            f'<a class="category-row" href="{e(category["path"])}"><strong>{e(category["title"])}</strong>'
            f'<span>{e(descriptor)}</span><span aria-hidden="true">↗</span></a>'
        )
    return f'<nav class="category-list" aria-label="Категории оборудования">{"".join(categories)}</nav>'


def fact_object(section) -> str:
    title = clean_text(section.get("title"))
    date_match = re.match(r"^((?:\d{1,2}\s+[а-яё]+\s+)?\d{4})", title, flags=re.I)
    if date_match:
        lead = date_match.group(1)
    else:
        words = [word for word in re.split(r"\s+", title) if word]
        lead = "".join(word[0] for word in words[:2]).upper() if len(words) > 1 else title[:3]
    return (
        '<div class="fact-object" aria-hidden="true">'
        f'<span>{e(lead)}</span><small>{e(title)}</small></div>'
    )


def product_duo() -> str:
    items = [
        ("assets/originals/beautyII4.png", "FastPay Beauty II"),
        ("assets/originals/FastPay Simple.png", "FastPay Simple"),
    ]
    figures = []
    for path, name in items:
        figures.append(
            f'<a class="product-duo__item" href="/equipment/payment-terminals/{"fastpay-beauty-ii" if "Beauty" in name else "fastpay-simple"}/">'
            f'{image_tag(path, name, css="product-duo__image")}<strong>{e(name)}</strong><span>Характеристики ↗</span></a>'
        )
    return f'<div class="product-duo">{"".join(figures)}</div>'


def render_media(visual_id: str, section, page_path: str, *, eager: bool = False) -> str:
    if not visual_id:
        return ""
    if visual_id == "provider-logos":
        return provider_wall()
    if visual_id == "html-feature-list":
        return feature_list(section)
    if visual_id == "html-process":
        return process_visual(section)
    if visual_id == "partner-routes":
        return partner_routes()
    if visual_id == "contact-panel":
        return contact_panel(section, page_path)
    if visual_id == "software-catalog":
        return software_catalog()
    if visual_id == "equipment-catalog":
        return equipment_index(section.get("id", ""))
    if visual_id == "download-list":
        if page_path == "/software/" and section.get("id") == "downloads":
            return (
                '<nav class="route-list" aria-label="Материалы SkySend">'
                '<a class="route-row" href="/downloads/">'
                '<strong>Открыть каталог ПО и документации</strong><span aria-hidden="true">↗</span></a></nav>'
            )
        compact = page_path != "/downloads/" and page_path != "/system-rules/"
        return download_rows(section_downloads(section, page_path), compact=compact)
    if visual_id == "text-only":
        return fact_object(section)
    if visual_id == "html-report-fields":
        binding = BINDINGS[visual_id]
        return (
            '<div class="visual-stack">'
            f'{picture_figure(binding["paths"], binding["alt"])}{feature_list(section)}</div>'
        )
    if visual_id == "terminal-product" and page_path == "/" and section.get("id") == "equipment":
        return product_duo()
    binding = BINDINGS.get(visual_id)
    if not binding:
        return ""
    paths = binding.get("paths", [])
    if not paths or binding.get("kind") == "reference-only":
        return ""
    caption = section.get("caption")
    if visual_id in {"terminal-screen", "rma-desktop", "rma-android"}:
        caption = caption or "Интерфейс ПО SkySend"
    lightbox = visual_id in {"terminal-screen", "rma-desktop", "rma-android", "interface-variants"}
    if binding.get("kind") in {"svg", "html-and-svg"}:
        return picture_figure(paths, binding.get("alt", ""), caption=caption, lightbox=lightbox)
    return figure_image(
        paths[0],
        binding.get("alt", ""),
        caption=caption,
        lightbox=lightbox,
        eager=eager,
        css=f'media-object media-object--{e(visual_id)}',
    )


def section_visual_id(section) -> str:
    if section.get("visual_id"):
        return section["visual_id"]
    media = section.get("media") or []
    return media[0] if media else ""


def section_copy(section, *, primary_first: bool = False, include_links: bool = True) -> str:
    paragraphs = section.get("paragraphs", [])
    if section.get("body"):
        paragraphs = [section["body"]]
    body = "".join(f'<p>{e(paragraph)}</p>' for paragraph in paragraphs if paragraph)
    bullets = [] if section_visual_id(section) == "partner-routes" else section.get("bullets", [])
    bullet_html = ""
    if bullets:
        bullet_html = '<ul class="bullet-list">' + "".join(f'<li>{e(item)}</li>' for item in bullets) + "</ul>"
    links = [*section.get("cta", []), *section.get("links", [])] if include_links else []
    return f'{body}{bullet_html}{action_links(links, primary_first=primary_first)}'


def alias_anchors(section) -> str:
    return "".join(
        f'<span class="anchor-alias" id="{e(alias)}" aria-hidden="true"></span>'
        for alias in section.get("anchor_aliases", [])
    )


def render_section(section, page_path: str, index: int) -> str:
    visual_id = section_visual_id(section)
    dark = visual_id == "terminal-screen" and page_path == "/"
    full = (
        visual_id in {"software-catalog", "provider-catalog", "equipment-catalog", "download-list", "partner-routes"}
        or (page_path == "/" and section.get("id") == "equipment")
    )
    reverse = index % 2 == 1 and not full
    motion = section.get("motion_alias") or section.get("motion") or "none"
    safe_reveal_visuals = {
        "fastpay-product", "commerce-flow", "supplier-exchange",
        "xml-flow", "payment-network", "pos-product", "finger-product", "infokiosk-screen",
        "html-report-fields", "html-feature-list", "html-process", "fingerprint-scanner",
        "provider-logos",
    }
    reveal = (
        index > 0
        and motion in {"section-reveal", "process-step"}
        and visual_id in safe_reveal_visuals
    )
    classes = ["evidence-section"]
    if dark:
        classes.append("evidence-section--dark")
    if full:
        classes.append("evidence-section--full")
    if reverse:
        classes.append("evidence-section--reverse")
    if reveal:
        classes.append("reveal")
    if page_path == "/" and section.get("id") in {"commerce", "partners", "equipment"}:
        classes.append(f'evidence-section--{section["id"]}')
    media = render_media(visual_id, section, page_path)
    section_body = (
        '<div class="evidence-section__copy">'
        f'<h2>{e(section.get("title"))}</h2>'
        f'{section_copy(section, include_links=not (page_path == "/about/" and section.get("id") == "information"))}</div>'
    )
    if media:
        section_body += f'<div class="evidence-section__visual">{media}</div>'
    return (
        f'{alias_anchors(section)}<section class="{" ".join(classes)}" id="{e(section.get("id"))}"'
        f'{" data-reveal" if reveal else ""}><div class="section-shell">{section_body}</div></section>'
    )


def home_hero(section) -> str:
    visual = render_media("terminal-product", section, "/", eager=True)
    return (
        '<section class="home-hero" id="hero"><div class="home-hero__shell">'
        '<div class="home-hero__copy">'
        f'<h1>{e(section["title"])}</h1>{action_links(section.get("cta", []), primary_first=True)}</div>'
        f'<div class="home-hero__visual">{visual}</div>'
        '</div></section>'
    )


def family_label(path: str) -> str:
    if path.startswith("/partners/"):
        return "Партнёрам"
    if path.startswith("/software/"):
        return "Программное обеспечение"
    if path.startswith("/equipment/"):
        return "Оборудование"
    if path.startswith("/about/"):
        return "О системе"
    if path == "/providers/":
        return "Каталог"
    if path == "/downloads/":
        return "Материалы"
    return "SkySend"


def page_hero(page) -> str:
    cta = [page["primary_cta"]] if page.get("primary_cta") else []
    sections = page.get("sections", [])
    jumps = ""
    if len(sections) > 3:
        links = "".join(
            f'<a href="#{e(section["id"])}">{e(section["title"])}</a>' for section in sections
        )
        jumps = f'<nav class="jump-nav" aria-label="Разделы страницы">{links}</nav>'
    return (
        '<section class="page-hero"><div class="page-hero__shell">'
        f'<p class="eyebrow">{e(family_label(page["path"]))}</p><h1>{e(page["title"])}</h1>'
        f'<p class="page-hero__lead">{e(page.get("lead", ""))}</p>{action_links(cta, primary_first=True)}'
        f'{jumps}</div></section>'
    )


def software_detail_hero(page, section) -> str:
    visual_id = section_visual_id(section)
    dark = visual_id == "terminal-screen"
    visual = render_media(visual_id, section, page["path"], eager=True)
    classes = "detail-hero detail-hero--dark" if dark else "detail-hero"
    return (
        f'{alias_anchors(section)}<section class="{classes}" id="{e(section["id"])}">'
        '<div class="detail-hero__shell"><div class="detail-hero__copy">'
        f'<p class="eyebrow">{e(page["title"])}</p>'
        f'<h1>{e(section.get("title") or page["title"])}</h1>'
        f'{section_copy(section, primary_first=True)}</div>'
        f'<div class="detail-hero__visual">{visual}</div></div></section>'
    )


def product_detail_hero(product, image_path: str) -> str:
    facts = dict(product.get("facts", []))
    visual = figure_image(
        image_path,
        product["title"],
        eager=True,
        css="product-hero__image",
    )
    dimensions = (
        '<div class="dimensioned-product">'
        f'{visual}<span class="dimension dimension--height"><small>Высота</small><strong>{e(facts.get("Высота"))}</strong></span>'
        f'<span class="dimension dimension--width"><small>Ширина</small><strong>{e(facts.get("Ширина"))}</strong></span></div>'
    )
    return (
        '<section class="product-hero"><div class="product-hero__shell">'
        '<div class="product-hero__copy"><p class="eyebrow">Оборудование</p>'
        f'<h1>{e(product["title"])}</h1><p>{e(product["lead"])}</p>'
        f'{action_links([product["cta"]], primary_first=True)}</div>'
        f'<div class="product-hero__visual">{dimensions}</div></div></section>'
    )


def header(path: str) -> str:
    partner_submenu = "".join(
        f'<a href="{e(item["href"])}">{e(item["label"])}</a>' for item in NAVIGATION["partners"]
    )
    desktop_links = []
    for item in NAVIGATION["primary"]:
        if item.get("children") == "partners":
            current = ' aria-current="page"' if path.startswith("/partners/") else ""
            desktop_links.append(
                '<details class="nav-partners" data-partner-menu>'
                f'<summary{current}>Партнёрам</summary><div class="nav-partners__panel">{partner_submenu}</div></details>'
            )
            continue
        active = path == item["href"] or (item["href"] != "/" and path.startswith(item["href"]))
        current = ' aria-current="page"' if active else ""
        desktop_links.append(f'<a href="{e(item["href"])}"{current}>{e(item["label"])}</a>')
    mobile_primary = "".join(
        f'<a href="{e(item["href"])}">{e(item["label"])}</a>'
        for item in NAVIGATION["primary"] if item.get("children") != "partners"
    )
    mobile_extra = "".join(
        f'<a href="{e(item["href"])}">{e(item["label"])}</a>' for item in NAVIGATION["footer"][:4]
        if item["label"] != "ПО"
    )
    actions = NAVIGATION["actions"]
    fallback_links = "".join(
        f'<a href="{e(item["href"])}">{e(item["label"])}</a>' for item in NAVIGATION["primary"]
    )
    return (
        '<div id="top-sentinel" aria-hidden="true"></div><a class="skip-link" href="#main">К содержанию</a>'
        '<header class="site-header" data-header><div class="site-header__shell">'
        '<a class="brand" href="/" aria-label="SkySend, главная">'
        '<img src="/assets/brand/skysend-logo.svg" width="100" height="64" alt="SkySend"></a>'
        f'<nav class="desktop-nav" aria-label="Основная навигация">{"".join(desktop_links)}</nav>'
        '<div class="header-actions">'
        f'<a class="header-login" href="{e(actions[0]["href"])}">{e(actions[0]["label"])}</a>'
        f'<a class="button button--primary button--compact" href="{e(actions[1]["href"])}">{e(actions[1]["label"])}</a>'
        '</div><button class="menu-trigger" type="button" data-menu-open aria-controls="site-menu" aria-expanded="false">'
        '<span>Меню</span><img src="/assets/icons/menu.svg" width="24" height="24" alt=""></button>'
        '</div></header>'
        f'<nav class="fallback-nav" aria-label="Основная навигация без JavaScript">{fallback_links}</nav>'
        '<dialog class="site-menu" id="site-menu" aria-labelledby="menu-title"><div class="site-menu__panel">'
        '<div class="site-menu__head"><strong id="menu-title">Навигация</strong>'
        '<button type="button" class="icon-button" data-menu-close aria-label="Закрыть меню">'
        '<img src="/assets/icons/close.svg" width="24" height="24" alt=""></button></div>'
        '<nav class="mobile-nav" aria-label="Мобильная навигация"><details><summary>Партнёрам</summary>'
        f'<div>{partner_submenu}</div></details>{mobile_primary}<div class="mobile-nav__secondary">{mobile_extra}</div>'
        f'<a href="{e(actions[0]["href"])}">{e(actions[0]["label"])}</a>'
        f'<a class="button button--primary" href="{e(actions[1]["href"])}">{e(actions[1]["label"])}</a>'
        '</nav></div></dialog>'
    )


def footer() -> str:
    contacts = NAVIGATION["contact_defaults"]
    nav_links = "".join(
        f'<a href="{e(item["href"])}">{e(item["label"])}</a>' for item in NAVIGATION["footer"]
    )
    return (
        '<footer class="site-footer"><div class="site-footer__shell">'
        '<div class="site-footer__brand"><img src="/assets/brand/skysend-logo.svg" width="100" height="64" alt="SkySend">'
        '<p>Система приёма платежей и программное обеспечение для устройств самообслуживания.</p></div>'
        f'<nav aria-label="Разделы сайта">{nav_links}</nav>'
        '<address><small>Связаться</small>'
        f'<a href="{e(contacts["phoneHref"])}">{e(contacts["phone"])}</a>'
        f'<a href="mailto:{e(contacts["supportEmail"])}">{e(contacts["supportEmail"])}</a>'
        f'<a href="{e(contacts["telegram"])}" target="_blank" rel="noopener noreferrer">Telegram @infsysgroup</a></address>'
        '</div><div class="site-footer__bottom"><span>ООО «СкайСенд»</span>'
        '<span>Информация и файлы собраны из материалов SkySend</span></div></footer>'
    )


def media_dialog() -> str:
    return (
        '<dialog class="media-dialog" id="media-dialog" aria-labelledby="media-dialog-title">'
        '<div class="media-dialog__bar"><p id="media-dialog-title">Просмотр изображения</p>'
        '<button class="icon-button icon-button--light" type="button" data-lightbox-close aria-label="Закрыть изображение">'
        '<img src="/assets/icons/close.svg" width="24" height="24" alt=""></button></div>'
        '<div class="media-dialog__viewport"><img data-lightbox-image src="" alt=""></div>'
        '<p class="media-dialog__caption" data-lightbox-caption>Экран из материалов действующего сайта. Внешний вид зависит от версии и настроек ПО.</p>'
        '</dialog>'
    )


def document(title: str, path: str, main: str, *, description: str = "") -> str:
    page_title = "SkySend" if path == "/" else f"{title} | SkySend"
    canonical = BASE_URL + path
    description = clean_text(description)[:180] or "Публичный сайт платёжной системы SkySend."
    return f'''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(page_title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{e(canonical)}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ru_RU">
  <meta property="og:title" content="{e(page_title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{e(canonical)}">
  <link rel="icon" href="/assets/brand/skysend-logo.svg" type="image/svg+xml">
  <link rel="preload" href="/assets/fonts/InterVariable.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/design-tokens.css">
  <link rel="stylesheet" href="/static/styles.css">
  <script>document.documentElement.classList.add('js')</script>
</head>
<body data-path="{e(path)}">
  {header(path)}
  <main id="main" tabindex="-1">{main}</main>
  {footer()}
  {media_dialog()}
  <script src="/static/app.js" defer></script>
</body>
</html>
'''


def render_content_page(page) -> str:
    path = page["path"]
    if path == "/":
        sections = page["sections"]
        main = home_hero(sections[0])
        main += "".join(render_section(section, path, index) for index, section in enumerate(sections[1:], 1))
        description = clean_text((sections[0].get("paragraphs") or [sections[0]["title"]])[0])
    elif page.get("template") == "software-detail":
        first, *rest = page["sections"]
        main = software_detail_hero(page, first)
        main += "".join(render_section(section, path, index) for index, section in enumerate(rest, 1))
        description = clean_text((first.get("paragraphs") or [""])[0])
    elif path == "/providers/":
        main = page_hero(page) + provider_catalog_section(page["sections"][0])
        main += render_section(page["sections"][1], path, 1)
        description = page["lead"]
    else:
        main = page_hero(page)
        main += "".join(render_section(section, path, index) for index, section in enumerate(page.get("sections", [])))
        description = page.get("lead") or clean_text((page.get("sections") or [{}])[0].get("paragraphs", [""])[0])
    return document(page["title"], path, main, description=description)


def provider_logo_path(provider) -> str | None:
    match = re.search(r"[?&]provider=(\d+)", provider.get("logo_url", ""))
    if not match:
        return None
    path = f"assets/originals/providers/provider-{match.group(1)}.png"
    return path if (ROOT / path).exists() else None


def provider_card(provider) -> str:
    path = provider_logo_path(provider)
    if path:
        visual = image_tag(path, "", css="provider-card__logo")
    else:
        initials = "".join(word[0] for word in re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", provider["name"])[:2]).upper()
        visual = f'<span class="provider-card__fallback" aria-hidden="true">{e(initials or "SS")}</span>'
    return (
        f'<li class="provider-card">{visual}<span><strong>{e(provider["name"])}</strong>'
        f'<small>{e(provider["category"])}</small></span></li>'
    )


def provider_catalog_section(section) -> str:
    present_categories = {provider["category_id"] for provider in PROVIDERS["providers"]}
    categories = {
        key: value for key, value in PROVIDERS["categories"].items() if key in present_categories
    }
    chips = ['<button type="button" class="filter-chip is-active" data-provider-category="all" aria-pressed="true">Все</button>']
    chips.extend(
        f'<button type="button" class="filter-chip" data-provider-category="{e(key)}" aria-pressed="false">{e(value)}</button>'
        for key, value in categories.items()
    )
    initial = SORTED_PROVIDERS[:30]
    cards = "".join(provider_card(item) for item in initial)
    return (
        f'<section class="provider-catalog" id="{e(section["id"])}" data-provider-app>'
        '<div class="provider-catalog__shell"><div class="provider-catalog__head">'
        f'<h2>{e(section["title"])}</h2>'
        f'<p class="catalog-date">{e(section.get("body") or "Данные каталога SkySend от 10 сентября 2026 года.")}</p></div>'
        '<form class="provider-controls" data-provider-form role="search"><label for="provider-search">Поиск по названию</label>'
        '<div class="search-field"><input id="provider-search" name="q" type="search" autocomplete="off" '
        'placeholder="Например, МТС" data-provider-search><button type="button" data-provider-reset>Сбросить</button></div>'
        f'<div class="filter-chips" aria-label="Категории">{"".join(chips)}</div></form>'
        '<div class="provider-results-head"><p aria-live="polite" tabindex="-1" data-provider-count>Показано 30 из 600</p>'
        '<p>Доступность услуги уточняйте в службе поддержки.</p></div>'
        f'<ul class="provider-grid" data-provider-results>{cards}</ul>'
        '<div class="provider-empty" data-provider-empty hidden><p>По вашему запросу ничего не найдено</p>'
        '<button class="button button--secondary" type="button" data-provider-reset>Сбросить фильтры</button></div>'
        '<nav class="pagination" aria-label="Страницы каталога" data-provider-pages></nav>'
        '<noscript><p class="no-script-note">Показаны первые 30 записей. Для поиска и фильтрации включите JavaScript.</p></noscript>'
        '</div></section>'
    )


def render_equipment_category(category) -> str:
    path = category["path"]
    lead = "Модели и комплектующие из материалов SkySend. Цены и наличие уточняйте у менеджера."
    page = {"path": path, "title": category["title"], "lead": lead, "sections": []}
    rows = []
    detail_paths = {product["slug"]: product["path"] for product in EQUIPMENT["products"]}
    for row in category.get("rows", []):
        image_path = local_equipment_image(row)
        visual = image_tag(image_path, row["name"], css="catalog-item__image") if image_path else '<span class="catalog-item__placeholder" aria-hidden="true">SS</span>'
        detail = detail_paths.get("fastpay-beauty-ii" if row["id"] == "fastpay-beauty-1" else row["id"])
        title = f'<a href="{e(detail)}">{e(row["name"])}</a>' if detail else e(row["name"])
        rows.append(
            f'<article class="catalog-item" id="{e(row["id"])}"><div class="catalog-item__visual">{visual}</div>'
            f'<div class="catalog-item__copy"><h2>{title}</h2><p>{e(row.get("description"))}</p>'
            f'{action_links([row["public_cta"]])}</div></article>'
        )
    empty = ""
    if not rows:
        empty = (
            '<div class="catalog-empty"><p>' + e(category.get("empty_copy") or "Состав и условия поставки уточняйте у менеджера.") + '</p>'
            '<a class="text-link" href="/contacts/">Связаться с менеджером ↗</a></div>'
        )
    body = page_hero(page) + f'<section class="catalog-page"><div class="catalog-page__shell">{"".join(rows)}{empty}</div></section>'
    return document(category["title"], path, body, description=lead)


def render_equipment_product(product) -> str:
    path = product["path"]
    image_path = "assets/originals/beautyII4.png" if product["slug"] == "fastpay-beauty-ii" else "assets/originals/FastPay Simple.png"
    facts = "".join(f'<tr><th scope="row">{e(label)}</th><td>{e(value)}</td></tr>' for label, value in product["facts"])
    config = "".join(f'<li>{e(item)}</li>' for item in product["base_configuration"])
    limits = "".join(f'<li>{e(item)}</li>' for item in product.get("source_limits", []))
    body = product_detail_hero(product, image_path)
    body += (
        '<section class="product-detail"><div class="product-detail__shell product-detail__shell--spec">'
        f'<div class="product-detail__spec"><h2>Характеристики</h2><table><tbody>{facts}</tbody></table>'
        f'<p class="caption">{e(product["specification_caption"])}</p></div></div></section>'
        '<section class="evidence-section"><div class="section-shell"><div class="evidence-section__copy">'
        '<h2>Базовая комплектация</h2><p>Перечень из материалов SkySend.</p>'
        f'{action_links([product["cta"]])}</div><div class="evidence-section__visual"><ul class="spec-list">{config}</ul></div></div></section>'
        '<section class="product-notes"><div><h2>Уточнения по исходным данным</h2>'
        f'<ul>{limits}</ul></div></section>'
    )
    return document(product["title"], path, body, description=product["lead"])


def error_page(status: int) -> str:
    if status == 410:
        title = "Материал больше не доступен"
        body = "Перейдите к информации о системе SkySend."
    else:
        title = "Страница не найдена"
        body = "Проверьте адрес или откройте нужный раздел сайта."
    main = (
        '<section class="error-page"><div><p class="error-code">' + str(status) + '</p>'
        f'<h1>{e(title)}</h1><p>{e(body)}</p>'
        '<div class="actions"><a class="button button--primary" href="/">На главную</a>'
        '<a class="text-link" href="/support/">Поддержка ↗</a></div></div></section>'
    )
    return document(title, f"/{status}.html", main, description=body)


def copy_production_assets() -> set[str]:
    copied: set[str] = set()
    for folder in ["brand", "fonts", "icons", "diagrams", "ready"]:
        source = ASSETS / folder
        target = DIST / "assets" / folder
        shutil.copytree(source, target, dirs_exist_ok=True)
        for file in target.rglob("*"):
            if file.is_file():
                copied.add(file.relative_to(DIST).as_posix())
    shutil.copy2(ASSETS / "design-tokens.css", DIST / "assets" / "design-tokens.css")
    copied.add("assets/design-tokens.css")

    originals = {
        "beautyII4.png", "FastPay Simple.png", "RMA_android.jpg", "RMA_win_lin.png",
        "scaner.png", "17.png", "17bu.png", "apro.png", "atx_300.png", "CashCode_MVU_bu.png",
        "CashCode_MVU.png", "CashCode_SM.png", "CashCode_SM8.png", "ddr3.png", "fiskalniy-server.png",
        "ide.png", "keetouch.png", "mini_itx.png", "pay.png", "siemens.png", "term.png",
        "termoprinter.png", "usb.png", "vkp_pow.png",
    }
    target_originals = DIST / "assets" / "originals"
    target_originals.mkdir(parents=True, exist_ok=True)
    for name in sorted(originals):
        source = ASSETS / "originals" / name
        if source.exists():
            shutil.copy2(source, target_originals / name)
            copied.add(f"assets/originals/{name}")
    provider_source = ASSETS / "originals" / "providers"
    provider_target = target_originals / "providers"
    shutil.copytree(provider_source, provider_target, dirs_exist_ok=True)
    for file in provider_target.glob("*"):
        copied.add(file.relative_to(DIST).as_posix())
    return copied


def build_provider_data() -> None:
    rows = []
    for provider in SORTED_PROVIDERS:
        rows.append({
            "name": provider["name"],
            "category_id": provider["category_id"],
            "category": provider["category"],
            "logo": asset_url(provider_logo_path(provider)) if provider_logo_path(provider) else None,
        })
    data_dir = DIST / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "providers.json").write_text(
        json.dumps({"count": len(rows), "providers": rows}, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def build_migration_files() -> dict[str, int]:
    redirects = {}
    gone = set()
    seen_sources: dict[str, str] = {}
    with (DATA / "migration-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            status = str(row.get("http_action", "")).strip()
            old_url = row.get("old_url", "")
            source = urlparse(old_url).path or "/"
            if status in {"301", "410"} and source in seen_sources:
                raise ValueError(
                    f"Legacy URL path collision for {source}: {seen_sources[source]} and {old_url}. "
                    "Nginx locations cannot distinguish query strings."
                )
            if status in {"301", "410"}:
                seen_sources[source] = old_url
            if status == "301":
                redirects[source] = row.get("new_url", "")
            elif status == "410":
                gone.add(source)
    deploy = ROOT / "deploy"
    deploy.mkdir(exist_ok=True)
    locations = [
        "# Generated from data/migration-map.csv. Include in every public server block before broad redirects."
    ]
    for source, target in sorted(redirects.items()):
        if source == "/":
            continue
        escaped_source = source.replace("\\", "\\\\").replace('"', '\\"')
        escaped_target = (BASE_URL + target).replace("\\", "\\\\").replace('"', '\\"')
        locations.append(f'location = "{escaped_source}" {{ return 301 "{escaped_target}"; }}')
    for source in sorted(gone):
        escaped_source = source.replace("\\", "\\\\").replace('"', '\\"')
        locations.append(f'location = "{escaped_source}" {{ return 410; }}')
    (deploy / "legacy-locations.inc").write_text("\n".join(locations) + "\n", encoding="utf-8")
    static_redirects = [f"{source} {target} 301" for source, target in sorted(redirects.items()) if source != "/"]
    (DIST / "_redirects").write_text("\n".join(static_redirects) + "\n", encoding="utf-8")
    return {"redirects": len(redirects), "gone": len(gone)}


def build_sitemap(paths: list[str]) -> None:
    urls = "".join(f"  <url><loc>{e(BASE_URL + path)}</loc></url>\n" for path in sorted(paths))
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")


def build() -> dict:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "static").mkdir()
    shutil.copy2(SITE / "static" / "styles.css", DIST / "static" / "styles.css")
    shutil.copy2(SITE / "static" / "app.js", DIST / "static" / "app.js")
    copied = copy_production_assets()
    build_provider_data()

    canonical_paths = []
    for page in PAGES:
        output = route_output(page["path"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_content_page(page), encoding="utf-8")
        canonical_paths.append(page["path"])
    for category in EQUIPMENT["categories"]:
        output = route_output(category["path"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_equipment_category(category), encoding="utf-8")
        canonical_paths.append(category["path"])
    for product in EQUIPMENT["products"]:
        output = route_output(product["path"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_equipment_product(product), encoding="utf-8")
        canonical_paths.append(product["path"])

    (DIST / "404.html").write_text(error_page(404), encoding="utf-8")
    (DIST / "410.html").write_text(error_page(410), encoding="utf-8")
    migration = build_migration_files()
    build_sitemap(canonical_paths)
    digest = hashlib.sha256()
    for file in sorted(DIST.rglob("*")):
        if file.is_file():
            digest.update(file.relative_to(DIST).as_posix().encode())
            digest.update(file.read_bytes())
    manifest = {
        "routes": len(canonical_paths),
        "html_files": len(list(DIST.rglob("*.html"))),
        "provider_rows": len(PROVIDERS["providers"]),
        "download_rows": len(DOWNLOADS["items"]),
        "copied_assets": len(copied),
        "external_accounts_verified": EXTERNAL_ACCOUNTS_VERIFIED,
        "external_account_links_emitted": sum(
            file.read_text(encoding="utf-8").count(account.get("href", ""))
            for file in DIST.rglob("*.html")
            for key, account in NAVIGATION.get("external_accounts", {}).items()
            if key in {"registration", "login"} and isinstance(account, dict)
        ),
        **migration,
        "sha256": digest.hexdigest(),
    }
    (DIST / "build-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
