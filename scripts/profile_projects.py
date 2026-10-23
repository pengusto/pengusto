"""Public repository validation and original Landmarks-style SVG cards."""
from datetime import datetime
from html import escape
from pathlib import Path
import math
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

def render_projects(assets, projects):
    if [p['name'] for p in projects]!=list(PROJECT_NAMES):
        raise ValueError('Selected public project order changed')
    for mobile in (False,True):
        height=1510 if mobile else 670
        svg='<defs><linearGradient id="ambient" x2="1" y2="1"><stop stop-color="#432c62" stop-opacity=".3"/><stop offset="1" stop-color="#131119" stop-opacity="0"/></linearGradient></defs>'
        svg+=f'<rect x="1" y="1" width="858" height="{height-2}" rx="18" fill="#131119" stroke="#49375f"/>'
        svg+=f'<rect x="2" y="2" width="856" height="{height-4}" rx="18" fill="url(#ambient)"/>'
        svg+=text(28,45,'PUBLIC PROJECTS / LANDMARKS',24 if mobile else 17,'#bd93f9',700,True)
        if not mobile:svg+=text(830,45,'04 repositories',14,'#a79bb7',mono=True,anchor='end')
        svg+='<path d="M28 65H832" stroke="#49375f"/>'
        for i,p in enumerate(projects):
            x=24 if mobile else 24+(i%2)*416;y=88+i*350 if mobile else 88+(i//2)*281
            cw=812 if mobile else 396;ch=326 if mobile else 262
            svg+=f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="#191320" stroke="#49375f"/>'
            svg+=text(x+20,y+32,'pengusto/'+p['name'],23 if mobile else 14,'#a79bb7',mono=True)
            svg+=f'<path d="M{x} {y+48}H{x+cw}" stroke="#393047"/>'
            svg+=text(x+20,y+91,p['name'],36 if mobile else 23,'#f1edf7',700,True)
            desc=textwrap.wrap(p['description'],width=48 if mobile else 32)
            if len(desc)>3:desc=desc[:3];desc[-1]=desc[-1].rstrip(' .,')+'…'
            for j,line in enumerate(desc):svg+=text(x+20,y+133+j*(34 if mobile else 24),line,27 if mobile else 17)
            langs=list(p['languages'].items());total=sum(v for _,v in langs)
            cx=x+cw-(88 if mobile else 54);cy=y+(156 if mobile else 148);radius=43 if mobile else 31
            circumference=2*math.pi*radius
            svg+=f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#393047" stroke-width="{12 if mobile else 8}"/>'
            offset=0
            for j,(_,count) in enumerate(langs):
                length=count/total*circumference if total else 0
                color=['#bd93f9','#8057a4','#c8c0d5','#624b7d'][min(j,3)]
                svg+=f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="{12 if mobile else 8}" stroke-dasharray="{length:.3f} {circumference-length:.3f}" stroke-dashoffset="{-offset:.3f}" transform="rotate(-90 {cx} {cy})"/>'
                offset+=length
            share=round(langs[0][1]/total*100) if total else 0
            svg+=text(cx,cy+6,str(share)+'%' if total else '—',24 if mobile else 17,'#f1edf7',700,anchor='middle')
            svg+=text(cx,cy+radius+29,'code share',17 if mobile else 11,'#a79bb7',anchor='middle')
            # The description and language chart occupy separate columns.
            topics_y=y+252 if mobile else y+220;tx=x+20
            for topic in p['topics']:
                label=topic if len(topic)<=21 else topic[:20]+'…';size=20 if mobile else 11
                width=len(label)*(12 if mobile else 6.8)+20
                if tx+width>x+cw-16:break
                svg+=f'<rect x="{tx}" y="{topics_y-19 if mobile else topics_y-14}" width="{width}" height="{30 if mobile else 22}" rx="11" fill="#2b223a" stroke="#49375f"/>'
                svg+=text(tx+10,topics_y,label,size,'#bd93f9',mono=True);tx+=width+8
            pushed=datetime.fromisoformat(p['pushed_at'].replace('Z','+00:00')).strftime('%d %b %Y')
            main=langs[0][0] if langs else 'No language data'
            svg+=text(x+20,y+ch-16,f'★ {p["stars"]}   {main}   ·   {pushed}',21 if mobile else 13,'#a79bb7',mono=True)
        label='Public repository landmarks; rings show actual language-byte share, not completion.'
        raw=f'<svg xmlns="http://www.w3.org/2000/svg" width="860" height="{height}" viewBox="0 0 860 {height}" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>{svg}</svg>'
        stem='projects-mobile' if mobile else 'projects'
        light='projects-light-mobile' if mobile else 'projects-light'
        (assets/(stem+'.svg')).write_text(dark_svg(raw));(assets/(light+'.svg')).write_text(light_svg(raw))
