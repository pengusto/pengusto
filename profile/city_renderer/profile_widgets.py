"""Portable purple profile renderer; no network, Git writes or workspace dependencies."""
from pathlib import Path
from html import escape
import json, math, io, re
import xml.etree.ElementTree as E
from copy import deepcopy
from PIL import Image, ImageFilter
from datetime import date, timedelta
from profile_theme import dark_svg, light_svg
from profile_projects import render_projects
def t(x,y,s,size=20,color='#d6c9e8',weight=400,anchor='start'):
 return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>'
def frame(w,h,inner,label):
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(label)}"><title>{escape(label)}</title><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="#131119" stroke="#9e75d6"/>{inner}</svg>'
def animate_city_svg(raw):
 """Grow all three cuboid faces from a two-unit tile; retain final geometry."""
 S='{http://www.w3.org/2000/svg}';E.register_namespace('',S[1:-1]);root=E.fromstring(raw)
 if root.find(S+'style') is not None:return raw
 style=E.SubElement(root,S+'style');style.text='.city-still{display:none}@media(prefers-reduced-motion:reduce){.city-growing{display:none}.city-still{display:inline}}'
 for building in list(root.iter(S+'g')):
  title=building.find(S+'title');faces=building.findall(S+'polygon')
  if title is None or len(faces)!=3 or 'contributions' not in (title.text or ''):continue
  right,left,top=faces
  points=lambda face:[list(map(float,p.split(','))) for p in face.get('points').split()]
  rp,lp,tp=map(points,faces);base_y=rp[2][1];dy=rp[3][1]-base_y
  starts=[[[rp[0][0],rp[3][1]-2],[rp[1][0],base_y-2],rp[2],rp[3]],
          [[lp[0][0],lp[3][1]-2],[lp[1][0],lp[2][1]-2],lp[2],lp[3]],
          [[tp[0][0],base_y-2-dy],[tp[1][0],base_y-2],[tp[2][0],base_y-2+dy],[tp[3][0],base_y-2]]]
  still=E.SubElement(building,S+'g',{'class':'city-still'});growing=E.SubElement(building,S+'g',{'class':'city-growing'})
  for face,start in zip(faces,starts):
   still.append(deepcopy(face));building.remove(face);growing.append(face)
   E.SubElement(face,S+'animate',{'attributeName':'points','from':' '.join(f'{x},{y}' for x,y in start),'to':face.get('points'),'dur':'3s','begin':'0s','fill':'freeze','repeatCount':'1'})
 return E.tostring(root,encoding='unicode')
def daily_average(days):
 end=max(date.fromisoformat(d['date']) for d in days)
 window=[d for d in days if end-timedelta(days=364)<=date.fromisoformat(d['date'])<=end]
 return sum(d['count'] for d in window)/len(window)
def average_label(days):
 return 'Ø '+f'{daily_average(days):.1f}'.replace('.',',')+' Beiträge pro Tag'
def render(out, days, profile, avatar, fetched_at, input_hash):
 a=out/'assets';a.mkdir(parents=True,exist_ok=True)
 total=sum(d['count'] for d in days);active=sum(d['count']>0 for d in days);peak=max(d['count'] for d in days)
 data={'source':'https://github.com/users/pengusto/contributions','fetched_at':fetched_at,'input_hash':input_hash,'days':days,'total':total,'active_days':active,'peak':peak,'average_per_day':daily_average(days),'public_repos':profile['public_repos'],'followers':profile['followers'],'projects':profile['projects']}
 (out/'github-data.json').write_text(json.dumps(data,indent=2)+'\n')
 # Independent isometric calendar: one cuboid per real contribution-calendar day.
 inner='<defs><radialGradient id="glow"><stop stop-color="#9d61e8" stop-opacity=".28"/><stop offset="1" stop-color="#131119" stop-opacity="0"/></radialGradient></defs><ellipse cx="480" cy="230" rx="350" ry="170" fill="url(#glow)"/>'
 display_total=f'{total/1000:.1f}K' if total>=1000 else str(total)
 inner+=t(28,42,'CONTRIBUTION CITY',12,'#c4a1ff',700).replace('Arial,sans-serif','monospace').replace('font-size=', 'letter-spacing="2" font-size=')
 inner+=t(28,79,display_total,36,'#f4edff',700)+t(28,101,'contributions in the last year',13,'#c4a1ff',700)
 inner+=t(28,132,f'{active} active days',12,'#c4a1ff',700)+t(28,151,f'Busiest day: {peak}',12,'#c4a1ff',700)
 inner+=t(28,172,average_label(days),12,'#c4a1ff',700)
 first=date.fromisoformat(days[0]['date']);buildings=[]
 for day in days:
  delta=(date.fromisoformat(day['date'])-first).days;week,weekday=divmod(delta,7)
  x=160+week*10.1+weekday*19.5;y=184+week*3.05-weekday*8.5
  height=2 if day['count']==0 else 8+math.log1p(day['count'])/math.log1p(peak)*92
  buildings.append((y,x,height,day))
 city_scene=''
 for y,x,h,day in sorted(buildings):
  dx,dy=8.3,3.8
  top=f'{x},{y-h-dy} {x+dx},{y-h} {x},{y-h+dy} {x-dx},{y-h}'
  right=f'{x},{y-h+dy} {x+dx},{y-h} {x+dx},{y} {x},{y+dy}'
  left=f'{x-dx},{y-h} {x},{y-h+dy} {x},{y+dy} {x-dx},{y}'
  level=day['level'];tops=['#2b223a','#67458b','#9767c7','#c197f0','#e7caff'];rights=['#211a2c','#432c62','#614080','#8057a4','#a97ad0'];lefts=['#191420','#322044','#49305e','#63417e','#80539f']
  city_scene+=f'<g><title>{day["date"]}: {day["count"]} contributions</title><polygon points="{right}" fill="{rights[level]}"/><polygon points="{left}" fill="{lefts[level]}"/><polygon points="{top}" fill="{tops[level]}" stroke="#c4a1ff" stroke-opacity=".12" stroke-width=".5"/></g>'
 inner+=city_scene
 inner+=f'<rect x="170" y="190" width="605" height="1" fill="#d3b0ff" opacity=".16"><animate attributeName="y" values="155;355;155" dur="9s" repeatCount="indefinite"/></rect>'
 inner+=t(28,391,'@pengusto',12,'#bd93f9',700)
 (a/'city.svg').write_text(animate_city_svg(frame(860,420,inner,'Pengusto contribution city: '+str(total)+' actual contributions across '+str(len(days))+' calendar days. Purple isometric view.')))
 # Mobile city has larger summary labels and its own taller composition.
 mobile=re.search(r'(<defs>.*?</defs>)',inner).group(1)
 mobile+=t(28,47,'CONTRIBUTION CITY',20,'#c4a1ff',700).replace('Arial,sans-serif','monospace').replace('font-size=', 'letter-spacing="3" font-size=')
 mobile+=t(28,105,display_total,54,'#f4edff',700)+t(28,142,'contributions in the last year',27,'#c4a1ff',700)
 mobile+=t(28,189,f'{active} active days',24,'#c4a1ff',700)+t(28,222,f'Busiest day: {peak}',24,'#c4a1ff',700)
 mobile+=t(28,255,average_label(days),24,'#c4a1ff',700)
 mobile+=f'<g transform="translate(-45 190) scale(1.1)">{city_scene}</g>'
 mobile+=t(28,643,'@pengusto',23,'#bd93f9',700)
 (a/'city-mobile.svg').write_text(animate_city_svg(frame(860,680,mobile,'Pengusto contribution city — mobile. '+str(total)+' actual contributions.')))
 # ASCII portrait derived from the unmodified public avatar embedded in the earlier draft.
 im=Image.open(io.BytesIO(avatar)).convert('L').resize((44,27)).filter(ImageFilter.FIND_EDGES)
 ramp=' .,:;+*#%@';ascii_rows=[''.join(ramp[p*(len(ramp)-1)//256] for p in list(im.crop((0,y,44,y+1)).get_flattened_data())) for y in range(27)]
 for mobile in [False,True]:
  h=1100 if mobile else 500
  inner='<path d="M0 44H860" stroke="#77549f"/>'+t(430,29,'pengusto@github ~ $ ./profile-scan --updated',15,'#c4a1ff',anchor='middle')
  for i in range(3):inner+=f'<circle cx="{20+i*15}" cy="22" r="4" fill="{["#754e9c","#a77ad7","#d5b3ff"][i]}"/>'
  ax=100 if mobile else 30;ay=100;px=25 if mobile else 430;py=555 if mobile else 72;pw=810 if mobile else 405;ph=510 if mobile else 395
  inner+=f'<rect x="{25 if mobile else 15}" y="62" width="{810 if mobile else 400}" height="{450 if mobile else 405}" rx="10" fill="#191320" stroke="#664480"/>'
  for i,row in enumerate(ascii_rows):
   if i in (0,26):row=' '*44
   else:row=' '+row[1:-1]+' '
   inner+=f'<text xml:space="preserve" x="{ax}" y="{ay+i*(14 if not mobile else 15)}" fill="{["#a779d6","#bc91ee","#d9b6ff"][i%3]}" font-family="monospace" font-size="{14 if not mobile else 20}">{escape(row)}</text>'
  inner+=f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="10" fill="#191320" stroke="#664480"/>'
  entries=[('Handle','@pengusto'),('Focus','Agents · tools · learning'),('Repositories',profile['public_repos']),('Contributions',f'{total:,}'),('Active days',active),('Busiest day',peak),('Followers',profile['followers']),('Updated',fetched_at[:10]),('Contact','github.com/pengusto')]
  for i,(key,value) in enumerate(entries):
   row_y=py+43+i*(51 if mobile else 39);size=34 if mobile else 16
   inner+=t(px+20,row_y,key,size,'#b98ae9',700)+t(px+(295 if mobile else 160),row_y,value,size,'#e3d6f3')
  inner+=f'<rect x="{25 if mobile else 15}" y="90" width="{810 if mobile else 400}" height="2" fill="#d3aaff" opacity=".36"><animate attributeName="y" values="80;450;80" dur="6s" repeatCount="indefinite"/></rect>'
  inner+=t(838,h-12,'CUSTOM / UPDATED GITHUB DATA',10,'#a897bd',anchor='end')
  (a/('scan-mobile.svg' if mobile else 'scan.svg')).write_text(frame(860,h,inner,'Pengusto system scan. Updated public GitHub data. '+str(total)+' contributions, '+str(active)+' active days.'))

 # Both themes derive from the same validated data and layout.
 for dark_name,light_name in [('city.svg','city-light.svg'),('city-mobile.svg','city-light-mobile.svg'),('scan.svg','scan-light.svg'),('scan-mobile.svg','scan-light-mobile.svg')]:
  raw=(a/dark_name).read_text()
  (a/dark_name).write_text(dark_svg(raw))
  (a/light_name).write_text(light_svg(raw))
 render_projects(a,profile['projects'])
