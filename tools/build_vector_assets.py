from pathlib import Path
from html import escape
import json,hashlib,xml.etree.ElementTree as ET
ROOT=Path.cwd();out=ROOT/'assets/diagrams';out.mkdir(parents=True,exist_ok=True);icons=ROOT/'assets/icons';icons.mkdir(exist_ok=True)
STYLE='''<style>text{font-family:Inter,Arial,sans-serif;fill:#111315}.h{font-size:30px;font-weight:600;letter-spacing:-.4px}.label{font-size:21px;font-weight:600}.small{font-size:15px;fill:#5F6368}.blue{fill:#0066B3}</style>'''
def svg(name,w,h,title,desc,body):
 s=f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>{STYLE}<rect width="100%" height="100%" fill="#FFFFFF"/><defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M1 1 9 5 1 9" fill="none" stroke="#0066B3" stroke-width="1.5" stroke-linejoin="round"/></marker></defs>{body}</svg>'''
 (out/name).write_text(s,encoding='utf-8')
def text(x,y,t,c='label',anchor='start'):return f'<text x="{x}" y="{y}" class="{c}" text-anchor="{anchor}">{escape(t)}</text>'
def rect(x,y,w,h,fill='#F4F5F6'):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}"/>'
def line(d):return f'<path d="{d}" fill="none" stroke="#0066B3" stroke-width="2" marker-end="url(#arrow)"/>'
body=text(32,52,'Приём платежей через SkySend','h')+text(32,84,'Каналы приёма и направление платежа','small')
for y,t in [(138,'Терминал'),(252,'Кассир'),(366,'Смартфон')]:body+=rect(32,y,240,78)+text(62,y+46,t)+line(f'M272 {y+39} H330 V291 H427')
body+=rect(442,234,234,114,'#111315')+'<text x="559" y="303" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="30" font-weight="600" style="fill:white">SkySend</text>'+line('M676 291 H820')+rect(836,234,252,114)+text(962,303,'Провайдеры','label','middle')
svg('payment-network.svg',1120,500,'Приём платежей через SkySend','Терминал, кассир и смартфон передают платежи через систему SkySend провайдерам. Концептуальная схема каналов, не география сети.',body)
body=text(32,52,'Интеграция через XML','h')+text(32,84,'Платежи и обмен информацией','small')
for x,label in [(32,'Ваша система'),(432,'SkySend'),(832,'Провайдеры')]:body+=rect(x,153,256,112,'#111315' if label=='SkySend' else '#F4F5F6')+(f'<text x="{x+128}" y="220" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="24" font-weight="600" style="fill:white">SkySend</text>' if label=='SkySend' else text(x+128,220,label,'label','middle'))
body+=line('M288 190 H420')+text(360,175,'Платежи','small','middle')+line('M688 190 H820')+text(760,175,'Платежи','small','middle')+line('M432 240 H300')+line('M832 240 H700')+text(560,317,'Информация о провайдерах и условиях','small','middle')
svg('xml-flow.svg',1120,380,'Интеграция через XML','Ваша система передаёт платежи в SkySend, затем провайдерам. В обратном направлении предусмотрен обмен информацией о провайдерах и условиях. Схема не специфицирует поля протокола.',body)
steps=['Загрузка справочника товаров','Формирование заказов','Оплата заказов']
body=text(32,52,'Заказ и оплата продукции','h')
for i,t in enumerate(steps):
 x=32+i*366;body+=rect(x,102,324,166)+text(x+24,141,'0'+str(i+1),'small')
 for j,z in enumerate(['Загрузка справочника','товаров'] if i==0 else [t]):body+=text(x+24,189+j*30,z)
 if i<2:body+=line(f'M{x+328} 185 H{x+353}')
svg('commerce-flow.svg',1120,310,'Заказ и оплата продукции','Последовательность работы: загрузка справочника товаров, формирование заказов, оплата заказов.',body)
body=text(20,40,'Заказ и оплата','h')
for i,t in enumerate(steps):
 y=80+i*170;body+=rect(20,y,320,136)+text(40,y+34,'0'+str(i+1),'small')
 for j,z in enumerate(['Загрузка справочника','товаров'] if i==0 else (['Формирование','заказов'] if i==1 else [t])):body+=text(40,y+74+j*27,z)
 if i<2:body+=line(f'M180 {y+143} V{y+160}')
svg('commerce-flow-mobile.svg',360,590,'Заказ и оплата продукции','Последовательность работы: загрузка справочника товаров, формирование заказов, оплата заказов.',body)
body=text(32,52,'Техническая поддержка','h')+text(32,88,'Связаться с SkySend','small')
contacts=[('Телефон','8 (800) 555-25-36','tel:+78005552536'),('Электронная почта','support@inf-sys.ru','mailto:support@inf-sys.ru'),('Telegram','@infsysgroup','https://t.me/infsysgroup')]
for i,(label,value,url) in enumerate(contacts):
 y=130+i*86;body+=text(32,y,label,'small')+f'<a href="{url}">'+text(32,y+31,value,'label')+'</a>'
 if i<2:body+=f'<path d="M32 {y+49} H688" stroke="#D8DADD"/>'
svg('contact-panel.svg',720,390,'Контакты технической поддержки SkySend','Телефон: 8 800 555 25 36. Электронная почта: support@inf-sys.ru. Telegram: @infsysgroup.',body)
shapes={
 'terminal':'<rect x="6" y="2.5" width="12" height="19" rx="1.5"/><path d="M8.5 5h7v6h-7zM9 14.5h6M10 18h4"/>',
 'phone':'<rect x="6.5" y="2" width="11" height="20" rx="2"/><path d="M10 5h4M11 19h2"/>',
 'desktop':'<rect x="2.5" y="3.5" width="19" height="13" rx="1.5"/><path d="M12 16.5v4M8 20.5h8"/>',
 'xml':'<path d="m8 6-6 6 6 6M16 6l6 6-6 6M14 3l-4 18"/>',
 'document':'<path d="M6 2.5h8l4 4v15H6zM14 2.5v5h4M9 11h6M9 15h6M9 18h4"/>',
 'arrow-right':'<path d="M3 12h17M14 5l7 7-7 7"/>',
 'menu':'<path d="M3 6h18M3 12h18M3 18h18"/>',
 'close':'<path d="m5 5 14 14M19 5 5 19"/>'}
for name,shape in shapes.items():(icons/(name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{shape}</svg>',encoding='utf-8')
print('Created 5 diagrams, 8 icons')

# Exact vector bounds measured once from every original path using svgpathtools.
# Source paths and colours are preserved; only page whitespace is removed.
import re,base64
brand=ROOT/'assets/brand';brand.mkdir(exist_ok=True)
brand_source=(ROOT/'assets/originals/logotip_skysend.svg').read_text(encoding='utf-8')
brand_svg=re.sub(r'viewBox="[^"]+"','viewBox="44.700 258.848 505.600 324.152"',brand_source,count=1)
brand_svg=re.sub(r'\sstyle="enable-background:[^"]+"','',brand_svg,count=1)
brand_svg=brand_svg.replace('<svg version=','<svg role="img" aria-label="SkySend" version=',1)
(brand/'skysend-logo.svg').write_text(brand_svg,encoding='utf-8')
# Two real screenshots; SVG viewports hide the lower promotional row.
source=ROOT/'evidence/skysend/asset-review/po/8_full.png'
assert source.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n', 'Expected the verified PNG source'
encoded=base64.b64encode(source.read_bytes()).decode('ascii')
composition=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="404" viewBox="0 0 1120 404" role="img" aria-labelledby="title desc"><title id="title">Персонализация интерфейса SkySend</title><desc id="desc">Два реальных экрана из верхнего ряда оригинального 8_full.png. Слева меню провайдеров, справа меню услуг. Изображения показаны через ограниченные области просмотра SVG без изменения исходных пикселей. Нижний ряд с промо полностью скрыт. Это архивные экраны ПО, не макет нового интерфейса.</desc><rect width="1120" height="404" fill="#FFFFFF"/><defs><image id="source-screen" width="1188" height="904" href="data:image/png;base64,{encoded}"/></defs><svg x="24" y="10" width="524" height="384" viewBox="16 15 566 420" overflow="hidden" preserveAspectRatio="xMidYMid meet"><use href="#source-screen"/></svg><svg x="572" y="10" width="524" height="384" viewBox="609 10 566 426" overflow="hidden" preserveAspectRatio="xMidYMid meet"><use href="#source-screen"/></svg></svg>'''
(out/'interface-customization.svg').write_text(composition,encoding='utf-8')

# Real historical ALLVEND infokiosk UI isolated from the verified source strip.
infokiosk_source=ROOT/'evidence/skysend/asset-review/po/12_full.png'
assert infokiosk_source.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n', 'Expected the verified ALLVEND PNG source'
infokiosk_encoded=base64.b64encode(infokiosk_source.read_bytes()).decode('ascii')
infokiosk=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="680" viewBox="0 0 1120 680" role="img" aria-labelledby="title desc"><title id="title">ALLVEND в режиме информационного киоска</title><desc id="desc">Реальный архивный экран ALLVEND с навигацией по отделам магазина. Изображение выделено из оригинального 12_full.png без дорисовки интерфейса. Бренд на архивном экране не означает действующее партнёрство.</desc><rect width="1120" height="680" fill="#F4F5F6"/><defs><image id="allvend-source" width="3164" height="944" href="data:image/png;base64,{infokiosk_encoded}"/></defs><svg x="18" y="18" width="1084" height="644" viewBox="2130 135 990 602" overflow="hidden" preserveAspectRatio="xMidYMid meet"><use href="#allvend-source"/></svg></svg>'''
(out/'allvend-infokiosk.svg').write_text(infokiosk,encoding='utf-8')

# Official raster wordmark with its large transparent margins removed by viewport.
allvend_source=ROOT/'assets/originals/allvend.png'
allvend_encoded=base64.b64encode(allvend_source.read_bytes()).decode('ascii')
allvend_brand=f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="500" viewBox="0 0 760 500" role="img" aria-labelledby="title desc"><title id="title">ALLVEND</title><desc id="desc">Оригинальный знак ALLVEND из материалов SkySend. Прозрачные поля исходного PNG скрыты через SVG viewport, форма знака не изменена.</desc><defs><image id="allvend-logo-source" width="5555" height="5555" href="data:image/png;base64,{allvend_encoded}"/></defs><svg width="760" height="500" viewBox="960 1460 3790 2500" overflow="hidden" preserveAspectRatio="xMidYMid meet"><use href="#allvend-logo-source"/></svg></svg>'''
(out/'allvend-brand.svg').write_text(allvend_brand,encoding='utf-8')
print('Created exact-viewBox brand adaptation and source screenshot composition')

body=text(32,52,'Штрих-Mobile Pay PRO','h')+text(32,86,'Схема возможностей POS-терминала','small')
body+=rect(32,116,292,250)
body+='<g transform="translate(123 144)" fill="none" stroke="#111315" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><rect width="110" height="158" rx="9"/><rect x="15" y="16" width="80" height="43" rx="2"/><path d="M21 85h12m17 0h12m17 0h12M21 108h12m17 0h12m17 0h12M21 131h12m17 0h12m17 0h12"/></g>'
body+=text(178,346,'Условное обозначение','small','middle')
body+=text(372,174,'Аккумулятор')+text(372,276,'GPRS-модем')+'<path d="M372 211 H854" stroke="#D8DADD"/>'
svg('pos-capabilities.svg',890,406,'Штрих-Mobile Pay PRO: возможности','Схема возможностей POS-терминала Штрих-Mobile Pay PRO. Аккумулятор и GPRS-модем. Устройство обозначено условной пиктограммой, это не изображение внешности модели.',body)
finger=base64.b64encode((ROOT/'assets/originals/logotip_finger.png').read_bytes()).decode('ascii')
body=text(32,52,'FINGER','h')+text(32,86,'Схема возможностей сервиса','small')
body+=f'<image x="66" y="136" width="156" height="190" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{finger}"/>'
for i,t in enumerate(['Платежи','Шаблоны платежей','Выписка']):
 y=166+i*78;body+=text(314,y,t)
 if i<2:body+=f'<path d="M314 {y+31} H850" stroke="#D8DADD"/>'
svg('finger-functions.svg',890,390,'FINGER: возможности сервиса','Оригинальный логотип FINGER и три описанные функции: платежи, шаблоны платежей, выписка. Схема возможностей, не screenshot личного кабинета.',body)
print('Created POS and FINGER capability diagrams')

body=text(32,52,'Интеграция поставщика','h')+text(32,86,'Схема XML-обмена SkyMarket','small')
body+=rect(32,177,276,114)+text(170,222,'Система','label','middle')+text(170,251,'поставщика','label','middle')
body+=rect(436,177,244,114,'#111315')+'<text x="558" y="245" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="26" font-weight="600" fill="#FFFFFF" style="fill:#FFFFFF">SkyMarket</text>'
body+=line('M308 214 H424')+line('M436 254 H320')
body+=rect(836,128,252,84)+text(962,178,'Терминалы','label','middle')+rect(836,256,252,84)+text(962,306,'FINGER','label','middle')
body+=line('M680 234 H752 V170 H824')+line('M680 234 H752 V298 H824')
body+=text(32,372,'Справочник товаров')+text(320,372,'Заказы')+text(486,372,'Доставка')
svg('supplier-exchange.svg',1120,416,'Интеграция поставщика со SkyMarket','Система поставщика обменивается данными со SkyMarket: справочник товаров, заказы и доставка. SkyMarket передаёт справочник на терминалы SkySend и в FINGER. Концептуальная схема, без технических полей XML.',body)
body='<text x="20" y="38" font-family="Inter,Arial,sans-serif" font-size="25" font-weight="600" fill="#111315">Интеграция поставщика</text>'+text(20,70,'Схема XML-обмена SkyMarket','small')
body+=rect(20,102,320,84)+text(180,152,'Система поставщика','label','middle')
body+=line('M166 194 V235')+line('M194 237 V196')
body+=rect(20,246,320,84,'#111315')+'<text x="180" y="297" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="25" font-weight="600" style="fill:#FFFFFF">SkyMarket</text>'
body+=line('M180 330 V361 H95 V389')+line('M180 330 V361 H265 V389')
body+=rect(20,404,150,72)+text(95,448,'Терминалы','label','middle')+rect(190,404,150,72)+text(265,448,'FINGER','label','middle')
for i,t in enumerate(['Справочник товаров','Заказы','Доставка']):body+=text(20,523+i*33,t)
svg('supplier-exchange-mobile.svg',360,620,'Интеграция поставщика со SkyMarket','Система поставщика обменивается данными со SkyMarket: справочник товаров, заказы и доставка. SkyMarket передаёт справочник на терминалы SkySend и в FINGER. Вертикальная концептуальная схема для узкого экрана.',body)
body=text(32,52,'Автоматизация отчётности','h')+text(32,86,'Платежи, реестры и отчёты в личном кабинете','small')
for i,t in enumerate(['Платежи за период','Реестр','Отчёт']):
 x=32+i*366;body+=rect(x,123,324,124)+text(x+24,162,'0'+str(i+1),'small')+text(x+24,209,t)
 if i<2:body+=line(f'M{x+328} 185 H{x+353}')
svg('report-flow.svg',1120,295,'Автоматизация отчётности','Платежи за выбранный период, реестр и отчёт. Это схема возможностей личного кабинета по тексту исходного сайта; примеры сумм и фиктивные таблицы не используются.',body)
print('Created supplier exchange desktop/mobile and reporting diagrams')
