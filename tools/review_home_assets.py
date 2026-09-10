from pathlib import Path
import re,urllib.parse,concurrent.futures,requests,hashlib,json
from bs4 import BeautifulSoup
root=Path.cwd()
soup=BeautifulSoup((root/'evidence/skysend/home.html').read_text(encoding='utf-8'),'html.parser')
urls=set()
for x in soup.find_all(['img','a']):
 for a in ['src','data-src','href']:
  value=x.get(a,'')
  if re.search(r'\.(?:jpg|jpeg|png|gif|svg|webp)(?:[?#].*)?$',value,re.I):
   u=urllib.parse.urljoin('https://skysend.ru/',value)
   if urllib.parse.urlparse(u).netloc in ('skysend.ru','www.skysend.ru') and not any(t in u for t in ('/templates/','/modules/','/banners/','/favicons/','/soc','twitter','instagram')): urls.add(u)
out=root/'evidence/skysend/asset-review'
out.mkdir(parents=True,exist_ok=True)
def one(u):
 name=urllib.parse.urlparse(u).path.strip('/').replace('/','__')
 p=out/name
 if not p.exists():
  r=requests.get(u,timeout=30);r.raise_for_status();p.write_bytes(r.content)
 return {'url':u,'path':str(p.relative_to(root))}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: vals=list(pool.map(one,sorted(urls)))
(root/'data/asset-review-home.json').write_text(json.dumps(vals,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(vals,ensure_ascii=False,indent=2))
