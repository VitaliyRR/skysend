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
routes=['Платёжным агентам','Провайдерам услуг','Поставщикам товаров','Торговым сетям','Представителям','Шлюзовикам']
route_visuals=['assets/originals/RMA_win_lin.png',None,'assets/diagrams/supplier-exchange.svg',beauty,'assets/diagrams/payment-network.svg','assets/diagrams/xml-flow.svg']

b=Board(1440,4500,'SkySend: главная, desktop 1440 px')
b.image(brand,80,8,92,56)
b.text(250,43,'Партнёрам      ПО      Оборудование      Провайдеры      Поддержка',15,weight=500)
b.button(1150,15,'Вход | Регистрация',w=210)
b.line(0,72,1440,72)
b.rect(0,73,1440,447,C['gray'])
b.text(80,235,['Система приёма','платежей SkySend'],56,weight=600,lh=62)
b.button(80,395,'Подключиться',w=183)
b.text(80,650,['Более 5 000','провайдеров услуг'],40,weight=600,lh=47)
b.text(80,775,['Оплата услуг федеральных','и местных поставщиков.'],20,C['muted'],lh=29)
b.link(80,875,'Открыть каталог'); b.arrow(226,869)
for i,item in enumerate(logos): b.image(item['path'],650+(i%4)*170,565+(i//4)*116,120,78)
b.rect(0,1120,1440,760,C['ink'])
b.text(80,1235,['Терминальное','ПО'],44,'white',600,52)
b.text(80,1365,['Универсальное программное','обеспечение для платёжных','и информационных терминалов.'],19,'#CCD1D5',lh=29)
b.text(80,1492,['ПО предустанавливается на flash-','накопитель и содержит модуль','обнаружения и настройки','периферийных устройств.'],18,'#CCD1D5',lh=27)
b.link(80,1718,'Подробнее о терминальном ПО',True)
b.image(ui,557,1195,803,602)
b.text(557,1825,'Интерфейс ПО SkySend',13,'#CCD1D5')
b.text(80,1980,'Персонализация интерфейса',40,weight=600)
b.image(variants,80,2035,650,280)
for i,title in enumerate(['Цвета и фон','Положение, размеры и форма элементов','Логика экранов']):
 y=2075+i*82
 b.line(810,y-35,1360,y-35);b.text(810,y,title,22,weight=500)
b.link(810,2380,'Возможности интерфейса');b.arrow(1041,2375)
b.rect(0,2460,1440,430,C['gray'])
b.text(80,2560,'SkyMarket',40,weight=600)
b.text(80,2625,'Заказы формируются и оплачиваются прямо на устройствах самообслуживания.',18,C['muted'])
b.link(80,2765,'Поставщикам товаров');b.arrow(288,2760)
for i,title in enumerate(['Загрузка справочника товаров','Формирование заказов','Оплата заказов']):
 y=2548+i*98
 b.line(760,y-28,1360,y-28);b.text(760,y+12,title,23,weight=500);b.arrow(1325,y+7)
b.text(80,2990,'Партнёрам',40,weight=600)
for i,title in enumerate(routes):
 x=80+(i%3)*430;y=3050+(i//3)*165
 b.rect(x,y,390,145,C['gray'],8)
 if route_visuals[i]: b.image(route_visuals[i],x+18,y+16,120,82)
 else:
  for j,item in enumerate(logos[:4]): b.image(item['path'],x+18+(j%2)*60,y+16+(j//2)*42,52,34)
 b.text(x+155,y+66,title,19,weight=500);b.arrow(x+342,y+112)
b.rect(0,3415,1440,835,C['gray'])
b.text(80,3515,'Платёжные терминалы',40,weight=600)
for x,img,title,lead,fact in [
 (80,beauty,'FastPay Beauty II',['Киоск для помещений.','Информационный терминал,','терминал заказа товаров,','касса оплаты заказов и услуг','или платёжный терминал.'],'Высота 145 см · масса 75 кг'),
 (730,fastpay,'FastPay Simple',['Платёжный терминал для помещений','с сенсорным экраном. Поставляется','с предустановленным программным','обеспечением.'],'Высота 144 см · масса 80 кг')]:
 b.rect(x,3570,610,590,C['white'],8,stroke=C['line']);b.image(img,x+25,3635,180,385)
 b.text(x+230,3645,title,23,weight=600);b.text(x+230,3705,lead,16,C['muted'],lh=25)
 b.text(x+230,3870,fact,15,weight=500);b.text(x+230,3905,'Сенсорный экран 17″',15,weight=500)
 b.link(x+230,4070,'Характеристики');b.arrow(x+376,4065)
b.line(80,4250,1360,4250)
b.image(brand,80,4280,104,66)
b.text(270,4315,'Терминальное ПО     Скачать     О системе     Контакты     Правила системы',15)
b.text(270,4360,'sales@inf-sys.ru     support@inf-sys.ru',15,C['muted'])
b.text(80,4460,'© SkySend. Группа компаний «Информ-Системы».',13,C['muted'])
b.save('home-desktop.svg')

m=Board(390,5260,'SkySend: главная, mobile 390 px')
m.image(brand,20,7,75,48);m.button(112,9,'Вход | Регистрация',w=202);m.line(337,24,365,24,C['ink']);m.line(337,34,365,34,C['ink']);m.line(337,44,365,44,C['ink'])
m.rect(0,64,390,396,C['gray'])
m.text(20,150,['Система приёма','платежей','SkySend'],36,weight=600,lh=40)
m.button(20,340,'Подключиться',w=167)
m.text(20,535,['Более 5 000','провайдеров услуг'],32,weight=600,lh=37)
m.text(20,640,['Оплата услуг федеральных','и местных поставщиков.'],17,C['muted'],lh=25)
m.link(20,725,'Открыть каталог');m.arrow(166,720)
for i,item in enumerate(logos):m.image(item['path'],24+(i%3)*120,770+(i//3)*70,99,58)
m.rect(0,1250,390,790,C['ink'])
m.text(20,1325,'Терминальное ПО',32,'white',600)
m.text(20,1385,['Универсальное программное','обеспечение для платёжных','и информационных терминалов.'],17,'#CCD1D5',lh=25)
m.image(ui,20,1490,350,263)
m.text(20,1780,'Интерфейс ПО SkySend',12,'#CCD1D5')
m.text(20,1830,['ПО предустанавливается на flash-накопитель','и содержит модуль автоматического обнаружения','и настройки подключённых периферийных','устройств.'],15,'#CCD1D5',lh=22)
m.link(20,1975,'Подробнее о терминальном ПО',True)
m.text(20,2120,['Персонализация','интерфейса'],32,weight=600,lh=38)
m.image(variants,20,2190,350,150)
for i,title in enumerate(['Цвета и фон','Положение, размеры и форма элементов','Логика экранов']):
 y=2375+i*65;m.text(20,y,title,16,weight=500);m.line(20,y+23,370,y+23)
m.link(20,2595,'Возможности интерфейса');m.arrow(253,2590)
m.rect(0,2660,390,580,C['gray'])
m.text(20,2740,'SkyMarket',32,weight=600)
m.text(20,2810,['Заказы формируются и оплачиваются','прямо на устройствах','самообслуживания.'],17,C['muted'],lh=25)
m.link(20,2935,'Поставщикам товаров');m.arrow(227,2930)
for i,title in enumerate(['Загрузка справочника товаров','Формирование заказов','Оплата заказов']):
 y=3025+i*75;m.text(20,y,title,17,weight=500);m.line(20,y+23,370,y+23)
m.text(20,3320,'Партнёрам',32,weight=600)
for i,title in enumerate(routes):
 y=3370+i*135;m.rect(20,y,350,120,C['gray'],8)
 if route_visuals[i]: m.image(route_visuals[i],35,y+15,96,90)
 else:
  for j,item in enumerate(logos[:4]): m.image(item['path'],35+(j%2)*48,y+15+(j//2)*43,42,34)
 m.text(150,y+63,title,17,weight=500);m.arrow(330,y+91)
m.rect(0,4220,390,820,C['gray'])
m.text(20,4295,['Платёжные','терминалы'],32,weight=600,lh=38)
for x,img,title,lead,facts in [
 (20,beauty,['FastPay','Beauty II'],['Киоск для помещений:','инфокиоск, терминал','заказа товаров, касса','оплаты или платёжный','терминал.'],['145 см · 75 кг','экран 17″']),
 (200,fastpay,['FastPay','Simple'],['Терминал для помещений','с сенсорным экраном.','ПО предустановлено.'],['144 см · 80 кг','экран 17″'])]:
 m.rect(x,4385,170,560,C['white'],8,stroke=C['line']);m.image(img,x+15,4410,140,225)
 m.text(x+14,4670,title,17,weight=600,lh=21);m.text(x+14,4730,lead,12,C['muted'],lh=17)
 m.text(x+14,4835,facts,13,weight=500,lh=20);m.link(x+14,4915,'Характеристики',size=13)
m.line(20,5040,370,5040);m.image(brand,20,5060,82,52)
m.text(20,5140,'Терминальное ПО    Скачать    О системе',13)
m.text(20,5175,'Контакты    Правила системы',13)
m.text(20,5230,'© SkySend. «Информ-Системы».',12,C['muted'])
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
