"""Original colourful Shields badges and GitSkins project-link chips."""
from html import escape
import json
import xml.etree.ElementTree as E

S='{http://www.w3.org/2000/svg}'

def sections(root):
 records=json.loads((root/'toolkit-sources.json').read_text())
 def badge(item):
  if not (root/item['file']).exists():raise ValueError('Missing badge: '+item['label'])
  return f'<img src="{item["file"]}" alt="{escape(item["label"])}" height="28" align="absmiddle">'
 toolkit='## Creative toolkit\n\n<p align="center">'+' '.join(badge(r) for r in records)+'</p>\n\n'
 contacts=[r for r in json.loads((root/'badge-sources.json').read_text()) if r['group']=='connect']
 links=['<a href="'+escape(r['target'],quote=True)+'">'+badge(r)+'</a>' for r in contacts]
 from extras import SITES
 projects=[]
 for i,(_,label,url) in enumerate(SITES[2:]):
  for mode in ('dark','light'):
   svg=E.parse(root/'assets'/f'fusion-social-{mode}.svg').getroot();scene=svg[-1]
   svg.attrib.update(width='136',height='52',viewBox='0 0 136 52')
   svg.set('aria-label',label+' — website')
   chip=next(n for n in scene if n.get('class')=='aura-chip')
   for n in list(scene):scene.remove(n)
   scene.append(chip);chip.set('transform','translate(-338,-37)');chip.set('style','animation:none;opacity:1')
   rects=list(chip.iter(S+'rect'));rects[0].set('width','130');rects[1].set('width','128')
   icon=chip.find(S+'circle');icon.set('cx','356');icon.set('r','9')
   texts=list(chip.iter(S+'text'));texts[0].set('x','356');texts[0].set('font-size','11');texts[0].text='↗'
   texts[1].set('x','370');texts[1].set('font-size','9');texts[1].set('letter-spacing','.7');texts[1].text='Project'
   texts[2].set('x','370');texts[2].set('font-size','11');texts[2].text=label
   E.ElementTree(svg).write(root/'assets'/f'project-site-{i}-{mode}.svg',encoding='unicode')
  projects.append(f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-site-{i}-dark.svg"><img src="assets/project-site-{i}-light.svg" alt="{label} ↗" width="136" height="52" align="top"></picture></a>')
 connect='## 📫 Let’s Connect\n\n<p align="center">'+' '.join(links)+'</p>\n\n<p align="center">'+' '.join(projects)+'</p>\n\n'
 return toolkit,connect
