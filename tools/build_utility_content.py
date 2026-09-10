from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
downloads=json.loads((ROOT/'data/download-catalog.json').read_text(encoding='utf-8'))
def sec(id,title,body,visual,source,links=None,collection=None):
 return dict(id=id,title=title,body=body,visual_id=visual,source_urls=[source],links=links or [],motion_alias='none',collection=collection)
def page(path,title,lead,sections):return dict(path=path,title=title,lead=lead,sections=sections)
rules=next(x for x in downloads['items'] if x['source_title']=='Правила системы SkySend')
pages=[
page('/providers/','Провайдеры услуг','В каталоге представлены услуги федеральных и местных поставщиков.',[
 sec('catalog','Каталог провайдеров','Данные каталога SkySend от 10 сентября 2026 года.', 'provider-catalog','https://skysend.ru/providers.php',collection={'file':'data/providers-source.json','array':'providers','categories':'categories','filter':['name','category_id'],'countPolicy':'actual filtered array length'}),
 sec('support','Информация об услугах','Доступность услуги уточняйте в службе поддержки.', 'contact-panel','https://skysend.ru/about/feedback.html',[{'label':'Поддержка','href':'/support/'}])]),
page('/downloads/','Скачать','ПО, инструкции и документы системы SkySend.',[
 sec(g['id'],g['title'],'','download-list','https://skysend.ru/download.html',collection={'file':'data/download-catalog.json','array':'items','filter':'group='+g['id']}) for g in downloads['groups']]),
page('/equipment/','Оборудование','Платёжные терминалы и комплектующие.',[
 sec('terminals','Платёжные терминалы','','equipment-catalog','https://skysend.ru/buy/payment-terminals.html',collection={'file':'data/equipment-content.json','display':'Named product photographs and exact source characteristics. No unverified price/stock.'}),
 sec('accessories','Комплектующие терминалов','','equipment-catalog','https://skysend.ru/buy/accessories.html',collection={'file':'data/equipment-content.json','display':'Category rows; one exact source product per row, preserve used-part flags.'}),
 sec('contact','Обсудить оборудование','Свяжитесь с SkySend по вопросам оборудования.','contact-panel','https://skysend.ru/about/geografiy.html',[{'label':'Контакты','href':'/contacts/'}])]),
page('/system-rules/','Правила системы SkySend','Откройте документ с правилами системы SkySend.',[
 sec('document','Правила системы SkySend','PDF-документ из раздела загрузок SkySend.','download-list',rules['source_page'],[{'label':'Открыть PDF','href':rules['target_url']},{'label':'Все документы системы','href':'/downloads/#system-documents'}],collection={'file':'data/download-catalog.json','itemId':rules['id'],'statusPolicy':'Do not state current legal revision; preserve source file without rewriting.'})])
]
data=dict(version=1,date='2026-09-10',pages=pages,ui={'providerSearchPlaceholder':'Название провайдера','allCategories':'Все категории','resultCount':'Найдено: {count}','emptyResults':'По вашему запросу ничего не найдено','resetFilters':'Сбросить фильтры'},policy='Administrative copy labels are new UI text; product facts remain source-based. Collection references identify the exact supplied data, not future APIs.')
(ROOT/'data/utility-content.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Created 4 utility page contracts')
