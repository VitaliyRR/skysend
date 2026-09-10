from pathlib import Path
from urllib.parse import urlparse,parse_qs,urljoin
from bs4 import BeautifulSoup
from PIL import Image
from collections import defaultdict
import requests,concurrent.futures,re,json,hashlib,io,csv
import xml.etree.ElementTree as ET
ROOT=Path.cwd();originals=ROOT/'assets/originals';originals.mkdir(parents=True,exist_ok=True)
review=ROOT/'evidence/skysend/asset-review';review.mkdir(parents=True,exist_ok=True)
provs=json.loads((ROOT/'data/providers-source.json').read_text(encoding='utf-8'))['providers']
found=defaultdict(set)
for f in (ROOT/'evidence/skysend/html').glob('*.html'):
 s=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
 for e in s.find_all(['img','a']):
  for a in ['src','data-src','href']:
   raw=e.get(a,'')
   if re.search(r'\.(jpg|jpeg|png|gif|svg|webp)([?#].*)?$',raw,re.I):
    u=urljoin('https://skysend.ru/',raw)
    if urlparse(u).netloc=='skysend.ru' and '/images/' in u:found[u].add(f.name)
provider_map={}
for p in provs:
 if p['logo_url']:
  u=p['logo_url'];found[u].add('providers.php');provider_map[u]=p
for u in list(found):
 if '/product/resized/' in u:
  full=re.sub(r'_\d+x(?=\.)','',u.replace('/resized/','/'));found[full].update(found[u])
extra=['/images/stories/virtuemart/product/beautyII4.png','/images/stories/virtuemart/product/FastPay Simple.png','/images/stories/virtuemart/product/scaner.png']
for u in extra:found[urljoin('https://skysend.ru',u)].add('verified-fullsize-derivative-url')

def choose(u):
 p=urlparse(u).path;name=p.split('/')[-1]
 if 'image.php?provider=' in u:return 'providers','provider-logo','originals'
 if '/product/' in p and '/resized/' not in p:return '', 'hardware-product','originals'
 if name in ['logo.png','logotip_skysend.svg','logotip_skysend.png','logotip_gk_svg.svg','logotip_finger.png','allvend.png','Logotip_SkyMarket_15x1.png','logotip_skymarket_3x1.png','logotip_skymarket_1,5x1.png','finger-logo.png']:
  return '', 'brand','originals'
 if '/screenshots/' in p and '/thumbnails/' not in p:return '', 'software-screenshot','originals'
 if name in ['pop-up-full.jpg','enter_the_number.jpg']:return '', 'software-screenshot','originals'
 if name=='banf.png':return '', 'provider-wall-reference','originals'
 if '/downloads/po/' in p and (re.match(r'^\d',name) or name=='to_whom.png'):return 'po', 'software-feature-reference','review'
 if name in ['cluster_skysend.jpeg','Shema-klasternoy-sistemy-SkySend.jpeg']:return '', 'architecture-reference','originals'
 if '/banners/' in p or '/slaider/' in p or '/khow/' in p:return '', 'excluded-reference','review'
 return '', 'excluded','none'

def collect(item):
 u,pages=item;sub,kind,dest=choose(u);name=urlparse(u).path.split('/')[-1]
 row={'id':'asset-'+hashlib.sha256(u.encode()).hexdigest()[:12],'source_url':u,'source_pages':sorted(pages),'asset_type':kind,'path':None,'width':None,'height':None,'bytes':None,'sha256':None,'retrieved_date':'2026-09-10','download_status':'not-downloaded','production_status':'excluded','recommended_section':None,'quality_notes':None}
 if kind=='provider-logo':
  p=provider_map[u];row.update({'provider_name':p['name'],'provider_category':p['category'],'recommended_section':'home.providers / providers.catalog','production_status':'approved-original','quality_notes':'Логотип из действующего публичного каталога SkySend. Не увеличивать выше исходного разрешения; сохранить цвета и пропорции. Существование в каталоге не подтверждает доступность платежей.'})
  name='provider-'+parse_qs(urlparse(u).query)['provider'][0]+'.png'
 elif kind=='hardware-product':row.update({'recommended_section':'home.equipment / equipment.catalog','production_status':'approved-original','quality_notes':'Оригинальная предметная фотография/рендер из каталога SkySend. Фактическое разрешение ограничивает размер вывода; не дорисовывать детали. Наличие товара и характеристики подтверждаются отдельно.'})
 elif kind=='brand':row.update({'recommended_section':'global.brand / software.brand','production_status':'approved-original','quality_notes':'Официальный оригинал. Для SkySend предпочтителен logotip_skysend.svg; не обводить растр заново.'})
 elif kind=='software-screenshot':row.update({'recommended_section':'home.software / software.detail','production_status':'approved-original' if name!='enter_the_number.jpg' else 'reference-only','quality_notes':'Реальный интерфейс с исходного сайта. Подписать как экран исходной версии; при релизе заменять только реальным новым screenshot.' if name!='enter_the_number.jpg' else 'Встроен блок «Плати без комиссии / FINGER». Только evidence: перед публикацией необходим реальный экран без промоблока.'})
 elif kind=='provider-wall-reference':row.update({'recommended_section':'home.providers','production_status':'reference-only','quality_notes':'Подтверждает исходный headline и связь с логотипами. Фиолетовый градиент, встроенный текст и старые бренды не переносить. Заменить DOM-композицией отдельных provider-logo.'})
 elif kind=='architecture-reference':row.update({'recommended_section':'software.xml / partners.providers','production_status':'reference-only','quality_notes':'Историческая схема для проверки смысла. Перерисовать в простую SVG схему с текстовым эквивалентом; не публиковать неподтверждённую актуальную топологию.'})
 elif kind=='software-feature-reference':row.update({'recommended_section':'software.allvend','production_status':'reference-only','quality_notes':'Исходная иллюстрация функции ПО. Требуется визуальный отбор: содержит прежние стили, товары и местами рекламу. Хранится только в evidence, не копировать целиком в production.'})
 elif kind=='excluded-reference':row['quality_notes']='Исторический баннер / акция / стоковая фотография / оформление. Хранится только в evidence для аудита; запрещён перенос в новый сайт.'
 else:row['quality_notes']='Нерелевантный раздел, дубль thumbnail, устаревшая декоративная иконка, промо либо служебная графика. Не входит в комплект для разработки.'
 if dest=='none':return row
 folder=(originals/sub) if dest=='originals' else (review/sub)
 folder.mkdir(parents=True,exist_ok=True)
 p=folder/name
 try:
  if not p.exists():
   r=requests.get(u,timeout=20);r.raise_for_status();blob=r.content
   if blob[:5].lower()==b'<html' or 'text/html' in r.headers.get('Content-Type',''):raise ValueError('HTML instead of image')
   p.write_bytes(blob)
  blob=p.read_bytes()
  if p.suffix.lower()=='.svg':
   svg=ET.fromstring(blob);row['svg_viewbox']=svg.get('viewBox')
   row['width']=svg.get('width');row['height']=svg.get('height')
  else:
   im=Image.open(io.BytesIO(blob));row['width'],row['height']=im.size;row['image_format']=im.format
  row.update(path=p.relative_to(ROOT).as_posix(),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),download_status='verified')
 except Exception as e:
  row['download_status']='failed';row['production_status']='unavailable';row['error']=str(e)[:250]
 return row

items=sorted(found.items());out=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
 for i,row in enumerate(pool.map(collect,items)):
  out.append(row)
  if (i+1)%100==0:print('processed',i+1,'/',len(items),flush=True)
for name,url,kind in [('InterVariable.woff2','https://rsms.me/inter/font-files/InterVariable.woff2','font'),('OFL.txt','https://raw.githubusercontent.com/rsms/inter/master/LICENSE.txt','font-license')]:
 p=ROOT/'assets/fonts'/name;b=p.read_bytes();out.append({'id':'font-'+name,'source_url':url,'source_pages':[],'asset_type':kind,'path':p.relative_to(ROOT).as_posix(),'width':None,'height':None,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'retrieved_date':'2026-09-10','download_status':'verified','production_status':'approved-original','recommended_section':'global.typography','quality_notes':'Официальный Inter; кириллица и латиница, OFL 1.1. Self-host, font-display: swap.'})
manifest={'schema_version':1,'source':'https://skysend.ru/','retrieved_date':'2026-09-10','note':'originals are byte-preserved source assets; approved-original denotes design suitability, not proof of current product/service availability. Evidence paths must never enter production bundle. Provider logos fetched from source-declared public HTTP endpoint; local copies avoid mixed content.','counts':{'entries':len(out),'verified':sum(x['download_status']=='verified' for x in out),'production_approved':sum(x['production_status']=='approved-original' for x in out),'failed':sum(x['download_status']=='failed' for x in out)},'assets':out}
(ROOT/'data/assets-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
fields=['id','source_url','path','asset_type','width','height','bytes','download_status','production_status','recommended_section','quality_notes','sha256','provider_name','provider_category','source_pages']
with (ROOT/'data/assets-manifest.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
 for x in out:w.writerow({**x,'source_pages':' | '.join(x['source_pages'])})
print(json.dumps(manifest['counts']))
