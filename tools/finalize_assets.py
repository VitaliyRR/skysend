from pathlib import Path
from PIL import Image
import xml.etree.ElementTree as ET
import json,hashlib,csv,shutil
ROOT=Path.cwd();mp=ROOT/'data/assets-manifest.json';m=json.loads(mp.read_text(encoding='utf-8'))
for a in m['assets']:
 if a['asset_type']=='software-feature-reference' and a['source_url'].endswith(('/11_full.png','/12_full.png','/8_full.png')):
  dest=ROOT/'assets/source-with-review/software'/Path(a['source_url']).name;dest.parent.mkdir(parents=True,exist_ok=True);
  shutil.copyfile(ROOT/'evidence/skysend/asset-review/po'/dest.name,dest)
  a['path']=dest.relative_to(ROOT).as_posix();a['production_status']='source-with-review'
  a['quality_notes']={'11_full.png':'Реальные исторические экраны заказа товаров в теме Юлмарт. Нет промо-акции; не заявлять текущее партнёрство с Юлмарт. Для нового сайта по умолчанию использовать commerce-flow.svg, этот strip только как подписанный архивный пример функции.','12_full.png':'Реальные исторические экраны навигации в магазине с темой IKEA. Не заявлять текущее партнёрство с IKEA. По умолчанию использовать собственную схему функции.','8_full.png':'Внутри тем есть промо МТС (4G/антивирус). Целиком в публичный сайт запрещён. Источник для разбора настройки дизайна; по умолчанию использовать чистый pop-up-full.jpg и текст, не маскировать рекламу декоративными блоками.'}[dest.name]
files=[*sorted((ROOT/'assets/diagrams').glob('*.svg')),*sorted((ROOT/'assets/icons').glob('*.svg')),ROOT/'assets/brand/skysend-logo.svg']
for p in files:
 rel=p.relative_to(ROOT).as_posix();b=p.read_bytes();svg=ET.fromstring(b);kind='diagram' if '/diagrams/' in rel else 'icon' if '/icons/' in rel else 'brand-adaptation'
 if kind=='brand-adaptation':source='https://skysend.ru/images/downloads/logotip_skysend.svg';notes='Изменён только viewBox по точным границам исходных кривых +4 единицы поля, добавлена доступная подпись. Геометрия и цвета не менялись.';section='global.header'
 elif kind=='icon':source='original-code-native';notes='Создана вручную кодом как самостоятельный SVG: 24×24, stroke 1.75, currentColor. Не содержит сторонних библиотек или AI-растров.';section='global.ui'
 else:source='https://skysend.ru/program/xml-gateway.html' if p.stem=='xml-flow' else 'https://skysend.ru/allvend.html' if 'commerce' in p.stem else 'https://skysend.ru/about/feedback.html' if p.stem=='contact-panel' else 'https://skysend.ru/program.html';notes='Создана вручную кодом на основе описания функций старого сайта. Это схема, а не screenshot продукта. Проверены XML и визуальный рендер.';section={'payment-network':'home.hero / partners','xml-flow':'software.xml','commerce-flow':'home.commerce / software.allvend','commerce-flow-mobile':'home.commerce.mobile / software.allvend.mobile','contact-panel':'support.contacts','interface-customization':'software.customization','pos-capabilities':'software.pos','finger-functions':'software.finger','infokiosk-flow':'software.infokiosk','supplier-exchange':'partners.suppliers','supplier-exchange-mobile':'partners.suppliers.mobile','report-flow':'partners.providers.reporting'}.get(p.stem,'software.detail')
 if p.stem=='interface-customization':
  source='https://skysend.ru/images/downloads/po/8_full.png';notes='Компоновка двух реальных экранов из верхнего ряда: SVG viewport clipping без изменения пикселей. Видимый заголовок внутри изображения удалён; полный source PNG встроен один раз, нижние промо вне viewports.';kind='generated-layout'
 if p.stem=='allvend-infokiosk':
  source='https://skysend.ru/images/downloads/po/12_full.png';notes='Реальный архивный экран инфокиоска выделен из исходного strip через SVG viewport. Интерфейс не дорисован; подпись на странице сообщает об архивном статусе.';kind='generated-layout';section='software.allvend.infokiosk'
 if p.stem=='allvend-brand':
  source='https://skysend.ru/images/downloads/allvend.png';notes='Официальный растровый знак встроен в SVG, крупные прозрачные поля скрыты viewport. Геометрия и цвета не изменены.';kind='generated-layout';section='software.allvend.hero'
 if p.stem=='pos-capabilities':source='https://skysend.ru/program/software-for-pos-terminal.html'
 if p.stem=='finger-functions':source='https://skysend.ru/program/finger.html'
 if p.stem=='infokiosk-flow':source='https://skysend.ru/allvend.html'
 if p.stem.startswith('supplier-exchange'):source='https://skysend.ru/partners/suppliers/integration-in-xml.html'
 if p.stem=='report-flow':source='https://skysend.ru/partners/providers/automate-reporting.html'
 row={'id':'vector-'+p.stem,'source_url':source,'source_pages':[],'asset_type':kind,'path':rel,'width':svg.get('width'),'height':svg.get('height'),'svg_viewbox':svg.get('viewBox'),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'retrieved_date':'2026-09-10','download_status':'created-derived','production_status':'approved-original','recommended_section':section,'quality_notes':notes}
 m['assets']=[a for a in m['assets'] if a['id']!=row['id']];m['assets'].append(row)
ready=ROOT/'assets/ready/terminal-screen.png';ready.parent.mkdir(exist_ok=True)
source_asset=next(a for a in m['assets'] if a['source_url']=='https://skysend.ru/images/icon-other/pop-up-full.jpg')
shutil.copyfile(ROOT/source_asset['path'],ready)
ready_row={**source_asset,'id':'ready-terminal-screen','asset_type':'byte-identical-ready-copy','path':ready.relative_to(ROOT).as_posix(),'download_status':'copied-ready','derived_from':source_asset['id'],'quality_notes':'Побайтовая копия pop-up-full.jpg с правильным расширением PNG. SHA-256 совпадает с оригиналом. Для вёрстки использовать эту версию.'}
m['assets']=[a for a in m['assets'] if a['id']!='ready-terminal-screen']+[ready_row]
for a in m['assets']:
 fmt=a.get('image_format');a['actual_mime']={'PNG':'image/png','JPEG':'image/jpeg','WEBP':'image/webp','GIF':'image/gif'}.get(fmt)
 if a.get('path'):
  suffix=Path(a['path']).suffix.lower()
  if suffix=='.svg':a['actual_mime']='image/svg+xml'
  elif suffix=='.woff2':a['actual_mime']='font/woff2'
  elif suffix=='.txt':a['actual_mime']='text/plain'
  expected={'image/png':['.png'],'image/jpeg':['.jpg','.jpeg'],'image/webp':['.webp'],'image/gif':['.gif']}.get(a['actual_mime'])
  a['extension_mismatch']=bool(expected and suffix not in expected)
m['counts']={'ready_copies':sum(a['download_status']=='copied-ready' for a in m['assets']),'entries':len(m['assets']),'verified_downloads':sum(a['download_status']=='verified' for a in m['assets']),'derived_vectors':sum(a['download_status']=='created-derived' for a in m['assets']),'production_approved':sum(a['production_status']=='approved-original' for a in m['assets']),'source_with_review':sum(a['production_status']=='source-with-review' for a in m['assets']),'failed':sum(a['download_status']=='failed' for a in m['assets'])}
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
fields=['actual_mime','extension_mismatch','id','source_url','path','asset_type','width','height','bytes','download_status','production_status','recommended_section','quality_notes','sha256','provider_name','provider_category','source_pages']
with (ROOT/'data/assets-manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for a in m['assets']:w.writerow({**a,'source_pages':' | '.join(a['source_pages'])})
print(json.dumps(m['counts']))
