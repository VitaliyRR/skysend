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

b=Board(1440,4420,'SkySend: главная, desktop 1440 px')
b.image(brand,80,8,92,56)
b.text(270,43,'Партнёрам      ПО      Оборудование      Провайдеры      Поддержка',15,weight=500)
b.text(1100,43,'Войти',15); b.button(1195,15,'Подключиться',w=166)
b.line(0,72,1440,72)
b.rect(0,73,1440,639,C['gray'])
b.text(80,239,['Система приёма','платежей SkySend'],56,weight=600,lh=62)
b.button(80,402,'Подключиться',w=183); b.button(278,402,'Посмотреть ПО',False,w=190)
b.image(beauty,938,133,235,510)
b.text(902,690,'Платёжный терминал Beauty',13,C['muted'])
b.text(80,832,['Более 5 000','провайдеров услуг'],40,weight=600,lh=47)
b.text(80,955,['Оплата услуг федеральных','и местных поставщиков.'],20,C['muted'],lh=29)
b.link(80,1040,'Открыть каталог'); b.arrow(226,1034)
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
b.rect(0,2580,1440,430,C['gray'])
b.text(80,2680,'SkyMarket',40,weight=600)
b.text(80,2742,['Модуль формирования заказов включает загрузку','справочника товаров, формирование и оплату заказов','на устройствах самообслуживания.'],18,C['muted'],lh=27)
b.link(80,2915,'Поставщикам товаров');b.arrow(288,2910)
for i,title in enumerate(['Загрузка справочника товаров','Формирование заказов','Оплата заказов']):
 y=2670+i*98
 b.line(760,y-28,1360,y-28);b.text(760,y+12,title,23,weight=500);b.arrow(1325,y+7)
b.text(80,3090,'Партнёрам',40,weight=600)
routes=['Платёжным агентам','Провайдерам услуг','Поставщикам товаров','Торговым сетям','Представителям','Шлюзовикам']
for i,title in enumerate(routes):
 x=80+(i%3)*430;y=3150+(i//3)*126
 b.rect(x,y,390,100,C['gray'],6)
 b.text(x+24,y+58,title,21,weight=500);b.arrow(x+342,y+51)
b.rect(0,3430,1440,650,C['gray'])
b.text(80,3520,'Платёжные терминалы',40,weight=600)
b.image(beauty,430,3585,173,418);b.image(fastpay,795,3585,214,418)
b.text(430,4048,'FastPay Beauty II',20,weight=500);b.text(814,4048,'FastPay Simple',20,weight=500)
b.line(80,4140,1360,4140)
b.image(brand,80,4180,104,66)
b.text(275,4210,'ПО     Скачать     О системе     Контакты     Правила системы',15)
b.text(275,4254,'sales@inf-sys.ru     support@inf-sys.ru',15,C['muted'])
b.text(80,4382,'© SkySend. Группа компаний «Информ-Системы».',13,C['muted'])
b.save('home-desktop.svg')

m=Board(390,4770,'SkySend: главная, mobile 390 px')
m.image(brand,20,7,75,48);m.text(276,37,'Меню',15,weight=500);m.line(337,24,365,24,C['ink']);m.line(337,34,365,34,C['ink']);m.line(337,44,365,44,C['ink'])
m.rect(0,64,390,766,C['gray'])
m.text(20,142,['Система приёма','платежей','SkySend'],36,weight=600,lh=40)
m.button(20,300,'Подключиться',w=167);m.button(199,300,'Посмотреть ПО',False,w=171)
m.image(beauty,122,410,150,330);m.text(86,774,'Платёжный терминал Beauty',12,C['muted'])
m.text(20,903,['Более 5 000','провайдеров услуг'],32,weight=600,lh=37)
m.text(20,1003,['Оплата услуг федеральных','и местных поставщиков.'],17,C['muted'],lh=25)
for i,item in enumerate(logos):m.image(item['path'],24+(i%3)*120,1065+(i//3)*77,99,58)
m.link(20,1562,'Открыть каталог');m.arrow(166,1557)
m.rect(0,1600,390,650,C['ink'])
m.text(20,1674,'Терминальное ПО',32,'white',600)
m.text(20,1731,['Универсальное программное','обеспечение для платёжных','и информационных терминалов.'],17,'#CCD1D5',lh=25)
m.image(ui,20,1840,350,263)
m.text(20,2125,'Интерфейс ПО SkySend',12,'#CCD1D5')
m.link(20,2190,'Подробнее о терминальном ПО',True)
m.text(20,2325,['Изменение цветов','и фона'],32,weight=600,lh=38)
m.text(20,2430,['Изменяйте расположение, размеры','и форму элементов экранов,','а также логику работы ПО.'],17,C['muted'],lh=25)
m.image(variants,20,2530,350,266)
m.link(20,2830,'Возможности интерфейса');m.arrow(253,2825)
m.rect(0,2880,390,520,C['gray'])
m.text(20,2954,'SkyMarket',32,weight=600)
m.text(20,3020,['Модуль формирования заказов включает','загрузку справочника товаров,','формирование и оплату заказов.'],17,C['muted'],lh=25)
m.link(20,3125,'Поставщикам товаров');m.arrow(227,3120)
for i,title in enumerate(['Загрузка справочника товаров','Формирование заказов','Оплата заказов']):
 y=3200+i*67;m.text(20,y,title,17,weight=500);m.line(20,y+23,370,y+23)
m.text(20,3485,'Партнёрам',32,weight=600)
for i,title in enumerate(routes):
 y=3525+i*78;m.rect(20,y,350,66,C['gray'],6);m.text(38,y+41,title,18,weight=500);m.arrow(328,y+34)
m.rect(0,4045,390,500,C['gray'])
m.text(20,4119,['Платёжные','терминалы'],32,weight=600,lh=38)
m.image(beauty,39,4195,110,270);m.image(fastpay,221,4195,139,270)
m.text(39,4495,'FastPay Beauty II',15,weight=500);m.text(221,4495,'FastPay Simple',15,weight=500)
m.line(20,4580,370,4580);m.text(20,4620,'ПО    Скачать    О системе    Контакты',14)
m.text(20,4730,'© SkySend. «Информ-Системы».',12,C['muted'])
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
