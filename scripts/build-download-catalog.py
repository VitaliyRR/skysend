"""Build a reviewed download manifest from the preserved source crawl.

No software or document bodies are downloaded or executed. Optional key-link
checks use HEAD only; TLS validation stays enabled. This creates handoff data,
not a frontend or a backend.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "downloads-source.json"
OUTPUT = ROOT / "data" / "download-catalog.json"

GROUPS = [
    ("terminal", "Терминальное ПО"),
    ("rma", "РМА Windows / Linux"),
    ("rma-android", "РМА Android"),
    ("xml", "XML"),
    ("pos", "POS"),
    ("system-documents", "Документы системы"),
    ("other", "Технические материалы"),
]

SOFTWARE = {
    "awp-5.24.zip": ("rma", "software"),
    "awp-5.24.exe": ("rma", "software"),
    "awp-5.24_linux_x64.tar.gz": ("rma", "software"),
    "terminal_demo_5.45.2191.zip": ("terminal", "software_demo"),
    "MPProSkyConfig.zip": ("pos", "software"),
    "fastsys5_allvend.iso.zip": ("terminal", "software_image"),
}
TECHNICAL_DOCS = {
    "scheme_fastsys_5.pdf", "technology_skysend_stack.pdf",
    "cluster_skysend.jpeg", "description_skysend.pdf",
    "presentation_fastsys.pdf", "screenshots_fastsys.pdf",
    "functions_dealer.pdf", "sphere_of_activity_dealer.pdf",
}
LEGAL_DOCS = {
    "activities.pdf", "decree_rules.pdf", "license_agreement.pdf",
    "memo_income_agent.pdf", "fisk_memo.pdf", "exclusive_dealer.pdf",
    "act_ERRP_AV.pdf", "act_ERRP.pdf", "conditions_overdraft.pdf",
    "overdraft_application.docx",
}
TERMINAL_DOCS = {
    "exploitation_terminal.pdf", "supported_devices.pdf",
    "instruction_programming_fw_writer.pdf", "instruction_service_mode.pdf",
    "instruction_setup_devices_kiosks.pdf", "instruction_downloads_logs.pdf",
    "instruction_nanoprotech.pdf", "instruction_installation_allvend.pdf",
    "instruction_setup_and_service_mode_allvend.pdf",
}
RMA_DOCS = {"instruction_rma_w.pdf", "instruction_setup_awp_linux.pdf"}
RMA_ANDROID_DOCS = {"instruction_rma_android.pdf", "instruction_setup_using_allvend_android.pdf"}
KNOWN_MISSING_LINKS = {
    "Установка и эксплуатация РМА Linux": "https://ftp.isg.dev/docs/instruction_setup_awp_linux.pdf",
}
KNOWN_UNAVAILABLE = {"scheme_fastsys_5.pdf"}
SUPPLEMENTAL_ROWS = [
    {
        "title": "Установка ПО ALLVEND",
        "source_page": "https://skysend.ru/allvend.html",
        "direct_file_url": "https://ftp.isg.dev/docs/instruction_installation_allvend.pdf",
        "links": ["https://ftp.isg.dev/docs/instruction_installation_allvend.pdf"],
        "flags": ["version_requires_review"],
    },
    {
        "title": "Настройка и сервисный режим ALLVEND",
        "source_page": "https://skysend.ru/allvend.html",
        "direct_file_url": "https://ftp.isg.dev/docs/instruction_setup_and_service_mode_allvend.pdf",
        "links": ["https://ftp.isg.dev/docs/instruction_setup_and_service_mode_allvend.pdf"],
        "flags": ["version_requires_review"],
    },
    {
        "title": "ISO-образ ALLVEND",
        "source_page": "https://skysend.ru/allvend.html",
        "direct_file_url": "https://ftp.isg.dev/soft/allvend/fastsys5_allvend.iso.zip",
        "links": ["https://ftp.isg.dev/soft/allvend/fastsys5_allvend.iso.zip"],
        "flags": ["version_requires_review", "compatibility_requires_review"],
    },
    {
        "title": "Приложение «Рабочее место Агента» для Windows, EXE",
        "source_page": "https://skysend.ru/program/rma-pc.html",
        "direct_file_url": "https://ftp.isg.dev/soft/awp/awp-5.24.exe",
        "links": ["https://ftp.isg.dev/soft/awp/awp-5.24.exe"],
        "flags": ["version_requires_review", "compatibility_requires_review"],
    },
    {
        "title": "Установка и настройка ALLVEND для Android",
        "source_page": "https://skysend.ru/program/rma-android.html",
        "direct_file_url": "https://ftp.isg.dev/docs/instruction_setup_using_allvend_android.pdf",
        "links": ["https://ftp.isg.dev/docs/instruction_setup_using_allvend_android.pdf"],
        "flags": ["version_requires_review", "compatibility_requires_review"],
    },
]
KEY_FILENAMES = {
    *SOFTWARE,
    "instruction_programming_fw_writer.pdf", "instruction_rma_w.pdf",
    "instruction_rma_android.pdf", "skysend_protocol_actual.pdf",
    "contract_agent_skysend.pdf", "rules_system_of_payments_skysend.pdf",
    "instruction_setup_awp_linux.pdf", "instruction_installation_allvend.pdf",
    "instruction_setup_and_service_mode_allvend.pdf", "fastsys5_allvend.iso.zip",
    "awp-5.24.exe", "instruction_setup_using_allvend_android.pdf",
}


def normalized_title(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", value)).strip()


def path_name(url: str | None) -> str:
    return urllib.parse.unquote(urllib.parse.urlsplit(url or "").path.rsplit("/", 1)[-1])


def classify(row: dict) -> tuple[str | None, str]:
    title = normalized_title(row["title"])
    url = row.get("direct_file_url") or ""
    name = path_name(url)
    folded = title.casefold()
    if re.search(r"прайс|предложени|презентаци|сравнени|преимуществ|реклам|автопробег|доходност|увеличить доход|бизнес.?план", folded):
        return None, "exclude_promotion"
    if "/offer/" in url or "/price/" in url or name in {"profit.pdf", "additional_income.pdf", "start_dealer.pdf", "soft.pdf", "cloud_server.pdf"}:
        return None, "exclude_commercial_material"
    if re.search(r"логотип|макеты|макет", folded):
        return None, "exclude_brand_assets_from_downloads"
    if "Приложение приема платежей для Android" == title:
        return "rma-android", "external_store"
    if title == "Установка и эксплуатация РМА Linux" and not url:
        return "rma", "instruction_missing_link"
    if name in SOFTWARE:
        return SOFTWARE[name]
    if name in RMA_DOCS:
        return "rma", "instruction"
    if name in RMA_ANDROID_DOCS:
        return "rma-android", "instruction"
    if name in {"skysend_protocol_actual.pdf", "example_C++.zip", "example_php.zip"}:
        return "xml", "protocol_or_code_example"
    if name in TERMINAL_DOCS:
        return "terminal", "instruction"
    if name.startswith("instruction_"):
        return "other", "instruction"
    if name in LEGAL_DOCS or name.startswith(("contract_", "agreement_", "statement_", "rules_", "regulations_")):
        return "system-documents", "system_document"
    if name in TECHNICAL_DOCS:
        return "other", "technical_document"
    if "Cхема кластер" in title:
        return "other", "technical_document"
    return None, "exclude_not_in_documentation_whitelist"


def probe_head(url: str) -> dict:
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    result = {"checked_at": now, "method": "HEAD", "body_downloaded": False}
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "SkySend-Design-Audit/1.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            result.update({
                "status": "reachable_head", "http_status": response.status,
                "final_url": response.url, "content_type": response.headers.get("Content-Type"),
                "content_length_header": response.headers.get("Content-Length"),
                "note": "HEAD подтверждает ответ сервера, но не целостность файла, версию или совместимость ПО.",
            })
    except urllib.error.HTTPError as exc:
        result.update({"status": "head_http_error", "http_status": exc.code, "note": str(exc)})
    except Exception as exc:
        result.update({"status": "head_network_error", "note": f"{type(exc).__name__}: {exc}"})
    return result


def confirm_store_status(url: str) -> dict:
    result = {
        "method": "GET_HEADERS_ONLY", "body_downloaded": False,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    try:
        request = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=10) as response:
            result.update(http_status=response.status, final_url=response.url)
    except urllib.error.HTTPError as exc:
        result.update(http_status=exc.code, note=str(exc))
    except Exception as exc:
        result.update(error=f"{type(exc).__name__}: {exc}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-key-links", action="store_true")
    args = parser.parse_args()
    raw = json.loads(SOURCE.read_text(encoding="utf-8-sig"))
    existing_items = {}
    if OUTPUT.exists():
        existing_items = {item["id"]: item for item in json.loads(OUTPUT.read_text(encoding="utf-8-sig")).get("items", [])}
    seen: dict[str, dict] = {}
    excluded = []
    duplicates = 0
    source_rows = [*raw["items"], *SUPPLEMENTAL_ROWS]
    for source_row in source_rows:
        row = dict(source_row)
        title = normalized_title(row["title"])
        if not row.get("direct_file_url") and title in KNOWN_MISSING_LINKS:
            row["direct_file_url"] = KNOWN_MISSING_LINKS[title]
            row["links"] = [row["direct_file_url"]]
            row["flags"] = [*row.get("flags", []), "recovered_from_source_audit"]
        group, kind = classify(row)
        if group is None:
            excluded.append({
                "source_title": row["title"], "source_page": row["source_page"],
                "direct_file_url": row.get("direct_file_url"), "source_links": row.get("links", []),
                "decision": kind, "publish": False,
            })
            continue
        original_url = row.get("direct_file_url")
        links = row.get("links", [])
        target = original_url
        link_kind = "file"
        if kind == "external_store":
            target = links[0] if links else None
            link_kind = "store"
        elif not target and kind == "technical_document":
            # A preserved source URL, not an invented extension or host rewrite.
            target = next((link for link in links if path_name(link) == "cluster_skysend.jpeg"), None)
        key = original_url or target or (row["source_page"] + "|" + row["title"])
        if key in seen:
            duplicates += 1
            seen[key]["source_occurrences"].append({"title": row["title"], "page": row["source_page"]})
            continue
        title = normalized_title(row["title"])
        size_match = re.search(r"\s+(\d+(?:[.,]\d+)?\s+(?:KB|MB|GB))$", title, re.I)
        display_title = title[:size_match.start()].strip() if size_match else title
        scheme = urllib.parse.urlsplit(target or "").scheme
        status = "missing_url" if not target else ("unsupported_browser_scheme" if scheme == "ftp" else "source_link_unverified")
        filename = path_name(target)
        extension = "tar.gz" if filename.lower().endswith(".tar.gz") else (filename.rsplit(".", 1)[-1] if "." in filename else None)
        item = {
            "id": group + "-" + hashlib.sha256(key.encode()).hexdigest()[:10],
            "group": group, "kind": kind, "source_title": row["title"],
            "display_title": display_title, "source_page": row["source_page"],
            "direct_file_url": original_url, "target_url": target, "link_kind": link_kind,
            "source_links": links, "source_occurrences": [{"title": row["title"], "page": row["source_page"]}],
            "source_flags": row.get("flags", []), "source_size_text": size_match.group(1) if size_match else None,
            "format_from_url": extension, "status": status,
            "version_policy": "Не обозначать архивную версию как актуальную и не заявлять совместимость с текущими ОС без проверки.",
            "content_review": "Отбор по исходному названию и URL; содержимое бинарных файлов не скачивалось и не проверялось.",
        }
        if status == "missing_url":
            item["fallback"] = {"text": "Инструкция для Linux недоступна на сайте. Обратитесь в поддержку.", "href": "/support/"}
        elif status == "unsupported_browser_scheme":
            item["fallback"] = {"text": "Файл недоступен для скачивания в браузере. Обратитесь в поддержку.", "href": "/support/"}
        if filename in KNOWN_UNAVAILABLE:
            item["status"] = "unavailable_checked"
            item["fallback"] = {"text": "Файл недоступен. Обратитесь в поддержку.", "href": "/support/"}
        previous = existing_items.get(item["id"])
        if previous and previous.get("target_url") == target and not args.check_key_links:
            for field in ("check", "confirmation_check", "fallback"):
                if field in previous:
                    item[field] = previous[field]
            if previous.get("check") and filename not in KNOWN_UNAVAILABLE:
                item["status"] = previous["status"]
        seen[key] = item
    items = list(seen.values())
    items.sort(key=lambda item: ([g[0] for g in GROUPS].index(item["group"]), item["display_title"].casefold()))
    if args.check_key_links:
        checks = [item for item in items if item["target_url"] and (path_name(item["target_url"]) in KEY_FILENAMES or item["link_kind"] == "store")]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            future_to_item = {pool.submit(probe_head, item["target_url"]): item for item in checks}
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                item["check"] = future.result()
                item["status"] = item["check"]["status"]
                if item["link_kind"] == "store" and item["check"].get("http_status") == 404:
                    item["confirmation_check"] = confirm_store_status(item["target_url"])
                    if item["confirmation_check"].get("http_status") == 404:
                        item["status"] = "unavailable_checked"
                        item["fallback"] = {"text": "Приложение недоступно по ссылке Google Play. Обратитесь в поддержку.", "href": "/support/"}
    catalog = {
        "schema_version": "1.0", "audit_date": raw["audit_date"],
        "source_file": "data/downloads-source.json", "source_rows": len(source_rows),
        "included_items": len(items), "excluded_rows": len(excluded), "duplicate_rows_merged": duplicates,
        "scope": "ПО, инструкции, технические и системные документы. Акции, цены, рекламные предложения и обещания роста доходов исключены.",
        "groups": [{"id": key, "title": label, "anchor": f"/downloads/#{key}", "count": sum(item["group"] == key for item in items)} for key, label in GROUPS],
        "render_policy": {
            "reachable_head": "Можно показать исходную ссылку. HEAD не подтверждает актуальность, содержимое или целостность документа.",
            "source_link_unverified": "Исходная ссылка сохранена; проверить до выпуска. Не показывать значок проверки или гарантировать актуальность.",
            "head_http_error": "Проверка HEAD не прошла; не объявлять файл удалённым по одному HEAD. Перед выпуском проверить ссылку безопасным обычным запросом без исполнения; при неудаче показать текст Файл недоступен. Обратитесь в поддержку.",
            "head_network_error": "Доступ не подтверждён из окружения аудита. Перед выпуском проверить; не обходить проверку TLS. Если проблема сохраняется, показать fallback поддержки.",
            "unavailable_checked": "Недоступность подтверждена HEAD и запросом GET без чтения тела. В строке не показывать кнопку скачивания; вывести заданный fallback поддержки.",
            "missing_url": "Не создавать кнопку скачивания и не угадывать адрес. Показать заданный fallback.",
            "unsupported_browser_scheme": "Сохранить исходный FTP URL в аудите; на публичной странице показать fallback поддержки, не придумывать HTTPS-замену.",
            "store": "Для магазина приложений подпись Открыть в Google Play, не Скачать APK. Наличие карточки не подтверждает совместимость приложения.",
            "excluded": "Не импортировать excluded_records в публичную страницу, поиск, sitemap или связанные материалы.",
        },
        "items": items,
        "excluded_records": excluded,
    }
    OUTPUT.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"included": len(items), "excluded": len(excluded), "duplicates_merged": duplicates, "statuses": {s: sum(i["status"] == s for i in items) for s in sorted({i["status"] for i in items})}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
