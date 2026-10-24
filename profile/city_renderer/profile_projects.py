"""Public repository validation and original Landmarks-style SVG cards."""
from datetime import datetime
from html import escape
from pathlib import Path
import textwrap
from profile_theme import dark_svg, light_svg

PROJECT_NAMES=('kaplum-studio','push-my-tabs','let-him-grill','penguin-patches')
DISPLAY_NAMES={'kaplum-studio':'Kaplum Studio','push-my-tabs':'Push My Tabs','let-him-grill':'Let Him Grill','penguin-patches':'Penguin Patches'}

def validate_project(meta, languages, name):
    if meta.get('full_name')!='pengusto/'+name or meta.get('private') is not False:
        raise ValueError('Expected selected public repository: '+name)
    if meta.get('html_url')!='https://github.com/pengusto/'+name:
        raise ValueError('Unexpected project URL')
    if type(meta.get('stargazers_count')) is not int or meta['stargazers_count']<0:
        raise ValueError('Invalid star count')
    if not isinstance(languages,dict) or any(not isinstance(k,str) or type(v) is not int or v<=0 for k,v in languages.items()):
        raise ValueError('Invalid public language bytes')
    topics=meta.get('topics',[])
    if not isinstance(topics,list) or any(not isinstance(t,str) for t in topics):
        raise ValueError('Invalid project topics')
    datetime.fromisoformat(meta['pushed_at'].replace('Z','+00:00'))
    description=meta.get('description') or ''
    if not isinstance(description,str): raise ValueError('Invalid description')
    return {'name':name,'description':description,'url':meta['html_url'],'topics':topics[:3],
            'stars':meta['stargazers_count'],'pushed_at':meta['pushed_at'],
            'languages':dict(sorted(languages.items(),key=lambda kv:(-kv[1],kv[0])))}

def text(x,y,value,size=16,color='#c8c0d5',weight=400,mono=False,anchor='start'):
    font='monospace' if mono else 'Arial,sans-serif'
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'

PROJECT_FILES=tuple('assets/project-'+name+suffix+'.svg' for name in PROJECT_NAMES for suffix in ('','-light'))

def render_projects(assets, projects):
    if [p['name'] for p in projects]!=list(PROJECT_NAMES):
        raise ValueError('Selected public project order changed')
    for p in projects:
        svg='<rect x="1" y="1" width="418" height="178" rx="14" fill="#131119" stroke="#49375f"/>'
        svg+=text(22,30,'PUBLIC PROJECT / '+p['name'],10,'#a79bb7',mono=True)
        svg+=text(22,65,DISPLAY_NAMES[p['name']],25,'#f1edf7',700)
        svg+=text(396,65,'↗',23,'#bd93f9',anchor='end')
        lines=textwrap.wrap(p['description'],width=49)
        if len(lines)>2:lines=lines[:2];lines[-1]=lines[-1].rstrip(' .,')+'…'
        for j,line in enumerate(lines):svg+=text(22,96+j*21,line,14)
        svg+='<path d="M22 137H398" stroke="#393047"/>'
        langs=list(p['languages']);main=langs[0] if langs else 'Code'
        pushed=datetime.fromisoformat(p['pushed_at'].replace('Z','+00:00')).strftime('%d %b %Y')
        svg+=text(22,161,main+' / '+(p['topics'][0] if p['topics'] else 'public repository'),10,'#bd93f9',mono=True)
        svg+=text(398,161,f'★ {p["stars"]}  ·  {pushed}',10,'#a79bb7',mono=True,anchor='end')
        label=DISPLAY_NAMES[p['name']]+': '+p['description']
        raw=f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="180" viewBox="0 0 420 180" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{svg}</svg>'
        stem='project-'+p['name']
        (assets/(stem+'.svg')).write_text(dark_svg(raw));(assets/(stem+'-light.svg')).write_text(light_svg(raw))
