from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,textwrap
root=Path.cwd();m=json.loads((root/'data/assets-manifest.json').read_text(encoding='utf-8'));font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);large=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',23)
out=root/'assets/contact-sheets';out.mkdir(exist_ok=True)
def sheet(items,name,title,cols=4,cellw=350,cellh=300,perpage=24):
 for page,offset in enumerate(range(0,len(items),perpage),1):
  batch=items[offset:offset+perpage];im=Image.new('RGB',(cols*cellw,70+math.ceil(len(batch)/cols)*cellh),'#f2f2f2');d=ImageDraw.Draw(im);d.text((20,18),title+' / '+str(page),font=large,fill='#202020')
  for i,a in enumerate(batch):
   src=root/a['path'];x=(i%cols)*cellw;y=70+(i//cols)*cellh
   try:
    art=Image.open(src).convert('RGBA');sz=art.size;art.thumbnail((cellw-30,cellh-88));im.paste(art,(x+(cellw-art.width)//2,y+6+(cellh-88-art.height)//2),art)
   except Exception:continue
   label=a.get('provider_name',src.name)
   lines=textwrap.wrap(label,35)[:2]
   for j,line in enumerate(lines):d.text((x+12,y+cellh-73+j*19),line,font=font,fill='#111')
   d.text((x+12,y+cellh-30),src.name+' | '+str(sz),font=font,fill='#555')
  im.save(out/(name+('-'+str(page).zfill(2) if len(items)>perpage else '')+'.jpg'),quality=91)
verified=[a for a in m['assets'] if a['download_status']=='verified' and a['path'] and not a['path'].endswith('.svg')]
providers=[a for a in verified if a['asset_type']=='provider-logo']
selected_ids=['359','6581','7','258','1134','631','241','168','9858','9849','4819','4816','4675','252','876','4754']
selected=sorted([a for a in providers if a['path'].split('provider-')[-1][:-4] in selected_ids],key=lambda a:selected_ids.index(a['path'].split('provider-')[-1][:-4]))
sheet(selected,'providers-selected','Логотипы из публичного каталога SkySend',4,330,230,16)
sheet(providers,'providers-catalog','Каталог оригинальных логотипов | 10.09.2026',6,260,210,60)
sheet([a for a in verified if a['asset_type']=='hardware-product'],'equipment','Оригинальные изображения оборудования',4,340,350,24)
sheet([a for a in verified if a['asset_type']=='software-feature-reference'],'software-reference','Архивные иллюстрации ПО. Не production',3,470,360,18)
sheet([a for a in verified if a['asset_type']=='software-screenshot'],'software','Реальные скриншоты исходного ПО',2,650,470,6)
sheet([a for a in verified if a['asset_type']=='brand'],'brands','Оригинальная графика брендов',3,450,340,12)
(root/'data/provider-wall-selection.json').write_text(json.dumps({'source':'https://skysend.ru/providers.php','retrieved_date':'2026-09-10','note':'16 examples from source catalogue; not a claim of current service availability. No Steam in current source catalogue snapshot; do not invent its entry.','items':[{k:a[k] for k in ['id','source_url','path','width','height','provider_name','provider_category']} for a in selected]},ensure_ascii=False,indent=2),encoding='utf-8')
print('Contact sheets generated:',len(list(out.glob('*.jpg'))))
