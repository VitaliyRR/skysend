from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlsplit
import json,csv,hashlib

src=json.loads(Path('data/source-pages.json').read_text(encoding='utf-8'))
pages=src['pages']
extra=json.loads(Path('data/extra-source-checks.json').read_text(encoding='utf-8'))
products=[
 {'slug':'fastpay-beauty-ii','title':'FastPay Beauty II','source_url':'https://skysend.ru/buy/payment-terminals/fastpay-beauty-1-detail.html','lead':'Киоск для помещений. Используется как информационный терминал, терминал заказа товаров, касса оплаты заказов и услуг или платёжный терминал.','facts':[('Назначение','Для помещений'),('Ширина','50 см'),('Высота','145 см'),('Масса','75 кг'),('Электропитание','220 В, 50 Гц'),('Потребляемая мощность','120 Вт'),('Сенсорная панель','17″')],'base_configuration':['Модем GPRS','Накопитель USB 2.0','Материнская плата Mini-ITX с процессором Intel','Блок питания ATX 300–350 W','Сенсорный экран KeeToutch 17″ USB','Монитор 17″'],'source_limits':['Глубина не указана в исходнике.','Купюроприёмник и термопринтер перечислены в конфигураторе как опции.','Возможности применения устройства не означают, что все лицензии и периферия входят в базовую поставку.']},
 {'slug':'fastpay-simple','title':'FastPay Simple','source_url':'https://skysend.ru/buy/payment-terminals/fastpay-simple-detail.html','lead':'Платёжный терминал для помещений с сенсорным экраном. Поставляется с предустановленным программным обеспечением.','facts':[('Назначение','Для помещений'),('Ширина','50 см'),('Высота','144 см'),('Глубина','38 см'),('Масса','80 кг'),('Электропитание','220 В, 50 Гц'),('Потребляемая мощность','120 Вт'),('Сенсорная панель','17″')],'base_configuration':['Купюроприёмник CashCode MVU1024 (б/у)','Модем 3G','Накопитель Pretec USB 2.0','Материнская плата Mini-ITX с процессором Intel','Блок питания ATX 300–350 W','Сенсорный экран KeeToutch 17″ USB','Монитор 17″ (б/у)','Citizen CTS-2000 (б/у)'],'source_limits':['Пометки «б/у» входят в исходную комплектацию и не удаляются.','В основном описании модем 3G, а в конфигураторе GPRS. Для таблицы используется основное описание; расхождение требует проверки.']}
]
for prod in products:
 e=next(x for x in extra if x['url']==prod['source_url'])
 s=BeautifulSoup(Path(e['html_path']).read_bytes(),'html.parser',from_encoding='utf-8')
 c=s.select_one('.productdetails-view') or s.select_one('#mainbody')
 prod['path']='/equipment/payment-terminals/'+prod['slug']+'/'
 prod['specification_caption']='Характеристики и комплектация из материалов SkySend. Комплектацию и условия поставки уточняйте у менеджера.'
 prod['cta']={'label':'Обсудить оборудование','href':'/contacts/'}
 prod['image_urls']=list(dict.fromkeys(urljoin(e['url'],i['src']) for i in c.select('img[src]') if 'virtuemart/product/' in i['src']))
 prod['visual']='Подлинное фото именно этой модели и размерные стрелки ширины/высоты. Глубину Beauty не дорисовывать. Таблица характеристик статична, галерея переключается вручную.'
 if not any(p['url']==e['url'] for p in pages):
  raw=Path(e['html_path']).read_bytes()
  tp='evidence/skysend/text/'+prod['slug']+'.txt'
  Path(tp).write_text(e['url']+'\n\n'+e['text'],encoding='utf-8')
  pages.append({'url':e['url'],'menu_label':prod['title'],'fetched_at':'2026-09-10','html_path':e['html_path'],'http_status':e['status'],'final_url':e['final_url'],'sha256':hashlib.sha256(raw).hexdigest(),'title':prod['title'],'meta_description':'','text':e['text'],'text_path':tp,'headings':[{'level':int(n.name[1]),'text':n.get_text(' ',strip=True)} for n in c.select('h1,h2,h3,h4')],'blocks':[{'id':f'b{n+1:03}','tag':x.name,'text':x.get_text(' ',strip=True)} for n,x in enumerate(c.select('p,li')) if x.get_text(' ',strip=True)],'images':[{'url':u,'alt':''} for u in prod['image_urls']],'links':[{'text':a.get_text(' ',strip=True),'url':urljoin(e['url'],a['href'])} for a in c.select('a[href]')],'downloads':[]})
categories=[]
for p in pages:
 if p['url'].startswith('https://skysend.ru/buy/') and not p['url'].endswith('-detail.html'):
  soup=BeautifulSoup(Path(p['html_path']).read_bytes(),'html.parser',from_encoding='utf-8')
  items=[]
  for n in soup.select('.product-list-item'):
   a=n.select_one('.prod-details h3 a');d=n.select_one('.desc');i=n.select_one('img.browseProductImage')
   if not a:continue
   old=urljoin(p['url'],a['href']);slug=urlsplit(old).path.rsplit('/',1)[-1].replace('-detail.html','')
   items.append({'id':slug,'name':a.get_text(' ',strip=True),'description':d.get_text(' ',strip=True) if d else '','image_url':urljoin(p['url'],i['src']) if i else None,'source_url':old,'category_source_url':p['url'],'public_cta':{'label':'Обсудить оборудование','href':'/contacts/'}})
  categories.append({'path':'/equipment/'+urlsplit(p['url']).path[5:].replace('.html','')+'/','title':p['menu_label'] or p['title'],'source_url':p['url'],'rows':items,'empty_copy':'Состав и условия поставки уточняйте у менеджера.' if not items else None})
for p in pages:
 p['content_status']='soft_404' if 'The page cannot be found.' in p.get('text','') else 'empty_main_content' if not p.get('text','').strip() else 'source_content'
for target in ['data/source-pages.json','evidence/skysend/pages.json']:
 Path(target).write_text(json.dumps(src,ensure_ascii=False,indent=2),encoding='utf-8')
out={'audit_date':'2026-09-10','products':products,'categories':categories,'policy':'Две полные карточки терминалов. Остальные компоненты как строки каталогов с названиями и описаниями из источника. Цены, наличие, корзина и конфигуратор не публикуются без актуальных коммерческих данных. Потребляемая мощность 120 Вт из спецификаций, без попытки согласовать старые рекламные месячные цифры.'}
Path('data/equipment-content.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
with Path('data/migration-map.csv').open(encoding='utf-8-sig',newline='') as f:mp=list(csv.DictReader(f))
for row in mp:
 if row['old_url'].endswith('/benefits.html'):row['new_url']='/#partners'
 if row['old_url'].endswith('/pravila-sistemy.html'):row['new_url']='/system-rules/'
 if any(row['old_url'].endswith(x) for x in ['belyaeva-olga-konstantinovna.html','lifanova-natalya-vladimirovna.html','starodub-igor-vladimirovich.html']):row.update(new_url='/about/team/',content_action='soft_404_consolidation',reason='Источник содержит soft 404; не создавать отсутствующую биографию')
 if any(row['old_url'].endswith(x) for x in ['203-connecting-terminals.html','201-business-mission-az.html']):row.update(new_url='',http_action='410',content_action='exclude',reason='Промо подключения/поездки исключено из нового архива')
for prod in products:
 if not any(r['old_url']==prod['source_url'] for r in mp):mp.append({'old_url':prod['source_url'],'new_url':prod['path'],'http_action':'301','content_action':'adapt_product','reason':'Точная карточка товара: характеристики и комплектация; цены только в evidence'})
for cat in categories:
 for item in cat['rows']:
  if not any(r['old_url']==item['source_url'] for r in mp):mp.append({'old_url':item['source_url'],'new_url':cat['path']+'#'+item['id'],'http_action':'301','content_action':'category_row','reason':'Сохраняется строка исходного каталога; отдельная непроверенная карточка не создаётся'})
with Path('data/migration-map.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(mp[0]));w.writeheader();w.writerows(mp)
append='\n## Оборудование: две полные карточки\n\nМашинная копия: `data/equipment-content.json`. Другие компоненты выводятся строками исходного каталога: название, описание, изображение, действие «Обсудить оборудование» → `/contacts/`. Не создавать выдуманные подробные карточки. Пометки «б/у» сохранять.\n\n'
for p in products:
 append+='### '+p['title']+' · `'+p['path']+'`\n\n'+p['lead']+'\n\n'+p['specification_caption']+'\n\n| Параметр | Значение |\n|---|---|\n'+''.join('| '+k+' | '+v+' |\n' for k,v in p['facts'])+'\n**Комплектация:**\n\n'+'\n'.join('- '+c for c in p['base_configuration'])+'\n\n**Действие:** «Обсудить оборудование» → `/contacts/`.\n\nВизуал: '+p['visual']+'\n\nИсточник: '+p['source_url']+'.\n\nСлужебные ограничения: '+' '.join(p['source_limits'])+'\n\n'
doc=Path('docs/03b-secondary-pages.md')
current=doc.read_text(encoding='utf-8').split('\n## Оборудование: две полные карточки')[0]
doc.write_text(current+append,encoding='utf-8')
print('Source pages',len(pages),'products',len(products),'category rows',sum(len(c['rows']) for c in categories),'migration',len(mp))
