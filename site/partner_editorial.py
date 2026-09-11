"""Subject photographs and original product material for partner sections.

Generated contextual artwork is recorded in data/editorial-artwork.json.
It illustrates the topic and does not document an actual SkySend location.
"""
from html import escape
from urllib.parse import quote


SCENES = {
    'agent-maintenance': ('terminal-maintenance', 'Терминал SkySend и купюроприёмник на сервисном столе'),
    'agent-remote': ('remote-management', 'Рабочее место с ноутбуком и терминалом SkySend'),
    'provider-processing': ('payment-processing', 'Две серверные стойки с сетевым оборудованием'),
    'provider-office-terminal': ('provider-office', 'Терминал SkySend рядом со стойкой обслуживания'),
    'supplier-sales-channels': ('supplier-goods', 'Товары, подготовленные к отправке покупателю'),
    'supplier-xml': ('xml-catalogue', 'Каталог и XML рядом с сервером обмена данными'),
    'supplier-sync': ('catalogue-updates', 'Один товар и его фотографии для общего каталога'),
    'retail-orders': ('retail-checkout', 'Товары в корзине, принтер чека и платёжное устройство'),
    'retail-deployment': ('provider-office', 'Размещение терминала в точке обслуживания'),
    'gateway-processing': ('payment-processing', 'Серверное оборудование для распределённой обработки'),
    'allvend-orders': ('retail-checkout', 'Выбранные товары и оборудование для оплаты заказа'),
}


def artwork_image(name, alt='', *, css='partner-editorial__image', sizes='(min-width: 64rem) 46vw, 100vw'):
    base = f'/assets/ready/editorial/{name}'
    return (f'<img class="{css}" src="{base}.webp" '
            f'srcset="{base}-768.webp 768w, {base}.webp 1536w" sizes="{sizes}" '
            f'width="1536" height="1024" loading="lazy" decoding="async" alt="{escape(alt)}">')


def original_image(path, alt, css=''):
    return (f'<img class="{css}" src="/{quote(path, safe="/")}" '
            f'loading="lazy" decoding="async" alt="{escape(alt)}">')


def brand_strip():
    return ('<figcaption class="partner-editorial__brands">'
            + original_image('assets/originals/logotip_skymarket_3x1.png', 'SkyMarket', 'editorial-brand--market')
            + original_image('assets/originals/logotip_finger.png', 'FINGER', 'editorial-brand--finger')
            + '</figcaption>')


def render_partner_editorial(scene_id):
    if scene_id == 'agent-innovation':
        return ('<figure class="partner-editorial partner-editorial--interface" data-scene="agent-innovation">'
                + original_image('assets/diagrams/interface-customization.svg',
                                 'Варианты оформления экрана терминала SkySend', 'partner-editorial__screen')
                + brand_strip() + '</figure>')
    if scene_id not in SCENES:
        return None
    name, alt = SCENES[scene_id]
    extra = brand_strip() if scene_id == 'supplier-sales-channels' else ''
    return (f'<figure class="partner-editorial" data-scene="{escape(scene_id)}">'
            + artwork_image(name, alt) + extra + '</figure>')
