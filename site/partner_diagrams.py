"""Workflow diagrams using authentic product assets and licensed Lucide symbols.

The diagrams show channels and responsibilities, never invented product screens.
Lucide source and license are recorded under assets/icons/process/.
"""
from html import escape
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TERMINAL = 'assets/originals/FastPay Simple.png'
FINGER = 'assets/originals/logotip_finger.png'
MARKET = 'assets/originals/logotip_skymarket_3x1.png'
SKYSEND = 'assets/brand/skysend-logo.svg'


def photo(path, x, y, width, height):
    return f'<image href="/{quote(path, safe="/")}" x="{x}" y="{y}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid meet"/>'


def icon(name, x, y, size=76):
    source = (ROOT/'assets/icons/process'/f'{name}.svg').read_text(encoding='utf-8')
    content = re.sub(r'^.*?<svg[^>]*>|</svg>\s*$', '', source, flags=re.S)
    return f'<g class="pd-icon" transform="translate({x} {y}) scale({size/24})">{content}</g>'


def label(lines, x, y, *, small=False):
    lines = (lines,) if isinstance(lines, str) else lines
    css = 'pd-label pd-label--small' if small else 'pd-label'
    return f'<text class="{css}" x="{x}" y="{y}" text-anchor="middle">' + ''.join(f'<tspan x="{x}" dy="{0 if i==0 else 31}">{escape(line)}</tspan>' for i,line in enumerate(lines)) + '</text>'


def panel(x,y,w,h):
    return f'<rect class="pd-panel" x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/>'


def line(path, *, arrow=True):
    return f'<path class="pd-connector" d="{path}"'+(' marker-end="url(#PD_ARROW)"' if arrow else '')+'/>'


def tile(x, y, title, *, symbol=None, asset=None, width=166, height=212):
    result = panel(x,y,width,height)
    if asset:
        result += photo(asset,x+30,y+18,width-60,height-89)
    if symbol:
        size=min(64 if height < 180 else 76,height-75)
        result += icon(symbol,x+(width-size)/2,y+24,size)
    return result + label(title,x+width/2,y+height-45)


def brand_node(path, x=177, y=25, width=246, height=112):
    return panel(x,y,width,height)+photo(path,x+25,y+20,width-50,height-40)


def chain(items):
    artwork = line('M190 182H213')+line('M387 182h23')
    for x,item in zip((23,217,411),items):
        artwork += tile(x,84,item[0],symbol=item[1])
    return artwork


def fanout(parent, children, *, parent_asset=None, parent_symbol=None):
    centers = (135,465) if len(children)==2 else (106,300,494)
    artwork = brand_node(parent_asset) if parent_asset else tile(190,20,parent,symbol=parent_symbol,width=220,height=157)
    start=137 if parent_asset else 177
    artwork += line(f'M300 {start}V210',arrow=False)
    artwork += line(f'M{centers[0]} 210H{centers[-1]}',arrow=False)
    for cx,item in zip(centers,children):
        artwork += line(f'M{cx} 210V223')
        title,symbol,asset=item
        artwork += tile(cx-83,230,title,symbol=symbol,asset=asset,height=180)
    return artwork


def maintenance():
    result = photo(TERMINAL,238,32,126,285)
    result += photo('assets/originals/CashCode_MVU.png',29,46,139,137)
    result += photo('assets/originals/siemens.png',433,46,139,137)
    result += label(('Купюро-', 'приёмник'),100,213)+label('Модем',501,213)
    result += line('M175 117H231')+line('M426 117H371')
    result += panel(114,333,372,64)+icon('refresh-cw',133,348,34)+label('Обновления и отладка',322,374)
    return result


def remote():
    result = panel(169,15,262,144)+icon('sliders-horizontal',266,33,68)+label('Кабинет SkySend',300,139)
    result += line('M210 159V234H256')+line('M346 288H390V184H454V88H436')
    result += photo(TERMINAL,262,202,81,169)
    result += icon('sliders-horizontal',66,189,60)+label(('Настройка', 'терминала'),95,282)
    result += icon('list-checks',477,185,60)+label(('Контроль', 'платежей'),506,282)
    return result


def innovation():
    result = brand_node(FINGER,24,76,159,227)+brand_node(MARKET,220,76,159,227)
    result += panel(416,76,159,227)+icon('sliders-horizontal',457,127,76)
    result += label(('Настройка','экрана'),495,250)
    return result


def processing():
    result = label('Обработка платежей',300,46)+line('M300 67v25',arrow=False)
    result += panel(28,127,225,206)+panel(347,127,225,206)
    result += icon('server',95,153,90)+icon('server',414,153,90)
    result += label('Центр данных',140,290)+label('Центр данных',460,290)
    result += line('M254 195h84')+line('M347 236h-84')
    result += line('M300 92H140v24')+line('M300 92h160v24')
    result += label('Синхронизация · IPsec',300,389)
    return result


def preprocessing():
    result = tile(20,107,('Платёжные','агенты'),symbol='network',width=155,height=213)
    result += brand_node(SKYSEND,206,119,188,105)
    result += label(('Договоры','и расчёты'),300,273)
    result += tile(425,107,'Провайдер',symbol='radio-tower',width=155,height=213)
    return result+line('M175 176h22')+line('M394 176h23')


def office():
    result = panel(209,22,182,268)+photo(TERMINAL,245,40,111,234)
    result += label(('Офис обслуживания','абонентов'),300,340)
    result += icon('store',48,112,60)+icon('file-check',491,112,60)
    return result+label(('Свой','терминал'),78,227)+label('Аренда',522,227)


def sales():
    result = brand_node(MARKET,184,16,232,91)
    result += line('M300 108v63H140v48')+line('M300 171h160v48')
    result += photo(TERMINAL,82,225,116,151)+photo(FINGER,406,230,108,139)
    return result+label('Терминал',140,408)+label('FINGER',460,408)


def xml_exchange():
    result = tile(30,95,('Система','поставщика'),symbol='server',width=196,height=231)
    result += brand_node(MARKET,365,104,211,202)
    result += line('M227 169h129')+line('M365 259H235')
    result += label('Каталог',296,143)+label('Заказы',296,303)
    return result+label('XML',300,214)


def sync():
    result = fanout('',[('Терминалы',None,TERMINAL),('FINGER',None,FINGER)],parent_asset=MARKET)
    result += icon('refresh-cw',57,43,58)+label('Каталог',86,141)
    return result


def retail_network():
    return fanout('Кабинет сети',[('Точка','store',None),('Точка','store',None),('Точка','store',None)],parent_symbol='monitor')


def deployment():
    result = photo(TERMINAL,269,15,61,126)
    result += line('M300 147v46',arrow=False)+line('M108 193h386',arrow=False)
    for cx in (108,300,492): result += line(f'M{cx} 193v41')
    result += tile(25,244,('Приобрести','устройство'),symbol='shopping-cart',height=159)
    result += tile(217,244,('Перевести','на ALLVEND'),symbol='refresh-cw',height=159)
    result += tile(409,244,('Разместить','в сети'),symbol='store',height=159)
    return result


def participants():
    return fanout('Представитель',[('Агенты',None,TERMINAL),('Провайдеры','radio-tower',None),('Поставщики','package-open',None)],parent_symbol='handshake')


def directions():
    result = ''
    for x,y,title,symbol in [(23,18,('Новые','участники'),'plug'),(217,18,'Сервис','wrench'),(411,18,'Инкассация','banknote'),(120,225,('Продажа','техники'),'boxes'),(314,225,('Касса','региона'),'landmark')]:
        result += tile(x,y,title,symbol=symbol,height=181)
    return result


def region():
    result = '<rect class="pd-region" x="28" y="42" width="544" height="345" rx="45"/>'
    result += label('Регион',300,28)+brand_node(SKYSEND,194,145,212,104)
    result += line('M194 174H158V109H132')+line('M406 174H438V109H460')
    result += line('M194 222H158V315H132')+line('M406 222H438V315H460')
    for x,y,sym in [(65,79,'store'),(466,79,'radio-tower'),(65,285,'monitor'),(466,285,'package-open')]:
        result += icon(sym,x,y,60)
    return result+label('Представительство',300,286)


SCENES = {
    'agent-maintenance': maintenance,
    'agent-remote': remote,
    'agent-innovation': innovation,
    'provider-payment-points': lambda: fanout(('Услуги','провайдера'),[('Терминалы',None,TERMINAL),('FINGER',None,FINGER)],parent_symbol='radio-tower'),
    'provider-connection': lambda: chain([('Договор','handshake'),(('Настройка','обмена'),'plug'),(('Проверка','платежей'),'clipboard-check')]),
    'provider-processing': processing,
    'provider-preprocessing': preprocessing,
    'provider-office-terminal': office,
    'supplier-sales-channels': sales,
    'supplier-order-management': lambda: chain([(('Приём','заказа'),'clipboard-check'),(('Подготовка','товаров'),'package-open'),('Доставка','truck')]),
    'supplier-xml': xml_exchange,
    'supplier-sync': sync,
    'supplier-connection': lambda: chain([(('Договор и','доступ'),'file-check'),(('Загрузка','каталога'),'upload'),(('Продажи в','SkyMarket'),'shopping-cart')]),
    'retail-orders': lambda: chain([('Каталог','book-open'),('Заказ','shopping-cart'),('Оплата','wallet')]),
    'retail-management': retail_network,
    'retail-deployment': deployment,
    'representative-participants': participants,
    'representative-directions': directions,
    'representative-region': region,
    'representative-cashdesk': lambda: chain([(('Аванс','агента'),'banknote'),(('Касса','региона'),'landmark'),(('Счёт','в SkySend'),'wallet')]),
    'gateway-steps': lambda: chain([('Договор','handshake'),(('Интеграция','XML'),'plug'),(('Проверка','платежей'),'clipboard-check')]),
    'gateway-processing': processing,
    'allvend-orders': lambda: chain([('Каталог','book-open'),('Заказ','shopping-cart'),('Оплата','wallet')]),
}


def render_partner_diagram(scene_id, instance):
    if scene_id not in SCENES:
        return None
    uid='workflow-'+instance
    artwork=SCENES[scene_id]().replace('PD_ARROW',uid+'-arrow')
    definitions=f'''<defs>
      <linearGradient id="{uid}-glass" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#edf6fa"/></linearGradient>
      <marker id="{uid}-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="m2 2 4 3-4 3" fill="none" stroke="#3584aa" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></marker>
    </defs>'''
    return f'<figure class="partner-diagram" data-scene="{escape(scene_id)}" aria-hidden="true"><svg class="partner-diagram__svg" viewBox="0 0 600 430" focusable="false" style="--pd-glass:url(#{uid}-glass)">{definitions}{artwork}</svg></figure>'
