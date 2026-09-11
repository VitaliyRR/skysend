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
ROUTE_ALIASES = {
    "/partners/": "/partners/agents/",
    "/software/": "/software/terminal/",
    "/software/rma-desktop/": "/software/rma/",
    "/software/rma-android/": "/software/rma/",
}


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
        if route in ROUTE_ALIASES:
            target = ROUTE_ALIASES[route]
            if 'http-equiv="refresh"' not in text or f'url={target}' not in text:
                fail(errors, f"{relative}: missing static redirect to {target}")
            if f'href="{target}"' not in text:
                fail(errors, f"{relative}: missing redirect fallback link to {target}")
            continue
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
    home_hero = section_markup(html_path_for_route("/"), "hero")
    home_providers = section_markup(html_path_for_route("/"), "providers")
    home_customization = section_markup(html_path_for_route("/"), "customization")
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
        "Изменяйте расположение, размеры и форму элементов экранов, а также логику работы ПО.",
        "Настройка дизайна производится через онлайн-кабинет курирующим менеджером.",
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
    if re.search(r'<a\b', home_hero):
        fail(errors, "home hero must not contain action links")
    if "Подключиться" in home_hero or "Открыть каталог" in home_hero:
        fail(errors, "home hero still contains a removed action label")
    if ".home-provider__head::before" in css_text:
        fail(errors, "home provider heading must not render the blue accent bar")
    if "media-object--terminal-product" in home_hero:
        fail(errors, "home hero must not contain a payment terminal")
    if "home-hero--provider-led" not in home_hero:
        fail(errors, "home hero must use the approved provider-led composition")
    if 'id="providers"' not in home_hero:
        fail(errors, "home providers must be integrated into the hero")
    if len(re.findall(r'class="provider-row"', home_providers)) != 3:
        fail(errors, "home provider showcase must contain three labelled rows")
    if len(re.findall(r'class="provider-strip__item"', home_providers)) != 15:
        fail(errors, "home provider showcase must contain 15 approved logos")
    expected_home_provider_assets = (
        "provider-359.png",
        "provider-6581.png",
        "provider-7.png",
        "provider-258.png",
        "provider-1134.png",
        "provider-631.png",
        "provider-241.png",
        "provider-168.png",
        "provider-9858.png",
        "provider-9849.png",
        "provider-4819.png",
        "provider-4816.png",
        "provider-4675.png",
        "provider-252.png",
        "provider-876.png",
    )
    for asset in expected_home_provider_assets:
        if home_providers.count(f"/{asset}") != 1:
            fail(errors, f"home provider showcase must contain approved asset once: {asset}")
    for label in ("Связь и ТВ", "Банки", "Сервисы и игры"):
        if f'<h3 class="provider-row__title">{label}</h3>' not in home_providers:
            fail(errors, f"home provider row is missing: {label}")
    if "evidence-section--providers" in home_text:
        fail(errors, "home providers must not be rendered as a separate evidence section")
    if "evidence-section--reverse" in home_providers:
        fail(errors, "home provider logos must remain on the right")
    if "<h2>Персонализация интерфейса</h2>" not in home_customization:
        fail(errors, "home customization title is not updated")
    interface_svg = (DIST / "assets" / "diagrams" / "interface-customization.svg").read_text(encoding="utf-8")
    if ">Настройка интерфейса SkySend</text>" in interface_svg:
        fail(errors, "interface image still contains the removed visible title")
    if "<h2>SkyMarket</h2>" not in home_commerce:
        fail(errors, "home commerce section must be titled SkyMarket")
    for label in ("Загрузка справочника товаров", "Формирование заказов", "Оплата заказов"):
        if label not in home_commerce:
            fail(errors, f"SkyMarket feature missing: {label}")
    if home_partners.count('class="partner-tile partner-tile--') != 6:
        fail(errors, "home partners section must contain six clickable tiles")
    if home_partners.count('<svg class="partner-infographic ') != 6:
        fail(errors, "home partner tiles must contain six inline infographics")
    if "<img" in home_partners:
        fail(errors, "home partner infographics must not fall back to unrelated images")
    expected_partner_tiles = (
        ("agents", "/partners/agents/", "Платёжным агентам"),
        ("providers", "/partners/providers/", "Провайдерам услуг"),
        ("suppliers", "/partners/suppliers/", "Поставщикам товаров"),
        ("retail", "/partners/retail/", "Торговым сетям"),
        ("representatives", "/partners/representatives/", "Представителям"),
        ("gateways", "/partners/gateways/", "Шлюзовикам"),
    )
    for kind, href, label in expected_partner_tiles:
        if home_partners.count(f"partner-tile--{kind}") != 1:
            fail(errors, f"home partner tile is missing its infographic type: {kind}")
        if home_partners.count(f"partner-infographic--{kind}") != 1:
            fail(errors, f"home partner infographic is missing: {kind}")
        if f'href="{href}"' not in home_partners or f"<strong>{label}</strong>" not in home_partners:
            fail(errors, f"home partner route is incomplete: {label}")
    for label in ("FastPay Beauty II", "FastPay Simple"):
        if label not in home_equipment:
            fail(errors, f"home equipment showcase missing: {label}")
    if '<dl' in home_equipment or 'Для помещений' in home_equipment or 'product-duo__lead' in home_equipment:
        fail(errors, "home equipment must only show the two models without specifications or indoor label")
    if ">Оборудование<" in home_equipment:
        fail(errors, "home equipment section must not contain the generic equipment link")
    for alias, target in ROUTE_ALIASES.items():
        alias_file = html_path_for_route(alias)
        if not alias_file.exists():
            fail(errors, f"removed index {alias} must resolve to {target}")
    if 'href="/software/"' in public_text:
        fail(errors, "public links must not point to the removed software index")
    if home_text.count("data-nav-menu") != 2:
        fail(errors, "desktop header must contain partner and software dropdowns")
    if home_text.count("Вход | Регистрация") < 2:
        fail(errors, "combined login and registration action is missing")
    emitted_external_accounts = sum(public_text.count(href) for href in public_external_accounts)
    for href in public_external_accounts:
        present = href in public_text
        if EXPECT_EXTERNAL_ACCOUNTS and not present:
            fail(errors, f"verified external account link missing: {href}")
        if not EXPECT_EXTERNAL_ACCOUNTS and present:
            fail(errors, f"unverified external account link was published: {href}")

    software_titles = {
        "/software/terminal/": "Терминальное ПО",
        "/software/rma/": "РМА для Windows, Linux и Android",
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
        ("/software/terminal/", "materials"): [
            "Виртуальная машина с ПО терминала - v. 5.45 (.zip 60.6 Mb)",
            "Скачивание логов терминала usb-накопителем",
            "Эксплуатация терминала",
        ],
        ("/software/rma/", "materials"): [
            'Приложение "Рабочее место Агента для ОС Windows"',
            "Приложение «Рабочее место Агента» для Windows, EXE",
            "Приложение для РМА для 64-битной версии OS Linux",
            "Инструкция по установке и эксплуатации РМА Windows",
            "Установка и эксплуатация РМА Windows",
            "Установка и эксплуатация РМА Linux",
            "Программа приема платежей на Android",
            "Установка и настройка ALLVEND для Android",
            "Приложение приема платежей для Android",
        ],
        ("/software/xml/", "protocol"): [
            "Описание протокола SkyTransact",
            "Пример для предпроцессинга C++",
            "Пример для препроцессинга PHP",
        ],
        ("/software/pos/", "start"): ["ПО для POS-терминала Штрих-Mobile Pay PRO - Версия 1.1 (7 Mb)"],
        ("/software/allvend/", "materials"): [
            "Установка ПО ALLVEND",
            "Настройка и сервисный режим ALLVEND",
            "Инструкция по подключению периферийного оборудования к устройствам самообслуживания ALLVEND",
            "ISO-образ ALLVEND",
            "Общее описание ОС FastSYS",
            "Снимки экрана ОС FastSYS",
            "Стек используемых технологий",
            "Общее описание работы Системы SkySend",
        ],
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

    for kind, route, label in expected_partner_tiles:
        markup = html_path_for_route(route).read_text(encoding="utf-8")
        main_markup = re.search(r'<main\b.*?</main>', markup, flags=re.S).group(0)
        if re.search(r'<a\b', main_markup):
            fail(errors, f"{route}: partner content must not contain hyperlinks")
        if 'jump-nav' in main_markup or 'Обсудить подключение' in main_markup or '>Партнёрам<' in main_markup:
            fail(errors, f"{route}: removed partner navigation or eyebrow is still rendered")
    expected_scenes = {
        'agents': {'cost-reduction':'agent-maintenance','remote-control':'agent-remote','innovation':'agent-innovation'},
        'providers': {'payment-collection':'provider-payment-points','connecting-to-skysend':'provider-connection','privacy-policy':'provider-data-security','high-speed':'provider-processing','automate-reporting':'provider-reporting','connecting-to-finger':'provider-finger','partnership':'provider-preprocessing','placing-terminals':'provider-office-terminal'},
        'suppliers': {'sales-network-products':'supplier-sales-channels','directory-of-products':'supplier-catalog','work-in-the-office':'supplier-order-management','integration-in-xml':'supplier-xml','ease-of-interaction':'supplier-sync','freeconnection':'supplier-connection'},
        'retail': {'orders':'retail-orders','management':'retail-management','deployment':'retail-deployment'},
        'representatives': {'cashier-in-the-region':'representative-cashdesk','exclusivity-in-the-region':'representative-region','mastering-directions':'representative-directions','connecting-players':'representative-participants'},
        'gateways': {'quick-start':'gateway-steps','highspeed':'gateway-processing','high-reward':'gateway-operations'},
    }
    for kind, sections in expected_scenes.items():
        for section_id, scene_id in sections.items():
            markup = section_markup(html_path_for_route(f'/partners/{kind}/'), section_id)
            if f'data-scene="{scene_id}"' not in markup or '<svg' not in markup:
                fail(errors, f"{kind}#{section_id}: missing subject illustration {scene_id}")
            if 'feature-list' in markup or 'process-node' in markup:
                fail(errors, f"{kind}#{section_id}: side list was not replaced")
    representatives = html_path_for_route('/partners/representatives/').read_text(encoding='utf-8')
    section_ids = re.findall(r'<section\b[^>]*id="([^"]+)"', representatives)
    if section_ids[-1] != 'publication-of-information':
        fail(errors, 'representative contacts must be the last section')
    contact = section_markup(html_path_for_route('/partners/representatives/'), 'publication-of-information')
    for value in ('+7 (861) 201-12-21','+7 (800) 555-25-36','sales@inf-sys.ru','support@inf-sys.ru','@infsysgroup'):
        if value not in contact:
            fail(errors, f'representative contact is missing: {value}')
    if section_markup(html_path_for_route('/partners/gateways/'), 'round-the-clock-support'):
        fail(errors, 'gateways support section must be removed')
    rma = html_path_for_route('/software/rma/').read_text(encoding='utf-8')
    for visual in ('media-object--rma-desktop','media-object--rma-android'):
        if visual not in rma:
            fail(errors, f'combined RMA is missing screenshot: {visual}')
    for old in ('/software/rma-desktop/','/software/rma-android/'):
        if f'href="{old}"' in home_text:
            fail(errors, f'software navigation still links to old RMA route: {old}')

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
        r"В исходном (?:описании|каталоге)",
        r"Исходный сайт (?:описывает|предусматривает)",
        r"На исходном сайте",
        r"Исходные материалы описывают",
        r"из исходн(?:ых материалов|ой страницы)",
        r"из материалов (?:SkySend|действующего сайта)",
    ]
    for pattern in forbidden_copy:
        if re.search(pattern, public_text, flags=re.I):
            fail(errors, f"forbidden public copy matched: {pattern}")
    forbidden_assets = ["banf.png", "allvend.png", "pop-up-full.jpg", "cluster_skysend.jpeg"]
    for name in forbidden_assets:
        if list(DIST.rglob(name)):
            fail(errors, f"forbidden/review-only asset copied: {name}")

    manifest = json.loads((DIST / "build-manifest.json").read_text(encoding="utf-8"))
    finger_text = html_path_for_route("/software/finger/").read_text(encoding="utf-8")
    for phrase in (
        "бескомиссионный онлайн-кошелёк",
        "Отсутствие комиссии за оплату услуг",
        "Отсутствие платы за содержание счёта кошелька",
        "Простота регистрации и работы",
        "Высокий уровень безопасности транзакций",
        "Круглосуточная поддержка пользователей",
        "Play Market",
        "App Store",
    ):
        if phrase not in finger_text:
            fail(errors, f"FINGER page missing source content: {phrase}")

    allvend_text = html_path_for_route("/software/allvend/").read_text(encoding="utf-8")
    for section_id in ("audiences", "capabilities", "interface", "payments", "orders", "infokiosk", "cashdesk", "management", "network", "fastsys", "materials"):
        if f'id="{section_id}"' not in allvend_text:
            fail(errors, f"ALLVEND page missing section: {section_id}")
    if "allvend-infokiosk.svg" not in allvend_text:
        fail(errors, "ALLVEND infokiosk must use the source-screen composition")

    expected = {"routes": 40, "provider_rows": 600, "download_rows": 72, "redirects": 157, "gone": 13}
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
