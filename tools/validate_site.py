#!/usr/bin/env python3
"""Static acceptance checks for the generated SkySend site."""

from __future__ import annotations

import csv
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DATA = ROOT / "data"
BASE_URL = "https://skysend.ru"
EXPECT_EXTERNAL_ACCOUNTS = os.environ.get("SKYSEND_EXTERNAL_ACCOUNTS_VERIFIED") == "1"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.lang = None
        self.ids: list[str] = []
        self.links: list[str] = []
        self.assets: list[str] = []
        self.img_without_alt = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "html":
            self.lang = values.get("lang")
        if tag == "h1":
            self.h1 += 1
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag in {"img", "script", "link", "source"}:
            source = values.get("src") or values.get("href") or values.get("srcset")
            if source:
                self.assets.append(source.split()[0])
        if tag == "img" and "alt" not in values:
            self.img_without_alt += 1


def html_path_for_route(route: str) -> Path:
    route = unquote(route)
    if route == "/":
        return DIST / "index.html"
    if route.endswith(".html"):
        return DIST / route.lstrip("/")
    return DIST / route.strip("/") / "index.html"


def fail(errors: list[str], message: str):
    errors.append(message)


def section_markup(path: Path, section_id: str) -> str:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf'<section\b[^>]*\bid="{re.escape(section_id)}"[^>]*>.*?</section>',
        text,
        flags=re.S,
    )
    return match.group(0) if match else ""


def download_titles(markup: str) -> list[str]:
    return [
        html.unescape(re.sub(r"<[^>]+>", "", value)).strip()
        for value in re.findall(r'<li class="download-row">.*?<strong>(.*?)</strong>', markup, flags=re.S)
    ]


def main() -> int:
    errors: list[str] = []
    pages: dict[str, PageParser] = {}
    html_files = sorted(DIST.rglob("*.html"))
    if not html_files:
        fail(errors, "dist has no HTML files; run python site/build.py")

    for file in html_files:
        parser = PageParser()
        text = file.read_text(encoding="utf-8")
        try:
            parser.feed(text)
        except Exception as exc:
            fail(errors, f"{file.relative_to(DIST)}: HTML parser error: {exc}")
        relative = file.relative_to(DIST).as_posix()
        route = "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")
        if relative in {"404.html", "410.html"}:
            route = "/" + relative
        pages[route] = parser
        if parser.lang != "ru":
            fail(errors, f"{relative}: lang must be ru")
        if parser.h1 != 1:
            fail(errors, f"{relative}: expected one h1, found {parser.h1}")
        duplicates = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
        if duplicates:
            fail(errors, f"{relative}: duplicate ids {duplicates}")
        if parser.img_without_alt:
            fail(errors, f"{relative}: {parser.img_without_alt} img elements without alt")
        if "<main id=\"main\"" not in text or "К содержанию" not in text:
            fail(errors, f"{relative}: missing main or skip link")
        if relative not in {"404.html", "410.html"} and "fallback-nav" not in text:
            fail(errors, f"{relative}: missing no-JavaScript fallback navigation")

    for route, parser in pages.items():
        source_file = html_path_for_route(route)
        for href in parser.links:
            parsed = urlparse(href)
            if parsed.scheme or href.startswith(("mailto:", "tel:", "#")):
                if href.startswith("#") and href[1:] not in parser.ids:
                    fail(errors, f"{source_file.relative_to(DIST)}: missing local anchor {href}")
                continue
            target_route = parsed.path or route
            target_asset = DIST / unquote(target_route.lstrip("/"))
            if target_asset.is_file():
                continue
            target_file = html_path_for_route(target_route)
            if not target_file.exists():
                fail(errors, f"{source_file.relative_to(DIST)}: missing internal target {href}")
                continue
            if parsed.fragment:
                target_parser = pages.get(target_route)
                if target_parser and parsed.fragment not in target_parser.ids:
                    fail(errors, f"{source_file.relative_to(DIST)}: missing target anchor {href}")
        for asset in parser.assets:
            parsed = urlparse(asset)
            if parsed.scheme or not parsed.path.startswith("/"):
                continue
            target = DIST / unquote(parsed.path.lstrip("/"))
            if not target.exists():
                fail(errors, f"{source_file.relative_to(DIST)}: missing asset {asset}")

    with (DATA / "migration-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        migration = list(csv.DictReader(handle))
    expected_nginx: dict[str, tuple[str, str | None]] = {}
    expected_static: dict[str, tuple[str, str]] = {}
    for row in migration:
        action = row["http_action"]
        source = urlparse(row["old_url"]).path or "/"
        target = row["new_url"]
        if action == "301":
            if source in expected_nginx:
                fail(errors, f"duplicate legacy path after query removal: {source}")
            expected_nginx[source] = ("301", BASE_URL + target)
            if source != "/":
                expected_static[source] = (target, "301")
            parsed = urlparse(target)
            target_file = html_path_for_route(parsed.path)
            if not target_file.exists():
                fail(errors, f"301 target does not exist: {target}")
            if parsed.fragment:
                target_parser = pages.get(parsed.path)
                if target_parser and parsed.fragment not in target_parser.ids:
                    fail(errors, f"301 target anchor does not exist: {target}")
        elif action == "410":
            if source in expected_nginx:
                fail(errors, f"duplicate legacy path after query removal: {source}")
            expected_nginx[source] = ("410", None)

    snippet = (ROOT / "deploy" / "legacy-locations.inc").read_text(encoding="utf-8")
    location_pattern = re.compile(
        r'^location = "(?P<source>[^"]+)" \{ return (?P<status>301|410)(?: "(?P<target>[^"]+)")?; \}$'
    )
    actual_nginx: dict[str, tuple[str, str | None]] = {}
    for line in snippet.splitlines():
        if not line.startswith("location = "):
            continue
        match = location_pattern.fullmatch(line)
        if not match:
            fail(errors, f"invalid nginx legacy rule: {line}")
            continue
        source = match.group("source")
        if source in actual_nginx:
            fail(errors, f"duplicate nginx source: {source}")
        actual_nginx[source] = (match.group("status"), match.group("target"))
    if actual_nginx != expected_nginx:
        for source in sorted(set(expected_nginx) | set(actual_nginx)):
            if actual_nginx.get(source) != expected_nginx.get(source):
                fail(
                    errors,
                    f"nginx rule mismatch for {source}: expected {expected_nginx.get(source)}, got {actual_nginx.get(source)}",
                )

    actual_static: dict[str, tuple[str, str]] = {}
    for line in (DIST / "_redirects").read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) != 3:
            fail(errors, f"invalid static redirect rule: {line}")
            continue
        source, target, status = parts
        if source in actual_static:
            fail(errors, f"duplicate static redirect source: {source}")
        actual_static[source] = (target, status)
    if actual_static != expected_static:
        for source in sorted(set(expected_static) | set(actual_static)):
            if actual_static.get(source) != expected_static.get(source):
                fail(
                    errors,
                    f"static redirect mismatch for {source}: expected {expected_static.get(source)}, got {actual_static.get(source)}",
                )

    hosting = json.loads((ROOT / ".openai" / "hosting.json").read_text(encoding="utf-8"))
    if hosting.get("static", {}).get("not_found_handling") != "404-page":
        fail(errors, "Sites hosting must serve the generated branded 404 page")

    public_external_accounts = [
        "https://cluster.skysend.ru:6716/#/",
        "https://control.skysend.ru:6710",
    ]
    public_text = "\n".join(file.read_text(encoding="utf-8") for file in html_files)
    if '<button class="media-open"' in public_text:
        fail(errors, "lightbox control must remain an ordinary asset link without JavaScript")
    lightbox_links = re.findall(r'<a class="media-open" href="([^"]+)" data-lightbox-src="([^"]+)"', public_text)
    if not lightbox_links or any(href != source for href, source in lightbox_links):
        fail(errors, "lightbox links must have matching no-JavaScript asset hrefs")
    css_text = (ROOT / "site" / "static" / "styles.css").read_text(encoding="utf-8")
    if not re.search(r"(?m)^\.menu-trigger\s*\{\s*display:\s*none;", css_text):
        fail(errors, "menu trigger must be hidden when JavaScript is unavailable")
    home_equipment = section_markup(html_path_for_route("/"), "equipment")
    if re.match(r'<section\b[^>]*\bdata-reveal\b', home_equipment):
        fail(errors, "home equipment links must not be hidden by reveal animation")
    home_text = html_path_for_route("/").read_text(encoding="utf-8")
    home_commerce = section_markup(html_path_for_route("/"), "commerce")
    home_partners = section_markup(html_path_for_route("/"), "partners")
    if '<span class="section-index">' in public_text:
        fail(errors, "decorative section numbering must not be rendered")
    if 'class="process-node__number"' in public_text:
        fail(errors, "decorative process numbering must not be rendered")
    for removed_copy in (
        "Платёжная система SkySend",
        "SkySend предоставляет возможность совершать оплаты в пользу более 5 000 поставщиков услуг.",
        "Примеры из каталога SkySend. Доступность услуги уточняйте в поддержке.",
        "Варианты интерфейса из материалов SkySend",
    ):
        if removed_copy in home_text:
            fail(errors, f"removed home copy is still rendered: {removed_copy}")
    if (
        '<span class="media-open__label">' in public_text
        or '>Увеличить</' in public_text
        or '>Далее<' in public_text
    ):
        fail(errors, "visible enlarge controls must not be rendered")
    if 'id="support"' in home_text:
        fail(errors, "home support section must be removed")
    if "<h2>SkyMarket</h2>" not in home_commerce:
        fail(errors, "home commerce section must be titled SkyMarket")
    for label in ("Загрузка справочника товаров", "Формирование заказов", "Оплата заказов"):
        if label not in home_commerce:
            fail(errors, f"SkyMarket feature missing: {label}")
    if home_partners.count('class="partner-tile"') != 6:
        fail(errors, "home partners section must contain six clickable tiles")
    if ">Оборудование<" in home_equipment:
        fail(errors, "home equipment section must not contain the generic equipment link")
    if (DIST / "partners" / "index.html").exists():
        fail(errors, "standalone partners index must not be generated")
    emitted_external_accounts = sum(public_text.count(href) for href in public_external_accounts)
    for href in public_external_accounts:
        present = href in public_text
        if EXPECT_EXTERNAL_ACCOUNTS and not present:
            fail(errors, f"verified external account link missing: {href}")
        if not EXPECT_EXTERNAL_ACCOUNTS and present:
            fail(errors, f"unverified external account link was published: {href}")

    software_titles = {
        "/software/terminal/": "Терминальное ПО",
        "/software/rma-desktop/": "ПО приёма платежей для кассира",
        "/software/rma-android/": "ПО приёма платежей для смартфонов",
        "/software/xml/": "Подключение по XML-протоколу",
        "/software/pos/": "Программное обеспечение для POS-терминала",
        "/software/finger/": "Приложение FINGER для смартфонов",
        "/software/allvend/": "ПО ALLVEND для систем самообслуживания",
    }
    for route, title in software_titles.items():
        page_text = html_path_for_route(route).read_text(encoding="utf-8")
        if f"<h1>{title}</h1>" not in page_text:
            fail(errors, f"{route}: missing approved software hero title {title}")

    expected_download_sections = {
        ("/software/terminal/", "flash"): [
            "Инструкция по организации прошивочной системы и программированию накопителей для ОС Windows",
            "Совместимые накопители",
        ],
        ("/software/xml/", "protocol"): ["Описание протокола SkyTransact"],
        ("/software/pos/", "start"): ["ПО для POS-терминала Штрих-Mobile Pay PRO - Версия 1.1 (7 Mb)"],
        ("/support/", "downloads"): [
            'Приложение "Рабочее место Агента для ОС Windows"',
            "Установка и эксплуатация РМА Windows",
            "Регламент работы службы поддержки",
        ],
        ("/connect/", "documents"): [
            "Правила системы SkySend",
            "Договор присоединения Агента к системе SkySend",
            "Договор с Провайдером",
        ],
        ("/system-rules/", "document"): ["Правила системы SkySend"],
    }
    for (route, section_id), expected_titles in expected_download_sections.items():
        markup = section_markup(html_path_for_route(route), section_id)
        if not markup:
            fail(errors, f"{route}#{section_id}: section missing")
            continue
        actual_titles = download_titles(markup)
        if actual_titles != expected_titles:
            fail(errors, f"{route}#{section_id}: downloads expected {expected_titles}, got {actual_titles}")

    report_markup = section_markup(html_path_for_route("/partners/providers/"), "automate-reporting")
    for label in ["Период отчёта", "Реестр платежей", "Выгрузка в систему учёта", "Сверка отчётности"]:
        if label not in report_markup:
            fail(errors, f"provider reporting visual missing field: {label}")

    for route, height in [
        ("/equipment/payment-terminals/fastpay-beauty-ii/", "145 см"),
        ("/equipment/payment-terminals/fastpay-simple/", "144 см"),
    ]:
        page_text = html_path_for_route(route).read_text(encoding="utf-8")
        if "dimension--height" not in page_text or height not in page_text or "Ширина" not in page_text:
            fail(errors, f"{route}: missing factual width/height treatment")

    forbidden_copy = [
        r"Это не просто",
        r"В современном мире",
        r"Независимо от того",
        r"автопробег",
        r"Предложение Рекламодателям",
        r"Как увеличить доходность терминалов",
    ]
    for pattern in forbidden_copy:
        if re.search(pattern, public_text, flags=re.I):
            fail(errors, f"forbidden public copy matched: {pattern}")
    forbidden_assets = ["banf.png", "allvend.png", "pop-up-full.jpg", "cluster_skysend.jpeg"]
    for name in forbidden_assets:
        if list(DIST.rglob(name)):
            fail(errors, f"forbidden/review-only asset copied: {name}")

    manifest = json.loads((DIST / "build-manifest.json").read_text(encoding="utf-8"))
    expected = {"routes": 42, "provider_rows": 600, "download_rows": 66, "redirects": 135, "gone": 13}
    for key, value in expected.items():
        if manifest.get(key) != value:
            fail(errors, f"manifest {key}: expected {value}, got {manifest.get(key)}")
    if manifest.get("external_accounts_verified") is not EXPECT_EXTERNAL_ACCOUNTS:
        fail(errors, f"manifest external account mode does not match validation mode: {EXPECT_EXTERNAL_ACCOUNTS}")
    if manifest.get("external_account_links_emitted") != emitted_external_accounts:
        fail(errors, "manifest external account link count does not match generated HTML")

    if errors:
        print(f"FAILED: {len(errors)} issues")
        for error in errors[:100]:
            print(f"- {error}")
        return 1
    print(
        f"OK: {manifest['routes']} routes, {manifest['html_files']} HTML files, "
        f"{manifest['provider_rows']} providers, {manifest['download_rows']} downloads, "
        f"{manifest['redirects']} redirects, {manifest['gone']} gone routes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
