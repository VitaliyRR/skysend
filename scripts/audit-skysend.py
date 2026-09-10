from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlsplit,urldefrag
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import requests,json,re,time,hashlib
BASE='https://skysend.ru/'
ROOT=Path(__file__).resolve().parents[1]
EV=ROOT/'evidence/skysend'; HTML=EV/'html'; HTML.mkdir(parents=True,exist_ok=True)
NOW=datetime.now(timezone.utc).isoformat()
home=BeautifulSoup((EV/'home.html').read_text(encoding='utf-8'),'html.parser')
menu=[]
for a in home.select('#main_menu a[href]'):
 url=urldefrag(urljoin(BASE,a['href']))[0]
 if not any(v['url']==url for v in menu): menu.append({'label':a.get_text(' ',strip=True),'url':url})
(EV/'menu.json').write_text(json.dumps(menu,ensure_ascii=False,indent=2),encoding='utf-8')
labels={x['url']:x['label'] for x in menu}
urls=[BASE]+[x['url'] for x in menu]
for a in home.select('#content a[href], #slideshow a[href], #footer a[href]'):
 u=urldefrag(urljoin(BASE,a['href']))[0]
 if urlsplit(u).netloc=='skysend.ru' and (urlsplit(u).path.endswith('.html') or urlsplit(u).path=='/') and u not in urls: urls.append(u)
for n in range(2,12): urls.append(BASE+f'download/{n}.html')

def filename(url):
 p=urlsplit(url); stem=p.path.strip('/').replace('/','__') or 'home.html'
 if not stem.endswith('.html'):stem+='.html'
 if p.query:stem=stem[:-5]+'__'+hashlib.sha1(p.query.encode()).hexdigest()[:8]+'.html'
 return stem

def collect(url):
 p=HTML/filename(url); record={'url':url,'menu_label':labels.get(url),'fetched_at':NOW,'html_path':str(p.relative_to(ROOT)).replace('\\','/')}
 try:
  if p.exists(): raw=p.read_bytes(); code=200; final=url
  else:
   response=requests.get(url,timeout=(10,30)); code=response.status_code; final=response.url; raw=response.content;p.write_bytes(raw)
  record.update(http_status=code,final_url=final,sha256=hashlib.sha256(raw).hexdigest())
  soup=BeautifulSoup(raw,'html.parser',from_encoding='utf-8')
  record['title']=soup.title.get_text(' ',strip=True) if soup.title else ''
  record['meta_description']=next((m.get('content','') for m in soup.select('meta[name="description"]')),'')
  scope=soup.select_one('#k2Container .itemBody') or soup.select_one('#yoo-zoo') or soup.select_one('#k2Container') or soup.select_one('#mainbody .span9') or soup.select_one('#mainbody') or soup.select_one('#content')
  if not scope:scope=soup.body or soup
  record['extraction_selector']=('#k2Container .itemBody' if soup.select_one('#k2Container .itemBody') else '#yoo-zoo' if soup.select_one('#yoo-zoo') else '#k2Container' if soup.select_one('#k2Container') else '#mainbody or #content')
  if url==BASE:
   scope=BeautifulSoup(str(soup.select_one('#slideshow'))+str(soup.select_one('#content')),'html.parser')
  for x in scope.select('script,style,nav,.itemBackToTop,.itemSocialSharing,.itemRelated,.itemNavigation,.itemAuthorBlock,.itemComments,#sidebar'):
   x.decompose()
  record['headings']=[{'level':int(x.name[1]),'text':x.get_text(' ',strip=True)} for x in scope.select('h1,h2,h3,h4,h5,h6')]
  record['text']='\n'.join(x.strip() for x in scope.get_text('\n',strip=True).splitlines() if x.strip())
  blocks=[]
  for x in scope.find_all(['h1','h2','h3','h4','h5','h6','p','li','tr']):
   if x.name in ['p','li','tr'] and x.find_parent(['p','li','tr']):continue
   t=x.get_text(' ',strip=True)
   if t:blocks.append({'id':f'b{len(blocks)+1:03}','tag':x.name,'text':t})
  record['blocks']=blocks
  record['images']=[]
  for img in scope.select('img'):
   for attr in ['src','data-src']:
    v=img.get(attr)
    if v and not v.startswith('data:'):
     record['images'].append({'url':urljoin(final,v),'alt':img.get('alt',''),'width':img.get('width'),'height':img.get('height'),'source_attribute':attr})
  record['links']=[]
  for a in scope.select('a[href]'):
   href=urljoin(final,a['href'])
   if a['href'].startswith(('javascript:','#')):continue
   label=a.get_text(' ',strip=True) or (a.img.get('alt','') if a.img else '')
   row={'text':label,'url':href}
   if row not in record['links']:record['links'].append(row)
  record['downloads']=[x for x in record['links'] if re.search(r'\.(zip|7z|rar|exe|msi|apk|pdf|docx?|xlsx?|psd|tar\.gz|xml)(?:$|[?#])',x['url'],re.I) or '/download/item/' in x['url'] or '/downloads/' in x['url'] or 'ftp.' in x['url']]
  record['requires_review']=bool(re.search(r'акци[яиюй]|скидк|подар|бесплат|[0-9]+\s*%|[0-9]{4}\s*(?:год|г\.)',record['text'],re.I))
 except Exception as e: record['error']=str(e)
 return record
results=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 jobs={pool.submit(collect,url):url for url in dict.fromkeys(urls)}
 for future in as_completed(jobs):
  record=future.result();results.append(record)
  print(len(results),record.get('http_status','ERR'),record['url'],flush=True)
results.sort(key=lambda x:urls.index(x['url']))
out={'source':'https://skysend.ru/','audit_date':NOW,'method':'HTTP GET; exact DOM text; excludes shared navigation/footer; image-embedded text requires visual transcription.','pages':results}
(ROOT/'data/source-pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
(EV/'pages.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',len(results))
