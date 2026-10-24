"""Refresh boundaries: no partial failed updates, no-op updates and native card links."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from urllib.parse import urlparse,parse_qs
from html.parser import HTMLParser
import io,json,shutil,sys,tempfile,unittest,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import refresh,fetch_gitskins
from PIL import Image

def fixture_source(_):
 now=datetime.now(timezone.utc).date();days=[{'date':str(now-timedelta(days=364-i)),'count':2 if i%5==0 else 0,'level':1 if i%5==0 else 0} for i in range(365)]
 p={'public_repos':16,'followers':2,'projects':[{'name':n,'url':'https://github.com/pengusto/'+n,'description':'A useful public project','topics':['tools'],'stars':0,'languages':{'Python':1},'pushed_at':'2026-10-24T00:00:00Z'} for n in fetch_gitskins.NAMES]}
 b=io.BytesIO();Image.new('RGB',(12,12),'#a78bfa').save(b,format='PNG');return days,p,b.getvalue()
def source(url):
 records=json.loads((ROOT/'gitskins-sources.json').read_text())+json.loads((ROOT/'extra-sources.json').read_text())
 record=next(r for r in records if r['url']==url)
 return (ROOT/record['file']).read_bytes()

def snap(root):return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
class RefreshTests(unittest.TestCase):
 def test_failed_fetch_keeps_all_previous_outputs(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'kit';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','.refresh-lock'))
   before=snap(root);calls=[]
   def fail(url):
    calls.append(url)
    if len(calls)==14:raise RuntimeError('Simulated additional widget outage')
    return source(url)
   with self.assertRaises(RuntimeError):refresh.refresh(root,write=True,fetcher=fail,city_source=fixture_source)
   self.assertEqual(snap(root),before);self.assertFalse((root/'.refresh-lock').exists())
 def test_dry_run_then_success_and_repeat_noop(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'kit';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','.refresh-lock'))
   before=snap(root);refresh.refresh(root,fetcher=source,city_source=fixture_source);self.assertEqual(snap(root),before)
   refresh.refresh(root,write=True,fetcher=source,city_source=fixture_source)
   before=snap(root);self.assertEqual(refresh.refresh(root,write=True,fetcher=source,city_source=fixture_source),[]);self.assertEqual(snap(root),before)
 def test_calendar_render_failure_preserves_previous_outputs(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'kit';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','.refresh-lock'));before=snap(root)
   def broken(today):
    days,profile,_=fixture_source(today);return days,profile,b'not an avatar'
   with self.assertRaises(Exception):refresh.refresh(root,write=True,fetcher=source,city_source=broken)
   self.assertEqual(snap(root),before)
 def test_private_or_changed_project_target_is_rejected(self):
  raw=(ROOT/'originals/gitskins-projects-dark.svg').read_bytes()
  with self.assertRaises(ValueError):fetch_gitskins.validate(raw.replace(b'https://github.com/pengusto/kaplum-studio',b'https://github.com/another/private'),'projects')
 def test_separate_native_card_and_social_links(self):
  class Links(HTMLParser):
   def __init__(self):super().__init__();self.link=None;self.cards={};self.social=[]
   def handle_starttag(self,tag,attrs):
    a=dict(attrs)
    if tag=='a':self.link=a.get('href')
    if tag=='img' and a.get('src','').startswith('assets/project-') and not a.get('src','').startswith('assets/project-site-'):self.cards[a['src']]=self.link
    if tag=='img' and a.get('alt')=='GitHub':self.social.append(self.link)
   def handle_endtag(self,tag):
    if tag=='a':self.link=None
  for filename in ('README.md','preview-rendered.html'):
   p=Links();p.feed((ROOT/filename).read_text())
   self.assertEqual(p.cards,{'assets/project-'+n+'-light.svg':'https://github.com/pengusto/'+n for n in fetch_gitskins.NAMES});self.assertEqual(p.social,['https://github.com/pengusto'])
 def test_selected_variants_and_live_banner_remain_distinct(self):
  records=json.loads((ROOT/'extra-sources.json').read_text())
  self.assertEqual(len(records),18)
  self.assertEqual(len({r['url'] for r in records}),18)
  self.assertIn('variant=living-identity',next(r['url'] for r in records if r['name']=='wow-banner'))
  self.assertIn('style=terminal',next(r['url'] for r in records if r['name']=='neofetch-portrait'))
  self.assertIn('color=1',next(r['url'] for r in records if r['name']=='color-portrait'))
  for mode in ('dark','light'):
   svg=E.parse(ROOT/f'assets/extra-wow-banner-{mode}.svg').getroot()
   identities=[n for n in svg.iter() if n.get('class') in ('portrait','name')]
   self.assertTrue(identities)
   self.assertTrue(all(n.get('style')=='animation:none;opacity:1' for n in identities))
  for filename in ('README.md','preview-rendered.html'):
   markup=(ROOT/filename).read_text()
   for removed in ('extra-color-portrait','extra-neofetch-portrait','extra-terminal-toolchain'):
    self.assertNotIn(removed,markup)
   self.assertNotIn('assets/extra-wow-banner',markup)
   self.assertNotIn('assets/extra-original-city',markup)
   self.assertNotIn('comparison-',markup)
   self.assertNotIn('extra-showcase-',markup)
   self.assertLess(markup.index('fusion-hero'),markup.index('extra-franky-circle'))
   self.assertLess(markup.index('extra-franky-circle'),markup.index('extra-pengusto-terminal'))
   self.assertLess(markup.index('project-kaplum-studio'),markup.index('assets/city'))
   self.assertNotIn('fusion-stats-',markup);self.assertNotIn('fusion-stack-',markup)
   self.assertNotIn('## Building in public',markup);self.assertNotIn('## Visit',markup)
   self.assertNotIn('fusion-heatmap-',markup)
   if filename=='preview-rendered.html':self.assertNotIn('\n## Contribution trail',markup)
   for i in range(4):self.assertIn(f'assets/project-site-{i}-light.svg',markup)
 def test_badges_and_owner_contact_targets(self):
  records=json.loads((ROOT/'badge-sources.json').read_text())
  self.assertEqual(len([r for r in records if r['group']=='tech']),19)
  self.assertEqual(len([r for r in records if r['group']=='creative']),8)
  contacts={r['label']:r['target'] for r in records if r['group']=='connect'}
  self.assertEqual(contacts,{'Portfolio':'https://kikaio.de','GitHub':'https://github.com/pengusto','LinkedIn':'https://www.linkedin.com/in/enis-uysal/','Email':'mailto:hello@kikaio.de'})
  colourful=json.loads((ROOT/'toolkit-sources.json').read_text())
  self.assertEqual(len(colourful),24)
  self.assertEqual(len({r['label'].casefold() for r in colourful}),24)
  for r in colourful:self.assertIn('style=for-the-badge',r['url'])
  for filename in ('README.md','preview-rendered.html'):
   markup=(ROOT/filename).read_text()
   for r in colourful:self.assertIn(r['file'],markup)
   for r in records:
    if r['group']=='connect':self.assertIn(r['file'],markup)
   self.assertIn('Creative toolkit',markup);self.assertNotIn('🛠️ Tech Stack',markup)
   self.assertEqual(markup.count('alt="React"'),1)
   self.assertEqual(markup.count('alt="Python"'),1)
   self.assertIn('alt="TensorFlow Lite"',markup);self.assertIn('alt="MCP"',markup)
   self.assertNotIn('sachit1751@gmail.com',markup);self.assertNotIn('you@example.com',markup)
   for target in contacts.values():self.assertIn(target,markup)
 def test_circle_extraction_and_trail_palette(self):
  S='{http://www.w3.org/2000/svg}'
  for mode in ('dark','light'):
   circle=E.parse(ROOT/f'assets/extra-franky-circle-{mode}.svg').getroot()
   self.assertEqual(circle.get('viewBox'),'590 50 400 400')
   self.assertEqual(len([n for n in circle.iter(S+'g') if n.get('class')=='orbit']),1)
   self.assertEqual(len([n for n in circle.iter(S+'g') if n.get('class')=='portrait']),1)
   self.assertFalse(any(n.get('class')=='name' for n in circle.iter()))
   trail=(ROOT/f'assets/extra-contribution-trail-{mode}.svg').read_text()
   self.assertNotIn('#41d8c5',trail);self.assertNotIn('#40d8c6',trail)
   self.assertIn('#b18ae9' if mode=='dark' else '#b292d4',trail)
 def test_daily_average_uses_rolling_calendar_days_and_updates(self):
  sys.path.insert(0,str(ROOT/'city_renderer'))
  from profile_widgets import daily_average,average_label
  end=datetime(2026,10,24).date()
  days=[{'date':str(end-timedelta(days=370-i)),'count':9999 if i<6 else 2} for i in range(371)]
  self.assertEqual(daily_average(days),2)
  self.assertEqual(average_label(days),'Ø 2,0 Beiträge pro Tag')
  days[-1]['count']=367
  self.assertEqual(daily_average(days),3)
  self.assertEqual(average_label(days),'Ø 3,0 Beiträge pro Tag')
  actual=json.loads((ROOT/'inputs/github-data.json').read_text())
  for name in ('city.svg','city-light.svg','city-mobile.svg','city-light-mobile.svg'):
   raw=(ROOT/'assets'/name).read_text()
   self.assertIn(average_label(actual['days']),raw)
   svg=E.fromstring(raw)
   self.assertIn(average_label(actual['days']),[n.text for n in svg.iter('{http://www.w3.org/2000/svg}text')])
  authored=(ROOT/'README.md').read_text()
  self.assertLess(authored.index('## The city'),authored.index('## Contribution trail'))
  self.assertLess(authored.index('## Contribution trail'),authored.index('## Creative toolkit'))
 def test_purple_city_builds_without_changing_final_geometry(self):
  S='{http://www.w3.org/2000/svg}'
  days=json.loads((ROOT/'inputs/github-data.json').read_text())['days']
  for name in ('city.svg','city-light.svg','city-mobile.svg','city-light-mobile.svg'):
   root=E.parse(ROOT/'assets'/name).getroot()
   growing=[g for g in root.iter(S+'g') if g.get('class')=='city-growing']
   still=[g for g in root.iter(S+'g') if g.get('class')=='city-still']
   self.assertEqual(len(growing),len(days));self.assertEqual(len(still),len(days))
   self.assertIn('prefers-reduced-motion:reduce',root.find(S+'style').text)
   for moving,fixed in zip(growing,still):
    for face,fallback in zip(moving,fixed):
     anim=face.find(S+'animate')
     self.assertEqual(anim.get('to'),fallback.get('points'))
     self.assertEqual(face.get('points'),fallback.get('points'))
     self.assertEqual(anim.get('dur'),'3s');self.assertEqual(anim.get('fill'),'freeze')
     self.assertEqual(len(anim.get('from').split()),4)
 def test_mobile_heatmap_preserves_all_calendar_cells(self):
  S='{http://www.w3.org/2000/svg}'
  def cells(path):
   r=E.parse(path).getroot();return [n for n in list(r)[-1] if n.tag==S+'g' and len(n)>0 and n[0].tag==S+'rect' and n.get('transform','').startswith('translate')]
  for mode in ('dark','light'):
   desktop=cells(ROOT/f'assets/fusion-heatmap-{mode}.svg');mobile=cells(ROOT/f'assets/fusion-heatmap-{mode}-mobile.svg');self.assertEqual(len(desktop),len(mobile))
   for cell in desktop+mobile:
    self.assertGreater(float(cell[0].get('fill-opacity','0')),0)
    self.assertEqual(cell[0].get('transform'),'scale(1)')
if __name__=='__main__':unittest.main()
