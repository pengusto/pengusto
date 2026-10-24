"""Additional user-selected original widgets, retained separately for comparison."""
from html import escape
from pathlib import Path
import json
import re
from copy import deepcopy
import xml.etree.ElementTree as E

S='{http://www.w3.org/2000/svg}'
TITLES={
 'pengusto-terminal':'Pengusto terminal',
 'contribution-trail':'Contribution trail',
 'wow-banner':'WOW PROFILE · PENGUSTO · LIVE',
}
SITES=[('GitHub','@pengusto','https://github.com/pengusto'),('Website','kikaio.de','https://kikaio.de'),('Project','Kaplum Studio','https://pengusto.github.io/kaplum-studio/'),('Project','Push My Tabs','https://pengusto.github.io/push-my-tabs/'),('Project','Let Him Grill','https://pengusto.github.io/let-him-grill/'),('Project','Cookbook','https://pengusto.github.io/cookbook/'),('Project','Worldfolio','https://pengusto.github.io/worldfolio/')]

def build(root,picture):
 root=Path(root);assets=root/'assets';sections=[]
 for name,title in TITLES.items():
  for mode in ('dark','light'):
   src=root/'originals'/f'extra-{name}-{mode}.svg'
   if not src.exists():raise ValueError('Missing selected widget: '+str(src))
   raw=src.read_text()
   if name=='contribution-trail':
    palette={'#042f2e':'#171322','#134e4a':'#2b1d3c','#ccfbf1':'#f1e6ff','#41d8c5':'#b18ae9','#2dd4bf':'#a78bfa','#5eead4':'#d4b5ff','#96e9df':'#d9c5f5','#22d3ee':'#ad91ed','#4f8cff':'#8b73d3','#4ade80':'#c6a0f3', '#40d8c6':'#b292d4','#26baa8':'#8860b7','#209c8e':'#7545a5','#10b7d0':'#9872c9','#23be5b':'#a57fce','#004ee0':'#8056b4','#f6f8fc':'#faf7ff','#475569':'#665575','#0f172a':'#30203f','#d7dee8':'#ddd0ee'}
    raw=re.sub(r'#[0-9a-fA-F]{6}\b',lambda m:palette.get(m[0].lower(),m[0]),raw)
   svg=E.fromstring(raw)
   # Finish entry fades; preserve ongoing decorative motion and source colours.
   for parent in svg.iter():
    if name=='wow-banner' and parent.get('class') in ('portrait','name'):
     parent.set('style','animation:none;opacity:1')
    for child in list(parent):
     if child.tag==S+'animate' and child.get('attributeName') in ('opacity','fill-opacity','width','height') and child.get('fill')=='freeze':
      final=child.get('to') or child.get('values','').split(';')[-1]
      if final:parent.set(child.get('attributeName'),final);parent.remove(child)
   for suffix in ('','-mobile'):
    E.ElementTree(svg).write(assets/f'extra-{name}-{mode}{suffix}.svg',encoding='unicode')
   if name=='wow-banner':
    circle=E.Element(S+'svg',{'width':'320','height':'320','viewBox':'590 50 400 400','role':'img','aria-label':'Franky portrait with orbit ring'})
    for node in svg:
     if node.tag in (S+'defs',S+'style') or node.get('class')=='orbit' or node.get('transform')=='translate(630 98)':circle.append(deepcopy(node))
    for suffix in ('','-mobile'):E.ElementTree(circle).write(assets/f'extra-franky-circle-{mode}{suffix}.svg',encoding='unicode')
  if name=='contribution-trail':sections.append('## '+title+'\n\n'+picture('extra-'+name,title)+'\n')
 return '\n'.join(sections)+'\n'
