"""Regression checks for data loss, changed calendar markup and needless commits."""
import io
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from PIL import Image
from update_profile import FILES, parse_calendar, update

NOW=datetime(2026,10,23,12,tzinfo=timezone.utc)

def fixture(zero=False):
    days=[{'date':str(NOW.date()-timedelta(days=364-i)),'count':0 if zero or i%5 else 2,'level':0 if zero or i%5 else 1} for i in range(365)]
    buffer=io.BytesIO(); Image.new('RGB',(12,12),'#bd93f9').save(buffer,format='PNG')
    projects=[{'name':name,'description':'A public project with a useful purpose.','url':'https://github.com/pengusto/'+name,'topics':['developer-tools','learning'],'stars':i,'pushed_at':'2026-10-23T12:00:00Z','languages':{'JavaScript':80,'HTML':20}} for i,name in enumerate(('kaplum-studio','push-my-tabs','let-him-grill','penguin-patches'))]
    return days,{'public_repos':28,'followers':2,'projects':projects},buffer.getvalue()

def snapshot(root):
    return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}

class UpdateTests(unittest.TestCase):
    def test_calendar_counts_and_changed_markup(self):
        days,_,_=fixture()
        html=''.join(f'<td data-date="{d["date"]}" id="d{i}" data-level="{d["level"]}"></td><tool-tip for="d{i}">{str(d["count"])+" contributions" if d["count"] else "No contributions"} on a day.</tool-tip>' for i,d in enumerate(days))
        self.assertEqual(parse_calendar(html,NOW.date()),days)
        with self.assertRaises(ValueError):
            parse_calendar(html.replace('tool-tip','new-tooltip'),NOW.date())
        with self.assertRaisesRegex(ValueError,'stale'):
            parse_calendar(html,NOW.date()+timedelta(days=3))

    def test_dry_run_writes_nothing_and_repeat_is_noop(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'README.md').write_text('Preserve this')
            original=snapshot(root)
            source=lambda _:fixture()
            self.assertEqual(set(update(root,dry_run=True,source=source,now=NOW)),set(FILES))
            self.assertEqual(snapshot(root),original)
            self.assertEqual(set(update(root,source=source,now=NOW)),set(FILES))
            before=snapshot(root)
            self.assertEqual(update(root,source=source,now=NOW+timedelta(hours=2)),[])
            self.assertEqual(snapshot(root),before)

    def test_data_changes_refresh_metrics_and_both_scan_variants(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); update(root,source=lambda _:fixture(),now=NOW)
            days,profile,avatar=fixture();days[-1]['count']=33;days[-1]['level']=4
            changed=update(root,source=lambda _:(days,profile,avatar),now=NOW+timedelta(hours=1))
            self.assertEqual(set(changed),{name for name in FILES if '/project-' not in name})
            manifest=json.loads((root/'github-data.json').read_text())
            self.assertEqual(manifest['total'],sum(d['count'] for d in days))
            for name in ['scan.svg','scan-mobile.svg','scan-light.svg','scan-light-mobile.svg']:
                self.assertIn(f"{manifest['total']:,}",(root/'assets'/name).read_text())

    def test_fetch_or_avatar_failure_keeps_previous_outputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);update(root,source=lambda _:fixture(),now=NOW);before=snapshot(root)
            def fail(_): raise RuntimeError('Simulated GitHub outage')
            with self.assertRaises(RuntimeError): update(root,source=fail,now=NOW)
            self.assertEqual(snapshot(root),before)
            days,profile,_=fixture()
            with self.assertRaises(Exception):
                update(root,source=lambda _:(days,profile,b'not an image'),now=NOW)
            self.assertEqual(snapshot(root),before)
            self.assertFalse(list(root.parent.glob('.profile-update-*')))

    def test_light_palette_preserves_data_and_readable_text(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); update(root,source=lambda _:fixture(),now=NOW)
            for dark,light in [('city.svg','city-light.svg'),('city-mobile.svg','city-light-mobile.svg'),('scan.svg','scan-light.svg'),('scan-mobile.svg','scan-light-mobile.svg'),('project-kaplum-studio.svg','project-kaplum-studio-light.svg')]:
                import xml.etree.ElementTree as ET
                a=ET.parse(root/'assets'/dark).getroot()
                b=ET.parse(root/'assets'/light).getroot()
                self.assertEqual(list(a.itertext()),list(b.itertext()))
                self.assertIn('#f7f8ff',(root/'assets'/light).read_text())
                self.assertNotIn('<filter',(root/'assets'/light).read_text())
            from profile_theme import light_svg
            with self.assertRaisesRegex(ValueError,'missing'):
                light_svg('<svg fill="#123456"/>')

    def test_zero_activity_calendar_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);update(root,source=lambda _:fixture(zero=True),now=NOW)
            data=json.loads((root/'github-data.json').read_text())
            self.assertEqual((data['total'],data['active_days'],data['peak']),(0,0,0))


    def test_project_stats_refresh_all_variants_without_completion_claims(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); update(root,source=lambda _:fixture(),now=NOW)
            days,profile,avatar=fixture();profile['projects'][0]['stars']=17
            profile['projects'][0]['languages']={'JavaScript':55,'HTML':45}
            changed=update(root,source=lambda _:(days,profile,avatar),now=NOW)
            self.assertEqual(set(changed),{'assets/project-kaplum-studio.svg','assets/project-kaplum-studio-light.svg','github-data.json'})
            for name in ('project-kaplum-studio.svg','project-kaplum-studio-light.svg'):
                svg=(root/'assets'/name).read_text()
                self.assertIn('JavaScript',svg);self.assertIn('★ 17',svg)
                self.assertNotIn('code share',svg)
                self.assertNotIn('%',svg)
                self.assertNotIn('completion', ''.join(__import__('re').findall(r'<text[^>]*>(.*?)</text>',svg)))
            self.assertEqual(update(root,source=lambda _:(days,profile,avatar),now=NOW),[])

    def test_rejects_private_or_unexpected_project_data(self):
        from profile_projects import validate_project
        meta={'full_name':'pengusto/kaplum-studio','private':False,'html_url':'https://github.com/pengusto/kaplum-studio','stargazers_count':1,'pushed_at':'2026-10-23T12:00:00Z','topics':[]}
        self.assertEqual(validate_project(meta,{},'kaplum-studio')['name'],'kaplum-studio')
        for bad in ({**meta,'private':True},{**meta,'full_name':'another/kaplum-studio'},{**meta,'stargazers_count':-1}):
            with self.assertRaises(ValueError):validate_project(bad,{'JavaScript':3},'kaplum-studio')
        with self.assertRaises(ValueError):validate_project(meta,{'JavaScript':-3},'kaplum-studio')

    def test_city_has_handle_and_workflow_stages_every_generated_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);update(root,source=lambda _:fixture(),now=NOW)
            for name in ('city.svg','city-mobile.svg','city-light.svg','city-light-mobile.svg'):
                self.assertIn('@pengusto',(root/'assets'/name).read_text())
        workflow=(Path(__file__).parents[1]/'.github/workflows/refresh-profile.yml').read_text()
        for name in FILES:self.assertIn(name,workflow)

    def test_each_project_card_has_its_own_repository_link(self):
        from html.parser import HTMLParser
        class Cards(HTMLParser):
            def __init__(self): super().__init__(); self.href=None; self.cards={}
            def handle_starttag(self,tag,attrs):
                a=dict(attrs)
                if tag=='a': self.href=a.get('href')
                if tag=='img' and a.get('src','').startswith('profile/assets/project-') and not a.get('src','').startswith('profile/assets/project-site-'):
                    self.cards[a['src'].split('?')[0]]=self.href
            def handle_endtag(self,tag):
                if tag=='a':self.href=None
        parser=Cards();parser.feed((Path(__file__).parents[1]/'README.md').read_text())
        from profile_projects import PROJECT_NAMES
        self.assertEqual(parser.cards,{'profile/assets/project-'+n+'-light.svg':'https://github.com/pengusto/'+n for n in PROJECT_NAMES})

    def test_city_uses_last_year_labels_without_visible_dates(self):
        import xml.etree.ElementTree as ET
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);days,profile,avatar=fixture();days[-1]['count']=2930-sum(d['count'] for d in days[:-1])
            update(root,source=lambda _:(days,profile,avatar),now=NOW)
            for name in ('city.svg','city-mobile.svg','city-light.svg','city-light-mobile.svg'):
                svg=ET.parse(root/'assets'/name).getroot()
                labels=[n.text for n in svg.iter('{http://www.w3.org/2000/svg}text')]
                self.assertIn('CONTRIBUTION CITY',labels)
                self.assertIn('2.9K',labels)
                self.assertIn('contributions in the last year',labels)
                self.assertIn('@pengusto',labels)
                self.assertFalse(any(__import__('re').search(r'\d{4}-\d{2}-\d{2}',v or '') for v in labels))
                self.assertIn('2930',svg.attrib['aria-label'])

    def test_batched_upstream_acceptance_keeps_original_pr_status(self):
        data=json.loads((Path(__file__).parents[1]/'docs/merged-contributions.json').read_text())
        wallos=[x for x in data['items'] if x['repository']=='ellite/Wallos']
        self.assertEqual({x['number'] for x in wallos},{1260,1263})
        for entry in wallos:
            self.assertFalse(entry['merged'])
            self.assertEqual(entry['state'],'closed')
            self.assertEqual(entry['accepted_via']['number'],1267)
            self.assertTrue(entry['accepted_via']['merged'])
            self.assertIn('#issuecomment-',entry['maintainer_confirmation'])

if __name__=='__main__': unittest.main()
