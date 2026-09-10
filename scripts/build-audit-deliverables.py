from pathlib import Path
from urllib.parse import urlsplit
import json,csv,re
from bs4 import BeautifulSoup
root=Path('.');file=root/'data/source-pages.json';data=json.loads(file.read_text(encoding='utf-8'));pages=data['pages']
textdir=root/'evidence/skysend/text';textdir.mkdir(parents=True,exist_ok=True)
for p in pages:
 html=BeautifulSoup(Path(p['html_path']).read_bytes(),'html.parser',from_encoding='utf-8')
 scope=html.select_one('#k2Container .itemBody') or html.select_one('#yoo-zoo') or html.select_one('#content') or html
 emails=[]
 for c in scope.select('.cloaked_email'):
  def decode(n):
   bef=''.join(str(v) for k,v in n.attrs.items() if k.startswith('data-ep-a'))
   aft=''.join(str(v) for k,v in n.attrs.items() if k.startswith('data-ep-b'))
   return bef+''.join(decode(x) for x in n.find_all('span',recursive=False))+aft
  email=decode(c)
  if '@' in email and email not in emails:emails.append(email)
 p['decoded_emails']=emails
 p['forms']=[{'action':f.get('action'),'method':f.get('method','get'),'fields':[{'type':x.get('type',x.name),'label':x.get('placeholder') or x.get('title') or x.get('aria-label') or ''} for x in f.select('input:not([type="hidden"]),textarea,select')]} for f in scope.select('form')]
 p['text_path']='evidence/skysend/text/'+Path(p['html_path']).stem+'.txt'
 Path(p['text_path']).write_text(p['url']+'\n'+p['title']+'\n\n'+p.get('text','')+ ('\n\nE-mail из HTML: '+', '.join(emails) if emails else ''),encoding='utf-8')
file.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');Path('evidence/skysend/pages.json').write_text(file.read_text(encoding='utf-8'),encoding='utf-8')
software={'terminal-software':'terminal','rma-pc':'rma-desktop','rma-android':'rma-android','xml-gateway':'xml','software-for-pos-terminal':'pos','finger':'finger'}
about={'our-goals':'goals','history':'history','geografiy':'/contacts/','providers':'/providers/','news':'news','feedback':'/support/','leaders':'team','jobs':'careers'}
partners={'agent':'agents','providers':'providers','suppliers':'suppliers','representatives':'representatives','gateway':'gateways'}
benefits={'highest-award':'income','lower-costs':'cost-reduction','stable-job':'stable-work','exclusive-innovations':'innovation','the-high-speed':'/partners/gateways/#highspeed','protection-of-data':'/partners/providers/#privacy-policy','online-support':'/support/'}
rows=[]
for p in pages:
 old=p['url'];path=urlsplit(old).path;slug=path.rsplit('/',1)[-1].replace('.html','');action='301'; content='adapt';reason='Сохранить смысл; очистить оформление и промо'
 if path=='/':new='/';action='200';content='restructure';reason='Новая главная без акций, рекламных баннеров и ленты новостей'
 elif path=='/autorally.html' or '/partners/advertisers/' in path or path=='/about/news/76-sweetstock.html':new='';action='410';content='exclude';reason='Акция, промо-кампания или рекламный раздел исключён по заданию'
 elif path=='/partners.html':new='/partners/'
 elif path.startswith('/partners/'):
  parts=path.strip('/').split('/');base='/partners/'+partners.get(parts[1],parts[1])+'/'
  new=base if slug in ['information','predstavitelyam'] else base+'#'+slug
  if slug in ['income','high-reward','dealer-discounts','items-of-income','running-banks-fps','increase-sales']:reason='Убрать обещания процентов/скидок; сохранить только проверяемый механизм/формат работы'
 elif path=='/allvend.html':new='/software/allvend/';reason='Сохранить продукт и функции; исключить рекламные модули, акции, старые цены и обещания'
 elif path=='/trading.html' or '/component/k2/item/16.html' in path:new='/partners/retail/'
 elif path=='/program.html':new='/software/';reason='Программы переименовать в ПО'
 elif path.startswith('/program/'):new='/software/'+software[slug]+'/'
 elif path=='/buy.html':new='/equipment/'
 elif path.startswith('/buy/'):new='/equipment/'+path[5:].replace('.html','')+'/'
 elif path=='/download.html' or path.startswith('/download/'):new='/downloads/';content='consolidate';reason='Единый реестр 122 материалов, фильтры; убрать промо, проверить версии и ссылки'
 elif path=='/benefits.html':new='/partners/agents/';content='consolidate';reason='Преимущества разобрать по продуктовым механизмам в страницах партнёров'
 elif path.startswith('/benefits/'):
  dest=benefits.get(slug,slug);new=dest if dest.startswith('/') else '/partners/agents/#'+dest;content='consolidate';reason='Дублирующую статью объединить с профильной секцией; снять абсолютные обещания'
 elif path=='/about.html':new='/about/'
 elif path.startswith('/about/leaders/'):new='/about/team/#'+slug;reason='Сохранить в архиве; должности и биографии не выдавать за актуальные без проверки'
 elif path.startswith('/about/news/'):
  new='/about/news/#'+slug;content='dated_archive';reason='Сохранить исходную дату и факт; не выводить в главную и промо-ленты'
 elif path.startswith('/about/'):
  dest=about[slug];new=dest if dest.startswith('/') else '/about/'+dest+'/'
 elif path=='/pravila-sistemy.html':new='/downloads/#rules';reason='Юридический документ; актуальную редакцию публиковать после проверки'
 else:new='';action='review';reason='Необходимо ручное сопоставление'
 rows.append({'old_url':old,'new_url':new,'http_action':action,'content_action':content,'reason':reason})
with Path('data/migration-map.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('pages',len(pages),'migration',len(rows),'review',[r for r in rows if r['http_action']=='review'])
mainpaths=['/','/program.html','/program/terminal-software.html','/program/rma-pc.html','/program/rma-android.html','/program/xml-gateway.html','/program/software-for-pos-terminal.html','/program/finger.html','/partners/agent/information.html','/partners/providers/information.html','/partners/suppliers/information.html','/partners/representatives/predstavitelyam.html','/partners/gateway/information.html','/partners/agent/remote-control.html','/partners/agent/stable-work.html','/about/our-goals.html','/about/feedback.html']
report='''# Аудит текущего сайта SkySend\n\nДата снятия: 10 сентября 2026. Источник: https://skysend.ru/. Это аудит содержимого источника, а не подтверждение актуальности коммерческих условий.\n\n## Охват и метод\n\nСохранены 123 HTML-страницы: все уникальные URL главного меню, главная, основные связанные материалы, 11 страниц каталога загрузок. Каждый ответ получил HTTP 200 при проверке. Это не означает, что все функции страницы или внешние файлы работают. По каждому URL сохранены HTML, SHA-256, заголовки, точный основной DOM-текст, блоки с ID, изображения, ссылки, файлы и формы. Повторяющиеся меню и футер исключены из основного текста. Текст, встроенный в картинки, отдельно исследуется визуально в комплекте ассетов.\n\n- Машинный источник: `data/source-pages.json` и копия `evidence/skysend/pages.json`.\n- Читаемый точный текст каждой страницы: `evidence/skysend/text/`.\n- Карта переходов: `data/migration-map.csv`.\n- Все 122 карточки скачивания: `data/downloads-source.json`.\n- Динамический публичный справочник: `data/providers-source.json`, 600 записей, 13 категорий.\n- Проверка служебных ссылок: `data/service-link-checks.json`.\n\nВ `blocks` исходная пунктуация, регистр и факты сохранены. `text` разворачивает DOM в строки, поэтому слова внутри ссылок могут оказаться на разных строках. Поля `decoded_emails` восстановлены из доступных HTML data-атрибутов защиты от спама. Формы не отправлялись.\n\n## Основные блоки старой главной\n\n| Порядок | Содержимое источника | Решение |\n|---|---|---|\n| 1 | Шапка: логотип, телефон, вход/регистрация, большое многоуровневое меню | Компактная шапка; «Программы» → «ПО» |\n| 2 | Автопереключаемый слайдер: `po5.jpg`, акция `0_first.jpg` → `76-sweetstock.html`, поставщики `banf.png`, `2.jpg` | Убрать слайдер и промо. Функциональный смысл ПО и поставщиков использовать в самостоятельных секциях |\n| 3 | «ВЫСОКИЕ СТАВКИ ВОЗНАГРАЖДЕНИЯ», «ЭКОНОМИЯ 50% НА ОБСЛУЖИВАНИИ», «НЕТ УДЕРЖАНИЙ И СКРЫТЫХ КОМИССИЙ» | Не переносить неподтверждённые обещания в hero |\n| 4 | Шесть входов: «Платежным агентам», «Провайдерам услуг», «Поставщикам товаров», «Торговым сетям», «Представителям», «Шлюзовикам» | Сохранить шесть аудиторий; заменить стоковые картинки предметным визуалом |\n| 5 | Новости 15.05.2024, 24.02.2024, 10.10.2022, 29.09.2022 | Убрать с главной. Непромо-материалы сохранить датированным архивом |\n| 6 | «Продажа товаров и услуг», «Реклама продукции и акций», «Режим инфокиоска» | Сохранить торговые и информационные функции ПО; рекламу и акции удалить |\n| 7 | «Изменение цветов и фона», «Смена положений и форм элементов», «Перестроение логики работы ПО» | Секция настройки интерфейса с реальными скриншотами |\n| 8 | «Загрузка справочника товаров», «Формирование заказов», «Оплата заказов» | Секция заказа товаров с тремя связанными экранами |\n| 9 | Реклама: «Видео», «SMS», «Баннер», «Чек» | Полностью исключить |\n| 10 | Футер: другие сайты группы, статьи, загрузки, контакты | Краткий навигационный футер, проверенные ссылки и контакты |\n\nГлавная опирается на большой объём текста внутри растровых баннеров. Полный редизайн нельзя делать только по HTML-тексту. В новом сайте заголовки и подписи нужно вынести в живой текст, а визуал собирать из исходных изображений продуктов и интерфейсов.\n\n## Структура источника\n\nВерхний уровень: ПО ALLVEND, Автопробег, Партнерам, Купить, Преимущества, Программы, Скачать, О системе. Партнёрские страницы разбиты на множество коротких статей; одни и те же механизмы повторяются в «Преимуществах», ПО и страницах разных аудиторий.\n\nНовая структура консолидирует эти материалы, но сохраняет адреса через карту 301 и устойчивые якоря. Промо без смыслового эквивалента получает 410, без редиректа на главную.\n\n## Исключения и конфликтующие данные\n\n1. Полностью исключить `/autorally.html`, `/about/news/76-sweetstock.html`, `/partners/advertisers/*`, промо-баннеры и рекламные CTA. В ALLVEND исключить рекламные модули, блоки бесплатных услуг и ценовые примеры. В загрузках скрыть рекламные предложения/договоры из нового публичного каталога.\n2. «Более 5000» есть в title, страницах агентов, шлюза и ALLVEND. Публичный endpoint `/providers.php` вернул 600 записей услуг и 13 категорий. Эти величины могут описывать разный охват. Не подменять 5000 числом 600 и не объявлять 5000 проверенным на 2026. Steam в полученном справочнике не найден; логотип в старом баннере не подтверждает текущую доступность оплаты.\n3. Главная и общий футер: 350049, Краснодар, Монтажников, 1/4. Контакты: Краснодар, Красных Партизан, 218; внутри указан индекс 352500, а во всплывающем контакте 350049. До проверки использовать «Адрес офиса уточняйте по телефону».\n4. Шапка и контакты: +7 (800) 555-25-36; POS и часть старых статей поддержки: +7 (800) 200-25-36. Для новой версии использовать номер из текущей шапки, конфликт не замалчивать.\n5. `/about/geografiy.html`: `sales@inf-sys.ru`, `support@inf-sys.ru`. `/about/feedback.html`: `support@isg.dev`, Telegram `@infsysgroup`. Новый контактный слой должен явно выбрать источник; не смешивать адреса случайным образом.\n6. На старом сайте встречаются гарантии 50% снижения расходов, 20% роста доходов, «самое высокое вознаграждение в стране», 1000 транзакций/сек, «ни единого сбоя за 11 лет», «5 степеней криптозащиты», старые цены и сроки. В новом тексте использовать конкретные механизмы: удалённое управление, обновления, справочники, XML, отчётность. Числа и абсолютные утверждения не превращать в актуальные обещания.\n7. Новость 10.10.2022 сообщает о прекращении поддержки ПО 5-го поколения 10.12.2020. В загрузках одновременно есть демообраз v. 5.45 из `/old/`, РМА 5.24, POS 1.1. Не называть их автоматически последними версиями.\n8. В карточке «Установка и эксплуатация РМА Linux» в каталоге нет ссылки. `Play Market`/`App Store` в тексте FINGER не гарантируют наличие актуального приложения: магазинные CTA проверять отдельно.\n9. Регистрационный URL `https://cluster.skysend.ru:6716/agent.php` не прошёл проверку цепочки TLS в среде аудита (`unable to get local issuer certificate`). Не утверждать, что регистрация не работает везде; интеграцию нужно проверить в целевой среде. Пароли и формы не отправлялись.\n10. `map.php` содержит Yandex Maps и поиск `skysend`, а не выгрузку координат всех терминалов. Нельзя рисовать выдуманные точки сети. Ссылки логотипов провайдеров идут по HTTP на порт 6721, встречаются пустые src и некорректные сайты `http://`, `http://нет`. Нужны локальные ассеты и валидация URL.\n11. Биографии руководства, вакансии, реквизиты, банковские сведения и контакты дилеров сохранены как исходные сведения; актуальность не установлена. Их нельзя обновлять догадками. Юридические документы не редактировать стилистически.\n\n## Точные тексты ключевых страниц\n\nНиже приведён исходный основной текст. Это материал для сопоставления; рекламные обещания и старые сведения не являются утверждённой копией нового сайта. Полный текст всех остальных страниц находится по ссылкам в реестре ниже.\n\n'''
for p in pages:
 if urlsplit(p['url']).path in mainpaths:
  report+='### '+(p['menu_label'] or p['title'] or p['url'])+'\n\nИсточник: '+p['url']+'\n\n'
  report+='```text\n'+p['text']+'\n```\n\n'
report+='## Реестр всех обследованных страниц\n\n| Источник | Заголовок | Точный текст | Новый адрес / действие |\n|---|---|---|---|\n'
for p,r in zip(pages,rows):
 title=(p['menu_label'] or p['title']).replace('|','/')
 report+='| ['+urlsplit(p['url']).path+(('?'+urlsplit(p['url']).query) if urlsplit(p['url']).query else '')+']('+p['url']+') | '+title+' | [TXT](../'+p['text_path']+') | '+(r['new_url'] or '410')+' |\n'
Path('docs/01-current-site-audit.md').write_text(report,encoding='utf-8')
print('report chars',len(report),'decoded support',[p['decoded_emails'] for p in pages if 'feedback' in p['url']])
