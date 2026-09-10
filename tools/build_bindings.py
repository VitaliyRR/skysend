"""Deterministic section-to-asset bindings and navigation for implementation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def media(kind,paths,alt,*,max_css_width=640,sizes=None,note=''):
 return dict(kind=kind,paths=paths,alt=alt,max_css_width=max_css_width,
             export_widths=sizes or [360,720,1280],fit='contain',note=note)

terminal_screen='assets/ready/terminal-screen.png' if (ROOT/'assets/ready/terminal-screen.png').exists() else 'assets/originals/pop-up-full.jpg'
bindings={
 'software-catalog':media('data',['data/site-content.json'],'',note='HTML индекс семи страниц ПО; title/path, первый абзац и первый media из software-detail.'),
 'provider-catalog':media('data',['data/providers-source.json','data/assets-manifest.json'],'',note='Поиск по 600 исходным строкам и 13 категориям; labels и состояния из utility-content.json. Не считать логотипы услугами.'),
 'equipment-catalog':media('data',['data/equipment-content.json'],'',note='Две реальные модели и 24 строки категорий, без неподтверждённых цен и наличия.'),
 'fingerprint-scanner':media('image',['assets/originals/scaner.png'],'Сканер отпечатка из каталога оборудования SkySend',max_css_width=330,sizes=[330,503]),
 'html-feature-list':media('html',[],'',note='Definition list по visual_fields секции. Только реальные названия функций; без выдуманных показателей, строк транзакций и вида личного кабинета. Контракт в docs/08-content-components.md.'),
 'html-process':media('html',[],'',note='Отдельные подписанные узлы и связи из visual_nodes/visual_edges. Порядок и значения уже заданы секцией; не подставлять общую картинку. Контракт в docs08.'),
 'html-report-fields':media('html-and-svg',['assets/diagrams/report-flow.svg'],'Платежи за период, реестр, отчёт',note='HTML последовательность либо готовая схема. Не имитировать реальные суммы/платежи.'),
 'text-only':media('html',[],'',note='Наборный информационный блок: дата, имя, должность или источник. Не добавлять картинку другого предмета. Контент является самим визуальным элементом.'),
 'supplier-exchange':media('svg',['assets/diagrams/supplier-exchange.svg','assets/diagrams/supplier-exchange-mobile.svg'],'Обмен справочником и заказами между поставщиком, SkyMarket и терминалами или FINGER',note='Вторая версия для мобильной колонки. Не путать с XML-шлюзом оплаты провайдерам.'),
 'terminal-product':media('image',['assets/originals/beautyII4.png'],'Платёжный терминал FastPay Beauty II',max_css_width=260,sizes=[260,355],note='355×858 px. Без увеличения по пикселям; DPR2 ограничен исходником. Маркировка корпуса является частью исходной фотографии.'),
 'fastpay-product':media('image',['assets/originals/FastPay Simple.png'],'Платёжный терминал FastPay Simple',max_css_width=270,sizes=[270,425]),
 'terminal-screen':media('image',[terminal_screen],'Экран выбора услуг в терминальном ПО SkySend',max_css_width=803,sizes=[480,800,1440],note='Исходный .jpg содержит PNG bytes. Использовать MIME image/png; готовая копия имеет расширение png. Архивный экран, без новых обещаний о брендах.'),
 'provider-logos':media('collection',['data/provider-wall-selection.json'],'Примеры провайдеров из каталога SkySend',max_css_width=108,sizes=[150],note='Точный alt каждого логотипа = provider_name из selection. Сами файлы берутся по items[].path; независимая сетка, без движения.'),
 'interface-variants':media('svg',['assets/diagrams/interface-customization.svg'],'Два варианта интерфейса ПО SkySend',max_css_width=720,sizes=[360,720,1200],note='Видны только два верхних кадра исходного 8_full.png. Не ссылаться на полный исходник в lightbox.'),
 'commerce-flow':media('svg',['assets/diagrams/commerce-flow.svg','assets/diagrams/commerce-flow-mobile.svg'],'Загрузка справочника товаров, формирование заказов, оплата заказов',note='Вторая версия для mobile. HTML список шагов обязателен.'),
 'commerce-screen':media('reference-only',[],'Последовательность заказа товаров из старого ПО',note='Основной готовый визуал commerce-flow. 11_full.png только в исследовательском архиве; не нужен для релиза. Готовый статический сценарий полностью покрывает смысл.'),
 'infokiosk-screen':media('svg',['assets/diagrams/allvend-infokiosk.svg'],'Реальный архивный экран ALLVEND в режиме информационного киоска',note='Композиция использует только экран инфокиоска из исходного 12_full.png. Это архивный пример интерфейса, а не обещание текущей темы.'),
 'allvend-brand':media('svg',['assets/diagrams/allvend-brand.svg'],'ALLVEND',max_css_width=560,sizes=[320,560],note='Оригинальный знак ALLVEND в SVG viewport с удалёнными пустыми полями исходного PNG.'),
 'partner-routes':media('navigation',['assets/icons/arrow-right.svg','assets/originals/RMA_win_lin.png','assets/diagrams/supplier-exchange.svg','assets/originals/beautyII4.png','assets/diagrams/payment-network.svg','assets/diagrams/xml-flow.svg'],'',note='Шесть ссылок из navigation.json. Каждая плитка использует связанный с направлением продукт, экран или схему; плитка провайдеров собирается из оригинальных логотипов.'),
 'contact-panel':media('html-and-svg',['assets/diagrams/contact-panel.svg'],'Телефон, электронная почта и Telegram поддержки SkySend',note='В production контактные значения и ссылки выводить HTML, SVG иллюстрирует расположение. Телефон и email копируемые.'),
 'rma-desktop':media('image',['assets/originals/RMA_win_lin.png'],'Рабочее место Агента SkySend на компьютере',max_css_width=960,sizes=[480,960,1920]),
 'rma-android':media('image',['assets/originals/RMA_android.jpg'],'РМА SkySend для Android',max_css_width=260,sizes=[260,308],note='308×545 px. Только один экран, не выдумывать остальные состояния.'),
 'xml-flow':media('svg',['assets/diagrams/xml-flow.svg'],'Обмен между системой Агента, SkySend и провайдерами',note='Схема направления обмена, не backend topology и не образец wire payload.'),
 'payment-network':media('svg',['assets/diagrams/payment-network.svg'],'Терминалы, кассир и смартфон связаны с провайдерами через SkySend',note='Концептуальная схема, не карта фактических адресов и серверов.'),
 'pos-product':media('svg',['assets/diagrams/pos-capabilities.svg'],'Штрих-Mobile Pay PRO: аккумулятор и GPRS-модем',note='Условная схема возможностей. Фото POS отсутствует в источнике; не подставлять другую модель.'),
 'finger-product':media('svg',['assets/diagrams/finger-functions.svg'],'FINGER: платежи, шаблоны платежей и выписка',note='Реальный логотип и схема функций, без выдуманного экрана.'),
 'finger-brand':media('image',['assets/originals/logotip_finger.png'],'FINGER',max_css_width=260,sizes=[260,520],note='Оригинальный логотип FINGER из материалов SkySend.'),
 'download-list':media('data',['data/download-catalog.json','assets/icons/document.svg'],'',note='Названия файлов, форматы, версии и ссылки из каталога; оформление HTML-строками.'),
 'brand':media('svg',['assets/brand/skysend-logo.svg'],'SkySend',max_css_width=104,sizes=[],note='Исходные векторные пути и цвета, скорректирован только viewBox.'),
}
out=dict(version=1,bindings=bindings,
         policy='Only resolved bindings and approved manifest items enter production. Never recursively publish assets/, evidence/ or data/ as a public directory.',
         layout_contract=dict(hero={'desktop':{'imageHeight':510,'textColumns':5,'gapColumns':1,'imageColumns':6},'mobile':{'imageHeight':360}},
                              image_pipeline='Use width/height attributes, srcset, contain; no AI upscale. Derive sizes no larger than source. SVG files are already editable source.'),
         authoring_notice='Illustrative diagrams do not assert measured service speed, financial returns, uptime, or current availability of pictured services.')
(ROOT/'data/section-assets.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
software_links=[('Терминальное ПО','/software/terminal/'),('РМА Windows / Linux','/software/rma-desktop/'),('РМА Android','/software/rma-android/'),('XML-шлюз','/software/xml/'),('ПО для POS-терминала','/software/pos/'),('Приложение FINGER','/software/finger/'),('ПО ALLVEND','/software/allvend/')]
partner_links=[
 ('Платёжным агентам','/partners/agents/','assets/originals/RMA_win_lin.png','Рабочее место платёжного агента'),
 ('Провайдерам услуг','/partners/providers/','provider-logos','Логотипы провайдеров SkySend'),
 ('Поставщикам товаров','/partners/suppliers/','assets/diagrams/supplier-exchange.svg','Обмен справочником товаров и заказами'),
 ('Торговым сетям','/partners/retail/','assets/originals/beautyII4.png','Терминал самообслуживания в торговой точке'),
 ('Представителям','/partners/representatives/','assets/diagrams/payment-network.svg','Сеть приёма платежей SkySend'),
 ('Шлюзовикам','/partners/gateways/','assets/diagrams/xml-flow.svg','Подключение по XML-протоколу'),
]
nav=dict(primary=[{'id':'partners','label':'Партнёрам','href':'/partners/agents/','children':'partners'},
                  {'id':'software','label':'ПО','href':'/software/terminal/','children':'software'},
                  *[{'label':a,'href':b} for a,b in [('Оборудование','/equipment/'),('Провайдеры','/providers/'),('Поддержка','/support/')]]],
    actions=[{'label':'Вход | Регистрация','href':'/connect/'}],
    partners=[{'label':a,'href':b,'visual':visual,'visual_alt':alt} for a,b,visual,alt in partner_links],
    software=[{'label':a,'href':b} for a,b in software_links],
    footer=[{'label':a,'href':b} for a,b in [('Терминальное ПО','/software/terminal/'),('Скачать','/downloads/'),('О системе','/about/'),('Контакты','/contacts/'),('Правила системы','/system-rules/')]],
    contact_defaults={'phone':'+7 (800) 555-25-36','phoneHref':'tel:+78005552536','officePhone':'+7 (861) 201-12-21','supportEmail':'support@inf-sys.ru','salesEmail':'sales@inf-sys.ru','telegram':'https://t.me/infsysgroup','addressText':'Адрес офиса уточняйте по телефону'},
    external_accounts={'registration':{'href':'https://cluster.skysend.ru:6716/#/','verification':'TLS verification failed during source audit'},'login':{'href':'https://control.skysend.ru:6710','verification':'Source form action. DNS lookup failed during audit; GET login behavior not confirmed'},'source':'https://skysend.ru/exit.php?ml=1','fallback':'Use /connect/#existing with support channels; no password form or proxy for credentials in this site.'})
(ROOT/'data/navigation.json').write_text(json.dumps(nav,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Created {len(bindings)} asset bindings and navigation')
