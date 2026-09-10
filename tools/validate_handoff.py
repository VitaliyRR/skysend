"""Validate the design handoff, not the future website. Standard library only."""
from pathlib import Path
import csv, hashlib, json, re, sys
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, unquote
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]; checks={}

def read(rel):return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def require(rel):
 if not (ROOT/rel).exists():errors.append('Missing file: '+rel)

for rel in ['README.md','docs/00-art-direction.md','docs/01-current-site-audit.md','docs/02-information-architecture.md',
 'docs/03-sections-and-copy.md','docs/03b-secondary-pages.md','docs/04-assets.md','docs/05-frontend-and-motion.md',
 'docs/06-work-plan-and-acceptance.md','docs/07-developer-handoff.md','data/equipment-content.json',
 'assets/fonts/InterVariable.woff2','assets/fonts/OFL.txt','design/home-desktop.svg','design/home-mobile.svg',
 'design/home-desktop.png','design/home-mobile.png','design/xml-detail-desktop.png']:
 require(rel)

jsons=list((ROOT/'data').glob('*.json'))
for p in jsons:
 try:json.loads(p.read_text(encoding='utf-8-sig'))
 except Exception as e:errors.append(f'Invalid JSON {p.relative_to(ROOT)}: {e}')
checks['json_files']=len(jsons)

svgfiles=list((ROOT/'assets').rglob('*.svg'))+list((ROOT/'design').glob('*.svg'))
for p in svgfiles:
 try:
  tree=ET.parse(p)
  if any(n.tag.endswith('script') for n in tree.iter()):errors.append(f'Script in SVG: {p.relative_to(ROOT)}')
 except Exception as e:errors.append(f'Invalid SVG {p.relative_to(ROOT)}: {e}')
checks['svg_files']=len(svgfiles)

manifest=read('data/assets-manifest.json'); assetchecks=0
for a in manifest['assets']:
 if not a.get('path'):continue
 p=ROOT/a['path']
 if not p.exists():errors.append('Manifest file missing: '+a['path']);continue
 if a.get('sha256'):
  actual=hashlib.sha256(p.read_bytes()).hexdigest()
  if actual!=a['sha256']:errors.append('SHA256 mismatch: '+a['path'])
  assetchecks+=1
checks['asset_sha256_checked']=assetchecks

bindings=read('data/section-assets.json')['bindings']
for bid,b in bindings.items():
 for rel in b['paths']:
  require(rel)
  if rel.startswith(('evidence/','assets/source-with-review/')):errors.append('Unsafe production binding: '+bid+' -> '+rel)

primary=read('data/site-content.json')['pages']
secondary=read('data/secondary-content.json')['pages'] if (ROOT/'data/secondary-content.json').exists() else []
motions=read('data/motion-spec.json'); aliases=motions.get('contentAliases',{})
if isinstance(aliases,list):aliases={x['alias']:x for x in aliases}
utility=read('data/utility-content.json')['pages'] if (ROOT/'data/utility-content.json').exists() else []
allpages=primary+secondary+utility
checks['curated_pages']=len(allpages)
checks['curated_sections']=sum(len(p.get('sections',[])) for p in allpages)

def public_copy(page):
 out=[page.get('title',''),page.get('lead','')]
 for s in page.get('sections',[]):
  out += [s.get('title',''),s.get('body','')]+s.get('paragraphs',[])+s.get('bullets',[])
 return '\n'.join(x for x in out if isinstance(x,str))
bad=re.compile(r'Это не просто|В современном мире|Независимо от того|\b(?:delve|tapestry|landscape|robust|seamless|elevate|unlock|harness|empower|leverage|cutting-edge)\b|\bскидк\w*|\bакци[яиюей]\b|самое высокое вознаграждение',re.I)
known_paths=set(); anchors={}
for page in allpages:
 path=page['path']
 if path in known_paths:errors.append('Duplicate curated route: '+path)
 known_paths.add(path)
 ids=set()
 for s in page.get('sections',[]):
  if s['id'] in ids:errors.append('Duplicate section ID: '+path+'#'+s['id'])
  ids.add(s['id']);ids.update(s.get('anchor_aliases',[]))
  media_ids=s.get('media',[]) or ([s['visual_id']] if s.get('visual_id') else [])
  for bid in media_ids:
   if bid not in bindings:errors.append('Unknown asset binding: '+path+'#'+s['id']+' -> '+bid)
  alias=s.get('motion_alias') or (s.get('motion') if path in {p['path'] for p in primary} else None)
  if alias and alias not in aliases:errors.append('Unknown motion alias: '+str(alias))
  nodes=s.get('visual_nodes',[])
  if nodes:
   node_ids={n['id'] for n in nodes}
   for edge in s.get('visual_edges',[]):
    if edge['from'] not in node_ids or edge['to'] not in node_ids:errors.append('Invalid visual graph edge: '+path+'#'+s['id'])
 anchors[path]=ids
 m=bad.search(public_copy(page))
 if m:errors.append('Forbidden active copy: '+path+' -> '+m.group(0))
checks['primary_motion_aliases']=list(aliases)

# All primary source URLs must trace to the saved page set or asset source manifest.
source=read('data/source-pages.json')
source_urls={p['url'] for p in source['pages']}
asset_urls={p.get('source_url') for p in manifest['assets']}
for p in primary:
 for s in p['sections']:
  for u in s['source_urls']:
   if u not in source_urls|asset_urls:errors.append('Untraced primary source: '+u)
checks['audited_menu_pages']=len(source['pages'])
checks['providers']=read('data/providers-source.json')['count']

with (ROOT/'data/migration-map.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
old=[r['old_url'] for r in rows]
if len(old)!=len(set(old)):errors.append('Duplicate old URL in migration map')
for row in rows:
 if row['http_action']=='410' and row.get('new_url'):errors.append('410 with a target URL: '+row['old_url'])
 dest=urlsplit(row.get('new_url',''))
 if dest.path in anchors and dest.fragment and dest.fragment not in anchors[dest.path]:
  errors.append('Missing migration anchor: '+row['new_url'])
checks['migration_rows']=len(rows)

# Internal links on authored pages and navigation must resolve, including known anchors.
for p in allpages:
 links=[]
 cta=p.get('primary_cta')
 if isinstance(cta,dict):links.append(cta)
 for s in p['sections']:links+=s.get('cta',[])+s.get('links',[])
 for link in links:
  dest=urlsplit(link.get('href',''))
  if not dest.netloc and dest.path in anchors and dest.fragment and dest.fragment not in anchors[dest.path]:errors.append('Missing CTA anchor: '+link['href'])
nav=read('data/navigation.json')
for link in nav['primary']+nav['actions']+nav['footer']+nav['partners']:
 dest=urlsplit(link['href'])
 if dest.path not in known_paths:errors.append('Unknown navigation route: '+link['href'])
 elif dest.fragment and dest.fragment not in anchors[dest.path]:errors.append('Missing navigation anchor: '+link['href'])

# Validate local documentation links; site route examples start with / and are intentionally future routes.
for p in [ROOT/'README.md',*(ROOT/'docs').glob('*.md'),ROOT/'design/README.md']:
 if not p.exists():continue
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  target=target.strip('<>').split('#')[0]
  if not target or target.startswith(('/','http:','https:','mailto:','tel:','codex:')):continue
  target=unquote(target)
  if not (p.parent/target).exists():errors.append(f'Broken document link: {p.relative_to(ROOT)} -> {target}')

report={'checked_at':'2026-09-10','scope':'Artifact integrity, editorial consistency, and generated frontend source data',
         'status':'pass' if not errors else 'fail','checks':checks,'errors':errors,'warnings':warnings,
         'limitations':['Source existence does not establish current payment availability or product compatibility.',
                        'Accessibility and Core Web Vitals require testing the future implementation.',
                        'Visual design boards were reviewed separately; SVG/PNG are static artifacts.']}
(ROOT/'data/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
