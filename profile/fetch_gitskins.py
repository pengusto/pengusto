"""Fetch selected public GitSkins outputs. The caller stages the complete refresh first."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode,urlsplit,urlunsplit,parse_qsl
import json,xml.etree.ElementTree as ET,hashlib,time
SECTIONS=('hero','projects','heatmap','stats','social','stack')
S='{http://www.w3.org/2000/svg}'
NAMES=('kaplum-studio','push-my-tabs','let-him-grill','penguin-patches')
def fetch(url):
 for attempt in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response:data=response.read(4000001)
   if len(data)>4000000:raise ValueError('Unexpected oversized GitSkins response')
   return data
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)
def validate(data,section):
 svg=ET.fromstring(data)
 if svg.tag!=S+'svg':raise ValueError('Expected SVG section: '+section)
 for n in svg.iter():
  if n.tag.split('}')[-1] in ('script','foreignObject'):raise ValueError('Unexpected active SVG content')
  if any(k.startswith('on') for k in n.attrib):raise ValueError('Unexpected SVG event handler')
  if n.tag==S+'image':
   href=n.get('href') or n.get('{http://www.w3.org/1999/xlink}href','')
   if href and not href.startswith('data:image/'):raise ValueError('Expected self-contained embedded image')
 if section=='projects':
  urls=[n.get('href') for n in svg.iter(S+'a')]
  if urls!=['https://github.com/pengusto/'+name for name in NAMES]:raise ValueError('GitSkins project selection changed; keep previous cards until reviewed')
 return svg
def download(root,fetcher=fetch):
 root=Path(root);(root/'originals').mkdir(exist_ok=True);records=[]
 for section in SECTIONS:
  for mode in ('dark','light'):
   params={'username':'pengusto','theme':'dracula' if mode=='dark' else 'pastel','style':'jet' if section=='heatmap' else 'aura','avatar':'https://avatars.githubusercontent.com/u/106893073?v=4','mode':mode}
   url='https://www.gitskins.com/api/section/'+section+'?'+urlencode(params)
   data=fetcher(url);svg=validate(data,section);path='originals/gitskins-'+section+'-'+mode+'.svg';(root/path).write_bytes(data)
   records.append({'section':section,'mode':mode,'url':url,'file':path,'sha256':hashlib.sha256(data).hexdigest(),'viewBox':svg.get('viewBox'),'bytes':len(data)})
   print(section,mode,svg.get('viewBox'))
 (root/'gitskins-sources.json').write_text(json.dumps(records,indent=2)+'\n')
 download_extras(root,fetcher)
def download_extras(root,fetcher=fetch):
 root=Path(root);records=[]
 for item in json.loads((root/'extra-requests.json').read_text()):
  for mode in ('dark','light'):
   parts=urlsplit(item['url']);params=dict(parse_qsl(parts.query));params['mode']=mode
   url=urlunsplit(parts._replace(query=urlencode(params)))
   data=fetcher(url);svg=validate(data,item['name'])
   path=f"originals/extra-{item['name']}-{mode}.svg";(root/path).write_bytes(data)
   records.append({'name':item['name'],'mode':mode,'url':url,'file':path,'sha256':hashlib.sha256(data).hexdigest(),'viewBox':svg.get('viewBox'),'bytes':len(data)})
 (root/'extra-sources.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':download(Path(__file__).parent)
