"""Create portable SVG design boards from actual SkySend assets. No raster edits."""
from pathlib import Path
import base64, html, json, mimetypes
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design'; OUT.mkdir(exist_ok=True)
C={'ink':'#111315','muted':'#5F6368','blue':'#0066B3','gray':'#F4F5F6','line':'#D9DDE1','white':'#FFFFFF'}

class Board:
 def __init__(self,w,h,title):
  self.w=w; self.h=h
  self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">Дизайн-макет SkySend. Реальные изображения продуктов и провайдеров из исходного сайта. Полный текст доступен в спецификации.</desc>',
   '<style>@font-face{font-family:Inter;src:url(data:font/woff2;base64,'+base64.b64encode((ROOT/'assets/fonts/InterVariable.woff2').read_bytes()).decode()+')}text{font-family:Inter,Arial,sans-serif} .small{font-size:14px}</style>',f'<rect width="{w}" height="{h}" fill="white"/>']
 def rect(self,x,y,w,h,fill,rx=0,stroke=None):
  self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" rx="{rx}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')
 def text(self,x,y,lines,size=20,fill=None,weight=400,lh=None):
  if isinstance(lines,str): lines=[lines]
  lh=lh or round(size*1.25)
  for i,l in enumerate(lines): self.s.append(f'<text xml:space="preserve" x="{x}" y="{y+i*lh}" font-size="{size}" font-weight="{weight}" fill="{fill or C["ink"]}">{html.escape(l)}</text>')
 def line(self,x1,y1,x2,y2,color=None):self.s.append(f'<path d="M{x1} {y1}H{x2}" stroke="{color or C["line"]}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color or C["line"]}"/>')
 def arrow(self,x,y,color=None): self.s.append(f'<path d="M{x} {y}h20m-7-7 7 7-7 7" fill="none" stroke="{color or C["blue"]}" stroke-width="1.7"/>')
 def image(self,path,x,y,w,h):
  p=ROOT/path
  if not p.exists(): raise FileNotFoundError(p)
  raw=p.read_bytes()
  mime='image/png' if raw.startswith(b'\x89PNG') else ('image/jpeg' if raw.startswith(b'\xff\xd8') else mimetypes.guess_type(str(p))[0] or 'image/png')
  uri=f'data:{mime};base64,'+base64.b64encode(raw).decode()
  self.s.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" xlink:href="{uri}"/>')
 def button(self,x,y,label,primary=True,w=178):
  self.rect(x,y,w,46,C['ink'] if primary else 'none',24,None if primary else '#7A8085')
  self.text(x+22,y+29,label,16,'white' if primary else C['ink'],500)
 def link(self,x,y,label,white=False,size=16):
  self.text(x,y,label,size,'white' if white else C['blue'],500)
 def save(self,name):
  (OUT/name).write_text('\n'.join(self.s+['</svg>']),encoding='utf-8')

logos=json.loads((ROOT/'data/provider-wall-selection.json').read_text(encoding='utf-8'))['items']
ui='assets/originals/pop-up-full.jpg'
variants='assets/diagrams/interface-customization.svg'
beauty='assets/originals/beautyII4.png'; fastpay='assets/originals/FastPay Simple.png'
brand='assets/brand/skysend-logo.svg'

b=Board(1440,4620,'SkySend: главная, desktop 1440 px')
b.image(brand,80,8,92,56)
b.text(270,43,'Партнёрам      ПО      Оборудование      Провайдеры      Поддержка',15,weight=500)
b.text(1100,43,'Войти',15); b.button(1195,15,'Подключиться',w=166)
b.line(0,72,1440,72)
b.rect(0,73,1440,639,C['gray'])
b.text(80,239,['Система приёма','платежей SkySend'],56,weight=600,lh=62)
b.text(80,392,['SkySend предоставляет возможность совершать','оплаты в пользу более 5 000 поставщиков услуг.'],20,C['muted'],lh=30)
b.button(80,479,'Подключиться',w=183); b.button(278,479,'Посмотреть ПО',False,w=190)
b.image(beauty,938,133,235,510)
b.text(902,690,'Платёжный терминал Beauty',13,C['muted'])
b.text(80,832,['Более 5 000','провайдеров услуг'],40,weight=600,lh=47)
b.text(80,955,['Оплата услуг федеральных','и местных поставщиков.'],20,C['muted'],lh=29)
b.link(80,1040,'Провайдеры услуг'); b.arrow(248,1034)
for i,item in enumerate(logos): b.image(item['path'],680+(i%4)*160,752+(i//4)*94,108,70)
b.rect(0,1142,1440,740,C['ink'])
b.text(80,1250,['Терминальное','ПО'],44,'white',600,52)
b.text(80,1380,['Универсальное программное','обеспечение для платёжных','и информационных терминалов.'],19,'#CCD1D5',lh=29)
b.text(80,1506,['ПО предустанавливается на flash-','накопитель и содержит модуль','обнаружения и настройки','периферийных устройств.'],18,'#CCD1D5',lh=27)
b.link(80,1680,'Подробнее о терминальном ПО',True)
b.image(ui,557,1217,803,602)
b.text(557,1840,'Интерфейс ПО SkySend',13,'#CCD1D5')
b.text(80,1980,'Изменение цветов и фона',40,weight=600)
b.image(variants,80,2030,630,479)
b.text(802,2090,['Меняйте расположение, размеры','и форму элементов экранов,','а также логику работы ПО.'],24,lh=34)
b.text(802,2250,['Настройка дизайна производится','через онлайн-кабинет','курирующим менеджером.'],19,C['muted'],lh=29)
b.link(802,2420,'Возможности интерфейса');b.arrow(1033,2415)
b.text(80,2536,'Варианты интерфейса из материалов SkySend',13,C['muted'])
b.rect(0,2580,1440,416,C['gray'])
b.text(80,2670,'Продажа товаров и услуг',40,weight=600)
b.text(80,2720,'Модуль формирования заказов на устройствах самообслуживания.',20,C['muted'])
for i,(num,lines) in enumerate([('01',['Загрузка справочника','товаров']),('02',['Формирование','заказов']),('03',['Оплата','заказов'])]):
 x=80+i*437
 b.text(x,2800,num,14,C['blue'],600);b.text(x,2840,lines,23,weight=500,lh=29)
 if i<2:b.arrow(x+365,2836)
b.link(80,2951,'Поставщикам товаров');b.arrow(288,2946)
b.text(80,3090,'Партнёрам',40,weight=600)
routes=[('Платёжным агентам','Терминалы и операторские точки'),('Провайдерам услуг','Точки оплаты ваших услуг'),('Поставщикам товаров','Справочник и заказы'),('Торговым сетям','Устройства самообслуживания'),('Представителям','Подключение участников системы'),('Шлюзовикам','Работа по XML-протоколу')]
for i,(title,subtitle) in enumerate(routes):
 x=80+(i%2)*665;y=3160+(i//2)*114
 b.line(x,y-26,x+615,y-26);b.text(x,y+8,title,24,weight=500);b.text(x,y+42,subtitle,16,C['muted']);b.arrow(x+585,y+4)
b.rect(0,3520,1440,650,C['gray'])
b.text(80,3610,'Платёжные терминалы',40,weight=600);b.link(1212,3600,'Оборудование')
b.image(beauty,360,3665,173,418);b.image(fastpay,920,3665,214,418)
b.text(382,4127,'Beauty',20,weight=500);b.text(940,4127,'FastPay Simple',20,weight=500)
b.text(80,4260,'Круглосуточная поддержка',36,weight=600)
b.text(80,4310,'Сведения о продуктах, руководства и обновления.',18,C['muted'])
b.text(850,4260,'+7 (800) 555-25-36',28,weight=500);b.link(850,4310,'Telegram: @infsysgroup',size=20)
b.link(80,4360,'Поддержка');b.line(80,4400,1360,4400)
b.image(brand,80,4440,104,66)
b.text(275,4470,'ПО     Скачать     О системе     Контакты     Правила системы',15)
b.text(275,4514,'sales@inf-sys.ru     support@inf-sys.ru',15,C['muted'])
b.text(80,4582,'© SkySend. Группа компаний «Информ-Системы».',13,C['muted'])
b.save('home-desktop.svg')

m=Board(390,5010,'SkySend: главная, mobile 390 px')
m.image(brand,20,7,75,48);m.text(276,37,'Меню',15,weight=500);m.line(337,24,365,24,C['ink']);m.line(337,34,365,34,C['ink']);m.line(337,44,365,44,C['ink'])
m.rect(0,64,390,766,C['gray'])
m.text(20,142,['Система приёма','платежей','SkySend'],36,weight=600,lh=40)
m.text(20,295,['SkySend предоставляет возможность','совершать оплаты в пользу более','5 000 поставщиков услуг.'],17,C['muted'],lh=26)
m.button(20,382,'Подключиться',w=167);m.button(199,382,'Посмотреть ПО',False,w=171)
m.image(beauty,122,468,150,330);m.text(86,816,'Платёжный терминал Beauty',12,C['muted'])
m.text(20,903,['Более 5 000','провайдеров услуг'],32,weight=600,lh=37)
m.text(20,1003,['Оплата услуг федеральных','и местных поставщиков.'],17,C['muted'],lh=25)
for i,item in enumerate(logos):m.image(item['path'],24+(i%3)*120,1065+(i//3)*77,99,58)
m.link(20,1562,'Провайдеры услуг');m.arrow(192,1557)
m.rect(0,1600,390,650,C['ink'])
m.text(20,1674,'Терминальное ПО',32,'white',600)
m.text(20,1731,['Универсальное программное','обеспечение для платёжных','и информационных терминалов.'],17,'#CCD1D5',lh=25)
m.image(ui,20,1840,350,263)
m.text(20,2125,'Интерфейс ПО SkySend',12,'#CCD1D5')
m.link(20,2190,'Подробнее о терминальном ПО',True)
m.text(20,2325,['Изменение цветов','и фона'],32,weight=600,lh=38)
m.text(20,2430,['Изменяйте расположение, размеры','и форму элементов экранов,','а также логику работы ПО.'],17,C['muted'],lh=25)
m.image(variants,20,2530,350,266)
m.text(20,2828,'Варианты интерфейса SkySend',12,C['muted'])
m.link(20,2880,'Возможности интерфейса');m.arrow(253,2875)
m.rect(0,2920,390,556,C['gray'])
m.text(20,2994,['Продажа товаров','и услуг'],32,weight=600,lh=38)
m.text(20,3090,['Модуль формирования заказов','на устройствах самообслуживания.'],17,C['muted'],lh=25)
for i,(num,txt) in enumerate([('01','Загрузка справочника товаров'),('02','Формирование заказов'),('03','Оплата заказов')]):
 y=3185+i*77;m.text(20,y,num,14,C['blue'],600);m.text(55,y,txt,17,weight=500);m.line(20,y+24,370,y+24)
m.link(20,3431,'Поставщикам товаров');m.arrow(227,3426)
m.text(20,3550,'Партнёрам',32,weight=600)
for i,(title,subtitle) in enumerate(routes):
 y=3610+i*88;m.line(20,y-18,370,y-18);m.text(20,y+8,title,21,weight=500);m.text(20,y+36,subtitle,14,C['muted']);m.arrow(344,y+2)
m.rect(0,4140,390,490,C['gray'])
m.text(20,4214,['Платёжные','терминалы'],32,weight=600,lh=38)
m.image(beauty,39,4290,110,270);m.image(fastpay,221,4290,139,270)
m.text(60,4591,'Beauty',16,weight=500);m.text(218,4591,'FastPay Simple',16,weight=500)
m.text(20,4694,['Круглосуточная','поддержка'],30,weight=600,lh=36)
m.text(20,4800,'+7 (800) 555-25-36',26,weight=500);m.link(20,4844,'Telegram: @infsysgroup',size=18)
m.line(20,4880,370,4880);m.text(20,4920,'ПО    Скачать    О системе    Контакты',14)
m.text(20,4970,'© SkySend. «Информ-Системы».',12,C['muted'])
m.save('home-mobile.svg')

d=Board(1440,1800,'SkySend: XML-шлюз, пример внутренней страницы')
d.image(brand,80,8,92,56);d.text(270,43,'Партнёрам      ПО      Оборудование      Провайдеры      Поддержка',15,weight=500);d.button(1195,15,'Подключиться',w=166)
d.rect(0,72,1440,56,C['gray']);d.text(80,108,'XML-шлюз',18,weight=600);d.text(860,107,'Обзор    Обмен данными    Документация',15)
d.text(80,222,'ПО / XML-шлюз',14,C['muted']);d.text(80,307,'Подключение по XML-протоколу',48,weight=600)
d.text(80,379,['Агенты SkySend могут организовать приём платежей посредством интеграции','собственной предпроцессинговой системы с системой SkySend по XML-протоколу.'],21,C['muted'],lh=32)
for x,title,sub in [(80,'Система Агента','Предпроцессинг'),(540,'SkySend','XML-протокол'),(1000,'Провайдеры','Услуги')]:
 d.rect(x,490,360,224,C['gray'],8);d.text(x+32,568,title,28,weight=600);d.text(x+32,614,sub,18,C['muted'])
 if x<1000:d.arrow(x+390,591)
d.text(80,764,'Схема взаимодействия. Не является схемой серверной инфраструктуры.',14,C['muted'])
d.line(80,842,1360,842)
d.text(80,945,'Обмен данными',36,weight=600)
d.text(650,943,['Информация о провайдерах','Технические и финансовые условия оплаты','Информация о совершаемых платежах'],22,lh=60)
d.rect(0,1160,1440,360,C['ink']);d.text(80,1260,'Протокол SkyTransact',40,'white',600)
d.text(80,1320,'Для интеграции ознакомьтесь с описанием протокола SkyTransact.',20,'#CCD1D5')
d.link(80,1418,'Документация XML',True,size=20);d.text(740,1418,'SkyTransact · описание протокола',18,'#CCD1D5')
d.text(80,1630,'Поддержка',30,weight=600);d.text(650,1630,'+7 (800) 555-25-36',27,weight=500);d.link(650,1680,'support@inf-sys.ru',size=18)
d.line(80,1730,1360,1730);d.text(80,1770,'© SkySend. Группа компаний «Информ-Системы».',13,C['muted'])
d.save('xml-detail-desktop.svg')
print('Created home-desktop.svg, home-mobile.svg, xml-detail-desktop.svg')
