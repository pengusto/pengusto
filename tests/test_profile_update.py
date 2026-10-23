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
    return days,{'public_repos':28,'followers':2},buffer.getvalue()

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
            self.assertEqual(set(changed),set(FILES))
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
            for dark,light in [('city.svg','city-light.svg'),('city-mobile.svg','city-light-mobile.svg'),('scan.svg','scan-light.svg'),('scan-mobile.svg','scan-light-mobile.svg')]:
                import xml.etree.ElementTree as ET
                a=ET.parse(root/'assets'/dark).getroot()
                b=ET.parse(root/'assets'/light).getroot()
                self.assertEqual(list(a.itertext()),list(b.itertext()))
                self.assertIn('#faf7ff',(root/'assets'/light).read_text())
                self.assertNotIn('<filter',(root/'assets'/light).read_text())
            from profile_theme import light_svg
            with self.assertRaisesRegex(ValueError,'missing'):
                light_svg('<svg fill="#123456"/>')

    def test_zero_activity_calendar_is_supported(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);update(root,source=lambda _:fixture(zero=True),now=NOW)
            data=json.loads((root/'github-data.json').read_text())
            self.assertEqual((data['total'],data['active_days'],data['peak']),(0,0,0))

if __name__=='__main__': unittest.main()
