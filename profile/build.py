"""Build a local-only profile composition from the owner's assets and selected GitSkins outputs."""
from pathlib import Path
from html import escape
from copy import deepcopy
import xml.etree.ElementTree as E
import shutil,re,sys,textwrap,json,subprocess
ROOT=Path(__file__).resolve().parent;out=ROOT;assets=out/'assets';repo=out/'inputs'
S='{http://www.w3.org/2000/svg}';E.register_namespace('','http://www.w3.org/2000/svg')
originals=out/'originals';originals.mkdir(exist_ok=True)

dark_map={'#38bdf8':'#a78bfa','#1a1d2e':'#171322','#94a3b8':'#bdafd0','#f8f8f2':'#f5efff','#ff79c6':'#c39af6','#8be9fd':'#9f8ef2','#50fa7b':'#d0b6fa'}
light_map={'#f6f8fc':'#faf7ff','#ffffff':'#fefcff','#d7dee8':'#ddd0ee','#475569':'#665575','#0f172a':'#30203f','#3d09d7':'#7545b7','#5823f6':'#8050c2'}
def recolor(raw,theme):
 palette=dark_map if theme=='dark' else light_map
 return re.sub(r'#[0-9a-fA-F]{6}\b',lambda m:palette.get(m[0].lower(),m[0]),raw)
def save(r,p):E.ElementTree(r).write(p,encoding='unicode')
for theme in ('dark','light'):
 for section in ('hero','projects','heatmap','stats','social','stack'):
  raw=(originals/f'gitskins-{section}-{theme}.svg').read_text();raw=recolor(raw,theme)
  if section in ('projects','heatmap','stats','social','stack'):
   stable=E.fromstring(raw)
   for g in stable.iter(S+'g'):
    for anim in list(g):
     if anim.tag==S+'animate' and anim.get('attributeName')=='opacity':
      g.remove(anim);g.set('opacity','1')
   for parent in stable.iter():
    if parent.get('class')=='aura-chip':parent.set('style','animation:none;opacity:1')
    for anim in list(parent):
     if anim.tag==S+'animate' and anim.get('fill')=='freeze' and (anim.get('to') or anim.get('values')) and anim.get('attributeName') in ('opacity','fill-opacity'):
      parent.set(anim.get('attributeName'),anim.get('to') or anim.get('values').split(';')[-1]);parent.remove(anim)
     elif anim.tag==S+'animateTransform' and anim.get('fill')=='freeze' and (anim.get('to') or anim.get('values')):
      parent.set('transform',anim.get('type')+'('+(anim.get('to') or anim.get('values').split(';')[-1])+')');parent.remove(anim)
   raw=E.tostring(stable,encoding='unicode')
  (assets/f'fusion-{section}-{theme}.svg').write_text(raw)
  r=E.fromstring(raw);scene=r[-1]
  if section=='projects':
   # Keep the original card drawing, including metadata and language donuts.
   cards=[deepcopy(n) for n in scene if n.tag==S+'a']
   for i,a in enumerate(cards):
    single=E.Element(S+'svg',{'width':'400','height':'168','viewBox':'0 0 400 168','role':'img','aria-label':a.get('href').split('/')[-1]+' — GitSkins project card'})
    single.append(deepcopy(r[0]));single.append(deepcopy(r[1]));surface=E.SubElement(single,S+'g',{'id':scene.get('id')})
    E.SubElement(surface,S+'rect',{'width':'400','height':'168','rx':'15','fill':'#171322' if theme=='dark' else '#faf7ff'})
    cg=deepcopy(a[0]);cg.set('transform','translate(3,3)');cg.set('opacity','1');surface.append(cg)
    name=a.get('href').split('/')[-1];save(single,assets/f'project-{name}-{theme}.svg')
   for n in list(scene):scene.remove(n)
   r.attrib.update(width='440',height='804',viewBox='0 0 440 804')
   E.SubElement(scene,S+'rect',{'width':'440','height':'804','rx':'20','fill':'#171322' if theme=='dark' else '#faf7ff','stroke':'#a78bfa' if theme=='dark' else '#ddd0ee'})
   label=E.SubElement(scene,S+'text',{'x':'22','y':'29','font-family':'monospace','font-size':'13','letter-spacing':'2','fill':'#a78bfa' if theme=='dark' else '#7545b7'});label.text='PROJECTS.LIST / PENGUSTO'
   for i,a in enumerate(cards):
    g=a[0];g.set('transform',f'translate(22,{49+i*185})');g.set('opacity','1')
    for n in list(g):
     if n.tag==S+'animate' and n.attrib.get('attributeName')=='opacity':g.remove(n)
    # Slightly larger small text on narrow displays; original content/layout remains.
    for n in g.iter(S+'text'):
     size=float(n.get('font-size','12'))
     if size<12:n.set('font-size',str(size+0.8))
    scene.append(a)
   save(r,assets/f'fusion-projects-{theme}-mobile.svg')
  elif section=='hero':
   # Reflow the original avatar/name/chips rather than shrinking the desktop hero.
   r.attrib.update(width='440',height='315',viewBox='0 0 440 315')
   for n in list(scene):
    tag=n.tag.split('}')[-1]
    if tag=='ellipse':
     n.set('cx',str(float(n.get('cx','0'))*.51));n.set('cy',str(float(n.get('cy','0'))*1.3))
    elif tag=='rect':
     if n.get('x')=='26':n.attrib.update(x='15',y='15',width='410',height='285')
     elif n.get('x')=='0.5':n.attrib.update(width='439',height='314')
     else:n.attrib.update(width='440',height='315')
    elif tag=='text':
     x=n.get('x');value=n.text or ''
     if x=='735':
      n.set('x','376');n.set('y','80' if 'TOTAL' not in value else '99');n.set('font-size','26' if 'TOTAL' not in value else '8')
     elif value=='@pengusto':n.attrib.update(x='164',y='66',**{'font-size':'11','letter-spacing':'1.5'})
     elif value=='Pengusto':n.attrib.update(x='161',y='106',**{'font-size':'33'})
     else:scene.remove(n)
    elif tag=='circle' and n.get('cx')=='735':scene.remove(n)
    elif tag=='g' and n.get('transform','').startswith('rotate'):scene.remove(n)
    elif tag=='path':scene.remove(n)
   for i,g in enumerate([n for n in scene if n.get('class')=='aura-chip']):
    g.set('style','animation:none;opacity:1')
    scene.remove(g)
    wrapper=E.SubElement(scene,S+'g',{'transform':f'translate({28+(i%2)*192-(46+i*126)},{234+(i//2)*35-166})'})
    wrapper.append(g)
   bio='AI agents, local-first tools and developer workflows. Useful tools. Thoughtful interactions.'
   for j,line in enumerate(textwrap.wrap(bio,46)):
    n=E.SubElement(scene,S+'text',{'x':'28','y':str(153+j*21),'font-family':'Arial,sans-serif','font-size':'14','fill':'#bdafd0' if theme=='dark' else '#665575'});n.text=line
   save(r,assets/f'fusion-hero-{theme}-mobile.svg')
# Reflow the extra original sections for narrow screens.
for theme in ('dark','light'):
 for section in ('stats','stack','heatmap','social'):
  r=E.parse(assets/f'fusion-{section}-{theme}.svg').getroot();scene=r[-1];nodes=list(scene)
  height={'stats':390,'stack':430,'heatmap':345,'social':126}[section]
  r.attrib.update(width='440',height=str(height),viewBox=f'0 0 440 {height}')
  for n in list(scene):scene.remove(n)
  E.SubElement(scene,S+'rect',{'x':'1','y':'1','width':'438','height':str(height-2),'rx':'20','fill':'#171322' if theme=='dark' else '#faf7ff','stroke':'#685188' if theme=='dark' else '#ddd0ee'})
  def put(node,x=0,y=0):
   w=E.SubElement(scene,S+'g',{'transform':f'translate({x},{y})'});w.append(node)
  texts=[n for n in nodes if n.tag==S+'text']
  if section in ('stats','stack'):
   title=deepcopy(texts[0]);title.attrib.update(x='24',y='42',**{'font-size':'25'});scene.append(title)
   sub=deepcopy(texts[1]);sub.attrib.update(x='24',y='66',**{'font-size':'11'});scene.append(sub)
   chips=[n for n in nodes if n.get('class')=='aura-chip']
   for i,g in enumerate(chips):
    g.set('style','animation:none;opacity:1')
    if section=='stats':put(g,28+(i%2)*204-(34+i*204),98+(i//2)*136-92)
    else:
     for n in g:
      if n.tag==S+'circle':n.set('cx','32')
      elif n.tag==S+'text':
       n.set('x','48' if n.get('text-anchor')!='end' else '405');n.set('font-size','16')
      elif n.tag==S+'rect':
       old=float(n.get('width','0'));n.set('x','28');n.set('y',str(float(n.get('y','0'))+27));n.set('width',str(old*380/466))
     put(g,0,10+i*29)
  elif section=='heatmap':
   for i,n in enumerate(texts[:2]):n.attrib.update(x='24',y=str(40+i*26),**{'font-size':'23' if i==0 else '14'});scene.append(n)
   cells=[n for n in nodes if n.tag==S+'g' and n.get('transform','').startswith('translate') and len(n)>0 and n[0].tag==S+'rect']
   xs=sorted({float(re.match(r'translate\(([^,]+),',n.get('transform'))[1]) for n in cells})
   for n in cells:
    x,y=map(float,re.findall(r'[-\d.]+',n.get('transform')));week=xs.index(x);half,col=divmod(week,27)
    n.set('transform',f'translate({30+col*14},{103+(y-105.5)+half*128})');scene.append(n)
   footer=E.SubElement(scene,S+'text',{'x':'24','y':'326','font-family':'Arial,sans-serif','font-size':'11','fill':'#bdafd0' if theme=='dark' else '#665575'});footer.text='Last 12 months · oldest weeks first'
  else:
   chip=next(n for n in nodes if n.get('class')=='aura-chip');chip.set('style','animation:none;opacity:1');put(chip,-210,0)
  save(r,assets/f'fusion-{section}-{theme}-mobile.svg')

# Copy approved imagery byte-for-byte.
for name in ('profile-banner-purple.png','profile-banner-purple-mobile.png','profile-banner-purple-light.png','profile-banner-purple-light-mobile.png','kaplum-demo.gif'):
 shutil.copy2(repo/'assets'/name,assets/name)
# Match the owner's existing city to the local lavender palette; data/layout unchanged.
sys.path.insert(0,str(out/'city_renderer'));from profile_theme import DARK,LIGHT
for suffix,palette in [('',DARK),('-light',LIGHT)]:
 inv={v:k for k,v in palette.items()}
 for mobile in ('','-mobile'):
  src=repo/'assets'/('city'+suffix+mobile+'.svg');raw=src.read_text()
  if not suffix:
   raw=re.sub(r'#[0-9a-fA-F]{6}\b',lambda m:inv.get(m[0].lower(),m[0]),raw)
   raw=raw.replace('#131119','#171322').replace('#bd93f9','#a78bfa')
  else:raw=raw.replace('#f7f8ff','#faf7ff').replace('#eef1fb','#f6effc')
  (assets/src.name).write_text(raw)
# Linked titles below the full projects image remain native README links on GitHub.
for stem in ('link-03','link-05','link-06','link-07','link-28'):
 for suffix in ('','-light'):
  raw=(repo/'assets'/(stem+suffix+'.svg')).read_text()
  raw=raw.replace('#a4b0ff','#b89aef').replace('#5047a8','#7545b7')
  (assets/(stem+suffix+'.svg')).write_text(raw)

def picture(stem,alt):
 return f'''<picture>
<source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="assets/{stem}-dark-mobile.svg">
<source media="(prefers-color-scheme: light) and (max-width: 600px)" srcset="assets/{stem}-light-mobile.svg">
<source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.svg">
<img src="assets/{stem}-light.svg" alt="{alt}" width="860">
</picture>'''
existing=(repo/'README.md').read_text();banner=existing[:existing.index('</picture>')+10]
city_start=existing.index('## The city');city_end=existing.index('## Selected work');city=existing[city_start:city_end];city=re.sub(r'\?v=[^" ]+','',city)
def label(stem,url,alt,width):
 return f'<a href="{url}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/{stem}.svg"><img src="assets/{stem}-light.svg" alt="{alt}" width="{width}" height="25" align="absmiddle"></picture></a>'
cards=[]
for name,title in [('kaplum-studio','Kaplum Studio'),('push-my-tabs','Push My Tabs'),('let-him-grill','Let Him Grill'),('penguin-patches','Penguin Patches')]:
 cards.append(f'<a href="https://github.com/pengusto/{name}"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/project-{name}-dark.svg"><img src="assets/project-{name}-light.svg" alt="{title} — open repository" width="400" align="top"></picture></a>')
from extras import build as build_extras
from toolkit import sections as toolkit_sections
trail=build_extras(out,picture)
toolkit,contacts=toolkit_sections(out)
hero=picture('fusion-hero','Pengusto — original GitSkins hero, locally matched lavender palette.')
portrait='<p align="center">'+picture('extra-franky-circle','Franky portrait with orbit ring').replace('\n','').replace('width="860"','width="240"')+'</p>'
terminal='<p align="center">'+picture('extra-pengusto-terminal','Pengusto terminal').replace('\n','').replace('width="860"','width="640"')+'</p>'
selected='## Selected work\n\n[![Actual Kaplum Studio lesson recording — click to try it](assets/kaplum-demo.gif)](https://pengusto.github.io/kaplum-studio/#course/square)\n\n'+label('link-03','https://pengusto.github.io/kaplum-studio/#course/square','Try the real lesson →',159)+'\n\n<p align="center">'+'\n'.join(cards)+'</p>\n\n'
about='<details>\n<summary>About this preview</summary>\n\nOriginal GitSkins hero, project cards, wordmark and snake, adapted locally. Penguin banner and actual Kaplum lesson recording retained. Purple city uses actual public GitHub calendar data. Project cards link individually to their repositories. The Creative toolkit uses original colourful Shields badges with logos; project-language percentages describe code composition. Saved SVGs are refreshed by the prepared local updater; scheduled publication remains inactive. Nothing is pushed.\n\n</details>\n'
md='\n\n'.join((banner,hero,portrait,terminal,selected,city,trail,toolkit,contacts,about))
(out/'README.md').write_text(md)
(out/'NOTES.md').write_text('''# Local fusion preview

Nothing purchased, committed, pushed or published. The online profile is unchanged.

- Retained the approved penguin banner and real Kaplum GIF byte-for-byte.
- Retained the existing city data and geometry; matched local lavender fills/strokes.
- Removed the duplicate system scan, long introduction and workbench from this new preview only.
- Hero and projects: actual GitSkins section outputs, not our earlier custom substitute. Official Dracula (dark) and Pastel (light) themes were used. The dark API output still contained cyan accents; these were replaced explicitly in local SVGs, with no CSS filters.
- Each project is extracted from the original GitSkins card into a separate linked SVG. GitHub-native 400px images wrap naturally; no custom README CSS, JavaScript, image maps or links inside embedded SVGs are needed. Mobile hero, stats, heatmap, stack and social compositions reuse the original elements with readable reflow. Activity calendar halves preserve the original cell order.
- Local project fade-in is frozen at full opacity for reliable image embedding. Mobile chip positioning uses outer groups because the original chip animation otherwise overrides SVG transforms.
- The four project donut percentages belong to the GitSkins original and indicate language-byte proportions. They are not project progress.
- Untouched downloads: originals/. Exact source URLs: gitskins-sources.json.
- Run `python refresh.py --write` to refresh the local files. Downloads and rendering finish in temporary staging before replacing output; a failed refresh preserves the previous preview. The daily workflow is an inactive `.yml.example` template until explicitly installed and published. GitSkins must remain reachable for future refreshes; saved local SVGs continue displaying through an outage. The currently published profile is unchanged.
- No renderer/server source code was exported. Keep original attribution and examine service dependencies before any publication.
''')
# Render entirely locally: the README can contain owner-supplied contact details.
if '--assets-only' in sys.argv:
 print('Local assets and README generated.');sys.exit(0)
p=subprocess.run(['pandoc','--from=gfm','--to=html5','--wrap=none'],input=md,capture_output=True,text=True,check=True)
rendered=p.stdout;(out/'preview-rendered.html').write_text(rendered)
from preview_pages import write_pages
styles=''.join(f'<link rel="stylesheet" href="assets/{p.name}">' for p in assets.glob('github*.css'));write_pages(out,rendered,styles)
print(out/'index.html')
